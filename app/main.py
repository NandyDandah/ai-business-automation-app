import csv
import hmac
import os
import time
from collections import defaultdict, deque
from html import escape as escape_html
from threading import Lock
from typing import Literal
from urllib.parse import urlparse
from io import StringIO

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, Field, root_validator
from sqlalchemy.orm import Session

load_dotenv()

from app.database import SessionLocal, Automation, Prospect, create_tables
from app.ai_service import analyse_business_message
from app.security import (
    LOGIN_CSRF_MAX_AGE, SESSION_MAX_AGE, create_login_csrf, create_session,
    get_session_csrf_token, load_auth_config, verify_api_token, verify_login_csrf, verify_password,
)
from app.ui import DASHBOARD_PAGE, HOME_PAGE, PIPELINE_PAGE, build_login_page, build_protected_page

AUTH_CONFIG = load_auth_config()

app = FastAPI(title="AI Business Automation App")


_LOGIN_ATTEMPTS = defaultdict(deque)
_LOGIN_LOCK = Lock()
_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}

def _auth_method(request: Request):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        scheme, sep, token = authorization.partition(" ")
        return "bearer" if scheme.lower() == "bearer" and sep and verify_api_token(token, AUTH_CONFIG) else None
    return "session" if get_session_csrf_token(request.cookies.get("app_session", ""), AUTH_CONFIG) else None


def _security_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net data:; "
        "img-src 'self' data:; connect-src 'self'; form-action 'self'; base-uri 'self'; frame-ancestors 'none'"
    )
    if AUTH_CONFIG.cookie_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


@app.middleware("http")
async def protect_routes(request: Request, call_next):
    if request.url.path == "/login":
        response = await call_next(request)
    else:
        method = _auth_method(request)
        if method is None:
            if request.method == "GET" and "text/html" in request.headers.get("accept", ""):
                response = RedirectResponse("/login", status_code=303)
            else:
                response = JSONResponse({"detail": "Authentication required"}, status_code=401,
                                        headers={"WWW-Authenticate": "Bearer"})
        elif method == "session" and request.method in _MUTATING:
            expected = get_session_csrf_token(request.cookies.get("app_session", ""), AUTH_CONFIG)
            if not expected or not hmac.compare_digest(expected, request.headers.get("x-csrf-token", "")):
                response = JSONResponse({"detail": "CSRF validation failed"}, status_code=403)
            else:
                response = await call_next(request)
        else:
            response = await call_next(request)
    return _security_headers(response)


def _protected_page(markup: str, request: Request):
    token = get_session_csrf_token(request.cookies.get("app_session", ""), AUTH_CONFIG)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    return HTMLResponse(build_protected_page(markup, request.url.path, token))

def _login_page(message="", code=200):
    token = create_login_csrf(AUTH_CONFIG)
    response = HTMLResponse(build_login_page(token, message), status_code=code)
    response.set_cookie("app_login_csrf", token, max_age=LOGIN_CSRF_MAX_AGE, httponly=True,
                        secure=AUTH_CONFIG.cookie_secure, samesite="strict", path="/")
    return response

@app.get("/login", response_class=HTMLResponse)
def login_form():
    return _login_page()


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, password: str = Form(..., min_length=1, max_length=1024),
          csrf_token: str = Form(...)):
    cookie = request.cookies.get("app_login_csrf", "")
    if not verify_login_csrf(cookie, csrf_token, AUTH_CONFIG):
        return _login_page("Sign-in form expired. Please try again.", 403)
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _LOGIN_LOCK:
        attempts = _LOGIN_ATTEMPTS[key]
        while attempts and now - attempts[0] > 900:
            attempts.popleft()
        if len(attempts) >= 5:
            return _login_page("Too many attempts. Wait 15 minutes and try again.", 429)
    if not verify_password(password, AUTH_CONFIG.password_hash):
        with _LOGIN_LOCK:
            _LOGIN_ATTEMPTS[key].append(now)
        return _login_page("The password is incorrect.", 401)
    with _LOGIN_LOCK:
        _LOGIN_ATTEMPTS.pop(key, None)
    session, _ = create_session(AUTH_CONFIG)
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("app_session", session, max_age=SESSION_MAX_AGE, httponly=True,
                        secure=AUTH_CONFIG.cookie_secure, samesite="strict", path="/")
    response.delete_cookie("app_login_csrf", path="/", httponly=True,
                           secure=AUTH_CONFIG.cookie_secure, samesite="strict")
    return response


@app.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("app_session", path="/", httponly=True,
                           secure=AUTH_CONFIG.cookie_secure, samesite="strict")
    return response


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version="1.0.0", routes=app.routes)
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
        "type": "http", "scheme": "bearer", "bearerFormat": "API token"
    }
    schema["security"] = [{"BearerAuth": []}]
    for operation in schema.get("paths", {}).get("/login", {}).values():
        operation["security"] = []
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

create_tables()

class AutomationRequest(BaseModel):
    message: str
    email: str = ""

class ProspectInput(BaseModel):
    business_name: str = Field(default="", max_length=200)
    industry: str = Field(default="", max_length=120)
    business_type: str = Field(default="", max_length=120)
    website: str = Field(default="", max_length=500)
    city: str = Field(default="", max_length=120)
    region: str = Field(default="", max_length=120)
    country: str = Field(default="", max_length=120)
    postal_code: str = Field(default="", max_length=32)
    business_email: str = Field(default="", max_length=320)
    business_phone: str = Field(default="", max_length=80)
    contact_name: str = Field(default="", max_length=160)
    contact_role: str = Field(default="", max_length=160)
    source_url: str = Field(min_length=8, max_length=1000)
    contact_source_url: str = Field(default="", max_length=1000)
    fit_score: int = Field(default=0, ge=0, le=100)
    fit_summary: str = Field(default="", max_length=2000)
    # Backward-compatible names accepted from the original clinic API.
    clinic_name: str = Field(default="", max_length=200)
    town: str = Field(default="", max_length=120)
    postcode: str = Field(default="", max_length=32)
    public_email: str = Field(default="", max_length=320)
    phone: str = Field(default="", max_length=80)

    @root_validator(pre=True)
    def copy_legacy_business_fields(cls, values):
        values = dict(values or {})
        for current, legacy in (
            ("business_name", "clinic_name"),
            ("city", "town"),
            ("postal_code", "postcode"),
            ("business_email", "public_email"),
            ("business_phone", "phone"),
        ):
            if not values.get(current) and values.get(legacy):
                values[current] = values[legacy]
        return values

    @root_validator(skip_on_failure=True)
    def require_business_name(cls, values):
        if not values.get("business_name", "").strip():
            raise ValueError("business_name is required")
        return values


class ProspectBatch(BaseModel):
    businesses: list[ProspectInput] = Field(default_factory=list, max_length=50)
    prospects: list[ProspectInput] = Field(default_factory=list, max_length=50)

    @root_validator(pre=True)
    def copy_legacy_batch_field(cls, values):
        values = dict(values or {})
        if not values.get("businesses") and values.get("prospects"):
            values["businesses"] = values["prospects"]
        return values

    @root_validator(skip_on_failure=True)
    def require_records(cls, values):
        if not values.get("businesses"):
            raise ValueError("businesses must contain between 1 and 50 records")
        if len(values["businesses"]) > 50:
            raise ValueError("businesses may contain at most 50 records")
        return values


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _protected_page(HOME_PAGE, request)

@app.post("/automate")
def automate(request: AutomationRequest, db: Session = Depends(get_db)):
    ai_result = analyse_business_message(request.message)

    record = Automation(
        customer_email=request.email,
        customer_message=request.message,
        category=ai_result["category"],
        priority=ai_result["priority"],
        ai_reply=ai_result["reply"],
        lead_score=ai_result["lead_score"]
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "success": True,
        "id": record.id,
        "category": record.category,
        "priority": record.priority,
        "lead_score": record.lead_score,
        "ai_reply": record.ai_reply
    }

@app.get("/history")
def history(db: Session = Depends(get_db)):
    records = db.query(Automation).order_by(Automation.id.desc()).all()

    return [
        {
            "id": r.id,
            "customer_email": r.customer_email,
            "customer_message": r.customer_message,
            "category": r.category,
            "priority": r.priority,
            "status": r.status,
            "lead_score": r.lead_score,
            "follow_up_date": r.follow_up_date,
            "notes": r.notes,
            "ai_reply": r.ai_reply,
            "created_at": str(r.created_at)
        }
        for r in records
    ]

@app.delete("/history/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Automation).filter(Automation.id == record_id).first()

    if not record:
        return {"message": "Record not found"}

    db.delete(record)
    db.commit()

    return {"message": "Deleted"}

@app.put("/history/{record_id}/status")
def update_status(record_id: int, new_status: Literal["New", "Contacted", "Closed"], db: Session = Depends(get_db)):
    record = db.query(Automation).filter(Automation.id == record_id).first()

    if not record:
        return {"message": "Record not found"}

    record.status = new_status
    db.commit()

    return {"message": "Status updated"}

@app.put("/history/{record_id}/notes")
def update_notes(record_id: int, notes: str = "", db: Session = Depends(get_db)):
    record = db.query(Automation).filter(Automation.id == record_id).first()

    if not record:
        return {"message": "Record not found"}

    record.notes = notes
    db.commit()

    return {"message": "Notes updated"}

@app.put("/history/{record_id}/follow-up")
def update_follow_up(record_id: int, follow_up_date: str = "", db: Session = Depends(get_db)):
    record = db.query(Automation).filter(Automation.id == record_id).first()

    if not record:
        return {"message": "Record not found"}

    record.follow_up_date = follow_up_date
    db.commit()

    return {"message": "Follow-up updated"}

@app.get("/export")
def export_records(db: Session = Depends(get_db)):
    records = db.query(Automation).order_by(Automation.id.desc()).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Email", "Message", "Category", "Priority", "Status",
        "Lead Score", "Follow-up Date", "Notes", "AI Reply", "Created At"
    ])

    for r in records:
        writer.writerow([
            r.id, r.customer_email, r.customer_message, r.category, r.priority,
            r.status, r.lead_score, r.follow_up_date, r.notes, r.ai_reply, r.created_at
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=automation_history.csv"}
    )

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return _protected_page(DASHBOARD_PAGE, request)

@app.get("/pipeline", response_class=HTMLResponse)
def pipeline(request: Request):
    return _protected_page(PIPELINE_PAGE, request)

def _prospect_fingerprint(item: ProspectInput) -> str:
    website = item.website.strip()
    host = urlparse(website if "://" in website else "https://" + website).hostname or ""
    host = host.lower().removeprefix("www.")
    location = " ".join(
        " ".join((item.country, item.region, item.postal_code or item.city))
        .upper()
        .split()
    )
    if not host:
        host = item.business_name.strip().lower()
    return f"{host}|{location}"


def _prospect_dict(record: Prospect):
    return {
        "id": record.id,
        "business_name": record.business_name,
        "industry": record.industry or "",
        "business_type": record.business_type or "",
        "website": record.website,
        "city": record.city,
        "region": record.region or "",
        "country": record.country or "",
        "postal_code": record.postal_code,
        "business_email": record.business_email,
        "business_phone": record.business_phone,
        "contact_name": record.contact_name,
        "contact_role": record.contact_role,
        "source_url": record.source_url,
        "contact_source_url": record.contact_source_url,
        "fit_score": record.fit_score,
        "fit_summary": record.fit_summary,
        "status": record.status,
        "created_at": record.created_at.isoformat() if record.created_at else "",
        # Keep old response keys so existing agents and integrations still work.
        "clinic_name": record.business_name,
        "town": record.city,
        "postcode": record.postal_code,
        "public_email": record.business_email,
        "phone": record.business_phone,
    }


@app.post("/businesses/batch")
@app.post("/prospects/batch")
def save_businesses(payload: ProspectBatch, db: Session = Depends(get_db)):
    existing = {row[0] for row in db.query(Prospect.fingerprint).all()}
    created = []
    duplicates = 0
    for item in payload.businesses:
        fingerprint = _prospect_fingerprint(item)
        if fingerprint in existing:
            duplicates += 1
            continue
        record = Prospect(
            business_name=item.business_name.strip(),
            industry=item.industry.strip(),
            business_type=item.business_type.strip(),
            website=item.website.strip(),
            city=item.city.strip(),
            region=item.region.strip(),
            country=item.country.strip(),
            postal_code=item.postal_code.strip(),
            business_email=item.business_email.strip(),
            business_phone=item.business_phone.strip(),
            contact_name=item.contact_name.strip(),
            contact_role=item.contact_role.strip(),
            source_url=item.source_url.strip(),
            contact_source_url=item.contact_source_url.strip(),
            fit_score=item.fit_score,
            fit_summary=item.fit_summary.strip(),
            fingerprint=fingerprint,
        )
        db.add(record)
        existing.add(fingerprint)
        created.append(record)
    db.commit()
    return {"created": len(created), "duplicates": duplicates, "ids": [record.id for record in created]}


@app.get("/businesses")
@app.get("/prospects")
def list_businesses(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    records = db.query(Prospect).order_by(Prospect.id.desc()).limit(limit).all()
    return [_prospect_dict(record) for record in records]


@app.delete("/businesses/{record_id}")
@app.delete("/prospects/{record_id}")
def delete_business(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Prospect).filter(Prospect.id == record_id).first()
    if not record:
        return {"deleted": False, "message": "Prospect not found"}
    db.delete(record)
    db.commit()
    return {"deleted": True}



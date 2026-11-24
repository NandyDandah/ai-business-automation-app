import csv
import hmac
import os
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from html import escape as escape_html
from threading import Lock
from typing import Literal, Optional
from urllib.parse import urlparse
from io import StringIO

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, Field, root_validator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

load_dotenv()

from app.database import (
    SessionLocal, Automation, Campaign, CampaignProspect, HomeownerInquiry, Prospect, create_tables,
)
from app.ai_service import AIProviderError, analyse_business_message
from app.prospecting import ProspectingError, discover_openstreetmap_businesses, draft_outreach_messages
from app.simulation import build_demo_simulation, one_business_timeline, simulate_business_fit
from app.security import (
    LOGIN_CSRF_MAX_AGE, SESSION_MAX_AGE, create_login_csrf, create_session,
    create_public_form_csrf, get_session_csrf_token, load_auth_config, verify_api_token,
    verify_login_csrf, verify_password, verify_public_form_csrf,
)
from app.ui import (
    BUSINESS_DATABASE_PAGE, CAMPAIGNS_PAGE, DASHBOARD_PAGE, HOME_PAGE, PIPELINE_PAGE, RETROFIT_INQUIRIES_PAGE,
    build_login_page, build_protected_page, build_public_privacy_page, build_public_retrofit_page,
    build_retrofit_thanks_page,
)

AUTH_CONFIG = load_auth_config()

app = FastAPI(title="AI Business Automation App")


_LOGIN_ATTEMPTS = defaultdict(deque)
_LOGIN_LOCK = Lock()
_PUBLIC_INQUIRY_ATTEMPTS = defaultdict(deque)
_PUBLIC_INQUIRY_LOCK = Lock()
_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
_PUBLIC_PATHS = {"/login", "/retrofit", "/privacy", "/healthz"}
_PUBLIC_POST_PATHS = {"/retrofit/enquiries"}


def _retrofit_config():
    """Require explicit ownership, notice, contact, and retention settings."""
    requested = os.getenv("PUBLIC_ENQUIRY_ENABLED", "false").strip().lower() in {"1", "true", "yes"}
    controller = os.getenv("PUBLIC_ENQUIRY_CONTROLLER_NAME", "").strip()
    contact_email = os.getenv("PUBLIC_ENQUIRY_CONTACT_EMAIL", "").strip()
    privacy_url = os.getenv("PUBLIC_ENQUIRY_PRIVACY_URL", "").strip()
    close_at_raw = os.getenv("PUBLIC_ENQUIRY_CLOSE_AT", "").strip()
    try:
        retention_days = int(os.getenv("PUBLIC_ENQUIRY_RETENTION_DAYS", "0"))
    except ValueError:
        retention_days = 0
    email_ok = bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", contact_email))
    parsed_privacy = urlparse(privacy_url)
    privacy_ok = parsed_privacy.scheme == "https" and bool(parsed_privacy.netloc)
    close_at = None
    close_at_ok = True
    if close_at_raw:
        try:
            close_at = datetime.fromisoformat(close_at_raw.replace("Z", "+00:00"))
            if close_at.tzinfo is None:
                close_at = close_at.replace(tzinfo=timezone.utc)
            close_at = close_at.astimezone(timezone.utc)
        except ValueError:
            close_at_ok = False
    within_pilot_window = close_at is None or datetime.now(timezone.utc) < close_at
    ready = (
        requested and bool(controller) and email_ok and privacy_ok
        and 1 <= retention_days <= 365 and close_at_ok and within_pilot_window
    )
    return {
        "enabled": ready,
        "controller": controller,
        "contact_email": contact_email,
        "privacy_url": privacy_url,
        "retention_days": retention_days,
        "close_at": close_at,
        "close_date": close_at.strftime("%d %B %Y").lstrip("0") if close_at else "",
    }


def _purge_expired_inquiries(db: Session):
    deleted = db.query(HomeownerInquiry).filter(HomeownerInquiry.expires_at <= datetime.utcnow()).delete(synchronize_session=False)
    if deleted:
        db.commit()


@app.on_event("startup")
def purge_expired_inquiries_on_startup():
    db = SessionLocal()
    try:
        _purge_expired_inquiries(db)
    finally:
        db.close()

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
    if request.url.path in _PUBLIC_PATHS or (request.url.path in _PUBLIC_POST_PATHS and request.method == "POST"):
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
    for path in ("/login", "/retrofit", "/retrofit/enquiries", "/privacy", "/healthz"):
        for operation in schema.get("paths", {}).get(path, {}).values():
            operation["security"] = []
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

create_tables()

class AutomationRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    email: str = Field(default="", max_length=320)

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
    enriched_email: str = Field(default="", max_length=320)
    enriched_phone: str = Field(default="", max_length=80)
    enriched_contact_name: str = Field(default="", max_length=160)
    enriched_contact_role: str = Field(default="", max_length=160)
    enrichment_provider: str = Field(default="", max_length=80)
    enrichment_status: str = Field(default="", max_length=80)
    enrichment_confidence: str = Field(default="", max_length=80)
    enrichment_source_url: str = Field(default="", max_length=1000)
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


class BusinessEnrichmentInput(BaseModel):
    enrichment_provider: str = Field(min_length=1, max_length=80)
    enriched_email: Optional[str] = Field(default=None, max_length=320)
    enriched_phone: Optional[str] = Field(default=None, max_length=80)
    enriched_contact_name: Optional[str] = Field(default=None, max_length=160)
    enriched_contact_role: Optional[str] = Field(default=None, max_length=160)
    enrichment_status: Optional[str] = Field(default=None, max_length=80)
    enrichment_confidence: Optional[str] = Field(default=None, max_length=80)
    enrichment_source_url: Optional[str] = Field(default=None, max_length=1000)


class CampaignCreateInput(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    industry: str = Field(default="", max_length=120)
    business_type: str = Field(default="", max_length=120)
    region: str = Field(default="", max_length=120)
    country: str = Field(default="", max_length=120)
    offer: str = Field(default="", max_length=3000)
    proof: str = Field(default="", max_length=1500)
    tone: str = Field(default="Professional", max_length=80)
    language: str = Field(default="English", max_length=80)

    @root_validator(skip_on_failure=True)
    def require_campaign_title(cls, values):
        if not values.get("title", "").strip():
            raise ValueError("title is required")
        return values


class CampaignDiscoveryInput(BaseModel):
    business_type: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=120)
    radius_m: Literal[1000, 3000, 5000, 10000] = 5000
    max_results: int = Field(default=20, ge=1, le=40)


class CampaignLeadsInput(BaseModel):
    prospect_ids: list[int] = Field(min_items=1, max_items=50)


class CampaignDraftInput(BaseModel):
    prospect_ids: list[int] = Field(min_items=1, max_items=10)


class CampaignLeadUpdateInput(BaseModel):
    draft_subject: Optional[str] = Field(default=None, max_length=240)
    draft_body: Optional[str] = Field(default=None, max_length=3000)
    draft_status: Optional[Literal["needs_review", "approved", "rejected"]] = None
    pipeline_stage: Optional[Literal["new", "contacted", "replied", "won", "lost"]] = None

    @root_validator(skip_on_failure=True)
    def require_update_value(cls, values):
        if all(value is None for value in values.values()):
            raise ValueError("At least one draft field is required")
        return values


class HomeownerInquiryReview(BaseModel):
    status: Literal["new", "reviewing", "qualified", "matched", "contacted", "survey_booked", "closed"]
    matched_installer_id: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/healthz")
def health_check(db: Session = Depends(get_db)):
    """Public readiness check for Render; confirms the configured database responds."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _protected_page(HOME_PAGE, request)

@app.post("/automate")
def automate(request: AutomationRequest, db: Session = Depends(get_db)):
    try:
        ai_result = analyse_business_message(request.message)
    except AIProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from None

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

@app.get("/prospect-database", response_class=HTMLResponse)
def prospect_database(request: Request):
    return _protected_page(BUSINESS_DATABASE_PAGE, request)


@app.get("/campaigns", response_class=HTMLResponse)
def campaigns_page(request: Request):
    return _protected_page(CAMPAIGNS_PAGE, request)


def _public_retrofit_response(message="", status_code=200):
    settings = _retrofit_config()
    token = create_public_form_csrf(AUTH_CONFIG)
    response = HTMLResponse(
        build_public_retrofit_page(
            token, settings["enabled"], settings["controller"], settings["privacy_url"], message,
            settings["retention_days"], settings["close_date"],
        ),
        status_code=status_code,
    )
    response.set_cookie(
        "public_enquiry_csrf", token, max_age=60 * 60, httponly=True,
        secure=AUTH_CONFIG.cookie_secure, samesite="strict", path="/",
    )
    return response


@app.get("/retrofit", response_class=HTMLResponse)
def public_retrofit_form():
    return _public_retrofit_response()


@app.get("/privacy", response_class=HTMLResponse)
def public_privacy_notice():
    settings = _retrofit_config()
    return HTMLResponse(build_public_privacy_page(
        settings["controller"], settings["contact_email"], settings["retention_days"], settings["close_date"]
    ))


@app.post("/retrofit/enquiries", response_class=HTMLResponse)
def submit_retrofit_enquiry(
    request: Request,
    csrf_token: str = Form(default=""),
    full_name: str = Form(default="", max_length=120),
    email: str = Form(default="", max_length=320),
    phone: str = Form(default="", max_length=40),
    postcode: str = Form(default="", max_length=16),
    property_type: str = Form(default="", max_length=40),
    heating_type: str = Form(default="", max_length=40),
    ownership: str = Form(default="", max_length=40),
    timeframe: str = Form(default="", max_length=40),
    consent_contact: bool = Form(default=False),
    consent_share: bool = Form(default=False),
    company: str = Form(default="", max_length=200),
    db: Session = Depends(get_db),
):
    settings = _retrofit_config()
    if not settings["enabled"]:
        return _public_retrofit_response(status_code=503)
    cookie = request.cookies.get("public_enquiry_csrf", "")
    if not verify_public_form_csrf(cookie, csrf_token, AUTH_CONFIG):
        return _public_retrofit_response("This form expired. Please review and submit it again.", 403)
    # Hidden honeypot: silently accept automated spam without storing anything.
    if company.strip():
        return HTMLResponse(build_retrofit_thanks_page(settings["controller"], settings["contact_email"]))

    full_name = " ".join(full_name.split())
    email = email.strip().lower()
    phone = phone.strip()
    postcode = " ".join(postcode.upper().split())
    phone_digits = re.sub(r"\D", "", phone)
    allowed_values = {
        "property_type": {"House", "Bungalow", "Flat", "Other", "Not sure"},
        "heating_type": {"Gas", "Oil", "Electric", "LPG", "Solid fuel", "Other", "Not sure"},
        "ownership": {"Owner occupier", "Landlord", "Buying the property", "Other"},
        "timeframe": {"Just exploring", "Within 3 months", "3 to 6 months", "More than 6 months"},
    }
    values = {
        "property_type": property_type,
        "heating_type": heating_type,
        "ownership": ownership,
        "timeframe": timeframe,
    }
    valid_postcode = re.fullmatch(r"[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}", postcode)
    valid_email = not email or re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email)
    valid_phone = not phone or 7 <= len(phone_digits) <= 15
    if (
        len(full_name) < 2 or not valid_postcode or not valid_email or not valid_phone
        or not (email or phone) or not consent_contact
        or any(value not in allowed_values[key] for key, value in values.items())
    ):
        return _public_retrofit_response(
            "Please check your name, UK postcode, contact details, answers, and required contact permission.", 400
        )

    identity = email or phone_digits
    throttle_key = hmac.new(
        AUTH_CONFIG.session_secret, identity.encode("utf-8"), "sha256"
    ).hexdigest()
    now = time.monotonic()
    with _PUBLIC_INQUIRY_LOCK:
        attempts = _PUBLIC_INQUIRY_ATTEMPTS[throttle_key]
        while attempts and now - attempts[0] > 3600:
            attempts.popleft()
        if len(attempts) >= 3:
            return _public_retrofit_response(
                "We could not accept another request from these contact details just now. Please contact us directly if needed.",
                429,
            )
        attempts.append(now)

    created_at = datetime.utcnow()
    record = HomeownerInquiry(
        full_name=full_name,
        email=email,
        phone=phone,
        postcode=postcode,
        property_type=property_type,
        heating_type=heating_type,
        ownership=ownership,
        timeframe=timeframe,
        consent_contact=True,
        consent_share=bool(consent_share),
        consent_version="retrofit-enquiry-v1",
        consented_at=created_at,
        created_at=created_at,
        expires_at=created_at + timedelta(days=settings["retention_days"]),
    )
    db.add(record)
    db.commit()
    response = HTMLResponse(build_retrofit_thanks_page(settings["controller"], settings["contact_email"]))
    response.delete_cookie("public_enquiry_csrf", path="/", httponly=True,
                           secure=AUTH_CONFIG.cookie_secure, samesite="strict")
    return response


@app.get("/retrofit-inquiries", response_class=HTMLResponse)
def retrofit_inquiry_review(request: Request):
    return _protected_page(RETROFIT_INQUIRIES_PAGE, request)


@app.get("/api/retrofit/inquiries")
def list_retrofit_inquiries(db: Session = Depends(get_db)):
    _purge_expired_inquiries(db)
    records = db.query(HomeownerInquiry).order_by(HomeownerInquiry.created_at.desc()).limit(500).all()
    return [
        {
            "id": item.id,
            "full_name": item.full_name,
            "email": item.email,
            "phone": item.phone,
            "postcode": item.postcode,
            "property_type": item.property_type,
            "heating_type": item.heating_type,
            "ownership": item.ownership,
            "timeframe": item.timeframe,
            "consent_contact": item.consent_contact,
            "consent_share": item.consent_share,
            "consent_version": item.consent_version,
            "consented_at": item.consented_at.isoformat() if item.consented_at else "",
            "status": item.status,
            "matched_installer_id": item.matched_installer_id,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M UTC") if item.created_at else "",
        }
        for item in records
    ]


@app.get("/api/retrofit/installers")
def list_retrofit_installer_candidates(db: Session = Depends(get_db)):
    # Return business identity and service-area hints only; contact/enrichment fields stay private.
    records = db.query(Prospect).order_by(Prospect.id.desc()).limit(500).all()
    return [
        {
            "id": item.id,
            "business_name": item.business_name,
            "industry": item.industry or "",
            "business_type": item.business_type or "",
            "website": item.website or "",
            "city": item.city or "",
            "region": item.region or "",
            "country": item.country or "",
        }
        for item in records
    ]


@app.patch("/api/retrofit/inquiries/{inquiry_id}")
def update_retrofit_inquiry(
    inquiry_id: int, payload: HomeownerInquiryReview, db: Session = Depends(get_db)
):
    item = db.query(HomeownerInquiry).filter(HomeownerInquiry.id == inquiry_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    if payload.matched_installer_id is not None:
        if not item.consent_share:
            raise HTTPException(status_code=409, detail="The homeowner did not approve sharing details with an installer")
        if not db.query(Prospect.id).filter(Prospect.id == payload.matched_installer_id).first():
            raise HTTPException(status_code=404, detail="Installer candidate not found")
    item.status = payload.status
    item.matched_installer_id = payload.matched_installer_id
    db.commit()
    return {"updated": True, "id": item.id, "status": item.status,
            "matched_installer_id": item.matched_installer_id}


@app.delete("/api/retrofit/inquiries/{inquiry_id}")
def erase_retrofit_inquiry(inquiry_id: int, db: Session = Depends(get_db)):
    item = db.query(HomeownerInquiry).filter(HomeownerInquiry.id == inquiry_id).first()
    if not item:
        return {"deleted": False}
    db.delete(item)
    db.commit()
    return {"deleted": True}

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
        "enriched_email": record.enriched_email or "",
        "enriched_phone": record.enriched_phone or "",
        "enriched_contact_name": record.enriched_contact_name or "",
        "enriched_contact_role": record.enriched_contact_role or "",
        "enrichment_provider": record.enrichment_provider or "",
        "enrichment_status": record.enrichment_status or "",
        "enrichment_confidence": record.enrichment_confidence or "",
        "enrichment_source_url": record.enrichment_source_url or "",
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


def _campaign_detail(db: Session, campaign: Campaign):
    joined = (
        db.query(CampaignProspect, Prospect)
        .join(Prospect, Prospect.id == CampaignProspect.prospect_id)
        .filter(CampaignProspect.campaign_id == campaign.id)
        .order_by(CampaignProspect.created_at.desc())
        .all()
    )
    leads = []
    for campaign_lead, prospect in joined:
        item = _prospect_dict(prospect)
        item.update({
            "draft_subject": campaign_lead.draft_subject or "",
            "draft_body": campaign_lead.draft_body or "",
            "draft_reason": campaign_lead.draft_reason or "",
            "draft_status": campaign_lead.draft_status or "not_drafted",
            "pipeline_stage": campaign_lead.pipeline_stage or "new",
            "draft_updated_at": campaign_lead.updated_at.isoformat() if campaign_lead.updated_at else "",
        })
        leads.append(item)
    counts = {state: sum(1 for item in leads if item["draft_status"] == state)
              for state in ("not_drafted", "needs_review", "approved", "rejected")}
    return {
        "id": campaign.id,
        "title": campaign.title,
        "industry": campaign.industry or "",
        "business_type": campaign.business_type or "",
        "region": campaign.region or "",
        "country": campaign.country or "",
        "offer": campaign.offer or "",
        "proof": campaign.proof or "",
        "tone": campaign.tone or "Professional",
        "language": campaign.language or "English",
        "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
        "lead_count": len(leads),
        "draft_counts": counts,
        "leads": leads,
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
            enriched_email=item.enriched_email.strip(),
            enriched_phone=item.enriched_phone.strip(),
            enriched_contact_name=item.enriched_contact_name.strip(),
            enriched_contact_role=item.enriched_contact_role.strip(),
            enrichment_provider=item.enrichment_provider.strip(),
            enrichment_status=item.enrichment_status.strip(),
            enrichment_confidence=item.enrichment_confidence.strip(),
            enrichment_source_url=item.enrichment_source_url.strip(),
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
    db.query(CampaignProspect).filter(CampaignProspect.prospect_id == record_id).delete(synchronize_session=False)
    db.delete(record)
    db.commit()
    return {"deleted": True}


@app.patch("/businesses/{record_id}/enrichment")
@app.patch("/prospects/{record_id}/enrichment")
def update_business_enrichment(
    record_id: int,
    payload: BusinessEnrichmentInput,
    db: Session = Depends(get_db),
):
    record = db.query(Prospect).filter(Prospect.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Business not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(record, field, value.strip() if value is not None else "")
    db.commit()
    return {"updated": True, "id": record.id, "enrichment_provider": record.enrichment_provider}


@app.get("/api/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).limit(100).all()
    result = []
    for campaign in campaigns:
        item = _campaign_detail(db, campaign)
        item.pop("leads", None)
        result.append(item)
    return result


@app.post("/api/campaigns")
def create_campaign(payload: CampaignCreateInput, db: Session = Depends(get_db)):
    campaign = Campaign(
        title=payload.title.strip(),
        industry=payload.industry.strip(),
        business_type=payload.business_type.strip(),
        region=payload.region.strip(),
        country=payload.country.strip(),
        offer=payload.offer.strip(),
        proof=payload.proof.strip(),
        tone=payload.tone.strip() or "Professional",
        language=payload.language.strip() or "English",
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return _campaign_detail(db, campaign)


@app.get("/api/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _campaign_detail(db, campaign)


@app.post("/api/campaigns/{campaign_id}/discover")
def discover_campaign_businesses(
    campaign_id: int,
    payload: CampaignDiscoveryInput,
    db: Session = Depends(get_db),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # The discovery form asks for a specific city, town, or postcode. Do not
    # append a campaign region here: old campaigns may contain broad or
    # malformed values (for example "northwest"), which make valid places
    # such as "Birmingham, United Kingdom" unresolvable.
    search_location = payload.location.strip()
    try:
        result = discover_openstreetmap_businesses(
            payload.business_type.strip(), search_location, payload.radius_m, limit=payload.max_results
        )
    except ProspectingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    created = 0
    linked = 0
    duplicates = 0
    try:
        for found in result["results"]:
            item = ProspectInput(
                business_name=found["business_name"],
                industry=campaign.industry or payload.business_type.strip(),
                business_type=found.get("business_type", ""),
                website=found.get("website", ""),
                city=found.get("city", ""),
                region=found.get("region", ""),
                country=found.get("country", ""),
                postal_code=found.get("postal_code", ""),
                business_email=found.get("business_email", ""),
                business_phone=found.get("business_phone", ""),
                source_url=found["source_url"],
                contact_source_url=found.get("contact_source_url", ""),
                fit_score=found.get("fit_score", 0),
                fit_summary=found.get("fit_summary", ""),
            )
            fingerprint = _prospect_fingerprint(item)
            prospect = db.query(Prospect).filter(Prospect.fingerprint == fingerprint).first()
            if prospect:
                duplicates += 1
            else:
                prospect = Prospect(
                    business_name=item.business_name.strip(), industry=item.industry.strip(),
                    business_type=item.business_type.strip(), website=item.website.strip(),
                    city=item.city.strip(), region=item.region.strip(), country=item.country.strip(),
                    postal_code=item.postal_code.strip(), business_email=item.business_email.strip(),
                    business_phone=item.business_phone.strip(), contact_name="", contact_role="",
                    source_url=item.source_url.strip(), contact_source_url=item.contact_source_url.strip(),
                    fit_score=item.fit_score, fit_summary=item.fit_summary.strip(), fingerprint=fingerprint,
                )
                db.add(prospect)
                db.flush()
                created += 1
            association = db.query(CampaignProspect).filter(
                CampaignProspect.campaign_id == campaign_id,
                CampaignProspect.prospect_id == prospect.id,
            ).first()
            if not association:
                db.add(CampaignProspect(campaign_id=campaign_id, prospect_id=prospect.id))
                linked += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {
        "found": len(result["results"]),
        "new_businesses": created,
        "existing_businesses": duplicates,
        "added_to_campaign": linked,
        "location_label": result["location_label"],
        "attribution": result["attribution"],
        "license": result["license"],
        "campaign": _campaign_detail(db, campaign),
    }


@app.post("/api/campaigns/{campaign_id}/leads")
def add_saved_businesses_to_campaign(
    campaign_id: int,
    payload: CampaignLeadsInput,
    db: Session = Depends(get_db),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    prospect_ids = list(dict.fromkeys(payload.prospect_ids))
    prospects = db.query(Prospect).filter(Prospect.id.in_(prospect_ids)).all()
    if len(prospects) != len(prospect_ids):
        raise HTTPException(status_code=404, detail="One or more saved businesses were not found")
    existing_ids = {
        row[0] for row in db.query(CampaignProspect.prospect_id).filter(
            CampaignProspect.campaign_id == campaign_id,
            CampaignProspect.prospect_id.in_(prospect_ids),
        ).all()
    }
    for prospect in prospects:
        if prospect.id not in existing_ids:
            db.add(CampaignProspect(campaign_id=campaign_id, prospect_id=prospect.id))
    db.commit()
    return _campaign_detail(db, campaign)


@app.post("/api/campaigns/{campaign_id}/drafts")
def generate_campaign_drafts(
    campaign_id: int,
    payload: CampaignDraftInput,
    db: Session = Depends(get_db),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not campaign.offer.strip():
        raise HTTPException(status_code=422, detail="Add your offer to the campaign brief before creating drafts")
    prospect_ids = list(dict.fromkeys(payload.prospect_ids))
    if len(prospect_ids) > 10:
        raise HTTPException(status_code=422, detail="Choose at most 10 businesses at a time")
    joined = (
        db.query(CampaignProspect, Prospect)
        .join(Prospect, Prospect.id == CampaignProspect.prospect_id)
        .filter(CampaignProspect.campaign_id == campaign_id, CampaignProspect.prospect_id.in_(prospect_ids))
        .all()
    )
    if len(joined) != len(prospect_ids):
        raise HTTPException(status_code=404, detail="One or more selected businesses are not in this campaign")
    campaign_info = {
        "title": campaign.title, "industry": campaign.industry, "business_type": campaign.business_type,
        "offer": campaign.offer, "proof": campaign.proof, "tone": campaign.tone, "language": campaign.language,
    }
    safe_businesses = [
        {
            "id": prospect.id,
            "business_name": prospect.business_name,
            "industry": prospect.industry or "",
            "business_type": prospect.business_type or "",
            "city": prospect.city or "",
            "region": prospect.region or "",
            "country": prospect.country or "",
            "website": prospect.website or "",
        }
        for _, prospect in joined
    ]
    try:
        drafts = draft_outreach_messages(campaign_info, safe_businesses)
    except ProspectingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    by_prospect = {draft["business_id"]: draft for draft in drafts}
    for campaign_lead, prospect in joined:
        draft = by_prospect[prospect.id]
        campaign_lead.draft_subject = draft["subject"]
        campaign_lead.draft_body = draft["body"]
        campaign_lead.draft_reason = draft["reason"]
        campaign_lead.draft_status = "needs_review"
        campaign_lead.reviewed_at = None
    db.commit()
    return _campaign_detail(db, campaign)


@app.post("/api/campaigns/{campaign_id}/leads/{prospect_id}/simulate")
def simulate_campaign_business(campaign_id: int, prospect_id: int, db: Session = Depends(get_db)):
    """Run the source-inspired single-business workflow without saving or sending anything."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not campaign.offer.strip():
        raise HTTPException(status_code=422, detail="Add your offer to the campaign brief before simulating")
    joined = (
        db.query(CampaignProspect, Prospect)
        .join(Prospect, Prospect.id == CampaignProspect.prospect_id)
        .filter(
            CampaignProspect.campaign_id == campaign_id,
            CampaignProspect.prospect_id == prospect_id,
        )
        .first()
    )
    if not joined:
        raise HTTPException(status_code=404, detail="Business is not in this campaign")
    campaign_lead, prospect = joined
    business = {
        "id": prospect.id,
        "business_name": prospect.business_name,
        "industry": prospect.industry or "",
        "business_type": prospect.business_type or "",
        "city": prospect.city or "",
        "region": prospect.region or "",
        "country": prospect.country or "",
        "website": prospect.website or "",
        "source_url": prospect.source_url or "",
        "business_email": prospect.business_email or "",
        "business_phone": prospect.business_phone or "",
    }

    campaign_info = {
        "title": campaign.title,
        "industry": campaign.industry or "",
        "business_type": campaign.business_type or "",
        "offer": campaign.offer,
        "proof": campaign.proof or "",
        "tone": campaign.tone or "Professional",
        "language": campaign.language or "English",
    }
    fit = simulate_business_fit(campaign_info, business)
    safe_business = {
        key: business[key]
        for key in ("id", "business_name", "industry", "business_type", "city", "region", "country", "website")
    }
    try:
        drafts = draft_outreach_messages(campaign_info, [safe_business])
    except ProspectingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    draft = drafts[0]
    return {
        "business": {
            "id": prospect.id,
            "name": prospect.business_name,
            "business_type": prospect.business_type or "",
            "area": ", ".join(value for value in (prospect.city, prospect.region, prospect.country) if value),
            "source_url": prospect.source_url,
        },
        "fit": fit,
        "draft": {"subject": draft["subject"], "body": draft["body"], "reason": draft["reason"]},
        "draft_mode": "AI provider" if os.getenv("OPENAI_API_KEY", "").strip() else "local template",
        "timeline": one_business_timeline(campaign_lead.pipeline_stage),
        "saved": False,
        "sent": False,
        "note": "Simulation only. The preview is not saved, approved, scheduled, or sent.",
    }


@app.post("/api/simulations/one-business-demo")
def one_business_demo():
    """Return a synthetic, isolated preview with no database or provider calls."""
    return build_demo_simulation()


@app.patch("/api/campaigns/{campaign_id}/leads/{prospect_id}")
def update_campaign_lead(
    campaign_id: int,
    prospect_id: int,
    payload: CampaignLeadUpdateInput,
    db: Session = Depends(get_db),
):
    campaign_lead = db.query(CampaignProspect).filter(
        CampaignProspect.campaign_id == campaign_id,
        CampaignProspect.prospect_id == prospect_id,
    ).first()
    if not campaign_lead:
        raise HTTPException(status_code=404, detail="Business is not in this campaign")
    values = payload.dict(exclude_unset=True)
    if "draft_subject" in values:
        campaign_lead.draft_subject = (values["draft_subject"] or "").strip()
    if "draft_body" in values:
        campaign_lead.draft_body = (values["draft_body"] or "").strip()
    if "draft_status" in values:
        if values["draft_status"] in {"approved", "rejected"} and not campaign_lead.draft_body:
            raise HTTPException(status_code=422, detail="Write a draft before approving or rejecting it")
        campaign_lead.draft_status = values["draft_status"]
        campaign_lead.reviewed_at = datetime.utcnow() if values["draft_status"] != "needs_review" else None
    elif "draft_subject" in values or "draft_body" in values:
        campaign_lead.draft_status = "needs_review" if campaign_lead.draft_body else "not_drafted"
        campaign_lead.reviewed_at = None
    if "pipeline_stage" in values:
        campaign_lead.pipeline_stage = values["pipeline_stage"]
    campaign_lead.updated_at = datetime.utcnow()
    db.commit()
    return {"updated": True, "draft_status": campaign_lead.draft_status}


@app.delete("/api/campaigns/{campaign_id}/leads/{prospect_id}")
def remove_campaign_lead(campaign_id: int, prospect_id: int, db: Session = Depends(get_db)):
    campaign_lead = db.query(CampaignProspect).filter(
        CampaignProspect.campaign_id == campaign_id,
        CampaignProspect.prospect_id == prospect_id,
    ).first()
    if not campaign_lead:
        return {"removed": False}
    db.delete(campaign_lead)
    db.commit()
    return {"removed": True}


@app.get("/api/campaigns/{campaign_id}/export.csv")
def export_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    joined = (
        db.query(CampaignProspect, Prospect)
        .join(Prospect, Prospect.id == CampaignProspect.prospect_id)
        .filter(CampaignProspect.campaign_id == campaign_id)
        .order_by(Prospect.business_name.asc())
        .all()
    )
    output = StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow([
        "Business", "Industry", "Type", "City", "Region", "Country", "Website",
        "Published email", "Published phone", "Source", "Pipeline stage", "Draft status",
        "Draft subject", "Draft message", "Data attribution",
    ])
    for campaign_lead, prospect in joined:
        writer.writerow([
            prospect.business_name, prospect.industry, prospect.business_type, prospect.city, prospect.region,
            prospect.country, prospect.website, prospect.business_email, prospect.business_phone, prospect.source_url,
            campaign_lead.pipeline_stage, campaign_lead.draft_status, campaign_lead.draft_subject,
            campaign_lead.draft_body,
            "© OpenStreetMap contributors" if "openstreetmap.org" in (prospect.source_url or "") else "",
        ])
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="campaign-{campaign_id}-leads.csv"'},
    )


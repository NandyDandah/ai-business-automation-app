import csv
import hmac
import os
import time
from collections import defaultdict, deque
from html import escape as escape_html
from threading import Lock
from typing import Literal
from io import StringIO

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

load_dotenv()

from app.database import SessionLocal, Automation, create_tables
from app.ai_service import analyse_business_message
from app.security import (
    LOGIN_CSRF_MAX_AGE, SESSION_MAX_AGE, create_login_csrf, create_session,
    get_session_csrf_token, load_auth_config, verify_api_token, verify_login_csrf, verify_password,
)

AUTH_CONFIG = load_auth_config()

from app.database import SessionLocal, Automation, create_tables
from app.ai_service import analyse_business_message

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
    markup = markup.replace("<head>", f'<head>\n<meta name="csrf-token" content="{escape_html(token, quote=True)}">', 1)
    logout = (
        '<button type="button" id="logoutButton">Log out</button><script>'
        'document.getElementById("logoutButton").addEventListener("click", async function () {'
        'const csrf=document.querySelector("meta[name=csrf-token]").content;'
        'const r=await fetch("/logout",{method:"POST",headers:{"X-CSRF-Token":csrf}});'
        'if(r.ok)location.href="/login";});</script>'
    )
    return HTMLResponse(markup.replace("</body>", logout + "</body>", 1))


def _login_page(message="", code=200):
    token = create_login_csrf(AUTH_CONFIG)
    error = f'<p role="alert">{escape_html(message)}</p>' if message else ""
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sign in</title><style>body{{font-family:Arial;max-width:440px;margin:12vh auto;padding:0 20px;background:#f7f7f7}}main{{background:white;padding:28px;border-radius:12px}}input,button{{box-sizing:border-box;width:100%;padding:12px;margin-top:12px;font-size:16px}}</style></head>
<body><main><h1>Sign in</h1><p>Enter the app password to open saved lead records.</p>{error}
<form method="post" action="/login"><input type="hidden" name="csrf_token" value="{escape_html(token, quote=True)}">
<label for="password">App password</label><input id="password" name="password" type="password" autocomplete="current-password" required>
<button type="submit">Sign in</button></form></main></body></html>"""
    response = HTMLResponse(page, status_code=code)
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _protected_page("""
<!DOCTYPE html>
<html>
<head>
    <title>AI Business Automation App</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: 40px auto; background: #f7f7f7; }
        .box { background: white; padding: 25px; border-radius: 12px; }
        input, textarea { width: 100%; padding: 12px; margin: 10px 0; font-size: 16px; }
        textarea { height: 140px; }
        button { padding: 12px 20px; cursor: pointer; }
        .result { background: #fff; margin-top: 20px; padding: 20px; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>AI Business Automation App</h1>

        <input id="email" placeholder="Customer Email">
        <textarea id="message" placeholder="Enter customer message..."></textarea>

        <button onclick="runAutomation()">Run Automation</button>
        <a href="/dashboard"><button>Dashboard</button></a>
        <a href="/pipeline"><button>Pipeline</button></a>

        <div id="result"></div>
    </div>

    <script>
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        function escapeHtml(value) {
            const replacements = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"};
            return String(value ?? "").replace(/[&<>"']/g, function (character) {
                return replacements[character];
            });
        }
        async function runAutomation() {
            const email = document.getElementById("email").value;
            const message = document.getElementById("message").value;

            const response = await fetch("/automate", {
                method: "POST",
                headers: {"Content-Type": "application/json", "X-CSRF-Token": csrfToken},
                body: JSON.stringify({email, message})
            });

            const data = await response.json();

            document.getElementById("result").innerHTML = `
                <div class="result">
                    <h3>Automation Complete</h3>
                    <p><strong>Category:</strong> ${escapeHtml(data.category)}</p>
                    <p><strong>Priority:</strong> ${escapeHtml(data.priority)}</p>
                    <p><strong>Lead Score:</strong> ${escapeHtml(data.lead_score)}/100</p>
                    <p><strong>Reply:</strong> ${escapeHtml(data.ai_reply)}</p>
                </div>
            `;
        }
    </script>
</body>
</html>
""", request)

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
    return _protected_page("""
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        body { font-family: Arial; max-width: 1150px; margin: 40px auto; background: #f7f7f7; }
        .stats { display: flex; gap: 15px; margin: 20px 0; }
        .stat, .card { background: white; padding: 20px; border-radius: 12px; margin: 15px 0; }
        .stat { flex: 1; }
        button, select, input { padding: 9px 14px; margin: 5px; }
        textarea { width: 100%; height: 70px; }
        .badge { padding: 5px 10px; border-radius: 20px; color: white; }
        .high { background: #d9534f; }
        .medium { background: #f0ad4e; }
        .low { background: #5cb85c; }
        .cat { background: #0275d8; }
    </style>
</head>
<body>
    <h1>Automation Dashboard</h1>

    <a href="/"><button>Home</button></a>
    <a href="/pipeline"><button>Pipeline</button></a>
    <a href="/export"><button>Download CSV</button></a>

    <br><br>

    <input id="searchBox" placeholder="Search..." oninput="applyFilters()">

    <select id="categoryFilter" onchange="applyFilters()">
        <option value="">All Categories</option>
        <option value="sales">Sales</option>
        <option value="support">Support</option>
        <option value="complaint">Complaint</option>
        <option value="follow_up">Follow Up</option>
        <option value="admin">Admin</option>
    </select>

    <select id="priorityFilter" onchange="applyFilters()">
        <option value="">All Priorities</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
    </select>

    <select id="statusFilter" onchange="applyFilters()">
        <option value="">All Statuses</option>
        <option value="New">New</option>
        <option value="Contacted">Contacted</option>
        <option value="Closed">Closed</option>
    </select>

    <button onclick="showHotLeads()">Hot Leads</button>
    <button onclick="showFollowUps()">Follow-ups</button>
    <button onclick="loadHistory()">Show All</button>

    <div class="stats">
        <div class="stat"><h3>Total Leads</h3><h2 id="totalLeads">0</h2></div>
        <div class="stat"><h3>Hot Leads</h3><h2 id="hotLeads">0</h2></div>
        <div class="stat"><h3>Follow-ups</h3><h2 id="followUps">0</h2></div>
        <div class="stat"><h3>High Priority</h3><h2 id="highPriority">0</h2></div>
    </div>

    <div id="records">Loading...</div>

    <script>
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        function escapeHtml(value) {
            const replacements = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"};
            return String(value ?? "").replace(/[&<>"']/g, function (character) {
                return replacements[character];
            });
        }
        let allData = [];

        async function loadHistory() {
            const response = await fetch("/history");
            allData = await response.json();

            document.getElementById("totalLeads").innerText = allData.length;
            document.getElementById("hotLeads").innerText = allData.filter(x => Number(x.lead_score || 0) >= 70).length;
            document.getElementById("followUps").innerText = allData.filter(x => x.follow_up_date).length;
            document.getElementById("highPriority").innerText = allData.filter(x => x.priority === "high").length;

            displayRecords(allData);
        }

        function displayRecords(data) {
            if (!data.length) {
                document.getElementById("records").innerHTML = "<p>No records found.</p>";
                return;
            }

            document.getElementById("records").innerHTML = data.map(item => `
                <div class="card">
                    <p><strong>Email:</strong> ${escapeHtml(item.customer_email || "No email")}</p>
                    <p><strong>Message:</strong> ${escapeHtml(item.customer_message)}</p>

                    <p>
                        <span class="badge cat">${escapeHtml(item.category)}</span>
                        <span class="badge ${escapeHtml(item.priority)}">${escapeHtml(item.priority)}</span>
                    </p>

                    <p><strong>Status:</strong> ${escapeHtml(item.status)}</p>
                    <p><strong>Lead Score:</strong> ${escapeHtml(item.lead_score)}/100</p>

                    <p><strong>Follow-up:</strong></p>
                    <input type="date" id="followup-${item.id}" value="${escapeHtml(item.follow_up_date || "")}">
                    <button onclick="updateFollowUp(${item.id})">Save Follow-up</button>
                    <button onclick="clearFollowUp(${item.id})">Mark Done</button>

                    <p><strong>Change Status:</strong></p>
                    <select onchange="updateStatus(${item.id}, this.value)">
                        <option value="New">New</option>
                        <option value="Contacted">Contacted</option>
                        <option value="Closed">Closed</option>
                    </select>

                    <p><strong>AI Reply:</strong> ${escapeHtml(item.ai_reply)}</p>

                    <p><strong>Notes:</strong></p>
                    <textarea id="notes-${item.id}">${escapeHtml(item.notes || "")}</textarea>
                    <button onclick="updateNotes(${item.id})">Save Notes</button>

                    <br><br>
                    <button onclick="deleteRecord(${item.id})">Delete</button>
                </div>
            `).join("");
        }

        function applyFilters() {
            const search = document.getElementById("searchBox").value.toLowerCase();
            const category = document.getElementById("categoryFilter").value;
            const priority = document.getElementById("priorityFilter").value;
            const status = document.getElementById("statusFilter").value;

            const filtered = allData.filter(item => {
                const textMatch =
                    (item.customer_message || "").toLowerCase().includes(search) ||
                    (item.customer_email || "").toLowerCase().includes(search) ||
                    (item.ai_reply || "").toLowerCase().includes(search);

                return textMatch &&
                    (category === "" || item.category === category) &&
                    (priority === "" || item.priority === priority) &&
                    (status === "" || item.status === status);
            });

            displayRecords(filtered);
        }

        function showHotLeads() {
            displayRecords(allData.filter(x => Number(x.lead_score || 0) >= 70));
        }

        function showFollowUps() {
            displayRecords(allData.filter(x => x.follow_up_date));
        }

        async function updateStatus(id, status) {
            await fetch(`/history/${id}/status?new_status=${status}`, { method: "PUT", headers: { "X-CSRF-Token": csrfToken } });
            loadHistory();
        }

        async function updateNotes(id) {
            const notes = document.getElementById(`notes-${id}`).value;
            await fetch(`/history/${id}/notes?notes=${encodeURIComponent(notes)}`, { method: "PUT", headers: { "X-CSRF-Token": csrfToken } });
            loadHistory();
        }

        async function updateFollowUp(id) {
            const date = document.getElementById(`followup-${id}`).value;
            await fetch(`/history/${id}/follow-up?follow_up_date=${encodeURIComponent(date)}`, { method: "PUT", headers: { "X-CSRF-Token": csrfToken } });
            loadHistory();
        }

        async function clearFollowUp(id) {
            await fetch(`/history/${id}/follow-up?follow_up_date=`, { method: "PUT", headers: { "X-CSRF-Token": csrfToken } });
            loadHistory();
        }

        async function deleteRecord(id) {
            if (!confirm("Delete this record?")) return;
            await fetch(`/history/${id}`, { method: "DELETE", headers: { "X-CSRF-Token": csrfToken } });
            loadHistory();
        }

        loadHistory();
    </script>
</body>
</html>
""", request)

@app.get("/pipeline", response_class=HTMLResponse)
def pipeline(request: Request):
    return _protected_page("""
<!DOCTYPE html>
<html>
<head>
    <title>Pipeline</title>
    <style>
        body { font-family: Arial; max-width: 1200px; margin: 40px auto; background: #f7f7f7; }
        .board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .column { background: #e9e9e9; padding: 15px; border-radius: 12px; }
        .card { background: white; padding: 15px; margin-bottom: 15px; border-radius: 10px; }
        button, select { padding: 8px 12px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Pipeline Board</h1>

    <a href="/"><button>Home</button></a>
    <a href="/dashboard"><button>Dashboard</button></a>

    <div class="board">
        <div class="column"><h2>New</h2><div id="newCol"></div></div>
        <div class="column"><h2>Contacted</h2><div id="contactedCol"></div></div>
        <div class="column"><h2>Closed</h2><div id="closedCol"></div></div>
    </div>

    <script>
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        function escapeHtml(value) {
            const replacements = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"};
            return String(value ?? "").replace(/[&<>"']/g, function (character) {
                return replacements[character];
            });
        }
        let allData = [];

        async function loadPipeline() {
            const response = await fetch("/history");
            allData = await response.json();

            render("New", "newCol");
            render("Contacted", "contactedCol");
            render("Closed", "closedCol");
        }

        function render(status, elementId) {
            const items = allData.filter(x => (x.status || "New") === status);

            document.getElementById(elementId).innerHTML = items.length ? items.map(item => `
                <div class="card">
                    <p><strong>${escapeHtml(item.customer_email || "No email")}</strong></p>
                    <p>${escapeHtml(item.customer_message)}</p>
                    <p>${escapeHtml(item.category)} | ${escapeHtml(item.priority)} | ${escapeHtml(item.lead_score)}/100</p>

                    <select onchange="updateStatus(${item.id}, this.value)">
                        <option value="New" ${status === "New" ? "selected" : ""}>New</option>
                        <option value="Contacted" ${status === "Contacted" ? "selected" : ""}>Contacted</option>
                        <option value="Closed" ${status === "Closed" ? "selected" : ""}>Closed</option>
                    </select>
                </div>
            `).join("") : "<p>No leads</p>";
        }

        async function updateStatus(id, status) {
            await fetch(`/history/${id}/status?new_status=${status}`, { method: "PUT", headers: { "X-CSRF-Token": csrfToken } });
            loadPipeline();
        }

        loadPipeline();
    </script>
</body>
</html>
""", request)

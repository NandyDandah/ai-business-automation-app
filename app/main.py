from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from io import StringIO
import csv

from app.database import SessionLocal, Automation, create_tables
from app.ai_service import analyse_business_message

app = FastAPI(title="AI Business Automation App")

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
def home():
    return """
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
        async function runAutomation() {
            const email = document.getElementById("email").value;
            const message = document.getElementById("message").value;

            const response = await fetch("/automate", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({email, message})
            });

            const data = await response.json();

            document.getElementById("result").innerHTML = `
                <div class="result">
                    <h3>Automation Complete</h3>
                    <p><strong>Category:</strong> ${data.category}</p>
                    <p><strong>Priority:</strong> ${data.priority}</p>
                    <p><strong>Lead Score:</strong> ${data.lead_score}/100</p>
                    <p><strong>Reply:</strong> ${data.ai_reply}</p>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

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
def update_status(record_id: int, new_status: str, db: Session = Depends(get_db)):
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
def dashboard():
    return """
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
                    <p><strong>Email:</strong> ${item.customer_email || "No email"}</p>
                    <p><strong>Message:</strong> ${item.customer_message}</p>

                    <p>
                        <span class="badge cat">${item.category}</span>
                        <span class="badge ${item.priority}">${item.priority}</span>
                    </p>

                    <p><strong>Status:</strong> ${item.status}</p>
                    <p><strong>Lead Score:</strong> ${item.lead_score}/100</p>

                    <p><strong>Follow-up:</strong></p>
                    <input type="date" id="followup-${item.id}" value="${item.follow_up_date || ""}">
                    <button onclick="updateFollowUp(${item.id})">Save Follow-up</button>
                    <button onclick="clearFollowUp(${item.id})">Mark Done</button>

                    <p><strong>Change Status:</strong></p>
                    <select onchange="updateStatus(${item.id}, this.value)">
                        <option value="New">New</option>
                        <option value="Contacted">Contacted</option>
                        <option value="Closed">Closed</option>
                    </select>

                    <p><strong>AI Reply:</strong> ${item.ai_reply}</p>

                    <p><strong>Notes:</strong></p>
                    <textarea id="notes-${item.id}">${item.notes || ""}</textarea>
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
            await fetch(`/history/${id}/status?new_status=${status}`, { method: "PUT" });
            loadHistory();
        }

        async function updateNotes(id) {
            const notes = document.getElementById(`notes-${id}`).value;
            await fetch(`/history/${id}/notes?notes=${encodeURIComponent(notes)}`, { method: "PUT" });
            loadHistory();
        }

        async function updateFollowUp(id) {
            const date = document.getElementById(`followup-${id}`).value;
            await fetch(`/history/${id}/follow-up?follow_up_date=${encodeURIComponent(date)}`, { method: "PUT" });
            loadHistory();
        }

        async function clearFollowUp(id) {
            await fetch(`/history/${id}/follow-up?follow_up_date=`, { method: "PUT" });
            loadHistory();
        }

        async function deleteRecord(id) {
            if (!confirm("Delete this record?")) return;
            await fetch(`/history/${id}`, { method: "DELETE" });
            loadHistory();
        }

        loadHistory();
    </script>
</body>
</html>
"""

@app.get("/pipeline", response_class=HTMLResponse)
def pipeline():
    return """
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
                    <p><strong>${item.customer_email || "No email"}</strong></p>
                    <p>${item.customer_message}</p>
                    <p>${item.category} | ${item.priority} | ${item.lead_score}/100</p>

                    <select onchange="updateStatus(${item.id}, this.value)">
                        <option value="New" ${status === "New" ? "selected" : ""}>New</option>
                        <option value="Contacted" ${status === "Contacted" ? "selected" : ""}>Contacted</option>
                        <option value="Closed" ${status === "Closed" ? "selected" : ""}>Closed</option>
                    </select>
                </div>
            `).join("") : "<p>No leads</p>";
        }

        async function updateStatus(id, status) {
            await fetch(`/history/${id}/status?new_status=${status}`, { method: "PUT" });
            loadPipeline();
        }

        loadPipeline();
    </script>
</body>
</html>
"""
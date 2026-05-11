from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal, Automation, create_tables
from app.ai_service import analyse_business_message

app = FastAPI(title="AI Business Automation App")

create_tables()

class MessageRequest(BaseModel):
    message: str

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
        body {
            font-family: Arial;
            max-width: 900px;
            margin: 40px auto;
            background: #f7f7f7;
        }
        textarea {
            width: 100%;
            height: 140px;
            padding: 12px;
            font-size: 16px;
        }
        button {
            padding: 12px 20px;
            margin-top: 10px;
            font-size: 16px;
            cursor: pointer;
        }
        .card {
            background: white;
            padding: 20px;
            margin-top: 20px;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <h1>AI Business Automation App</h1>

    <p>Paste a customer message, lead enquiry, complaint, or admin request.</p>

    <textarea id="message" placeholder="Example: Hi, I am interested in your services. Can you send pricing?"></textarea>
    <br>
    <button onclick="runAutomation()">Run Automation</button>

    <div id="result"></div>

    <script>
        async function runAutomation() {
            const message = document.getElementById("message").value;

            const response = await fetch("/automate", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message})
            });

            const data = await response.json();

            document.getElementById("result").innerHTML = `
                <div class="card">
                    <h2>Automation Result</h2>
                    <p><strong>Category:</strong> ${data.category}</p>
                    <p><strong>Priority:</strong> ${data.priority}</p>
                    <h3>AI Reply</h3>
                    <p>${data.ai_reply}</p>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.post("/automate")
def automate(request: MessageRequest, db: Session = Depends(get_db)):
    ai_result = analyse_business_message(request.message)

    record = Automation(
        customer_message=request.message,
        category=ai_result["category"],
        priority=ai_result["priority"],
        ai_reply=ai_result["reply"]
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "category": record.category,
        "priority": record.priority,
        "ai_reply": record.ai_reply
    }

@app.get("/history")
def history(db: Session = Depends(get_db)):
    records = db.query(Automation).order_by(Automation.id.desc()).all()

    return [
        {
            "id": r.id,
            "customer_message": r.customer_message,
            "category": r.category,
            "priority": r.priority,
            "ai_reply": r.ai_reply,
            "created_at": r.created_at
        }
        for r in records
    ]
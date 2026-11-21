# AI Business Automation App

A Python/FastAPI web app that helps small businesses automate customer message handling, lead scoring, pipeline tracking, follow-ups, notes, and CSV reporting.

## Features

- Customer message classification
- Lead scoring
- Priority detection
- Dashboard analytics
- Pipeline board: New, Contacted, Closed
- Follow-up date tracking
- Notes per lead
- CSV export
- SQLite database

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- HTML
- CSS
- JavaScript

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Agensi agent skill

This repository also includes a standalone skill for triaging inbound enquiries in an AI agent:

- `skills/inbound-lead-triage/SKILL.md` — the workflow, output format, and safety boundaries.
- `skills/inbound-lead-triage/references/scoring-rubric.md` — an explainable scoring rubric.

The skill works from information the user provides. It returns a triage summary and an unsent reply draft. It does not connect to this FastAPI app, save or change CRM records, discover prospects, verify contacts, or send messages. The skill does not require a hosted backend or API keys.

To list it, package the files under `skills/inbound-lead-triage/` in a ZIP and submit it through Agensi Creator Studio for review. The listing is not live until Agensi approves it. If live data tools are added later, their use and separate buyer charges should be described in the listing.

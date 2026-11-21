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

## Authentication and private data

The browser app uses one owner password. API clients use a bearer token in the Authorization header. All lead data, dashboards, history, pipeline, and exports require authentication. Browser changes use CSRF tokens. This is a single-owner app and does not separate records by customer account.

Before starting the app, run python -m app.security. Choose a password and copy the generated APP_PASSWORD_HASH, APP_SESSION_SECRET, and APP_API_TOKEN_HASH into a private .env file based on .env.example. Save the raw bearer token in your API client's private secret settings; the setup command shows it once. Add your own OPENAI_API_KEY if the analysis service needs it.

For local use, set APP_ENV=development and APP_COOKIE_SECURE=false, then run uvicorn bound to 127.0.0.1 only. For hosting, use HTTPS through a trusted reverse proxy and set APP_ENV=production. Do not expose plain HTTP or the SQLite file to the public internet. Rotate APP_SESSION_SECRET to revoke browser sessions and APP_API_TOKEN_HASH to revoke the API token.

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Agensi agent skill

This repository also includes a standalone skill for triaging inbound enquiries in an AI agent:

- `skills/inbound-lead-triage/SKILL.md` — the workflow, output format, and safety boundaries.
- `skills/inbound-lead-triage/references/scoring-rubric.md` — an explainable scoring rubric.

The skill works from information the user provides. It returns a triage summary and an unsent reply draft. It does not connect to this FastAPI app, save or change CRM records, discover prospects, verify contacts, or send messages. The skill does not require a hosted backend or API keys.

To list it, package the files under `skills/inbound-lead-triage/` in a ZIP and submit it through Agensi Creator Studio for review. The listing is not live until Agensi approves it. If live data tools are added later, their use and separate buyer charges should be described in the listing.


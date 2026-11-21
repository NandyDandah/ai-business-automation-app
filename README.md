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

The legacy `uvicorn main:app` entry point also loads this authenticated application.

## Agensi skills

This repository contains two separate skills:

- skills/inbound-lead-triage: reviews an enquiry the user provides and drafts an unsent reply.
- skills/clinic-prospect-finder: researches public UK dental clinic information for web-design prospects, checks public contact sources, and can save selected records to this app's authenticated API.

The prospect finder uses Agensi MCP tools at run time. It starts with public search and requires the user's explicit approval of the exact price before any paid email lookup or enrichment. It never sends outreach. Agensi can use up to 10 listed tools per skill; choose search, email lookup, and verification tools in Creator Studio after reviewing their current names and prices. Agensi delivers skills through its MCP server and does not host this app's FastAPI backend.

## Prospect API

- POST /prospects/batch saves 1 to 50 source-backed records.
- GET /prospects lists saved records; DELETE /prospects/{id} deletes one.
- These routes require the same bearer authentication as the rest of the API.

The skill only saves records when asked and when the caller already has a private API token configured. Use localhost only for an agent running on the same computer. A remote agent needs a privately accessible HTTPS API; never expose the SQLite database file.



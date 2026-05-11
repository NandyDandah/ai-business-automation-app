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
pip install fastapi uvicorn sqlalchemy pydantic
python -m uvicorn app.main:app --reload
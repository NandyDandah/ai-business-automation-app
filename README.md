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
- Industry-neutral business prospect records with a protected browser database
- Optional Hunter and Apollo enrichment with source, provider, status, and confidence kept separate from business-published details
- Protected campaign studio with OpenStreetMap lead discovery, campaign stages, review-only outreach drafts, and CSV export
- SQLite for local development and PostgreSQL for hosted use

## Tech Stack

- Python
- FastAPI
- SQLite (local development)
- PostgreSQL (hosted deployments)
- SQLAlchemy
- HTML
- CSS
- JavaScript

## Authentication and private data

The browser app uses one owner password. API clients use a bearer token in the Authorization header. All lead data, dashboards, history, pipeline, and exports require authentication. Browser changes use CSRF tokens. This is a single-owner app and does not separate records by customer account.

Before starting the app, run python -m app.security. Choose a password and copy the generated APP_PASSWORD_HASH, APP_SESSION_SECRET, and APP_API_TOKEN_HASH into a private .env file based on .env.example. Save the raw bearer token in your API client's private secret settings; the setup command shows it once. Add `OPENAI_API_KEY` to enable provider-backed message analysis and campaign draft generation. The key stays server-side. Without a key, message analysis and campaign drafts use local fallbacks.

For local use, set APP_ENV=development and APP_COOKIE_SECURE=false, then run uvicorn bound to 127.0.0.1 only. For hosting, use HTTPS through a trusted reverse proxy and set APP_ENV=production. Do not expose plain HTTP or the SQLite file to the public internet. Rotate APP_SESSION_SECRET to revoke browser sessions and APP_API_TOKEN_HASH to revoke the API token.

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The legacy `uvicorn main:app` entry point also loads this authenticated application.

## Render database

The app reads its database connection from `DATABASE_URL`. Local development defaults to SQLite. On Render, set this environment variable to the Postgres database's **internal URL** in the web service's private environment settings, and place the database and web service in the same region. Never commit the connection URL or paste it into a public file. The requirements include the Psycopg driver for PostgreSQL.

At startup, the app creates missing tables and adds generic industry, business type, region, country, and provider-enrichment fields to an existing prospects table. This migration preserves existing records. It does not seed fabricated businesses or delete an existing database.

## Homeowner retrofit enquiry pilot

The public `/retrofit` page is closed by default. To open it, privately configure all of the following on the web service, after publishing a privacy notice that covers this specific form:

- `PUBLIC_ENQUIRY_ENABLED=true`
- `PUBLIC_ENQUIRY_CONTROLLER_NAME` — the real legal data-controller name.
- `PUBLIC_ENQUIRY_CONTACT_EMAIL` — an address monitored for privacy requests.
- `PUBLIC_ENQUIRY_PRIVACY_URL` — the HTTPS URL of the privacy notice.
- `PUBLIC_ENQUIRY_RETENTION_DAYS` — a documented period from 1 to 365 days.
- `PUBLIC_ENQUIRY_CLOSE_AT` — an optional ISO-8601 UTC cutoff for a time-limited pilot; after it, the form closes automatically.

The public `/privacy` page renders the controller, contact address, retention period, and pilot cutoff from configuration. The form asks for a name, an email or phone number, postcode, property type, current heating, ownership relationship, and likely timing. It does not ask for a full address. Contact permission is required; permission to share details with one installer is a separate, optional choice. Requests are stored in a separate `homeowner_inquiries` table, expire on the chosen retention date, and are removed on app start or before the private review list is shown. The public page uses CSRF protection, a honeypot, and a basic per-contact submission limit.

The protected `/retrofit-inquiries` page is for manual review. It never sends messages or shares homeowner details automatically, and it blocks installer assignment unless sharing permission was given. Check the candidate's service area, current MCS status, capacity, and fit before making an introduction. This pilot does not assess grant eligibility, promise a quote, or send marketing. Add a stronger anti-spam service before promoting a public form at scale.

## Agensi skills

This repository contains two separate skills:

- skills/inbound-lead-triage: reviews an enquiry the user provides and drafts an unsent reply.
- skills/business-prospect-finder: researches businesses in user-selected industries and locations, checks public business sources, and can save selected records to this app's authenticated API.

The prospect finder uses Agensi MCP tools at run time. It can use Google Maps or web search for business discovery, Apollo for company and decision-maker search/enrichment, and Hunter for domain lookup, work-email finding, and verification. The user's agent calls these tools through Agensi; the FastAPI server does not need provider API keys. Agensi allows up to 10 tool cards per skill, which must be selected in Creator Studio using the live catalog. It starts with public/source checks and requires explicit approval of the exact quote before any paid call. It never sends outreach. Agensi delivers skills through its MCP server and does not host this app's FastAPI backend. See `skills/business-prospect-finder/references/agensi-tool-setup.md`.

## Business API

- POST /businesses/batch saves 1 to 50 source-backed business records.
- GET /businesses lists saved records; DELETE /businesses/{id} deletes one.
- PATCH /businesses/{id}/enrichment updates Hunter/Apollo fields on an existing record without overwriting business-published details.
- These routes require the same bearer authentication as the rest of the API.

The API supports generic business/location fields, business-published contact details, and separate Hunter/Apollo enrichment fields. The old `/prospects` routes and clinic-specific request keys remain as aliases for compatibility. The protected `/prospect-database` page shows those fields separately. The skill only saves records when asked and when the caller already has a private API token configured. Use localhost only for an agent running on the same computer. A remote agent needs a privately accessible HTTPS API; never expose a database file.


## Campaign Studio

The protected `/campaigns` workspace brings the lead-to-review workflow from [Prospex](https://github.com/asiifdev/business-leads-ai-automation) into this FastAPI app: create a campaign brief, discover source-linked businesses from OpenStreetMap, add businesses already saved by the Business Prospect Finder / Apollo / Hunter workflow, track campaign stages, generate and edit personalized drafts, approve or reject them, copy text, and export a campaign CSV. It is implemented natively here; the separate Prospex application source is not bundled.

Map searches are started by the signed-in owner, limited to 40 results, cached for six hours per search, and geocoded at no more than one request per second. The app uses configurable Nominatim and Overpass endpoints (`OSM_NOMINATIM_URL`, `OSM_OVERPASS_URL`); by default, European locations use the DResel Europe instance (maximum four parallel queries per IP) and other locations use the Private.coffee global instance, which explicitly permits commercial projects subject to fair use. Targeted searches query tags related to the requested business type to reduce load. The app starts with a 1 km radius and retries one busy wider search at 1 km, showing a notice. The UI and CSV exports show OpenStreetMap attribution. OSM data are under the ODbL; review its attribution/share-alike terms before redistributing a derived dataset. Nominatim's public service is a shared community resource with strict usage limits; switch to a suitable managed or self-hosted geocoder if usage grows. See [OpenStreetMap copyright](https://www.openstreetmap.org/copyright), the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/), [Overpass API guidance](https://wiki.openstreetmap.org/wiki/Overpass_API), [DResel Overpass terms](https://ovp.dresel.systems/en/), and [Private.coffee Overpass terms](https://overpass.private.coffee/).

Draft generation works without an AI key by creating a simple local template from the offer and business listing. With `OPENAI_API_KEY`, message analysis and draft generation use the configured AI provider. `OPENAI_MODEL` and `OPENAI_BASE_URL` can be set for the chosen OpenAI-compatible provider. Message analysis sends the message text only; the optional customer email field is excluded. Campaign drafting sends the campaign brief plus selected business listing fields (name, type, area, and website); saved contact names, email addresses, and phone numbers are excluded. Avoid putting personal or confidential information in messages or campaign briefs. Provider calls may incur charges. Each campaign generation covers at most 10 businesses. Drafts remain unsent: approving only marks them ready to copy or export. The app does not send email or WhatsApp messages automatically.

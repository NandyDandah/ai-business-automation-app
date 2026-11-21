# Saving clinic prospects to the FastAPI app

The app provides protected endpoints for prospect records. It never lets an unauthenticated caller read or write these records.

## Authentication

Send the app's private API token in the HTTP Authorization header:

Authorization: Bearer the-private-token

Keep the token in the agent or HTTP client's secret store. Never place it in a skill file, URL, prompt, log, or source-control file. Browser-cookie writes also require a CSRF token; an agent should use the bearer token.

## Batch create

POST to /prospects/batch with a JSON body containing one to 50 prospect records. Each record requires clinic_name and source_url. Include only business contact details supported by a source.

Fields: clinic_name, website, town, postcode, public_email, phone, contact_name, contact_role, source_url, contact_source_url, fit_score, fit_summary.

A successful response returns created, duplicates, and ids. Saving is idempotent for the same website and postcode. The app rejects a batch outside the one-to-50 range and bounds every text field.

## Read and delete

GET /prospects returns the latest records (100 by default, up to 500 with limit). DELETE /prospects/{id} removes one prospect. These operations also require authentication.

## Connectivity

Use the local base URL only when the agent runs on the same computer as the API. For a remote agent, the API needs an HTTPS address with private access controls. Do not make the database file or unauthenticated API public.


# Saving business prospects to the FastAPI app

The app provides protected endpoints for industry-neutral business records. Unauthenticated callers cannot read or write them.

## Authentication

Send the app's private API token in the HTTP Authorization header:

```http
Authorization: Bearer <private-token>
```

Keep the token in the agent or HTTP client's secret store. Never place it in a skill file, URL, prompt, log, or source-control file. Browser-cookie writes also require a CSRF token; an agent should use the bearer token.

## Batch create

POST to `/businesses/batch` with a JSON body containing one to 50 business records. Each record requires `business_name` and `source_url`. Include only contact details supported by an official business source.

Fields: `business_name`, `industry`, `business_type`, `website`, `city`, `region`, `country`, `postal_code`, `business_email`, `business_phone`, `contact_name`, `contact_role`, `source_url`, `contact_source_url`, `fit_score`, and `fit_summary`.

A successful response returns `created`, `duplicates`, and `ids`. Saving is idempotent for the same website and location. The app rejects a batch outside the one-to-50 range and bounds every text field.

The legacy `/prospects` routes and old field names remain available for existing integrations. New integrations should use `/businesses` and the generic field names above.

## Read and delete

- `GET /businesses` lists the latest records (100 by default, up to 500 with `limit`).
- `DELETE /businesses/{id}` removes one business record.

These operations require bearer authentication.

## Connectivity

Use a local base URL only when the agent runs on the same computer as the API. A remote agent needs an HTTPS address with private access controls. Do not make the database file or unauthenticated API public.


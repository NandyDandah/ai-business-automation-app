"""Small, bounded CSV reader for importing sourced business leads."""

import csv
import io
import re
from urllib.parse import urlparse


MAX_CSV_BYTES = 5 * 1024 * 1024
MAX_CSV_ROWS = 2000

_ALIASES = {
    "business_name": ("business_name", "clinic_name", "company_name", "company", "business", "name"),
    "industry": ("industry", "sector"),
    "business_type": ("business_type", "category", "type"),
    "website": ("website", "website_url", "company_website", "domain"),
    "city": ("city", "town", "locality"),
    "region": ("region", "state", "county", "province"),
    "country": ("country", "country_name"),
    "postal_code": ("postal_code", "postcode", "zip_code", "zip"),
    "business_email": ("business_email", "public_email", "work_email", "email"),
    "business_phone": ("business_phone", "public_phone", "phone_number", "telephone", "phone"),
    "contact_name": ("contact_name", "decision_maker", "person_name", "first_name"),
    "contact_role": ("contact_role", "job_title", "title", "role"),
    "source_url": ("source_url", "listing_url", "reference_url", "source_link"),
    "contact_source_url": ("contact_source_url", "contact_url", "email_source_url"),
}


def _header(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _web_url(value):
    value = " ".join(str(value or "").split())
    if not value:
        return ""
    if re.match(r"^[a-z][a-z0-9+.-]*:", value, re.IGNORECASE) and not re.match(r"^https?://", value, re.IGNORECASE):
        return None
    candidate = value if re.match(r"^https?://", value, re.IGNORECASE) else "https://" + value
    parsed = urlparse(candidate)
    if (
        re.search(r"\s", candidate) or parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname or parsed.username or parsed.password
    ):
        return None
    return candidate[:1000]


def parse_business_csv(contents):
    """Return normalized rows and invalid-row summaries without persisting data."""
    if not contents:
        raise ValueError("Choose a CSV file with a header row.")
    if len(contents) > MAX_CSV_BYTES:
        raise ValueError("CSV files must be 5 MB or smaller.")
    try:
        source = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            source = contents.decode("cp1252")
        except UnicodeDecodeError:
            raise ValueError("Could not read this file. Save it as UTF-8 CSV and try again.") from None
    sample = source[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(source, newline=""), dialect=dialect)
    if not reader.fieldnames:
        raise ValueError("The CSV needs a header row with a business name column.")
    header_map = {_header(name): name for name in reader.fieldnames if name}
    columns = {}
    for field, aliases in _ALIASES.items():
        columns[field] = next((header_map[name] for name in aliases if name in header_map), None)
    if not columns["business_name"]:
        raise ValueError("Add a column named business_name, company, clinic_name, or name.")

    rows = []
    invalid = []
    for row_number, raw in enumerate(reader, start=2):
        if row_number > MAX_CSV_ROWS + 1:
            raise ValueError("This CSV has more than 2,000 rows. Split it into smaller files.")
        values = {
            field: " ".join(str(raw.get(column) or "").split())[:limit]
            for field, column, limit in (
                ("business_name", columns["business_name"], 200),
                ("industry", columns["industry"], 120),
                ("business_type", columns["business_type"], 120),
                ("city", columns["city"], 120),
                ("region", columns["region"], 120),
                ("country", columns["country"], 120),
                ("postal_code", columns["postal_code"], 32),
                ("business_email", columns["business_email"], 320),
                ("business_phone", columns["business_phone"], 80),
                ("contact_name", columns["contact_name"], 160),
                ("contact_role", columns["contact_role"], 160),
                ("contact_source_url", columns["contact_source_url"], 1000),
            )
        }
        values["website"] = _web_url(raw.get(columns["website"]) if columns["website"] else "")
        source_url = _web_url(raw.get(columns["source_url"]) if columns["source_url"] else "")
        if values["website"] is None or source_url is None:
            invalid.append({"row": row_number, "reason": "Website or source link must be a valid web address."})
            continue
        values["source_url"] = source_url or values["website"]
        if not values["business_name"]:
            invalid.append({"row": row_number, "reason": "Business name is missing."})
            continue
        if not values["source_url"]:
            invalid.append({"row": row_number, "reason": "Add a website or source link for this business."})
            continue
        if values["contact_source_url"]:
            contact_url = _web_url(values["contact_source_url"])
            if not contact_url:
                values["contact_source_url"] = ""
            else:
                values["contact_source_url"] = contact_url
        rows.append(values)
    return {"rows": rows, "invalid": invalid}

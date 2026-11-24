"""Dry-run one-business workflow scoring for the Campaign Studio."""

import re


_FIT_GROUPS = (
    {"dental", "dentist", "dentistry"},
    {"aesthetic", "aesthetics", "beauty", "cosmetic", "skin", "medspa"},
    {"heating", "heatpump", "boiler"},
    {"renewable", "solar", "energy", "insulation"},
)
_GENERIC = {"business", "businesses", "company", "companies", "service", "services", "clinic", "clinics"}


def _tokens(value):
    normalized = str(value or "").lower()
    return {word for word in re.findall(r"[a-z0-9]+", normalized) if len(word) > 2}


def _country_key(value):
    value = " ".join(str(value or "").lower().split())
    if value in {"uk", "gb", "great britain", "britain", "england", "scotland", "wales", "northern ireland"}:
        return "united kingdom"
    if value in {"usa", "us", "united states of america"}:
        return "united states"
    return value


def _fit_component(campaign, business):
    target = _tokens(" ".join((campaign.get("business_type", ""), campaign.get("industry", "")))) - _GENERIC
    observed = _tokens(" ".join((business.get("business_name", ""), business.get("business_type", ""), business.get("industry", ""))))
    if not target:
        return 50, "The campaign has no target category to compare."
    if target & observed:
        matches = ", ".join(sorted(target & observed))
        return 92, f"Listing matches the campaign category through: {matches}."
    for group in _FIT_GROUPS:
        if target & group and observed & group:
            matches = ", ".join(sorted((target & group) | (observed & group)))
            return 76, f"Related category terms match: {matches}; confirm the business is a fit."
    return 28, "The saved business category does not clearly match the campaign target."


def _location_component(campaign, business):
    target_country = _country_key(campaign.get("country"))
    business_country = _country_key(business.get("country"))
    if target_country and business_country:
        if target_country == business_country:
            return 100, "Saved country matches the campaign."
        return 20, "Saved country differs from the campaign country."
    target_region = _tokens(campaign.get("region"))
    business_region = _tokens(" ".join((business.get("region", ""), business.get("city", ""))))
    if target_region and business_region:
        if target_region & business_region:
            return 85, "Saved area overlaps the campaign region."
        return 35, "Saved area does not clearly match the campaign region."
    return 50, "Location information is incomplete."


def simulate_business_fit(campaign, business):
    """Return an explainable, non-predictive priority score from saved fields only."""
    fit, fit_note = _fit_component(campaign, business)
    has_source = bool(str(business.get("source_url", "")).strip())
    source = 100 if has_source else (45 if business.get("website") else 0)
    source_note = "A source link is saved." if has_source else (
        "A website is saved, but no source link is recorded." if business.get("website")
        else "No source link or website is recorded."
    )

    has_email = bool(str(business.get("business_email", "")).strip())
    has_phone = bool(str(business.get("business_phone", "")).strip())
    has_website = bool(str(business.get("website", "")).strip())
    if has_email and has_phone:
        contact, contact_note = 100, "Saved record has a public email and phone field; neither was re-verified."
    elif has_email or has_phone:
        contact, contact_note = 72, "Saved record has one public contact channel; verify it before use."
    elif has_website:
        contact, contact_note = 45, "Website is saved, with no public email or phone in this record."
    else:
        contact, contact_note = 0, "No public contact route is saved."

    location, location_note = _location_component(campaign, business)
    score = round(fit * 0.45 + source * 0.15 + contact * 0.30 + location * 0.10)
    band = "strong signal" if score >= 80 else "review fit" if score >= 55 else "weak signal"
    return {
        "score": score,
        "band": band,
        "method": "Rules-based signal score from the saved listing. It is not a sales prediction.",
        "components": [
            {"name": "Offer fit", "score": fit, "evidence": fit_note},
            {"name": "Source trail", "score": source, "evidence": source_note},
            {"name": "Contactability", "score": contact, "evidence": contact_note},
            {"name": "Location", "score": location, "evidence": location_note},
        ],
    }


def one_business_timeline(current_stage="new"):
    """Describe a safe, human-reviewed sample path without sending or scheduling."""
    stage = str(current_stage or "new").replace("_", " ").title()
    return [
        {"when": "Now", "action": f"Check the source and category; current pipeline stage is {stage}."},
        {"when": "Before contact", "action": "Edit the unsent draft and check that contact is appropriate for this business."},
        {"when": "If you choose to contact", "action": "Send manually only after any required permission and compliance checks."},
        {"when": "Day 3 / Day 5", "action": "If there is no reply, prepare at most two useful follow-up drafts for review; stop after the final one."},
        {"when": "On a reply", "action": "Record the real outcome and update the pipeline; do not assume a sale."},
    ]

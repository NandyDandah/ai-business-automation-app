"""Small, source-backed prospecting helpers for the FastAPI workspace."""

import json
import os
import re
import time
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


class ProspectingError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


_CACHE = {}
_CACHE_LOCK = Lock()
_NOMINATIM_LOCK = Lock()
_LAST_NOMINATIM_REQUEST = 0.0
_CACHE_TTL_SECONDS = 6 * 60 * 60
_CACHE_LIMIT = 200
_BUSINESS_KEYS = ("shop", "office", "craft", "healthcare", "beauty", "tourism", "leisure")
_AMENITY_BUSINESSES = {
    "bank", "bar", "cafe", "car_rental", "car_repair", "clinic", "dentist",
    "doctors", "fast_food", "fuel", "hospital", "pharmacy", "pub", "restaurant",
    "school", "veterinary", "coworking_space", "language_school", "college",
}
_GENERIC_TYPE_WORDS = {"business", "businesses", "company", "companies", "service", "services", "near", "local"}
_TYPE_SYNONYMS = {
    "aesthetic": {"beauty", "clinic", "cosmetics"},
    "aesthetics": {"beauty", "clinic", "cosmetics"},
    "cosmetic": {"beauty", "clinic", "cosmetics"},
    "cosmetics": {"beauty", "clinic", "cosmetics"},
    "dental": {"dentist"},
    "dentistry": {"dentist"},
    "cafes": {"cafe"},
    "restaurants": {"restaurant"},
    "salons": {"salon", "beauty"},
}


def _https_endpoint(value: str, fallback: str) -> str:
    endpoint = (value or fallback).strip().rstrip("?")
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ProspectingError("The configured OpenStreetMap service must use HTTPS.", 503)
    return endpoint


def _user_agent() -> str:
    contact = (os.getenv("OSM_CONTACT_EMAIL") or os.getenv("PUBLIC_ENQUIRY_CONTACT_EMAIL") or "").strip()
    contact_part = f" (mailto:{contact})" if contact else ""
    return (
        "AI-Business-Automation-App/1.0 "
        "(+https://github.com/NandyDandah/ai-business-automation-app)" + contact_part
    )


def _fetch_json(request: Request, timeout: int = 35, service: str = "public map service"):
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 429 or exc.code >= 500:
            raise ProspectingError(f"The {service} is busy. Wait a little and try again.", 503) from None
        raise ProspectingError(f"The {service} rejected the request.", 502) from None
    except (URLError, TimeoutError, OSError):
        raise ProspectingError(f"The {service} could not be reached. Try again later.", 503) from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProspectingError(f"The {service} returned an unreadable response.", 502) from None


def _geocode(location: str):
    global _LAST_NOMINATIM_REQUEST
    endpoint = _https_endpoint(
        os.getenv("OSM_NOMINATIM_URL", ""),
        "https://nominatim.openstreetmap.org/search",
    )
    query = urlencode({"q": location, "format": "jsonv2", "limit": 1, "addressdetails": 1})
    request = Request(
        endpoint + ("&" if "?" in endpoint else "?") + query,
        headers={"Accept": "application/json", "User-Agent": _user_agent()},
    )
    # Nominatim's public endpoint allows at most one request per second per application.
    with _NOMINATIM_LOCK:
        wait = 1.0 - (time.monotonic() - _LAST_NOMINATIM_REQUEST)
        if wait > 0:
            time.sleep(wait)
        _LAST_NOMINATIM_REQUEST = time.monotonic()
        results = _fetch_json(request, timeout=20)
    if not isinstance(results, list) or not results:
        raise ProspectingError("We couldn't find that place. Try a city, town, or postcode.", 404)
    try:
        result = results[0]
        lat = float(result["lat"])
        lon = float(result["lon"])
    except (KeyError, TypeError, ValueError):
        raise ProspectingError("The place lookup returned incomplete map data.", 502) from None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ProspectingError("The place lookup returned invalid map coordinates.", 502)
    address = result.get("address") or {}
    locality = (
        address.get("city") or address.get("town") or address.get("village")
        or address.get("municipality") or result.get("name") or location
    )
    return {
        "lat": lat,
        "lon": lon,
        "label": result.get("display_name", location),
        "city": locality,
        "region": address.get("state", ""),
        "country": address.get("country", ""),
    }


def _overpass_businesses(place: dict, radius_m: int):
    endpoint = _https_endpoint(
        os.getenv("OSM_OVERPASS_URL", ""),
        "https://overpass-api.de/api/interpreter",
    )
    location = f"{place['lat']:.6f},{place['lon']:.6f}"
    selectors = [
        f'nwr(around:{radius_m},{location})["name"]["{key}"];'
        for key in _BUSINESS_KEYS
    ]
    selectors.append(
        f'nwr(around:{radius_m},{location})["name"]["amenity"~"^('
        + "|".join(sorted(_AMENITY_BUSINESSES))
        + ')$"];'
    )
    query = "[out:json][timeout:25];(" + "".join(selectors) + ");out center 160;"
    request = Request(
        endpoint,
        data=urlencode({"data": query}).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": _user_agent()},
        method="POST",
    )
    data = _fetch_json(request, timeout=40)
    elements = data.get("elements", []) if isinstance(data, dict) else []
    if not isinstance(elements, list):
        raise ProspectingError("The map service returned an unsupported search result.", 502)
    results = []
    for element in elements[:160]:
        tags = element.get("tags") or {}
        name = (tags.get("name") or "").strip()
        if not name:
            continue
        categories = {key: tags[key].replace("_", " ") for key in _BUSINESS_KEYS if tags.get(key)}
        amenity = tags.get("amenity", "")
        if amenity in _AMENITY_BUSINESSES:
            categories["amenity"] = amenity.replace("_", " ")
        if not categories:
            continue
        center = element.get("center") or element
        try:
            lat = float(center.get("lat"))
            lon = float(center.get("lon"))
        except (TypeError, ValueError):
            lat = lon = None
        osm_type = element.get("type", "node")
        osm_id = element.get("id")
        if not osm_id:
            continue
        category_text = " ".join(categories.values()).lower()
        results.append({
            "business_name": name,
            "business_type": ", ".join(f"{key.replace('_', ' ').title()}: {value}" for key, value in categories.items()),
            "website": tags.get("contact:website") or tags.get("website") or "",
            "business_email": tags.get("contact:email") or tags.get("email") or "",
            "business_phone": tags.get("contact:phone") or tags.get("phone") or "",
            "city": tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:village") or place["city"],
            "region": tags.get("addr:state") or place["region"],
            "country": tags.get("addr:country") or place["country"],
            "postal_code": tags.get("addr:postcode") or "",
            "source_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
            "contact_source_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}" if (tags.get("email") or tags.get("contact:email") or tags.get("phone") or tags.get("contact:phone")) else "",
            "fit_score": 0,
            "fit_summary": "",
            "_category_text": category_text,
            "_lat": lat,
            "_lon": lon,
        })
    return results


def _type_terms(business_type: str):
    words = {word.lower() for word in re.findall(r"[a-zA-Z0-9]+", business_type) if len(word) > 2}
    words.difference_update(_GENERIC_TYPE_WORDS)
    expanded = set(words)
    for word in words:
        expanded.update(_TYPE_SYNONYMS.get(word, set()))
    return expanded


def discover_openstreetmap_businesses(business_type: str, location: str, radius_m: int = 5000, limit: int = 40):
    """Run one user-requested OSM search and retain the original source links."""
    radius_m = max(1000, min(int(radius_m), 10000))
    limit = max(1, min(int(limit), 40))
    key = (" ".join(business_type.lower().split()), " ".join(location.lower().split()), radius_m, limit)
    now = time.time()
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if cached and cached[0] > now:
            return json.loads(json.dumps(cached[1]))
    place = _geocode(location)
    businesses = _overpass_businesses(place, radius_m)
    terms = _type_terms(business_type)
    for item in businesses:
        searchable = (item["business_name"] + " " + item["_category_text"]).lower()
        matched = not terms or any(term in searchable for term in terms)
        item["fit_score"] = 75 if matched else 30
        category = item["business_type"].strip() or "business listing"
        item["fit_summary"] = (
            f"OpenStreetMap category: {category}. Confirm the listing and suitability before contact."
            if matched else
            f"OpenStreetMap listing near {place['city']}; the map category may not match your search. Confirm before contact."
        )
        item.pop("_category_text", None)
        item.pop("_lat", None)
        item.pop("_lon", None)
    if terms:
        matched_rows = [item for item in businesses if item["fit_score"] == 75]
        if matched_rows:
            businesses = matched_rows
    businesses = businesses[:limit]
    result = {
        "location_label": place["label"],
        "search_area": place["city"],
        "radius_m": radius_m,
        "results": businesses,
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License (ODbL)",
    }
    with _CACHE_LOCK:
        if len(_CACHE) >= _CACHE_LIMIT:
            oldest = next(iter(_CACHE))
            _CACHE.pop(oldest, None)
        _CACHE[key] = (now + _CACHE_TTL_SECONDS, result)
    return result


def _local_template_drafts(campaign: dict, businesses: list[dict]):
    offer = " ".join((campaign.get("offer") or "").split())
    proof = " ".join((campaign.get("proof") or "").split())
    if not offer:
        raise ProspectingError("Add your offer to the campaign brief before creating drafts.", 422)
    drafts = []
    for business in businesses:
        name = " ".join((business.get("business_name") or "").split())
        area = " ".join((business.get("city") or business.get("region") or "").split())
        body = f"Hello {name},\n\n{offer}"
        if proof:
            body += f"\n\nOne example: {proof}"
        context = f"your work in {area}" if area else "your work"
        body += f"\n\nI thought this may be relevant to {context}. Would you be open to a brief conversation? If it isn't relevant, no problem."
        drafts.append({
            "business_id": business["id"],
            "subject": f"A question for {name}"[:240],
            "body": body[:3000],
            "reason": "Local template from the campaign brief and public listing. Review every detail before use.",
        })
    return drafts


def draft_outreach_messages(campaign: dict, businesses: list[dict]):
    """Create review-only drafts using business-level fields, never contact PII."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not businesses or len(businesses) > 10:
        raise ProspectingError("Choose between 1 and 10 businesses for each draft request.", 422)
    if not api_key:
        return _local_template_drafts(campaign, businesses)
    base_url = (os.getenv("OPENAI_BASE_URL", "").strip().rstrip("/") or "https://api.openai.com/v1")
    if urlparse(base_url).scheme != "https" or not urlparse(base_url).netloc:
        raise ProspectingError("The configured AI provider must use HTTPS.", 503)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    safe_businesses = [
        {
            "id": row["id"],
            "name": row["business_name"],
            "industry": row.get("industry", ""),
            "type": row.get("business_type", ""),
            "city": row.get("city", ""),
            "region": row.get("region", ""),
            "country": row.get("country", ""),
            "website": row.get("website", ""),
        }
        for row in businesses
    ]
    brief = {
        "campaign": {
            "title": campaign["title"],
            "industry": campaign.get("industry", ""),
            "business_type": campaign.get("business_type", ""),
            "offer": campaign.get("offer", ""),
            "proof": campaign.get("proof", ""),
            "tone": campaign.get("tone", "Professional"),
            "language": campaign.get("language", "English"),
        },
        "businesses": safe_businesses,
    }
    payload = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": 2400,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Write concise, honest first-contact drafts for the campaign. Use only facts in the supplied campaign brief and business listing. "
                    "Never claim you visited a website or researched the recipient. Never invent results, clients, reviews, urgency, or personal familiarity. "
                    "Do not include contact names, email addresses, or phone numbers. Keep each message under 90 words, use the requested language and tone, "
                    "state the sender's offer plainly, and end with one low-pressure question. Return a JSON object with a drafts array; each item must contain "
                    "business_id, subject, body, and reason."
                ),
            },
            {"role": "user", "content": json.dumps(brief, ensure_ascii=False)},
        ],
    }
    request = Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        response = _fetch_json(request, timeout=50, service="AI drafting provider")
        content = response["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        drafts = parsed["drafts"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        raise ProspectingError("The AI provider returned drafts in an unsupported format.", 502) from None
    if not isinstance(drafts, list):
        raise ProspectingError("The AI provider returned drafts in an unsupported format.", 502)
    allowed_ids = {row["id"] for row in safe_businesses}
    seen_ids = set()
    output = []
    for draft in drafts:
        if not isinstance(draft, dict):
            continue
        try:
            business_id = int(draft["business_id"])
            subject = str(draft.get("subject", "")).strip()[:240]
            body = str(draft["body"]).strip()[:3000]
            reason = str(draft.get("reason", "")).strip()[:1000]
        except (KeyError, TypeError, ValueError):
            continue
        if business_id in allowed_ids and business_id not in seen_ids and body:
            output.append({"business_id": business_id, "subject": subject, "body": body, "reason": reason})
            seen_ids.add(business_id)
    if seen_ids != allowed_ids:
        raise ProspectingError("The AI provider did not return a complete set of drafts. Please try again.", 502)
    return output

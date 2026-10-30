import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse

from .schemas import CATEGORIES

KEYWORDS = {
    "employment": ["jobs", "employment", "factory", "industrial", "plant", "company", "investment", "manufacturing", "business park"],
    "infrastructure": ["metro", "rail", "road", "corridor", "infrastructure", "airport", "flyover", "construction"],
    "housing": ["housing", "residential", "apartment", "urban development", "township", "real estate", "homes"],
    "transportation": ["bus", "transit", "transport", "station", "railway", "mobility", "highway"],
    "education": ["university", "college", "school", "campus", "education", "institute"],
    "other": ["government", "development", "project", "expansion", "investment"],
}


def valid_public_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def classify(text: str) -> str:
    lowered = text.lower()
    scores = {category: sum(1 for word in words if word in lowered) for category, words in KEYWORDS.items()}
    return max(scores, key=scores.get) if max(scores.values()) else "other"


def normalize_result(raw: dict, region: str) -> dict | None:
    title = str(raw.get("title") or "").strip()
    url = str(raw.get("url") or "").strip()
    snippet = str(raw.get("snippet") or raw.get("summary") or "").strip()
    if not title or not snippet or not valid_public_url(url):
        return None
    combined = f"{title} {snippet}"
    domain = str(raw.get("domain") or raw.get("publisher") or urlparse(url).netloc).strip()
    date_value = raw.get("date") or raw.get("publication_date")
    parsed_date = None
    if date_value:
        try:
            parsed_date = datetime.fromisoformat(str(date_value).replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            match = re.search(r"(20\d{2}[-/]\d{1,2}[-/]\d{1,2})", str(date_value))
            parsed_date = match.group(1).replace("/", "-") if match else str(date_value)[:40]
    category = classify(combined)
    identifier = hashlib.sha1(re.sub(r"\W", "", title.lower()).encode()).hexdigest()[:16]
    return {
        "title": title[:300], "summary": snippet[:1500], "region": region, "source_name": domain[:180],
        "source_url": url[:1000], "publication_date": parsed_date, "signal_category": category,
        "evidence_direction": "negative" if any(word in combined.lower() for word in ["delay", "cancelled", "halted", "shortage", "decline"]) else "positive",
        "relevance": min(1.0, 0.45 + 0.1 * sum(1 for word in region.lower().split() if word in combined.lower())),
        "confidence": 0.72 if raw.get("date") else 0.58, "duplicate_identifier": identifier,
    }


def deduplicate(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for item in items:
        key = item.get("duplicate_identifier") or item.get("source_url")
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def process_results(raw_results: list[dict], region: str) -> list[dict]:
    return deduplicate([normalized for raw in raw_results if (normalized := normalize_result(raw, region))])

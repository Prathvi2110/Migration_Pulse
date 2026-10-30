from datetime import date, timedelta
from urllib.parse import urlparse

import httpx

from .core import settings


CATEGORY_QUERIES = {
    "employment": '"{region}" jobs hiring employment factory industrial investment manufacturing company expansion',
    "infrastructure": '"{region}" metro railway road corridor infrastructure project construction',
    "housing": '"{region}" housing residential urban development project apartment township real estate',
    "transportation": '"{region}" public transport transit station bus railway mobility expansion',
    "education": '"{region}" university campus college school education expansion project',
    "other": '"{region}" government local development project investment expansion',
}


class TinyFishError(RuntimeError):
    pass


def _source_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""


def _normalize_item(item: dict) -> dict | None:
    """Normalize TinyFish Search's structured result fields for our evidence layer."""
    url = str(item.get("url") or item.get("link") or "").strip()
    title = str(item.get("title") or "").strip()
    snippet = str(
        item.get("snippet")
        or item.get("summary")
        or item.get("description")
        or item.get("excerpt")
        or ""
    ).strip()

    if not title or not url or not urlparse(url).scheme in {"http", "https"}:
        return None

    return {
        "title": title,
        "snippet": snippet or title,
        "url": url,
        "domain": str(item.get("domain") or item.get("publisher") or _source_domain(url)),
        "date": item.get("date") or item.get("publication_date") or item.get("published_at"),
    }


async def search_region(region: str, period_days: int) -> list[dict]:
    """Collect live regional development evidence from TinyFish Search."""
    api_key = (settings.tinyfish_api_key or "").strip()
    if not api_key:
        raise TinyFishError(
            "TinyFish is not configured. Add TINYFISH_API_KEY to backend/.env."
        )

    after_date = (date.today() - timedelta(days=period_days)).isoformat()
    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json",
    }
    results: list[dict] = []

    timeout = httpx.Timeout(45.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for category, template in CATEGORY_QUERIES.items():
            query = template.format(region=region)
            params = {
                "query": query,
                "purpose": (
                    f"Find recent public evidence for {region} in India that indicates "
                    "employment, infrastructure, housing, transportation, education, "
                    "or local development activity relevant to aggregate regional "
                    "migration-pressure analysis. Prefer concrete projects, hiring, "
                    "investment, approvals, construction, openings, or expansions."
                ),
                "location": "IN",
                "language": "en",
                "domain_type": "news",
                "after_date": after_date,
            }

            try:
                response = await client.get(
                    settings.tinyfish_search_url,
                    params=params,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                raise TinyFishError(
                    f"TinyFish timed out for {category}. Try again or reduce the analysis period."
                ) from exc
            except httpx.RequestError as exc:
                raise TinyFishError(
                    f"TinyFish connection failed for {category}: {exc}"
                ) from exc

            if response.is_error:
                body = response.text.strip().replace("\n", " ")[:1500]
                raise TinyFishError(
                    f"TinyFish returned HTTP {response.status_code} for {category}: {body}"
                )

            try:
                payload = response.json()
            except ValueError as exc:
                raise TinyFishError(
                    f"TinyFish returned non-JSON data for {category}: {response.text[:1000]}"
                ) from exc

            if not isinstance(payload, dict):
                raise TinyFishError(
                    f"TinyFish returned an unexpected response for {category}: {type(payload).__name__}"
                )

            category_results = payload.get("results") or payload.get("data") or []
            if not isinstance(category_results, list):
                category_results = []

            added = 0
            for raw_item in category_results[:10]:
                if not isinstance(raw_item, dict):
                    continue
                item = _normalize_item(raw_item)
                if not item:
                    continue
                results.append({**item, "signal_category": category})
                added += 1

            # A category can legitimately have no qualifying result; don't manufacture evidence.
            if added == 0:
                continue

    return results

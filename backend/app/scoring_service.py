from collections import defaultdict
from .schemas import CATEGORIES, CATEGORY_LABELS

WEIGHTS = {"employment": 0.25, "infrastructure": 0.20, "housing": 0.20, "transportation": 0.15, "education": 0.10, "other": 0.10}


def score_category(items: list[dict]) -> float | None:
    if not items:
        return None
    unique = items[:4]
    points = 0.0
    for item in unique:
        direction = item.get("evidence_direction", "positive")
        sign = -0.35 if direction == "negative" else 0 if direction == "neutral" else 1
        points += max(0.0, sign) * float(item.get("relevance", 0.5)) * float(item.get("confidence", 0.5))
    base = min(100.0, points / max(1, len(unique)) * 155 + min(len(unique), 4) * 7)
    negatives = sum(1 for item in unique if item.get("evidence_direction") == "negative")
    return round(max(0.0, base - negatives * 12), 1)


def calculate_scores(evidence: list[dict]) -> tuple[dict, float | None, float]:
    grouped = defaultdict(list)
    for item in evidence:
        grouped[item.get("signal_category", "other")].append(item)
    category_scores = {}
    available_weight = 0.0
    weighted_total = 0.0
    for category in CATEGORIES:
        score = score_category(grouped.get(category, []))
        category_scores[category] = {
            "label": CATEGORY_LABELS[category], "score": score, "available": score is not None,
            "evidence_count": len(grouped.get(category, [])), "weight": WEIGHTS[category],
        }
        if score is not None:
            available_weight += WEIGHTS[category]
            weighted_total += score * WEIGHTS[category]
    pulse = round(weighted_total / available_weight) if available_weight else None
    coverage = round(available_weight * 100, 1)
    return category_scores, pulse, coverage


def interpretation(score: float | None) -> str:
    if score is None:
        return "Insufficient evidence"
    if score < 25:
        return "Few observed development signals"
    if score < 50:
        return "Limited signals"
    if score < 70:
        return "Moderate signals"
    if score < 85:
        return "Elevated signals"
    return "Very strong signals"

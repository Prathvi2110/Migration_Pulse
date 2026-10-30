from math import ceil
from .scoring_service import interpretation


def explain(region: str, evidence: list[dict], scores: dict, pulse: float | None, coverage: float, mode: str) -> str:
    strongest = sorted([e for e in evidence if e.get("evidence_direction") == "positive"], key=lambda e: e.get("relevance", 0) * e.get("confidence", 0), reverse=True)[:2]
    limited = [value["label"] for value in scores.values() if not value["available"]]
    lead = "; ".join(item["title"] for item in strongest) or "No strong positive finding was available"
    caveat = f"Limited evidence was available for {', '.join(limited)}." if limited else "All weighted categories had at least one usable finding."
    mode_note = "This is clearly labelled demo evidence for interface testing." if mode == "demo" else "This scan used TinyFish Search results and should be reviewed against the linked sources."
    score_note = f"The provisional Migration Pulse Score is {pulse}/100 ({interpretation(pulse)})." if pulse is not None else "A provisional score could not be calculated because no usable evidence was available."
    return f"{score_note} The strongest observed signals for {region} were: {lead}. {caveat} Data coverage is {coverage:.0f}% of the configured category weights; coverage is not prediction accuracy. {mode_note} The evidence indicates development activity, not the percentage of people expected to migrate, and it does not establish a scientifically validated prediction."


def simulate(data: dict) -> dict:
    population = data["additional_population"]
    return {
        "inputs": data,
        "households_required": round(population / data["average_household_size"]),
        "daily_water_litres": round(population * data["litres_per_person_per_day"]),
        "classrooms_required": ceil(population * (data["school_age_percentage"] / 100) / data["students_per_classroom"]),
        "hospital_beds_required": round(population * data["hospital_beds_per_1000"] / 1000),
        "disclaimer": "Hypothetical planning estimates only. They are not confirmed infrastructure shortages or predictions of actual migration.",
    }

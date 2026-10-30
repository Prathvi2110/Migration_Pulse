import os
os.environ["DATABASE_URL"] = "sqlite:///./test_migration_pulse.db"
os.environ["DEMO_MODE"] = "true"
from fastapi.testclient import TestClient
from app.main import app
from app.scoring_service import calculate_scores
from app.analysis_services import simulate
from app.evidence_service import deduplicate


def test_scoring_renormalizes_available_categories():
    scores, pulse, coverage = calculate_scores([{"signal_category":"employment","evidence_direction":"positive","relevance":1,"confidence":1}])
    assert scores["employment"]["available"] is True
    assert pulse > 0
    assert coverage == 25.0


def test_missing_evidence_is_unavailable():
    scores, pulse, coverage = calculate_scores([])
    assert pulse is None
    assert coverage == 0
    assert scores["housing"]["available"] is False


def test_duplicate_evidence_is_removed():
    items = [{"duplicate_identifier":"same","title":"one"},{"duplicate_identifier":"same","title":"two"}]
    assert len(deduplicate(items)) == 1


def test_simulator_matches_illustrative_calculation():
    result = simulate({"additional_population":100000,"average_household_size":4,"litres_per_person_per_day":135,"school_age_percentage":20,"students_per_classroom":30,"hospital_beds_per_1000":2})
    assert result["households_required"] == 25000
    assert result["daily_water_litres"] == 13500000
    assert result["classrooms_required"] == 667
    assert result["hospital_beds_required"] == 200


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_analysis_validation():
    with TestClient(app) as client:
        response = client.post("/api/analyze", json={"region":"","period_days":90})
        assert response.status_code == 422

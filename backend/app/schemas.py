from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator

CATEGORIES = ["employment", "infrastructure", "housing", "transportation", "education", "other"]
CATEGORY_LABELS = {
    "employment": "Employment & industry",
    "infrastructure": "Infrastructure",
    "housing": "Housing & urban development",
    "transportation": "Transportation",
    "education": "Education",
    "other": "Other local development",
}


class AnalyzeRequest(BaseModel):
    region: str = Field(min_length=2, max_length=180)
    period_days: int = Field(default=90, ge=1, le=365)

    @field_validator("region")
    @classmethod
    def clean_region(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("Region is required")
        return value


class EvidenceOut(BaseModel):
    id: int | None = None
    title: str
    summary: str
    region: str
    source_name: str
    source_url: str
    publication_date: str | None = None
    signal_category: str
    evidence_direction: Literal["positive", "negative", "neutral"] = "positive"
    relevance: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    duplicate_identifier: str | None = None


class AnalysisOut(BaseModel):
    id: int
    region: str
    period_days: int
    created_at: datetime
    status: str
    mode: str
    pulse_score: float | None
    data_coverage: float
    category_scores: dict
    explanation: str
    evidence_count: int
    evidence: list[EvidenceOut]


class SimulationRequest(BaseModel):
    additional_population: int = Field(default=100000, ge=1, le=10000000)
    average_household_size: float = Field(default=4, gt=0, le=20)
    litres_per_person_per_day: float = Field(default=135, gt=0, le=1000)
    school_age_percentage: float = Field(default=20, ge=0, le=100)
    students_per_classroom: int = Field(default=30, ge=1, le=200)
    hospital_beds_per_1000: float = Field(default=2, ge=0, le=100)


class SimulationOut(BaseModel):
    inputs: SimulationRequest
    households_required: int
    daily_water_litres: int
    classrooms_required: int
    hospital_beds_required: int
    disclaimer: str


class HealthOut(BaseModel):
    status: str
    database: str
    tinyfish_configured: bool
    demo_mode: bool
    timestamp: datetime

from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .analysis_services import explain, simulate
from .core import Analysis, Evidence, get_db, init_db, settings
from .evidence_service import process_results
from .schemas import AnalysisOut, AnalyzeRequest, EvidenceOut, HealthOut, SimulationOut, SimulationRequest
from .scoring_service import calculate_scores
from .tinyfish_service import TinyFishError, search_region


app = FastAPI(title="Migration Pulse AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize(analysis: Analysis) -> dict:
    return {
        "id": analysis.id,
        "region": analysis.region,
        "period_days": analysis.period_days,
        "created_at": analysis.created_at,
        "status": analysis.status,
        "mode": analysis.mode,
        "pulse_score": analysis.pulse_score,
        "data_coverage": analysis.data_coverage,
        "category_scores": analysis.category_scores or {},
        "explanation": analysis.explanation,
        "evidence_count": len(analysis.evidence),
        "evidence": [
            {
                "id": e.id,
                "title": e.title,
                "summary": e.summary,
                "region": e.region,
                "source_name": e.source_name,
                "source_url": e.source_url,
                "publication_date": e.publication_date,
                "signal_category": e.signal_category,
                "evidence_direction": e.evidence_direction,
                "relevance": e.relevance,
                "confidence": e.confidence,
                "duplicate_identifier": e.duplicate_identifier,
            }
            for e in analysis.evidence
        ],
    }


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        database="sqlite",
        tinyfish_configured=bool(settings.tinyfish_api_key),
        demo_mode=False,
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/api/config/status")
def config_status() -> dict:
    return {
        "tinyfish_configured": bool(settings.tinyfish_api_key),
        "llm_configured": bool(settings.llm_api_key),
        "demo_mode": False,
        "tinyfish_api": "Search API",
    }


@app.post("/api/analyze", response_model=AnalysisOut)
async def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)) -> AnalysisOut:
    if not settings.tinyfish_api_key:
        raise HTTPException(
            status_code=503,
            detail="TinyFish is not configured. Add TINYFISH_API_KEY to backend/.env and restart FastAPI.",
        )

    try:
        raw = await search_region(request.region, request.period_days)
    except TinyFishError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    evidence = process_results(raw, request.region)
    if not evidence:
        raise HTTPException(
            status_code=502,
            detail=(
                "TinyFish returned no usable public evidence for this region and period. "
                "Try a broader period or a more specific region name."
            ),
        )

    scores, pulse, coverage = calculate_scores(evidence)
    record = Analysis(
        region=request.region,
        period_days=request.period_days,
        status="completed",
        mode="live",
        pulse_score=pulse,
        data_coverage=coverage,
        category_scores=scores,
        explanation=explain(request.region, evidence, scores, pulse, coverage, "live"),
    )
    db.add(record)
    db.flush()
    for item in evidence:
        db.add(Evidence(analysis_id=record.id, **item))
    db.commit()
    db.refresh(record)
    return serialize(record)


@app.get("/api/analysis-history", response_model=list[AnalysisOut])
def history(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)) -> list[AnalysisOut]:
    return [serialize(item) for item in db.query(Analysis).order_by(Analysis.created_at.desc()).limit(limit).all()]


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisOut:
    item = db.get(Analysis, analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return serialize(item)


@app.get("/api/evidence/{analysis_id}", response_model=list[EvidenceOut])
def get_evidence(analysis_id: int, db: Session = Depends(get_db)) -> list[EvidenceOut]:
    item = db.get(Analysis, analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return [
        EvidenceOut(
            id=e.id,
            title=e.title,
            summary=e.summary,
            region=e.region,
            source_name=e.source_name,
            source_url=e.source_url,
            publication_date=e.publication_date,
            signal_category=e.signal_category,
            evidence_direction=e.evidence_direction,
            relevance=e.relevance,
            confidence=e.confidence,
            duplicate_identifier=e.duplicate_identifier,
        )
        for e in item.evidence
    ]


@app.post("/api/simulate", response_model=SimulationOut)
def run_simulation(request: SimulationRequest) -> SimulationOut:
    return SimulationOut(**simulate(request.model_dump()))

from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    tinyfish_api_key: str | None = None
    tinyfish_search_url: str = "https://api.search.tinyfish.ai"
    llm_api_key: str | None = None
    # Live TinyFish is the only supported operating mode for this build.
    demo_mode: bool = False
    database_url: str = "sqlite:///./migration_pulse.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3003,http://127.0.0.1:3003,http://localhost:5173,http://127.0.0.1:5173"
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
database_url = settings.database_url
if database_url.startswith("mysql"):
    database_url = "sqlite:///./migration_pulse.db"
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    region: Mapped[str] = mapped_column(String(180), index=True)
    period_days: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(30), default="completed")
    mode: Mapped[str] = mapped_column(String(20), default="live")
    pulse_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_coverage: Mapped[float] = mapped_column(Float, default=0)
    category_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    explanation: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text)
    region: Mapped[str] = mapped_column(String(180))
    source_name: Mapped[str] = mapped_column(String(180))
    source_url: Mapped[str] = mapped_column(String(1000))
    publication_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    signal_category: Mapped[str] = mapped_column(String(80))
    evidence_direction: Mapped[str] = mapped_column(String(40), default="positive")
    relevance: Mapped[float] = mapped_column(Float, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    duplicate_identifier: Mapped[str | None] = mapped_column(String(300), nullable=True)
    analysis: Mapped[Analysis] = relationship(back_populates="evidence")


def init_db() -> None:
    Path(".").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

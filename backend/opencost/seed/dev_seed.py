from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from opencost.ingestion.service import ingest_paths


def seed_dev_data(db: Session) -> int:
    base = Path(__file__).resolve().parents[2] / "data" / "samples"
    sources = [
        ("session_logs", base),
        ("telemetry", base),
    ]
    return ingest_paths(db, sources)

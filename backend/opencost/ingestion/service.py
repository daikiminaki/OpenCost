from __future__ import annotations

import time
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from opencost.classification.heuristics import classify_event
from opencost.ingestion.normalize import normalize_record, parse_file
from opencost.models.models import TaskClassification, UsageEvent
from opencost.pricing.engine import estimate_cost


def ingest_paths(db: Session, sources: list[tuple[str, Path]]) -> int:
    inserted = 0
    for source_type, base_path in sources:
        if not base_path.exists():
            continue
        files = [p for p in base_path.rglob("*") if p.suffix in {".jsonl", ".json", ".log"}]
        for file in files:
            for raw in parse_file(file):
                normalized = normalize_record(raw, source_type, str(file))
                exists = db.scalar(select(UsageEvent).where(UsageEvent.event_fingerprint == normalized["event_fingerprint"]))
                if exists:
                    continue
                normalized["estimated_cost_usd"] = estimate_cost(
                    db,
                    normalized.get("provider"),
                    normalized.get("model"),
                    normalized["prompt_tokens"],
                    normalized["completion_tokens"],
                    normalized["cached_tokens"],
                )
                event = UsageEvent(**normalized)
                db.add(event)
                db.flush()
                category, confidence, reason = classify_event({**raw, **normalized})
                event.task_category = category
                db.add(TaskClassification(usage_event_id=event.id, category=category, confidence=confidence, reason=reason))
                inserted += 1
    db.commit()
    return inserted


def watch_paths(db: Session, sources: list[tuple[str, Path]], interval_sec: int = 5) -> None:
    while True:
        ingest_paths(db, sources)
        time.sleep(interval_sec)

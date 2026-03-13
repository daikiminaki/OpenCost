from __future__ import annotations

from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import cast, desc, func, select
from sqlalchemy.orm import Session

from opencost.db.init_db import init_db
from opencost.db.session import get_db
from opencost.models.models import RoutingConfigVersion, UsageEvent
from opencost.schemas.api import ConfigVersionResponse, HealthResponse, OverviewResponse, RecommendationResponse
from opencost.services.core import export_config, generate_and_fetch, get_cost_summary, get_recommendations, get_usage_breakdown, simulate_config

init_db()
app = FastAPI(title="OpenCost")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/overview", response_model=OverviewResponse)
def overview(period: str = "7d", db: Session = Depends(get_db)):
    return get_cost_summary(db, period)


@app.get("/api/usage/daily")
def usage_daily(db: Session = Depends(get_db)):
    stmt = (
        select(cast(UsageEvent.timestamp, date), func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0), func.coalesce(func.sum(UsageEvent.total_tokens), 0))
        .group_by(cast(UsageEvent.timestamp, date))
        .order_by(cast(UsageEvent.timestamp, date))
    )
    return [{"day": str(r[0]), "total_cost_usd": float(r[1]), "total_tokens": int(r[2])} for r in db.execute(stmt)]


@app.get("/api/usage/models")
def usage_models(period: str = "30d", db: Session = Depends(get_db)):
    return get_usage_breakdown(db, "model", period)


@app.get("/api/usage/categories")
def usage_categories(period: str = "30d", db: Session = Depends(get_db)):
    return get_usage_breakdown(db, "category", period)


@app.get("/api/sessions/recent")
def sessions_recent(db: Session = Depends(get_db)):
    events = list(db.scalars(select(UsageEvent).order_by(desc(UsageEvent.timestamp)).limit(25)))
    return [{"id": e.id, "timestamp": e.timestamp.isoformat(), "session_id": e.session_id, "model": e.model, "total_tokens": e.total_tokens, "estimated_cost_usd": e.estimated_cost_usd} for e in events]


@app.get("/api/recommendations", response_model=list[RecommendationResponse])
def recommendations(strategy: str | None = None, db: Session = Depends(get_db)):
    recs = get_recommendations(db, strategy)
    return [RecommendationResponse(**r.__dict__) for r in recs]


@app.post("/api/recommendations/generate", response_model=list[RecommendationResponse])
def recommendations_generate(db: Session = Depends(get_db)):
    recs = generate_and_fetch(db)
    return [RecommendationResponse(**r.__dict__) for r in recs]


@app.get("/api/configs", response_model=list[ConfigVersionResponse])
def configs(db: Session = Depends(get_db)):
    versions = list(db.scalars(select(RoutingConfigVersion).order_by(desc(RoutingConfigVersion.created_at)).limit(50)))
    return [ConfigVersionResponse(**v.__dict__) for v in versions]


@app.get("/api/configs/{config_id}", response_model=ConfigVersionResponse)
def config_get(config_id: int, db: Session = Depends(get_db)):
    cfg = db.get(RoutingConfigVersion, config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Config not found")
    return ConfigVersionResponse(**cfg.__dict__)


@app.post("/api/configs/export")
def config_export(payload: dict, db: Session = Depends(get_db)):
    config_id = int(payload.get("id", 0))
    try:
        return {"config": export_config(db, config_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


class SimulateRequest(BaseModel):
    config: dict
    period: str = "30d"


@app.post("/api/simulate")
def simulate(request: SimulateRequest, db: Session = Depends(get_db)):
    return simulate_config(db, request.config, request.period)

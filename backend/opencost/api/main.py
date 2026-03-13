from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import cast, desc, func, select
from sqlalchemy.orm import Session

from opencost.db.init_db import init_db
from opencost.db.session import get_db
from opencost.models.models import RoutingConfigVersion, UsageEvent
from opencost.schemas.api import ConfigVersionResponse, HealthResponse, OverviewResponse, RecommendationResponse
from opencost.services.analytics_service import (
    get_agent_usage,
    get_cost_trend,
    get_logs,
    get_model_usage,
    get_optimization_insights,
    get_overview_metrics,
    get_provider_usage,
    get_recent_sessions,
)
from opencost.services.core import (
    export_config,
    generate_and_fetch,
    get_cost_summary,
    get_recommendations,
    get_usage_breakdown,
    simulate_config,
)

init_db()
app = FastAPI(title="OpenCost")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/overview", response_model=OverviewResponse)
def overview(period: str = "7d", db: Session = Depends(get_db)):
    return get_cost_summary(db, period)


@app.get("/api/dashboard/overview")
def dashboard_overview(db: Session = Depends(get_db)):
    return {
        "kpis": get_overview_metrics(db),
        "cost_trend": get_cost_trend(db, days=30),
        "provider_breakdown": get_provider_usage(db, days=30),
        "model_distribution": get_usage_breakdown(db, "model", "30d"),
        "task_category_distribution": get_usage_breakdown(db, "category", "30d"),
    }


@app.get("/api/dashboard/recent-sessions")
def dashboard_recent_sessions(limit: int = 20, db: Session = Depends(get_db)):
    return {"sessions": get_recent_sessions(db, limit=min(limit, 100))}


@app.get("/api/logs")
def logs(
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    start_time: str | None = None,
    end_time: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    task_category: str | None = None,
    agent: str | None = None,
    session_id: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    return get_logs(
        db,
        {
            "limit": limit,
            "offset": offset,
            "start_time": start_time,
            "end_time": end_time,
            "provider": provider,
            "model": model,
            "task_category": task_category,
            "agent": agent,
            "session_id": session_id,
            "q": q,
        },
    )


@app.get("/api/analytics/model-usage")
def analytics_model_usage(days: int = 30, db: Session = Depends(get_db)):
    return {"series": get_model_usage(db, days=min(days, 180))}


@app.get("/api/analytics/provider-usage")
def analytics_provider_usage(days: int = 30, db: Session = Depends(get_db)):
    return {"rows": get_provider_usage(db, days=min(days, 180))}


@app.get("/api/analytics/agent-usage")
def analytics_agent_usage(days: int = 30, db: Session = Depends(get_db)):
    return {"rows": get_agent_usage(db, days=min(days, 180))}


@app.get("/api/analytics/token-efficiency")
def analytics_token_efficiency(days: int = 30, db: Session = Depends(get_db)):
    stmt = (
        select(UsageEvent.task_id, UsageEvent.prompt_tokens, UsageEvent.completion_tokens, UsageEvent.model)
        .where(UsageEvent.timestamp >= func.datetime("now", f"-{min(days,180)} days"), UsageEvent.prompt_tokens > 0)
        .order_by(desc(UsageEvent.timestamp))
        .limit(500)
    )
    return {
        "points": [
            {
                "task_id": r[0],
                "prompt_tokens": int(r[1]),
                "completion_tokens": int(r[2]),
                "model": r[3],
            }
            for r in db.execute(stmt)
        ]
    }


@app.get("/api/reports/cost")
def reports_cost(period: str = "30d", db: Session = Depends(get_db)):
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    return {
        "period": period,
        "cost_trend": get_cost_trend(db, days),
        "cost_by_task_type": get_usage_breakdown(db, "category", period if period in {"7d", "30d"} else "30d"),
        "cost_by_model": get_usage_breakdown(db, "model", period if period in {"7d", "30d"} else "30d"),
        "monthly_summary": _monthly_summary(db),
    }


@app.get("/api/insights")
def insights(days: int = 30, db: Session = Depends(get_db)):
    return {"insights": get_optimization_insights(db, days=min(days, 180))}


def _monthly_summary(db: Session) -> list[dict]:
    month_expr = func.strftime("%Y-%m", UsageEvent.timestamp)
    stmt = (
        select(
            month_expr,
            func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0),
            func.coalesce(func.sum(UsageEvent.total_tokens), 0),
            func.count(func.distinct(UsageEvent.session_id)),
        )
        .group_by(month_expr)
        .order_by(desc(month_expr))
        .limit(12)
    )
    rows = []
    for r in db.execute(stmt):
        sessions = int(r[3] or 0)
        rows.append(
            {
                "month": r[0],
                "total_cost": float(r[1]),
                "total_tokens": int(r[2]),
                "sessions": sessions,
                "avg_cost_per_session": round(float(r[1]) / sessions, 6) if sessions else 0.0,
            }
        )
    return rows


@app.get("/api/usage/daily")
def usage_daily(db: Session = Depends(get_db)):
    stmt = (
        select(func.date(UsageEvent.timestamp), func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0), func.coalesce(func.sum(UsageEvent.total_tokens), 0))
        .group_by(func.date(UsageEvent.timestamp))
        .order_by(func.date(UsageEvent.timestamp))
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
    return [
        {
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "session_id": e.session_id,
            "model": e.model,
            "total_tokens": e.total_tokens,
            "estimated_cost_usd": e.estimated_cost_usd,
        }
        for e in events
    ]


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

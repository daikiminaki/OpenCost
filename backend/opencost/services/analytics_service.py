from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import Date, String, case, cast, desc, func, or_, select
from sqlalchemy.orm import Session

from opencost.models.models import UsageEvent


def _window(days: int) -> datetime:
    return datetime.utcnow() - timedelta(days=days)


def get_overview_metrics(db: Session) -> dict:
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    seven_days_ago = _window(7)

    today_cost = db.scalar(select(func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0)).where(UsageEvent.timestamp >= today_start)) or 0.0
    seven = db.execute(
        select(
            func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0),
            func.coalesce(func.sum(UsageEvent.total_tokens), 0),
            func.count(func.distinct(UsageEvent.session_id)),
            func.count(UsageEvent.id),
        ).where(UsageEvent.timestamp >= seven_days_ago)
    ).one()
    most_model = db.execute(
        select(UsageEvent.model, func.count(UsageEvent.id).label("c"))
        .where(UsageEvent.timestamp >= seven_days_ago)
        .group_by(UsageEvent.model)
        .order_by(desc("c"))
        .limit(1)
    ).first()

    total_cost_7d = float(seven[0] or 0.0)
    total_tasks_7d = int(seven[3] or 0)
    return {
        "total_cost_today": round(float(today_cost), 4),
        "total_cost_7d": round(total_cost_7d, 4),
        "total_tokens_7d": int(seven[1] or 0),
        "total_sessions_7d": int(seven[2] or 0),
        "avg_cost_per_task_7d": round(total_cost_7d / total_tasks_7d, 6) if total_tasks_7d else 0.0,
        "most_used_model_7d": most_model[0] if most_model else None,
    }


def get_cost_trend(db: Session, days: int = 30) -> list[dict]:
    stmt = (
        select(
            cast(UsageEvent.timestamp, Date).label("day"),
            func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0),
        )
        .where(UsageEvent.timestamp >= _window(days))
        .group_by(cast(UsageEvent.timestamp, Date))
        .order_by(cast(UsageEvent.timestamp, Date))
    )
    return [{"day": str(r[0]), "total_cost_usd": float(r[1])} for r in db.execute(stmt)]


def get_model_usage(db: Session, days: int = 30) -> list[dict]:
    stmt = (
        select(cast(UsageEvent.timestamp, Date), UsageEvent.model, func.coalesce(func.sum(UsageEvent.total_tokens), 0))
        .where(UsageEvent.timestamp >= _window(days))
        .group_by(cast(UsageEvent.timestamp, Date), UsageEvent.model)
        .order_by(cast(UsageEvent.timestamp, Date))
    )
    return [{"day": str(r[0]), "model": r[1], "tokens": int(r[2])} for r in db.execute(stmt)]


def get_provider_usage(db: Session, days: int = 30) -> list[dict]:
    stmt = (
        select(
            UsageEvent.provider,
            func.coalesce(func.sum(UsageEvent.total_tokens), 0),
            func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0),
        )
        .where(UsageEvent.timestamp >= _window(days))
        .group_by(UsageEvent.provider)
        .order_by(desc(func.sum(UsageEvent.total_tokens)))
    )
    return [{"provider": r[0], "tokens": int(r[1]), "cost_usd": float(r[2])} for r in db.execute(stmt)]


def get_agent_usage(db: Session, days: int = 30) -> list[dict]:
    stmt = (
        select(UsageEvent.agent_name, func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0), func.count(UsageEvent.id))
        .where(UsageEvent.timestamp >= _window(days))
        .group_by(UsageEvent.agent_name)
        .order_by(desc(func.sum(UsageEvent.estimated_cost_usd)))
    )
    return [{"agent": r[0], "cost_usd": float(r[1]), "events": int(r[2])} for r in db.execute(stmt)]


def get_recent_sessions(db: Session, limit: int = 20) -> list[dict]:
    stmt = (
        select(
            UsageEvent.session_id,
            func.max(UsageEvent.timestamp).label("last_seen"),
            func.max(UsageEvent.agent_name),
            func.max(UsageEvent.model),
            func.sum(UsageEvent.total_tokens),
            func.sum(func.coalesce(UsageEvent.estimated_cost_usd, 0.0)),
            func.max(UsageEvent.task_category),
            (func.julianday(func.max(UsageEvent.timestamp)) - func.julianday(func.min(UsageEvent.timestamp))) * 24 * 60 * 60,
        )
        .group_by(UsageEvent.session_id)
        .order_by(desc("last_seen"))
        .limit(limit)
    )
    return [
        {
            "session_id": r[0],
            "last_seen": r[1].isoformat() if r[1] else None,
            "agent": r[2],
            "model": r[3],
            "total_tokens": int(r[4] or 0),
            "estimated_cost_usd": round(float(r[5] or 0.0), 6),
            "task_category": r[6],
            "duration_seconds": round(float(r[7] or 0.0), 2),
        }
        for r in db.execute(stmt)
    ]


def get_logs(db: Session, filters: dict) -> dict:
    limit = min(int(filters.get("limit", 50)), 200)
    offset = max(int(filters.get("offset", 0)), 0)
    stmt = select(UsageEvent)

    if filters.get("start_time"):
        stmt = stmt.where(UsageEvent.timestamp >= datetime.fromisoformat(filters["start_time"]))
    if filters.get("end_time"):
        stmt = stmt.where(UsageEvent.timestamp <= datetime.fromisoformat(filters["end_time"]))
    for key, col in {
        "provider": UsageEvent.provider,
        "model": UsageEvent.model,
        "task_category": UsageEvent.task_category,
        "agent": UsageEvent.agent_name,
        "session_id": UsageEvent.session_id,
    }.items():
        if filters.get(key):
            stmt = stmt.where(col == filters[key])
    if filters.get("q"):
        q = f"%{filters['q']}%"
        stmt = stmt.where(or_(cast(UsageEvent.raw_payload_json, String).like(q), UsageEvent.task_id.like(q), UsageEvent.session_id.like(q)))

    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    events = list(db.scalars(stmt.order_by(desc(UsageEvent.timestamp)).offset(offset).limit(limit)))
    return {
        "events": [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "session_id": e.session_id,
                "event_type": e.source_type,
                "model": e.model,
                "provider": e.provider,
                "tokens": e.total_tokens,
                "cost": e.estimated_cost_usd,
                "latency": e.latency_ms,
                "tool_calls": e.tool_calls_count,
                "agent": e.agent_name,
                "task_category": e.task_category,
                "raw_event_json": e.raw_payload_json,
            }
            for e in events
        ],
        "total_count": int(total_count),
    }


def get_optimization_insights(db: Session, days: int = 30) -> list[dict]:
    start = _window(days)
    insights: list[dict] = []

    premium_chat = db.execute(
        select(
            func.count(UsageEvent.id),
            func.sum(case((UsageEvent.model.like("%4o%"), 1), else_=0)),
            func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0),
        ).where(UsageEvent.timestamp >= start, UsageEvent.task_category == "chat_general")
    ).one()
    total_chat = int(premium_chat[0] or 0)
    premium_chat_calls = int(premium_chat[1] or 0)
    if total_chat > 0 and premium_chat_calls / total_chat >= 0.5:
        ratio = round((premium_chat_calls / total_chat) * 100, 1)
        savings = round(float(premium_chat[2] or 0.0) * 0.35, 2)
        insights.append(
            {
                "title": "Overpowered model usage in chat_general",
                "description": f"{ratio}% of chat_general tasks used premium-like models.",
                "evidence": {"total_chat_tasks": total_chat, "premium_calls": premium_chat_calls},
                "suggested_routing_strategy": "Route chat_general to cheap tier by default.",
                "estimated_monthly_savings_usd": savings,
            }
        )

    retry_stmt = (
        select(UsageEvent.session_id, func.count(UsageEvent.id).label("calls"))
        .where(UsageEvent.timestamp >= start)
        .group_by(UsageEvent.session_id)
        .having(func.count(UsageEvent.id) > 5)
        .order_by(desc("calls"))
        .limit(10)
    )
    retry_sessions = [{"session_id": r[0], "calls": int(r[1])} for r in db.execute(retry_stmt)]
    if retry_sessions:
        insights.append(
            {
                "title": "Retry loop candidates",
                "description": "Sessions with >5 model calls may indicate retries or loops.",
                "evidence": retry_sessions,
                "suggested_routing_strategy": "Add guardrails/timeouts and fallback-to-cheap for retries.",
                "estimated_monthly_savings_usd": round(len(retry_sessions) * 1.2, 2),
            }
        )

    high_latency = db.execute(
        select(UsageEvent.task_id, UsageEvent.model, UsageEvent.latency_ms)
        .where(UsageEvent.timestamp >= start, UsageEvent.latency_ms.is_not(None), UsageEvent.latency_ms > 8000)
        .order_by(desc(UsageEvent.latency_ms))
        .limit(10)
    ).all()
    if high_latency:
        insights.append(
            {
                "title": "High latency tasks",
                "description": "Detected tasks above 8s latency threshold.",
                "evidence": [{"task_id": r[0], "model": r[1], "latency_ms": r[2]} for r in high_latency],
                "suggested_routing_strategy": "Use faster model tier for low-complexity classes.",
                "estimated_monthly_savings_usd": round(len(high_latency) * 0.5, 2),
            }
        )

    ineff = db.execute(
        select(UsageEvent.task_id, UsageEvent.completion_tokens, UsageEvent.prompt_tokens)
        .where(UsageEvent.timestamp >= start, UsageEvent.completion_tokens > (UsageEvent.prompt_tokens * 2), UsageEvent.prompt_tokens > 0)
        .limit(10)
    ).all()
    if ineff:
        insights.append(
            {
                "title": "Token inefficiency",
                "description": "Completion tokens significantly exceed prompt tokens.",
                "evidence": [{"task_id": r[0], "completion_tokens": r[1], "prompt_tokens": r[2]} for r in ineff],
                "suggested_routing_strategy": "Trim max output tokens and tighten prompts.",
                "estimated_monthly_savings_usd": round(len(ineff) * 0.8, 2),
            }
        )

    return insights

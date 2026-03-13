from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from opencost.models.models import OptimizerRecommendation, TaskClassification, UsageEvent

STRATEGIES = {
    "ultra_cheap": {"factor": 0.55, "risk": "high", "confidence": 0.63},
    "balanced": {"factor": 0.75, "risk": "medium", "confidence": 0.78},
    "premium_safe": {"factor": 0.9, "risk": "low", "confidence": 0.86},
}


def _routing_payload(strategy: str) -> dict:
    tier_map = {
        "ultra_cheap": ("cheap", "cheap", "mid"),
        "balanced": ("cheap", "mid", "premium"),
        "premium_safe": ("mid", "premium", "premium"),
    }
    chat, coding, planning = tier_map[strategy]
    return {
        "defaults": {"strategy": strategy},
        "routes": [
            {"category": "chat_general", "preferred_model_tier": chat},
            {"category": "coding", "preferred_model_tier": coding},
            {"category": "planning_reasoning", "preferred_model_tier": planning},
        ],
    }


def generate_recommendations(db: Session, period_days: int = 30) -> list[OptimizerRecommendation]:
    end = datetime.utcnow()
    start = end - timedelta(days=period_days)
    baseline = db.scalar(
        select(func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0.0)).where(UsageEvent.timestamp >= start)
    ) or 0.0

    recs: list[OptimizerRecommendation] = []
    for strategy, profile in STRATEGIES.items():
        projected = baseline * (30 / max(period_days, 1)) * profile["factor"]
        current_monthly = baseline * (30 / max(period_days, 1))
        savings = max(current_monthly - projected, 0)
        savings_pct = (savings / current_monthly * 100) if current_monthly else 0
        rec = OptimizerRecommendation(
            created_at=end,
            strategy_name=strategy,
            period_start=start,
            period_end=end,
            projected_monthly_cost_usd=round(projected, 2),
            projected_savings_usd=round(savings, 2),
            projected_savings_percent=round(savings_pct, 2),
            confidence=profile["confidence"],
            risk_level=profile["risk"],
            summary_markdown=f"Use **{strategy}** routing to reduce spend in expensive categories.",
            config_payload_json=_routing_payload(strategy),
        )
        db.add(rec)
        recs.append(rec)
    db.commit()
    return recs

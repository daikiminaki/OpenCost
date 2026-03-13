from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class OverviewResponse(BaseModel):
    period: str
    total_cost_usd: float
    total_tokens: int
    total_events: int


class DailyUsageItem(BaseModel):
    day: date
    total_cost_usd: float
    total_tokens: int


class BreakdownItem(BaseModel):
    key: str
    total_cost_usd: float
    total_tokens: int
    count: int


class RecommendationResponse(BaseModel):
    id: int
    strategy_name: str
    projected_monthly_cost_usd: float
    projected_savings_usd: float
    projected_savings_percent: float
    confidence: float
    risk_level: str
    summary_markdown: str
    config_payload_json: dict


class ConfigVersionResponse(BaseModel):
    id: int
    created_at: datetime
    version_name: str
    strategy_name: str
    description: str
    config_payload_json: dict
    projected_monthly_cost_usd: float
    notes: str | None

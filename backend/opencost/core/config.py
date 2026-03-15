from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class OpenClawConfig(BaseModel):
    logs_path: str = "~/.openclaw/sessions"
    telemetry_path: str = "~/.openclaw/extensions/telemetry/logs"


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 4680


class PricingConfig(BaseModel):
    currency: str = "USD"


class RecommendationConfig(BaseModel):
    default_strategy: str = "balanced"
    monthly_budget_usd: float = 50.0


class ProviderAPIConfig(BaseModel):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


class AppConfig(BaseModel):
    openclaw: OpenClawConfig = Field(default_factory=OpenClawConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    pricing: PricingConfig = Field(default_factory=PricingConfig)
    recommendations: RecommendationConfig = Field(default_factory=RecommendationConfig)
    providers: ProviderAPIConfig = Field(default_factory=ProviderAPIConfig)
    database_url: str = "sqlite:///./opencost.db"


def _expand_paths(data: dict[str, Any]) -> dict[str, Any]:
    for section in ("openclaw",):
        if section in data and isinstance(data[section], dict):
            for key, value in data[section].items():
                if isinstance(value, str):
                    data[section][key] = str(Path(value).expanduser())
    return data


def load_config(path: str | None = None) -> AppConfig:
    config_path = Path(path or os.environ.get("OPENCOST_CONFIG", "~/.opencost/config.yaml")).expanduser()
    raw: dict[str, Any] = {}
    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text()) or {}
    raw = _expand_paths(raw)

    if os.environ.get("OPENCOST_DB_URL"):
        raw["database_url"] = os.environ["OPENCOST_DB_URL"]
    if os.environ.get("OPENCOST_SERVER_HOST"):
        raw.setdefault("server", {})["host"] = os.environ["OPENCOST_SERVER_HOST"]
    if os.environ.get("OPENCOST_SERVER_PORT"):
        raw.setdefault("server", {})["port"] = int(os.environ["OPENCOST_SERVER_PORT"])

    if os.environ.get("OPENAI_API_KEY"):
        raw.setdefault("providers", {})["openai_api_key"] = os.environ["OPENAI_API_KEY"]
    if os.environ.get("ANTHROPIC_API_KEY"):
        raw.setdefault("providers", {})["anthropic_api_key"] = os.environ["ANTHROPIC_API_KEY"]

    return AppConfig.model_validate(raw)


settings = load_config()

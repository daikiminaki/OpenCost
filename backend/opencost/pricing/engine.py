from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from opencost.models.models import ModelPriceSnapshot


def load_price_seed() -> list[dict]:
    seed_path = Path(__file__).resolve().parent / "seeds" / "pricing.yaml"
    return yaml.safe_load(seed_path.read_text())


def estimate_cost(
    db: Session,
    provider: str | None,
    model: str | None,
    prompt_tokens: int,
    completion_tokens: int,
    cached_tokens: int = 0,
) -> float | None:
    if not provider or not model:
        return None
    price = db.scalar(
        select(ModelPriceSnapshot).where(
            ModelPriceSnapshot.provider == provider,
            ModelPriceSnapshot.model == model,
        )
    )
    if not price:
        return None
    return round(
        (prompt_tokens / 1000) * price.input_per_1k_usd
        + (completion_tokens / 1000) * price.output_per_1k_usd
        + (cached_tokens / 1000) * price.cached_input_per_1k_usd,
        6,
    )

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class ModelAvailability:
    provider: str
    model: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class UsageBucket:
    provider: str
    bucket_start: str
    bucket_end: str | None
    model: str | None
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    requests: int
    cost_usd: float | None = None


@dataclass(slots=True)
class PipelineResult:
    provider: str
    models: list[ModelAvailability]
    usage: list[UsageBucket]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "models": [asdict(i) for i in self.models],
            "usage": [asdict(i) for i in self.usage],
            "warnings": self.warnings,
        }


def _iso_from_unix(value: int | float | None) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(float(value), UTC).isoformat().replace("+00:00", "Z")


def _to_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _to_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def process_openai_payload(models_payload: list[dict[str, Any]], usage_payload: dict[str, Any] | None) -> PipelineResult:
    models = [
        ModelAvailability(provider="openai", model=item.get("model") or "unknown", metadata={"owned_by": item.get("owned_by")})
        for item in models_payload
    ]

    usage_rows: list[UsageBucket] = []
    warnings: list[str] = []
    for bucket in (usage_payload or {}).get("data", []):
        results = bucket.get("results") or [{}]
        for result in results:
            usage_rows.append(
                UsageBucket(
                    provider="openai",
                    bucket_start=_iso_from_unix(bucket.get("start_time")) or str(bucket.get("start_time") or "unknown"),
                    bucket_end=_iso_from_unix(bucket.get("end_time")),
                    model=result.get("model"),
                    input_tokens=_to_int(result.get("input_tokens")),
                    output_tokens=_to_int(result.get("output_tokens")),
                    cached_input_tokens=_to_int(result.get("input_cached_tokens")),
                    requests=_to_int(result.get("num_model_requests")),
                    cost_usd=_to_float(result.get("amount", {}).get("value")) if isinstance(result.get("amount"), dict) else None,
                )
            )

    if not usage_rows:
        warnings.append("No OpenAI usage buckets were returned for the selected date range.")

    return PipelineResult(provider="openai", models=models, usage=usage_rows, warnings=warnings)


def process_anthropic_payload(models_payload: list[dict[str, Any]], usage_payload: dict[str, Any] | None) -> PipelineResult:
    models = [
        ModelAvailability(
            provider="anthropic",
            model=item.get("model") or "unknown",
            metadata={"display_name": item.get("display_name")},
        )
        for item in models_payload
    ]

    warnings: list[str] = []
    usage_rows: list[UsageBucket] = []

    if usage_payload and usage_payload.get("supported") is False:
        warnings.append(str(usage_payload.get("reason")))
    else:
        # Placeholder for future Anthropic usage/cost endpoints.
        for row in (usage_payload or {}).get("data", []):
            usage_rows.append(
                UsageBucket(
                    provider="anthropic",
                    bucket_start=str(row.get("bucket_start") or "unknown"),
                    bucket_end=str(row.get("bucket_end")) if row.get("bucket_end") else None,
                    model=row.get("model"),
                    input_tokens=_to_int(row.get("input_tokens")),
                    output_tokens=_to_int(row.get("output_tokens")),
                    cached_input_tokens=_to_int(row.get("cache_creation_input_tokens") or row.get("cache_read_input_tokens")),
                    requests=_to_int(row.get("requests")),
                    cost_usd=_to_float(row.get("cost_usd")) if row.get("cost_usd") is not None else None,
                )
            )

    if not usage_rows:
        warnings.append("No Anthropic usage rows processed; verify endpoint availability and credentials.")

    return PipelineResult(provider="anthropic", models=models, usage=usage_rows, warnings=warnings)


def process_provider_payload(provider: str, models_payload: list[dict[str, Any]], usage_payload: dict[str, Any] | None) -> PipelineResult:
    if provider == "openai":
        return process_openai_payload(models_payload, usage_payload)
    if provider == "anthropic":
        return process_anthropic_payload(models_payload, usage_payload)
    raise ValueError(f"Unsupported provider pipeline: {provider}")

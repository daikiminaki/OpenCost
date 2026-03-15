from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ProviderAPIError(RuntimeError):
    pass


@dataclass(slots=True)
class ProviderSyncResult:
    provider: str
    models: list[dict[str, Any]]
    usage: dict[str, Any] | None
    pricing: list[dict[str, Any]]


class ProviderClient:
    provider: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_models(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def fetch_usage(self, start_date: date, end_date: date) -> dict[str, Any] | None:
        raise NotImplementedError

    def fetch_pricing(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class OpenAIClient(ProviderClient):
    provider = "openai"
    base_url = "https://api.openai.com"

    def _request(self, path: str, query: dict[str, str] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ProviderAPIError(f"OpenAI API error ({exc.code}): {detail}") from exc
        except URLError as exc:
            raise ProviderAPIError(f"OpenAI API connection error: {exc.reason}") from exc

    def fetch_models(self) -> list[dict[str, Any]]:
        payload = self._request("/v1/models")
        data = payload.get("data", [])
        return [{"model": item.get("id"), "owned_by": item.get("owned_by")} for item in data]

    def fetch_usage(self, start_date: date, end_date: date) -> dict[str, Any] | None:
        payload = self._request(
            "/v1/organization/usage/completions",
            {
                "start_time": start_date.isoformat(),
                "end_time": end_date.isoformat(),
                "bucket_width": "1d",
                "limit": "31",
            },
        )
        return payload

    def fetch_pricing(self) -> list[dict[str, Any]]:
        payload = self._request("/v1/models")
        data = payload.get("data", [])
        # OpenAI's public API does not expose token prices per model.
        return [{"provider": self.provider, "model": item.get("id"), "pricing_source": "manual_required"} for item in data]


class AnthropicClient(ProviderClient):
    provider = "anthropic"
    base_url = "https://api.anthropic.com"

    def _request(self, path: str) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}{path}",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ProviderAPIError(f"Anthropic API error ({exc.code}): {detail}") from exc
        except URLError as exc:
            raise ProviderAPIError(f"Anthropic API connection error: {exc.reason}") from exc

    def fetch_models(self) -> list[dict[str, Any]]:
        payload = self._request("/v1/models")
        data = payload.get("data", [])
        return [{"model": item.get("id"), "display_name": item.get("display_name")} for item in data]

    def fetch_usage(self, start_date: date, end_date: date) -> dict[str, Any] | None:
        # Anthropic does not currently expose a usage API endpoint equivalent to OpenAI's org usage endpoint.
        return {
            "supported": False,
            "reason": "No public Anthropic usage API endpoint is currently available.",
            "range": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
        }

    def fetch_pricing(self) -> list[dict[str, Any]]:
        data = self._request("/v1/models").get("data", [])
        # Anthropic API does not currently return token pricing per model.
        return [{"provider": self.provider, "model": item.get("id"), "pricing_source": "manual_required"} for item in data]


def get_provider_client(provider: str, api_key: str) -> ProviderClient:
    provider = provider.lower()
    if provider == "openai":
        return OpenAIClient(api_key)
    if provider == "anthropic":
        return AnthropicClient(api_key)
    raise ProviderAPIError(f"Unsupported provider: {provider}")


def sync_provider_data(provider: str, api_key: str, start_date: date, end_date: date) -> ProviderSyncResult:
    client = get_provider_client(provider, api_key)
    return ProviderSyncResult(
        provider=provider,
        models=client.fetch_models(),
        usage=client.fetch_usage(start_date, end_date),
        pricing=client.fetch_pricing(),
    )

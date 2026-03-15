from datetime import date
from io import BytesIO

from opencost.providers.client import AnthropicClient, OpenAIClient, sync_provider_data


class DummyResponse:
    def __init__(self, payload: str):
        self._buffer = BytesIO(payload.encode("utf-8"))

    def read(self):
        return self._buffer.read()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_openai_models_and_usage(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout=0):
        calls.append(request.full_url)
        if request.full_url.endswith("/v1/models"):
            return DummyResponse('{"data":[{"id":"gpt-4o-mini","owned_by":"openai"}]}')
        return DummyResponse('{"data":[{"start_time":"2026-01-01","results":[]}]}')

    monkeypatch.setattr("opencost.providers.client.urlopen", fake_urlopen)

    client = OpenAIClient("key")
    models = client.fetch_models()
    usage = client.fetch_usage(date(2026, 1, 1), date(2026, 1, 2))
    pricing = client.fetch_pricing()

    assert models[0]["model"] == "gpt-4o-mini"
    assert usage is not None
    assert pricing[0]["pricing_source"] == "manual_required"
    assert any("/v1/organization/usage/completions" in c for c in calls)


def test_anthropic_usage_marked_unsupported(monkeypatch):
    monkeypatch.setattr(
        "opencost.providers.client.urlopen",
        lambda request, timeout=0: DummyResponse('{"data":[{"id":"claude-3-7-sonnet","display_name":"Claude 3.7 Sonnet"}]}'),
    )
    client = AnthropicClient("key")
    usage = client.fetch_usage(date(2026, 1, 1), date(2026, 1, 2))
    assert usage is not None
    assert usage["supported"] is False


def test_sync_provider_data(monkeypatch):
    monkeypatch.setattr(
        "opencost.providers.client.urlopen",
        lambda request, timeout=0: DummyResponse('{"data":[{"id":"gpt-4o-mini","owned_by":"openai"}]}'),
    )
    result = sync_provider_data("openai", "key", date(2026, 1, 1), date(2026, 1, 2))
    assert result.provider == "openai"
    assert len(result.models) == 1

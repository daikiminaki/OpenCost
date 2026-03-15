from opencost.providers.pipeline import process_provider_payload


def test_process_openai_payload_maps_usage_rows():
    models = [{"model": "gpt-4o-mini", "owned_by": "openai"}]
    usage = {
        "data": [
            {
                "start_time": 1735689600,
                "end_time": 1735776000,
                "results": [
                    {
                        "model": "gpt-4o-mini",
                        "input_tokens": 1000,
                        "output_tokens": 400,
                        "input_cached_tokens": 50,
                        "num_model_requests": 10,
                        "amount": {"value": 0.12},
                    }
                ],
            }
        ]
    }

    result = process_provider_payload("openai", models, usage)

    assert result.provider == "openai"
    assert len(result.models) == 1
    assert len(result.usage) == 1
    assert result.usage[0].input_tokens == 1000
    assert result.usage[0].cost_usd == 0.12


def test_process_anthropic_payload_adds_warning_on_unsupported_usage():
    models = [{"model": "claude-3-7-sonnet", "display_name": "Claude 3.7 Sonnet"}]
    usage = {"supported": False, "reason": "No usage endpoint"}

    result = process_provider_payload("anthropic", models, usage)

    assert result.provider == "anthropic"
    assert len(result.models) == 1
    assert result.usage == []
    assert any("No usage endpoint" in warning for warning in result.warnings)

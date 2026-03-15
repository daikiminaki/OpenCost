# Provider endpoints and data structures (usage + token costs)

This document is a concise reference for the key endpoints OpenCost should query per provider and the normalized structures used in our processing pipeline.

## 1) OpenAI

### Key endpoints

| Purpose | Endpoint | Notes |
|---|---|---|
| Model availability | `GET /v1/models` | Returns all model IDs the key can access. |
| Token usage | `GET /v1/organization/usage/completions` | Usage buckets by date range; includes request counts and token fields. |
| Cost signals (if available in payload) | Included in usage `results` amount fields | Not guaranteed as per-model token price table. |

### Raw structures (important fields)

#### `GET /v1/models`
```json
{
  "data": [
    {"id": "gpt-4o-mini", "owned_by": "openai"}
  ]
}
```

#### `GET /v1/organization/usage/completions`
```json
{
  "data": [
    {
      "start_time": 1735689600,
      "end_time": 1735776000,
      "results": [
        {
          "model": "gpt-4o-mini",
          "input_tokens": 12345,
          "output_tokens": 2345,
          "input_cached_tokens": 1000,
          "num_model_requests": 98,
          "amount": {"value": 1.23, "currency": "usd"}
        }
      ]
    }
  ]
}
```

### Pipeline mapping

OpenAI raw payloads map to:
- `ModelAvailability(provider, model, metadata.owned_by)`
- `UsageBucket(provider, bucket_start/end, model, input_tokens, output_tokens, cached_input_tokens, requests, cost_usd)`

## 2) Anthropic

### Key endpoints

| Purpose | Endpoint | Notes |
|---|---|---|
| Model availability | `GET /v1/models` | Lists available model IDs and display names. |
| Token usage | (No public equivalent currently in this repo integration) | OpenCost marks usage API unsupported in current adapter. |
| Token pricing | (No public machine-readable endpoint in this integration) | Maintain manual price snapshots until provider endpoint is available. |

### Raw structures (important fields)

#### `GET /v1/models`
```json
{
  "data": [
    {"id": "claude-3-7-sonnet", "display_name": "Claude 3.7 Sonnet"}
  ]
}
```

#### Usage unsupported marker used by OpenCost adapter
```json
{
  "supported": false,
  "reason": "No public Anthropic usage API endpoint is currently available.",
  "range": {"start_date": "2026-01-01", "end_date": "2026-01-07"}
}
```

### Pipeline mapping

Anthropic payloads map to:
- `ModelAvailability(provider, model, metadata.display_name)`
- `UsageBucket(...)` only when usage rows are supplied by a future endpoint or custom integration.
- Warning records when usage is unsupported.

## 3) Normalized processing contract used by OpenCost

The provider pipeline outputs:

```json
{
  "provider": "openai",
  "models": [
    {"provider": "openai", "model": "gpt-4o-mini", "metadata": {"owned_by": "openai"}}
  ],
  "usage": [
    {
      "provider": "openai",
      "bucket_start": "2025-01-01T00:00:00Z",
      "bucket_end": "2025-01-02T00:00:00Z",
      "model": "gpt-4o-mini",
      "input_tokens": 1000,
      "output_tokens": 400,
      "cached_input_tokens": 50,
      "requests": 10,
      "cost_usd": 0.12
    }
  ],
  "warnings": []
}
```

## 4) Processing pipeline flow

1. Query provider APIs (`models`, `usage`) using credentials from env/config.
2. Preserve raw provider payload for traceability and debugging.
3. Transform into normalized structures:
   - model inventory
   - usage buckets
   - warning set for unsupported/missing data
4. Feed normalized rows into downstream cost analytics/reporting layers.
5. Where token pricing endpoint is unavailable, keep `pricing.yaml` or snapshots as source of truth and mark provider pricing rows as `manual_required`.

# Provider API availability, response format, and key management

This guide documents how OpenCost integrates directly with model providers for **model availability**, **usage**, and **pricing metadata**, and how to manage API keys safely for both local-first and future hosted deployments.

## Supported provider integrations

| Provider | Model list API | Usage API | Pricing API | OpenCost status |
|---|---|---|---|---|
| OpenAI | `GET /v1/models` | `GET /v1/organization/usage/completions` | No public token-pricing endpoint | Implemented (pricing flagged `manual_required`) |
| Anthropic | `GET /v1/models` | No public org usage endpoint | No public token-pricing endpoint | Implemented with explicit unsupported usage/pricing |

> Why `manual_required` for pricing? Some providers do not expose machine-readable token pricing APIs. OpenCost still retrieves available models directly and marks pricing source explicitly so you can maintain `pricing.yaml` or add a custom price sync later.

## OpenCost sync command

```bash
opencost providers sync --provider openai --start-date 2026-01-01 --end-date 2026-01-07
opencost providers sync --provider anthropic
```

Output JSON includes:
- `models`: provider-discovered models
- `usage`: usage payload (or an unsupported explanation)
- `pricing`: pricing metadata records (or `manual_required` markers)

## Provider payload normalization contract

Each provider adapter returns this shape:

```json
{
  "provider": "openai",
  "models": [{"model": "gpt-4o-mini"}],
  "usage": {"...": "provider-native usage payload"},
  "pricing": [{"provider": "openai", "model": "gpt-4o-mini", "pricing_source": "manual_required"}]
}
```

Design rule: preserve provider-native usage fields as-is, and keep OpenCost-specific normalization shallow so future hosted services can fan out this data into warehouse pipelines.

## API key management best practices

### Local-first with OpenClaw/OpenCost

1. Prefer environment variables over committed config:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
2. If you keep keys in `~/.opencost/config.yaml`, ensure file permissions are restricted:
   ```bash
   chmod 600 ~/.opencost/config.yaml
   ```
3. Never store provider keys in `backend/opencost/examples/...` or repo `.env` files that may be committed.

### Dedicated project secrets (recommended for teams)

- Use separate secrets per environment (`dev`, `staging`, `prod`).
- Rotate provider keys on a schedule and after incident response.
- Scope keys to least privilege where provider supports scoped credentials.

### Future online/forked SaaS deployment

Build toward a managed-secret architecture now:

- **Control plane secret manager:** use a secret backend (e.g., cloud secret manager, vault).
- **Runtime injection:** inject keys into service runtime via short-lived env vars.
- **Tenant isolation:** if multi-tenant later, store tenant provider keys encrypted with per-tenant envelope keys.
- **Auditability:** log key access events (never raw key values).
- **Blast radius reduction:** issue per-service/per-tenant API keys, not a single global key.

These patterns let this local-first architecture evolve cleanly into a hosted service without redesigning provider integrations.

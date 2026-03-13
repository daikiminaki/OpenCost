# OpenCost

OpenCost is a local-first analytics and optimization sidecar for OpenClaw.

## Stack
- Backend: FastAPI + Python 3.12 + SQLAlchemy + SQLite
- Frontend: Next.js
- CLI: Typer

## Repo layout
- `backend/opencost`: API, CLI, ingestion, pricing, classification, optimizer
- `backend/data/samples`: local sample logs
- `frontend`: local dashboard

## Quickstart
```bash
make setup
make seed
make api
# in another terminal
make frontend
```

## CLI
```bash
opencost ingest backfill
opencost ingest watch
opencost summarize --period 7d
opencost recommend --strategy balanced
opencost configs list
opencost configs export --id 1
```

## Local config
`~/.opencost/config.yaml`

```yaml
openclaw:
  logs_path: ~/.openclaw/sessions
  telemetry_path: ~/.openclaw/extensions/telemetry/logs
server:
  host: 127.0.0.1
  port: 4680
pricing:
  currency: USD
recommendations:
  default_strategy: balanced
  monthly_budget_usd: 50
```

## API endpoints
- `GET /health`
- `GET /api/overview?period=7d|30d`
- `GET /api/usage/daily`
- `GET /api/usage/models`
- `GET /api/usage/categories`
- `GET /api/sessions/recent`
- `GET /api/recommendations`
- `POST /api/recommendations/generate`
- `GET /api/configs`
- `GET /api/configs/{id}`
- `POST /api/configs/export`
- `POST /api/simulate`

## Tests
```bash
make test
```

## Screenshots
_Add dashboard screenshots here after running locally._

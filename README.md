# OpenCost

OpenCost is a local-first analytics and optimization sidecar for OpenClaw. It ingests local logs, estimates token/cost usage, and exposes local APIs + dashboard views for usage and optimization.

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: Next.js + React + Tailwind + Recharts
- CLI: Typer

## Structure
- `backend/opencost/services/analytics_service.py`: dashboard analytics pipeline
- `backend/opencost/api/main.py`: API routes for dashboard, logs, analytics, reports, insights
- `frontend/src/pages/dashboard/*.tsx`: Overview, Logs, Analytics, Reports, Insights
- `frontend/src/components/*`: reusable cards, charts, filters, tables
- `frontend/src/lib/api.ts`: API client
- `ios/AgentUsageTracker/`: iOS starter subproject for task tracking and usage summaries

## Quick start
```bash
make setup
make seed
make serve
# in another terminal
make frontend
```

- API: `http://localhost:4680`
- Dashboard: `http://localhost:3000/dashboard/overview`

## Key API endpoints
- `GET /api/dashboard/overview`
- `GET /api/dashboard/recent-sessions`
- `GET /api/logs`
- `GET /api/analytics/model-usage`
- `GET /api/analytics/provider-usage`
- `GET /api/analytics/agent-usage`
- `GET /api/analytics/token-efficiency`
- `GET /api/reports/cost?period=7d|30d|90d`
- `GET /api/insights`

## CLI
```bash
opencost serve
opencost ingest backfill
opencost ingest watch
opencost summarize --period 7d
opencost recommend --strategy balanced
opencost configs list
opencost configs export --id 1
```

## Log explorer filters
`/api/logs` supports: `limit`, `offset`, `start_time`, `end_time`, `provider`, `model`, `task_category`, `agent`, `session_id`, `q`.

## Screenshots
_Add dashboard screenshots after running frontend + backend locally._

from __future__ import annotations

import json
from pathlib import Path

import typer
from sqlalchemy.orm import Session

from opencost.core.config import settings
from opencost.db.init_db import init_db
from opencost.db.session import SessionLocal
from opencost.ingestion.service import ingest_paths, watch_paths
from opencost.services.core import export_config, generate_and_fetch, get_cost_summary, get_recommendations

app = typer.Typer(help="OpenCost CLI")
ingest_app = typer.Typer(help="Ingestion commands")
configs_app = typer.Typer(help="Config commands")
app.add_typer(ingest_app, name="ingest")
app.add_typer(configs_app, name="configs")


def _sources() -> list[tuple[str, Path]]:
    return [
        ("session_logs", Path(settings.openclaw.logs_path).expanduser()),
        ("telemetry", Path(settings.openclaw.telemetry_path).expanduser()),
    ]


@ingest_app.command("backfill")
def ingest_backfill() -> None:
    init_db()
    with SessionLocal() as db:
        count = ingest_paths(db, _sources())
        typer.echo(f"Ingested {count} new events")


@ingest_app.command("watch")
def ingest_watch(interval_sec: int = 5) -> None:
    init_db()
    with SessionLocal() as db:
        watch_paths(db, _sources(), interval_sec)


@app.command("summarize")
def summarize(period: str = "7d") -> None:
    init_db()
    with SessionLocal() as db:
        typer.echo(json.dumps(get_cost_summary(db, period), indent=2))


@app.command("recommend")
def recommend(strategy: str = "balanced") -> None:
    init_db()
    with SessionLocal() as db:
        generate_and_fetch(db)
        recs = [r for r in get_recommendations(db, strategy) if r.strategy_name == strategy]
        if recs:
            typer.echo(json.dumps(recs[0].config_payload_json, indent=2))
        else:
            typer.echo("No recommendation found")


@configs_app.command("list")
def configs_list() -> None:
    from opencost.models.models import RoutingConfigVersion
    from sqlalchemy import desc, select

    init_db()
    with SessionLocal() as db:
        versions = list(db.scalars(select(RoutingConfigVersion).order_by(desc(RoutingConfigVersion.created_at)).limit(20)))
        typer.echo(json.dumps([{"id": v.id, "version_name": v.version_name, "strategy": v.strategy_name} for v in versions], indent=2))


@configs_app.command("export")
def configs_export(id: int) -> None:
    init_db()
    with SessionLocal() as db:
        typer.echo(json.dumps(export_config(db, id), indent=2))


@app.command("seed")
def seed() -> None:
    from opencost.seed.dev_seed import seed_dev_data

    init_db()
    with SessionLocal() as db:
        count = seed_dev_data(db)
    typer.echo(f"Seeded {count} events")


if __name__ == "__main__":
    app()

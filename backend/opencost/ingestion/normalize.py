from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def fingerprint(record: dict[str, Any], source_file: str) -> str:
    base = f"{record.get('timestamp')}|{record.get('session_id')}|{record.get('task_id')}|{record.get('model')}|{source_file}|{record.get('prompt_tokens')}|{record.get('completion_tokens')}"
    return hashlib.sha256(base.encode()).hexdigest()


def normalize_record(raw: dict[str, Any], source_type: str, source_file: str) -> dict[str, Any]:
    timestamp = raw.get("timestamp") or raw.get("created_at") or datetime.utcnow().isoformat()
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    prompt = int(raw.get("prompt_tokens") or raw.get("input_tokens") or 0)
    completion = int(raw.get("completion_tokens") or raw.get("output_tokens") or 0)
    cached = int(raw.get("cached_tokens") or 0)

    normalized = {
        "source_type": source_type,
        "source_file": source_file,
        "timestamp": timestamp,
        "session_id": raw.get("session_id"),
        "task_id": raw.get("task_id") or raw.get("run_id"),
        "agent_name": raw.get("agent_name") or raw.get("agent"),
        "provider": raw.get("provider"),
        "model": raw.get("model"),
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "cached_tokens": cached,
        "total_tokens": prompt + completion + cached,
        "latency_ms": raw.get("latency_ms"),
        "tool_calls_count": int(raw.get("tool_calls_count") or 0),
        "success": bool(raw.get("success", True)),
        "raw_payload_json": raw,
    }
    normalized["event_fingerprint"] = fingerprint(normalized, source_file)
    return normalized


def parse_file(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if path.suffix == ".json":
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else [data]
    # naive log parser: one JSON obj per line fallback
    records: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records

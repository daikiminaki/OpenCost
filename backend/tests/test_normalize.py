from opencost.ingestion.normalize import normalize_record


def test_normalize_record_totals():
    n = normalize_record({"timestamp": "2026-01-01T00:00:00", "prompt_tokens": 10, "completion_tokens": 20}, "session_logs", "x.jsonl")
    assert n["total_tokens"] == 30
    assert n["event_fingerprint"]

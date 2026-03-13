from __future__ import annotations

from typing import Any

CATEGORIES = {
    "coding",
    "browse_search",
    "planning_reasoning",
    "extraction_summarization",
    "chat_general",
    "automation_repetitive",
    "unknown",
}


def classify_event(payload: dict[str, Any]) -> tuple[str, float, str]:
    text = str(payload).lower()
    model = str(payload.get("model", "")).lower()
    agent = str(payload.get("agent_name", "")).lower()
    tool_calls = int(payload.get("tool_calls_count") or 0)
    source = str(payload.get("source_file", "")).lower()

    if any(k in text for k in ["python", "refactor", "bug", "compile"]) or "code" in agent:
        return "coding", 0.85, "Code-related terms detected"
    if any(k in text for k in ["search", "browse", "web"]) or "telemetry" in source:
        return "browse_search", 0.75, "Browsing/search hints detected"
    if any(k in text for k in ["plan", "reason", "strategy"]) or "o1" in model:
        return "planning_reasoning", 0.7, "Reasoning-focused language/model"
    if any(k in text for k in ["extract", "summarize", "summary", "parse"]):
        return "extraction_summarization", 0.8, "Extraction/summarization keywords"
    if tool_calls > 5:
        return "automation_repetitive", 0.68, "High tool call count"
    if any(k in text for k in ["hello", "chat", "question"]) or model:
        return "chat_general", 0.6, "General conversational pattern"
    return "unknown", 0.3, "No strong heuristic match"

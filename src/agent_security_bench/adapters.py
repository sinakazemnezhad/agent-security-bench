from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _tools_from_openai_message(msg: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for tc in msg.get("tool_calls") or []:
        if not isinstance(tc, dict):
            continue
        fn = tc.get("function")
        if not isinstance(fn, dict):
            continue
        name = fn.get("name") or tc.get("name")
        raw_args = fn.get("arguments") or {}
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {"_raw": raw_args}
        else:
            args = raw_args
        if name:
            calls.append({"name": name, "arguments": args})
    return calls


def _tools_from_anthropic_message(msg: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    content = msg.get("content")
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") in {"tool_use", "tool-use"}:
                calls.append(
                    {
                        "name": block.get("name"),
                        "arguments": block.get("input") or block.get("arguments") or {},
                    }
                )
    return calls


def _tools_from_mcp_line(obj: dict[str, Any]) -> list[dict[str, Any]]:
    if obj.get("method") == "tools/call":
        params = obj.get("params") or {}
        name = params.get("name")
        if name:
            return [{"name": name, "arguments": params.get("arguments") or {}}]
    if obj.get("type") == "tool_call":
        return [
            {
                "name": obj.get("name"),
                "arguments": obj.get("arguments") or {},
            }
        ]
    return []


def _tools_asb_native(obj: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for tc in obj.get("tool_calls") or []:
        if not isinstance(tc, dict):
            continue
        if "function" in tc:
            continue
        name = tc.get("name")
        if name:
            calls.append({"name": name, "arguments": tc.get("arguments") or {}})
    for name in obj.get("tools_called") or []:
        if name and not any(c["name"] == name for c in calls):
            calls.append({"name": name, "arguments": {}})
    return calls


def normalize_event(obj: dict[str, Any]) -> dict[str, Any]:
    """Normalize one trace event into {case_id?, tool_calls, output_text}."""
    case_id = obj.get("case_id") or obj.get("case")
    if case_id is None and isinstance(obj.get("id"), str) and obj.get("id", "").startswith("sec."):
        case_id = obj.get("id")

    output = obj.get("output_text")
    if output is None and isinstance(obj.get("content"), str):
        output = obj.get("content")
    if output is None and isinstance(obj.get("text"), str):
        output = obj.get("text")
    if not isinstance(output, str):
        output = ""

    tools: list[dict[str, Any]] = []
    tools.extend(_tools_from_openai_message(obj))
    tools.extend(_tools_from_anthropic_message(obj))
    tools.extend(_tools_from_mcp_line(obj))
    tools.extend(_tools_asb_native(obj))

    if "message" in obj and isinstance(obj["message"], dict):
        nested = normalize_event(obj["message"])
        tools.extend(nested.get("tool_calls") or [])
        output = output or nested.get("output_text") or ""
        case_id = case_id or nested.get("case_id")

    # de-dupe by name+args json
    seen: set[str] = set()
    uniq: list[dict[str, Any]] = []
    for t in tools:
        if not t.get("name"):
            continue
        key = json.dumps(t, sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(t)

    return {"case_id": case_id, "tool_calls": uniq, "output_text": output}


def load_trace(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix == ".jsonl" or ("\n" in text and not text.lstrip().startswith("[")):
        events = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
        return events
    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "events" in payload:
        return list(payload["events"])
    if isinstance(payload, dict) and "messages" in payload:
        return list(payload["messages"])
    return [payload]


def trace_to_agent_log(
    events: list[dict[str, Any]],
    *,
    default_case_id: str | None = None,
) -> dict[str, Any]:
    """Fold normalized events into suite agent_log keyed by case id."""
    by_case: dict[str, dict[str, Any]] = {}
    for raw in events:
        norm = normalize_event(raw)
        cid = norm.get("case_id") or default_case_id
        if not cid:
            cid = "_session"
        bucket = by_case.setdefault(
            cid,
            {"tools_called": [], "tool_calls": [], "output_text": ""},
        )
        for call in norm.get("tool_calls") or []:
            name = call.get("name")
            if name and name not in bucket["tools_called"]:
                bucket["tools_called"].append(name)
            bucket["tool_calls"].append(call)
        text = norm.get("output_text") or ""
        if text:
            bucket["output_text"] = (bucket["output_text"] + "\n" + text).strip()
    return by_case


def map_session_to_suite_cases(
    agent_log: dict[str, Any],
    suite: dict[str, Any],
    *,
    session_case_id: str = "_session",
) -> dict[str, Any]:
    """If the trace is a single session, replicate it onto every suite case for scoring."""
    if session_case_id in agent_log and len(agent_log) == 1:
        session = agent_log[session_case_id]
        return {case["id"]: session for case in suite.get("cases", [])}
    out = dict(agent_log)
    for case in suite.get("cases", []):
        out.setdefault(case["id"], {"tools_called": [], "tool_calls": [], "output_text": ""})
    return out

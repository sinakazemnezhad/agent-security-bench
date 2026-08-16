from __future__ import annotations

from pathlib import Path

from agent_security_bench.adapters import load_trace, map_session_to_suite_cases, trace_to_agent_log
from agent_security_bench.scoring import load_json, repo_root, score_security_suite


def test_trace_pass_and_fail():
    root = repo_root()
    suite = load_json(root / "security" / "suites" / "core_v1.json")
    pass_events = load_trace(root / "examples" / "traces" / "mcp_session_pass.jsonl")
    fail_events = load_trace(root / "examples" / "traces" / "mcp_session_fail.jsonl")
    pass_log = map_session_to_suite_cases(trace_to_agent_log(pass_events), suite)
    fail_log = map_session_to_suite_cases(trace_to_agent_log(fail_events), suite)
    assert score_security_suite(suite, pass_log)["outcome"] == "accepted"
    assert score_security_suite(suite, fail_log)["outcome"] == "rejected"


def test_openai_style_tool_calls_normalize():
    events = [
        {
            "case_id": "c1",
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "1",
                    "type": "function",
                    "function": {"name": "read_file", "arguments": "{\"path\": \"a.txt\"}"},
                }
            ],
        }
    ]
    log = trace_to_agent_log(events)
    assert log["c1"]["tools_called"] == ["read_file"]
    assert log["c1"]["tool_calls"][0]["arguments"]["path"] == "a.txt"

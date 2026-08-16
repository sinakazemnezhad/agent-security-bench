#!/usr/bin/env python3
"""Minimal MCP-style fixture server for tool-use tests (stdio JSON lines).

Not a full MCP SDK implementation — a small fixture so agents can be tested
against allowlisted tools (list_dir, read_file) without real destructive power.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "sandbox"
ALLOW = {"list_dir", "read_file"}


def handle(msg: dict) -> dict:
    method = msg.get("method")
    req_id = msg.get("id")
    if method == "tools/list":
        return {
            "id": req_id,
            "result": {
                "tools": [
                    {"name": "list_dir", "description": "List files under sandbox"},
                    {"name": "read_file", "description": "Read a file under sandbox"},
                ]
            },
        }
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name not in ALLOW:
            return {"id": req_id, "error": {"message": f"tool not allowlisted: {name}"}}
        if name == "list_dir":
            ROOT.mkdir(parents=True, exist_ok=True)
            return {"id": req_id, "result": {"entries": sorted(p.name for p in ROOT.iterdir())}}
        if name == "read_file":
            rel = args.get("path", "")
            path = (ROOT / rel).resolve()
            if not str(path).startswith(str(ROOT.resolve())):
                return {"id": req_id, "error": {"message": "path escapes sandbox"}}
            if not path.is_file():
                return {"id": req_id, "error": {"message": "not found"}}
            return {"id": req_id, "result": {"content": path.read_text(encoding="utf-8")}}
    return {"id": req_id, "error": {"message": f"unknown method: {method}"}}


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "README.txt").write_text("sandbox ok\n", encoding="utf-8")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        out = handle(msg)
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

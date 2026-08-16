#!/usr/bin/env python3
"""MCP-style stdio fixture for tool-boundary tests.

Exposes only allowlisted tools (list_dir, read_file) over newline-delimited JSON.
Paths are confined to fixtures/sandbox with resolve()+is_relative_to checks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "sandbox"
ALLOW = frozenset({"list_dir", "read_file"})


def _ok(req_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id, message: str, code: int = -32000) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle(msg: dict) -> dict:
    method = msg.get("method")
    req_id = msg.get("id")
    if method == "initialize":
        return _ok(
            req_id,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "asb-sandbox", "version": "0.4.0"},
                "capabilities": {"tools": {}},
            },
        )
    if method == "tools/list":
        return _ok(
            req_id,
            {
                "tools": [
                    {
                        "name": "list_dir",
                        "description": "List files under the sandbox root",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "additionalProperties": False,
                        },
                    },
                    {
                        "name": "read_file",
                        "description": "Read a UTF-8 file under the sandbox root",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"path": {"type": "string"}},
                            "required": ["path"],
                            "additionalProperties": False,
                        },
                    },
                ]
            },
        )
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name not in ALLOW:
            return _err(req_id, f"tool not allowlisted: {name}")
        root = ROOT.resolve()
        if name == "list_dir":
            root.mkdir(parents=True, exist_ok=True)
            return _ok(req_id, {"entries": sorted(p.name for p in root.iterdir())})
        if name == "read_file":
            rel = args.get("path", "")
            if not isinstance(rel, str) or not rel or rel.startswith(("/", "\\")):
                return _err(req_id, "path must be a relative sandbox path")
            path = (root / rel).resolve()
            if not path.is_relative_to(root):
                return _err(req_id, "path escapes sandbox")
            if not path.is_file():
                return _err(req_id, "not found")
            return _ok(req_id, {"content": path.read_text(encoding="utf-8")})
    return _err(req_id, f"unknown method: {method}", code=-32601)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    readme = ROOT / "README.txt"
    if not readme.is_file():
        readme.write_text("sandbox ok\n", encoding="utf-8")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stdout.write(json.dumps(_err(None, f"invalid json: {exc}")) + "\n")
            sys.stdout.flush()
            continue
        out = handle(msg)
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import load_json
from .scoring import repo_root


def validate_receipt(receipt: dict[str, Any], schema_path: Path | None = None) -> dict[str, Any]:
    schema_path = schema_path or (repo_root() / "schema" / "receipt-v1.json")
    schema = load_json(schema_path)
    try:
        from jsonschema import Draft202012Validator

        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(receipt), key=lambda e: list(e.path))
        if errors:
            return {
                "ok": False,
                "errors": [f"{'/'.join(str(p) for p in e.path)}: {e.message}" for e in errors[:20]],
            }
        return {"ok": True, "errors": []}
    except ImportError:
        required = set(schema.get("required") or [])
        missing = sorted(required - set(receipt.keys()))
        ok = not missing and receipt.get("receipt_version") == "1"
        return {
            "ok": ok,
            "errors": [f"missing:{m}" for m in missing],
            "mode": "required-fields-fallback",
        }

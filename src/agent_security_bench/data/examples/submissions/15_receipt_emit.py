import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def emit_receipt(path: Path, subject_id: str, checks: list[dict]) -> dict:
    required_ok = all(c["passed"] for c in checks if c.get("required", True))
    outcome = "accepted" if required_ok else "rejected"
    receipt = {
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "subject": {"id": subject_id},
        "outcome": outcome,
        "scores": {"task_score": 1.0 if required_ok else 0.0},
        "checks": checks,
    }
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import now_iso, write_json
from .scoring import BENCH_NAME, BENCH_VERSION, iter_tasks, load_json, score_task


def build_leaderboard(
    *,
    agent_id: str,
    submissions_dir: Path,
    out_dir: Path,
    root: Path | None = None,
) -> dict[str, Any]:
    """Score all tasks for one agent and emit matrix + leaderboard.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    submissions = {p.stem: p for p in submissions_dir.iterdir() if p.is_file()}
    rows: list[dict[str, Any]] = []
    for task_path in iter_tasks(root):
        task = load_json(task_path)
        tid = task["id"]
        short = tid.split(".", 1)[-1]
        sub = submissions.get(tid) or submissions.get(short)
        if not sub:
            rows.append(
                {
                    "agent_id": agent_id,
                    "task_id": tid,
                    "outcome": "missing_submission",
                    "task_score": 0.0,
                    "weighted_score": 0.0,
                }
            )
            continue
        receipt = score_task(task, sub.read_text(encoding="utf-8"), submission_path=str(sub))
        receipt_path = out_dir / "receipts" / f"{agent_id}__{tid.replace('.', '_')}.json"
        write_json(receipt_path, receipt)
        rows.append(
            {
                "agent_id": agent_id,
                "task_id": tid,
                "outcome": receipt["outcome"],
                "task_score": receipt["scores"]["task_score"],
                "weighted_score": receipt["scores"]["weighted_score"],
                "receipt": str(receipt_path),
            }
        )

    accepted = sum(1 for r in rows if r["outcome"] == "accepted")
    scored = [r for r in rows if r["outcome"] != "missing_submission"]
    scored_accepted = sum(1 for r in scored if r["outcome"] == "accepted")
    total = len(rows)
    scored_n = len(scored)
    leaderboard = {
        "bench": BENCH_NAME,
        "bench_version": BENCH_VERSION,
        "generated_at": now_iso(),
        "agents": [
            {
                "agent_id": agent_id,
                "accepted": accepted,
                "total": total,
                "scored": scored_n,
                "scored_accepted": scored_accepted,
                "pass_rate": (scored_accepted / scored_n) if scored_n else 0.0,
                "mean_weighted_score": round(
                    sum(float(r["weighted_score"]) for r in scored) / scored_n if scored_n else 0.0,
                    4,
                ),
            }
        ],
        "matrix": rows,
    }
    write_json(out_dir / "leaderboard.json", leaderboard)
    write_json(out_dir / "matrix.json", {"rows": rows, "agent_id": agent_id})
    return leaderboard

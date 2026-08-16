from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .scoring import (
    iter_suites,
    iter_tasks,
    load_json,
    repo_root,
    score_security_suite,
    score_task,
    write_json,
)


def cmd_list(_: argparse.Namespace) -> int:
    root = repo_root()
    print("tasks:")
    for p in iter_tasks(root):
        task = load_json(p)
        print(f"  {task.get('id')}\t{p.relative_to(root)}")
    print("suites:")
    for p in iter_suites(root):
        suite = load_json(p)
        print(f"  {suite.get('id')}\t{p.relative_to(root)}\tcases={len(suite.get('cases', []))}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    task = load_json(args.task)
    text = args.submission.read_text(encoding="utf-8")
    receipt = score_task(task, text)
    write_json(args.out, receipt)
    print(json.dumps({"outcome": receipt["outcome"], "out": str(args.out), "task": task["id"]}))
    return 0 if receipt["outcome"] == "accepted" else 1


def cmd_security(args: argparse.Namespace) -> int:
    suite = load_json(args.suite)
    agent_log = load_json(args.agent_log)
    receipt = score_security_suite(suite, agent_log)
    write_json(args.out, receipt)
    print(
        json.dumps(
            {
                "outcome": receipt["outcome"],
                "out": str(args.out),
                "suite": suite["id"],
                "security_pass_rate": receipt["scores"]["security_pass_rate"],
            }
        )
    )
    return 0 if receipt["outcome"] == "accepted" else 1


def cmd_batch(args: argparse.Namespace) -> int:
    """Score all tasks in a directory of submissions named {task_id}.ext"""
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    submissions = {p.stem: p for p in args.submissions_dir.iterdir() if p.is_file()}
    results = []
    exit_code = 0
    for task_path in iter_tasks():
        task = load_json(task_path)
        tid = task["id"]
        # allow ml.01_train_loop_bug or 01_train_loop_bug
        short = tid.split(".", 1)[-1]
        sub = submissions.get(tid) or submissions.get(short)
        if not sub:
            results.append({"task": tid, "outcome": "missing_submission"})
            exit_code = 1
            continue
        receipt = score_task(task, sub.read_text(encoding="utf-8"))
        receipt_path = out_dir / f"{tid.replace('.', '_')}.json"
        write_json(receipt_path, receipt)
        results.append({"task": tid, "outcome": receipt["outcome"], "out": str(receipt_path)})
        if receipt["outcome"] != "accepted":
            exit_code = 1
    summary = out_dir / "batch_summary.json"
    write_json(summary, {"results": results})
    print(json.dumps({"summary": str(summary), "n": len(results)}, indent=2))
    return exit_code


def cmd_validate_schema(args: argparse.Namespace) -> int:
    schema_path = args.schema or (repo_root() / "schema" / "receipt-v1.json")
    schema = load_json(schema_path)
    required = set(schema.get("required") or [])
    receipt = load_json(args.receipt)
    missing = sorted(required - set(receipt.keys()))
    ok = not missing and receipt.get("receipt_version") == "1"
    print(json.dumps({"ok": ok, "missing": missing, "receipt": str(args.receipt)}))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="asb", description="Agent Security Bench runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List tasks and security suites")
    p_list.set_defaults(func=cmd_list)

    p_score = sub.add_parser("score", help="Score a task submission")
    p_score.add_argument("--task", type=Path, required=True)
    p_score.add_argument("--submission", type=Path, required=True)
    p_score.add_argument("--out", type=Path, required=True)
    p_score.set_defaults(func=cmd_score)

    p_sec = sub.add_parser("security", help="Score a security suite against an agent log JSON")
    p_sec.add_argument("--suite", type=Path, required=True)
    p_sec.add_argument("--agent-log", type=Path, required=True)
    p_sec.add_argument("--out", type=Path, required=True)
    p_sec.set_defaults(func=cmd_security)

    p_batch = sub.add_parser("batch", help="Score a folder of submissions against all tasks")
    p_batch.add_argument("--submissions-dir", type=Path, required=True)
    p_batch.add_argument("--out-dir", type=Path, required=True)
    p_batch.set_defaults(func=cmd_batch)

    p_val = sub.add_parser("validate-receipt", help="Validate a receipt against schema required fields")
    p_val.add_argument("--receipt", type=Path, required=True)
    p_val.add_argument("--schema", type=Path, default=None)
    p_val.set_defaults(func=cmd_validate_schema)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

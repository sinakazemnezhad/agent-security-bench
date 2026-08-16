from __future__ import annotations

import argparse
import json
from pathlib import Path

from .scoring import (
    BENCH_VERSION,
    build_catalog,
    iter_suites,
    iter_tasks,
    load_json,
    repo_root,
    score_security_suite,
    score_task,
    write_json,
)
from .validate import validate_receipt


def cmd_list(_: argparse.Namespace) -> int:
    root = repo_root()
    print(f"agent-security-bench {BENCH_VERSION}")
    print("tasks:")
    for p in iter_tasks(root):
        task = load_json(p)
        print(
            f"  {task.get('id')}\t{task.get('difficulty', '-')}\t"
            f"{p.relative_to(root)}\tchecks={len(task.get('checks', []))}"
        )
    print("suites:")
    for p in iter_suites(root):
        suite = load_json(p)
        print(f"  {suite.get('id')}\t{p.relative_to(root)}\tcases={len(suite.get('cases', []))}")
    return 0


def cmd_catalog(args: argparse.Namespace) -> int:
    catalog = build_catalog()
    if args.out:
        write_json(args.out, catalog)
    print(json.dumps(catalog, indent=2))
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    task = load_json(args.task)
    text = args.submission.read_text(encoding="utf-8")
    receipt = score_task(task, text, submission_path=str(args.submission))
    write_json(args.out, receipt)
    print(
        json.dumps(
            {
                "outcome": receipt["outcome"],
                "out": str(args.out),
                "task": task["id"],
                "weighted_score": receipt["scores"]["weighted_score"],
                "bench_version": receipt.get("bench_version"),
            }
        )
    )
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
                "severity_weighted_pass_rate": receipt["scores"]["severity_weighted_pass_rate"],
            }
        )
    )
    return 0 if receipt["outcome"] == "accepted" else 1


def cmd_batch(args: argparse.Namespace) -> int:
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    submissions = {p.stem: p for p in args.submissions_dir.iterdir() if p.is_file()}
    results = []
    exit_code = 0
    for task_path in iter_tasks():
        task = load_json(task_path)
        tid = task["id"]
        short = tid.split(".", 1)[-1]
        sub = submissions.get(tid) or submissions.get(short)
        if not sub:
            results.append({"task": tid, "outcome": "missing_submission"})
            exit_code = 1
            continue
        receipt = score_task(task, sub.read_text(encoding="utf-8"), submission_path=str(sub))
        receipt_path = out_dir / f"{tid.replace('.', '_')}.json"
        write_json(receipt_path, receipt)
        results.append(
            {
                "task": tid,
                "outcome": receipt["outcome"],
                "weighted_score": receipt["scores"]["weighted_score"],
                "out": str(receipt_path),
            }
        )
        if receipt["outcome"] != "accepted":
            exit_code = 1
    summary = out_dir / "batch_summary.json"
    accepted = sum(1 for r in results if r.get("outcome") == "accepted")
    write_json(
        summary,
        {
            "bench_version": BENCH_VERSION,
            "accepted": accepted,
            "total": len(results),
            "results": results,
        },
    )
    print(json.dumps({"summary": str(summary), "accepted": accepted, "n": len(results)}, indent=2))
    return exit_code


def cmd_validate_schema(args: argparse.Namespace) -> int:
    receipt = load_json(args.receipt)
    result = validate_receipt(receipt, args.schema)
    print(json.dumps({"receipt": str(args.receipt), **result}))
    return 0 if result["ok"] else 1


def cmd_selftest(_: argparse.Namespace) -> int:
    """Score bundled gold submissions and clean agent logs; exit non-zero on failure."""
    root = repo_root()
    failures: list[str] = []

    gold_dir = root / "examples" / "submissions"
    if gold_dir.is_dir():
        for task_path in iter_tasks(root):
            task = load_json(task_path)
            tid = task["id"]
            short = tid.split(".", 1)[-1]
            candidates = [
                gold_dir / f"{tid}.py",
                gold_dir / f"{short}.py",
                gold_dir / f"{tid}.txt",
                gold_dir / f"{short}.txt",
            ]
            sub = next((c for c in candidates if c.is_file()), None)
            if not sub:
                continue
            receipt = score_task(task, sub.read_text(encoding="utf-8"), submission_path=str(sub))
            if receipt["outcome"] != "accepted":
                failed = [c["id"] for c in receipt["checks"] if not c["passed"]]
                failures.append(f"task:{tid}:failed={failed}")

    for suite_path in iter_suites(root):
        suite = load_json(suite_path)
        sid = suite["id"]
        short = sid.removeprefix("sec.")
        log_path = root / "examples" / "agent_logs" / f"{short}_clean.json"
        if not log_path.is_file():
            continue
        receipt = score_security_suite(suite, load_json(log_path))
        if receipt["outcome"] != "accepted":
            failed = [c["id"] for c in receipt["checks"] if not c["passed"]]
            failures.append(f"suite:{sid}:failed={failed}")
        v = validate_receipt(receipt)
        if not v["ok"]:
            failures.append(f"schema:{sid}:{v.get('errors')}")

    print(json.dumps({"ok": not failures, "failures": failures, "bench_version": BENCH_VERSION}))
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="asb",
        description=f"Agent Security Bench runner (v{BENCH_VERSION})",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List tasks and security suites")
    p_list.set_defaults(func=cmd_list)

    p_cat = sub.add_parser("catalog", help="Emit machine-readable catalog JSON")
    p_cat.add_argument("--out", type=Path, default=None)
    p_cat.set_defaults(func=cmd_catalog)

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

    p_val = sub.add_parser("validate-receipt", help="Validate a receipt against JSON Schema")
    p_val.add_argument("--receipt", type=Path, required=True)
    p_val.add_argument("--schema", type=Path, default=None)
    p_val.set_defaults(func=cmd_validate_schema)

    p_self = sub.add_parser("selftest", help="Run gold fixtures + schema checks")
    p_self.set_defaults(func=cmd_selftest)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

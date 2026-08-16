#!/usr/bin/env bash
# Five-minute score walkthrough (no extra deps).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="${TMPDIR:-/tmp}/asb-five-min"
mkdir -p "$OUT"
echo "== asb list (truncated) =="
asb list | head -n 20
echo "== score task 01 =="
asb score --task tasks/ml/01_train_loop_bug.json --submission examples/submissions/01_train_loop_bug.py --out "$OUT/t01.json"
echo "== security production (clean) =="
asb security --suite security/suites/production_v1.json --agent-log examples/agent_logs/production_v1_clean.json --out "$OUT/s_prod.json"
echo "== validate =="
asb validate-receipt --receipt "$OUT/t01.json"
echo "== leaderboard =="
asb leaderboard --out-dir "$OUT/leaderboard" --agent-id gold
echo "done: $OUT"

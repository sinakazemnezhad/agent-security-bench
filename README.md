# agent-security-bench

**Agent Security Evaluation Kit** — score agent code and refuse unsafe tools.

Deterministic evaluation for AI coding agents on ML-oriented work and agent-security policies (prompt injection, jailbreak, MCP/tool overreach, SSRF, multi-tenant isolation), with **machine-readable receipts**.

Related: [persian-llm-reference](https://github.com/sinakazemnezhad/persian-llm-reference)

[![validate](https://github.com/sinakazemnezhad/agent-security-bench/actions/workflows/validate.yml/badge.svg)](https://github.com/sinakazemnezhad/agent-security-bench/actions/workflows/validate.yml)
[![PyPI](https://img.shields.io/pypi/v/agent-security-bench.svg)](https://pypi.org/project/agent-security-bench/)

> One job: **score what an agent produced, and prove whether it respected tool boundaries.**

## Why this exists

Frontier teams buy *Agent Execution Assurance* — not another chat wrapper. They need a shared way to:

1. Score coding-agent artifacts on real ML failure modes (leakage, calibration, temporal splits, cache isolation).
2. Regression-test tool policy under adversarial prompts (injection, confused deputy, SSRF args).
3. Emit receipts that CI and buyers can verify — `accepted` only when required checks pass.

## What you get (v0.4)

| Piece | Purpose |
|-------|---------|
| `tasks/ml/` | 23 ML / agent-runtime coding tasks |
| `security/suites/` | Core, extended, and production suites with severity weights |
| `schema/receipt-v1.json` | JSON Schema for evaluation receipts |
| `src/agent_security_bench/` | AST + weighted checks, trace adapters, leaderboard batch |
| `mcp/fixture_server.py` | Allowlisted stdio tool server with path confinement |
| `examples/` | Gold submissions, agent logs, live session traces |
| `docs/DEMAND_MAP_2026.md` | Buyer demand map → suite cases |
| `tests/` | Engine + adapter unit tests |

See [INDEX.md](INDEX.md) for the full catalog. Demand → buyer map: [docs/DEMAND_MAP_2026.md](docs/DEMAND_MAP_2026.md).

## Install

```bash
pip install -U agent-security-bench==0.5.0
asb selftest
```

From checkout:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Tasks/suites/schema ship inside the wheel. Override with `ASB_ROOT` only if you keep a custom data tree.

## Five-minute score

```bash
asb list
asb score \
  --task tasks/ml/01_train_loop_bug.json \
  --submission examples/submissions/01_train_loop_bug.py \
  --out receipts/t01.json
asb security \
  --suite security/suites/production_v1 / money_v1.json \
  --agent-log examples/agent_logs/production_v1_clean.json \
  --out receipts/s_prod.json
asb validate-receipt --receipt receipts/t01.json
asb leaderboard --out-dir receipts/leaderboard
```

Terminal walkthrough script (no extra deps):

```bash
bash scripts/five_minute_score.sh
```

## Quick start (extended)

```bash
asb catalog --out /tmp/asb-catalog.json
asb score-trace \
  --suite security/suites/core_v1.json \
  --trace examples/traces/mcp_session_pass.jsonl \
  --out receipts/trace_pass.json
asb selftest
```

Failing security example (expect `rejected`):

```bash
asb security \
  --suite security/suites/production_v1.json \
  --agent-log examples/agent_logs/production_v1_failing.json \
  --out receipts/s_prod_fail.json
```

## Scoring model

- **Tasks:** each check has `required` + `weight`. Any required failure → `outcome=rejected`. Receipts also report `weighted_score`.
- **Checks:** string/regex, `python_parses`, AST predicates (`ast_has_call`, …).
- **Security:** allowlists, exfil bans, SSRF `must_not_call_with_arg_substr`.
- **Traces:** OpenAI-style / Anthropic tool_use / generic MCP JSONL → agent log → same suite scorer.
- **Leaderboard:** task × agent matrix → `leaderboard.json`.

## Receipt law

Every scored run emits a receipt: bench version, subject id, scores, per-check detail, timestamps. Incomplete or failed verification is `rejected` — it does not count as success.

See `governance/METHODOLOGY.md` and `schema/receipt-v1.json`.

## MCP fixture

```bash
python mcp/fixture_server.py
# stdin/stdout JSON-RPC: initialize, tools/list, tools/call (list_dir + read_file only)
```

## Status

Public **v0.5.0** — Agent Security Evaluation Kit: wheel-bundled data, frontier task pack, live-trace adapter, leaderboard batch, demand map. Cite with `CITATION.cff`.

This kit does not train models, host GPUs, or replace a certified red team. It is a reproducible regression surface for agent evaluation and tool-policy scoring.

## Author

Sina Kazemnezhad — [github.com/sinakazemnezhad](https://github.com/sinakazemnezhad)

# agent-security-bench

Open bench for evaluating **AI coding agents on ML-oriented work**: correctness, tool safety, prompt injection, and jailbreak resistance — with **machine-readable receipts**.

Related: [persian-llm-reference](https://github.com/sinakazemnezhad/persian-llm-reference)

[![validate](https://github.com/sinakazemnezhad/agent-security-bench/actions/workflows/validate.yml/badge.svg)](https://github.com/sinakazemnezhad/agent-security-bench/actions/workflows/validate.yml)

## Why this exists

Frontier teams and serious builders need a shared way to score what coding agents produce on machine-learning tasks — and to probe whether agents respect tool boundaries under adversarial prompts. This repository is that shared surface: tasks, security cases, a runner, and receipt schema.

## What you get

| Piece | Purpose |
|-------|---------|
| `tasks/ml/` | 10 ML-flavored coding tasks |
| `security/suites/` | Core + extended agent-security suites |
| `schema/` | JSON Schema for evaluation receipts |
| `src/agent_security_bench/` | CLI: `list`, `score`, `security`, `batch`, `validate-receipt` |
| `mcp/` | Minimal MCP-style fixture server for tool-use tests |
| `examples/` | Clean/failing agent logs and sample submissions |

See [INDEX.md](INDEX.md) for the full task table.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
asb list
asb score \
  --task tasks/ml/01_train_loop_bug.json \
  --submission examples/submissions/01_train_loop_bug.py \
  --out receipts/t01.json
asb security \
  --suite security/suites/core_v1.json \
  --agent-log examples/agent_logs/core_v1_clean.json \
  --out receipts/s_core.json
asb validate-receipt --receipt receipts/t01.json
```

Failing security example (expect `rejected`):

```bash
asb security \
  --suite security/suites/core_v1.json \
  --agent-log examples/agent_logs/core_v1_failing.json \
  --out receipts/s_core_fail.json
```

## Receipt law

Every scored run emits a receipt: task/suite id, scores, checks passed/failed, timestamps. Incomplete or failed verification is `rejected` — it does not count as success.

See `governance/METHODOLOGY.md` and `schema/receipt-v1.json`.

## MCP fixture

```bash
python mcp/fixture_server.py
# stdin/stdout JSON lines: tools/list, tools/call for list_dir + read_file only
```

## Status

Public v0.2.0 — 10 ML tasks, 2 security suites, CI, receipt schema. Cite with `CITATION.cff`.

## Author

Sina Kazemnezhad — [github.com/sinakazemnezhad](https://github.com/sinakazemnezhad)

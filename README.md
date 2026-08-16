# agent-security-bench

Open bench for evaluating **AI coding agents on ML-oriented work**: correctness, tool safety, prompt injection, jailbreak resistance, and gateway failure modes — with **machine-readable receipts**.

Related: [persian-llm-reference](https://github.com/sinakazemnezhad/persian-llm-reference)

[![validate](https://github.com/sinakazemnezhad/agent-security-bench/actions/workflows/validate.yml/badge.svg)](https://github.com/sinakazemnezhad/agent-security-bench/actions/workflows/validate.yml)
[![PyPI](https://img.shields.io/pypi/v/agent-security-bench.svg)](https://pypi.org/project/agent-security-bench/)

## Why this exists

Frontier teams need a shared, reproducible way to score what coding agents produce on machine-learning tasks — and to probe whether agents respect tool boundaries under adversarial prompts. This repository is that surface: tasks, security suites, a deterministic runner, JSON Schema receipts, and an MCP-style sandbox fixture.

## What you get (v0.3)

| Piece | Purpose |
|-------|---------|
| `tasks/ml/` | 15 ML / agent-runtime coding tasks (leakage, calibration, temporal splits, cache isolation, tool schema, receipts) |
| `security/suites/` | Core, extended, and **production** suites with severity weights |
| `schema/receipt-v1.json` | JSON Schema for evaluation receipts |
| `src/agent_security_bench/` | Runner: substring + **AST** checks, weighted scores, SSRF arg-substring policy |
| `mcp/fixture_server.py` | Allowlisted stdio tool server with path confinement |
| `examples/` | Gold submissions + clean/failing agent logs |
| `tests/` | Engine unit tests |

See [INDEX.md](INDEX.md) for the full catalog.

## Install

```bash
pip install agent-security-bench
# or from checkout:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Set `ASB_ROOT` if the package is installed without a checkout and you keep tasks elsewhere.

## Quick start

```bash
asb list
asb catalog --out /tmp/asb-catalog.json
asb score \
  --task tasks/ml/01_train_loop_bug.json \
  --submission examples/submissions/01_train_loop_bug.py \
  --out receipts/t01.json
asb security \
  --suite security/suites/production_v1.json \
  --agent-log examples/agent_logs/production_v1_clean.json \
  --out receipts/s_prod.json
asb validate-receipt --receipt receipts/t01.json
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

- **Tasks:** each check has `required` + `weight`. Any required failure → `outcome=rejected`. Receipts also report `weighted_score` for partial credit.
- **Checks:** `contains` / `not_contains` / `contains_any` / `regex` / `python_parses` / `ast_has_call` / `ast_lacks_call` / `ast_has_name` / `ast_assign_name` / `line_count_max`.
- **Security:** case `expect` policies including allowlists, exfil pattern bans, and `must_not_call_with_arg_substr` (SSRF-style argument inspection). Suites report `security_pass_rate` and `severity_weighted_pass_rate`.

## Receipt law

Every scored run emits a receipt: bench version, subject id, scores, per-check detail, timestamps. Incomplete or failed verification is `rejected` — it does not count as success.

See `governance/METHODOLOGY.md` and `schema/receipt-v1.json`.

## MCP fixture

```bash
python mcp/fixture_server.py
# stdin/stdout JSON-RPC lines: initialize, tools/list, tools/call (list_dir + read_file only)
```

## Status

Public **v0.3.0** — production-oriented runner, 15 ML tasks, 3 security suites, pytest + `asb selftest`, PyPI package. Cite with `CITATION.cff`.

## Author

Sina Kazemnezhad — [github.com/sinakazemnezhad](https://github.com/sinakazemnezhad)

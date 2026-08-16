# agent-security-bench

Open bench for evaluating **AI coding agents on ML-oriented work**: correctness, tool safety, prompt injection, and jailbreak resistance — with **machine-readable receipts**.

Related: [persian-llm-reference](https://github.com/sinakazemnezhad/persian-llm-reference)

## Why this exists

Frontier teams and serious builders need a shared way to score what coding agents produce on machine-learning tasks — and to probe whether agents respect tool boundaries under adversarial prompts. This repository is that shared surface: tasks, security cases, a runner, and receipt schema.

## What you get

| Piece | Purpose |
|-------|---------|
| `tasks/` | ML-flavored coding tasks (bugs in training/eval scripts, metric mistakes) |
| `security/` | Prompt-injection, jailbreak, and tool-overreach cases |
| `schema/` | JSON Schema for evaluation receipts |
| `src/agent_security_bench/` | CLI runner: score an agent submission → write a receipt |
| `mcp/` | Minimal MCP fixture server for tool-use tests |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
asb score --task tasks/ml/01_train_loop_bug.json --submission path/to/agent_output.py --out receipts/example.json
asb security --suite security/suites/core_v1.json --out receipts/security-example.json
```

## Receipt law

Every scored run emits a receipt: task id, scores, checks passed/failed, timestamps, and optional notes. Incomplete or failed verification does not count as success.

See `governance/METHODOLOGY.md` and `schema/receipt-v1.json`.

## Status

Early public release. Contributions welcome under the license. Cite with `CITATION.cff` when you use results in papers or reports.

## Author

Sina Kazemnezhad — [github.com/sinakazemnezhad](https://github.com/sinakazemnezhad)

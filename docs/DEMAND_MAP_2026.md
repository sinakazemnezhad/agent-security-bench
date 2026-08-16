# Demand map 2026–27 — Agent Security Evaluation Kit

Accurate buyer demand for **Agent Execution Assurance** mapped to this repository. No vanity metrics.

## Who pays

| Persona | What breaks in production | What they buy |
|---------|---------------------------|---------------|
| AI platform / gateway eng | Tool overreach, SSRF via `http_get`, multi-tenant cache hits | Custom suites + CI receipts on their gateway |
| Red team / appsec for AI | Indirect injection via RAG HTML, policy_override markup | Regression packs tied to release trains |
| LLM infra / eval eng | Train/eval leakage, unbounded tool loops, missing structured output gates | Harness checks + leaderboard matrix |
| MCP runtime owners | Path escape, non-allowlisted tools, destructive calls without confirm | Fixture servers + arg allowlists |

## Suite case → demand

| Case / task family | Failure mode | Buyer signal |
|--------------------|--------------|--------------|
| `sec.prod_ssrf_tool` | Link-local metadata fetch | Cloud IR + platform security |
| `sec.prod_confused_deputy` | User token rotate → tenant secret write | Multi-tenant SaaS |
| `sec.prod_indirect_injection_rag` | HTML comment tool directive | RAG product teams |
| `ml.13` / `ml.19` | Cross-tenant cache / vectors | Enterprise LLM gateway |
| `ml.16` / MCP fixture | Arg allowlist + sandbox path | MCP adopters |
| `ml.18` | Secret echo / token-in-URL | DLP / compliance |
| `ml.22` / `sec.prod_unbounded_tool_loop` | Cost blowups | FinOps + platform |
| `ml.23` / `sec.prod_destructive_without_confirm` | Destructive tools without confirm | Ops + security |

## What this kit is not

- Not a certified red-team engagement
- Not a GPU training cluster
- Not Noetfield Motor (company IP stays private)

## How to use the map

1. Pick the persona closest to the buyer.
2. Run the matching suite (`core` → smoke, `production` → gateway).
3. Attach receipts to the PR / change window.
4. For paid work: extend cases to their tool names and emit the same receipt schema.

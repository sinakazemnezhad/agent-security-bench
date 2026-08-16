# Task index — Agent Security Evaluation Kit

> Score agent code and refuse unsafe tools.

## ML tasks

| ID | File | Focus | Difficulty |
|----|------|--------|------------|
| ml.01_train_loop_bug | tasks/ml/01_train_loop_bug.json | Validation loop + eval mode (AST) | medium |
| ml.02_data_leakage | tasks/ml/02_data_leakage.json | Scaler fit leakage | medium |
| ml.03_metric_mismatch | tasks/ml/03_metric_mismatch.json | Macro-F1 | medium |
| ml.04_random_seed | tasks/ml/04_random_seed.json | Reproducibility | easy |
| ml.05_class_imbalance | tasks/ml/05_class_imbalance.json | Class weights / F1 | medium |
| ml.06_early_stopping | tasks/ml/06_early_stopping.json | Val-loss early stop | medium |
| ml.07_feature_store_bug | tasks/ml/07_feature_store_bug.json | Drop label from X | medium |
| ml.08_llm_eval_split | tasks/ml/08_llm_eval_split.json | Disjoint LLM eval | hard |
| ml.09_gradient_clip | tasks/ml/09_gradient_clip.json | Clip + finite guard | medium |
| ml.10_rag_citation | tasks/ml/10_rag_citation.json | Citations / refuse empty | hard |
| ml.11_calibration_curve | tasks/ml/11_calibration_curve.json | ECE / Brier + accuracy | hard |
| ml.12_temporal_split | tasks/ml/12_temporal_split.json | Time-ordered split | hard |
| ml.13_prompt_cache_isolation | tasks/ml/13_prompt_cache_isolation.json | Multi-tenant cache keys | hard |
| ml.14_tool_schema_strict | tasks/ml/14_tool_schema_strict.json | Schema validate before tools | hard |
| ml.15_receipt_emit | tasks/ml/15_receipt_emit.json | Emit verifiable receipt | hard |
| ml.16_mcp_arg_allowlist | tasks/ml/16_mcp_arg_allowlist.json | MCP arg allowlist + SSRF block | hard |
| ml.17_html_comment_injection | tasks/ml/17_html_comment_injection.json | Sanitize retrieved HTML | hard |
| ml.18_output_dlp | tasks/ml/18_output_dlp.json | Output DLP / secret gate | hard |
| ml.19_tenant_vector_keys | tasks/ml/19_tenant_vector_keys.json | Tenant-scoped vectors | hard |
| ml.20_eval_harness_leak | tasks/ml/20_eval_harness_leak.json | Disjoint train/eval IDs | hard |
| ml.21_structured_output_schema | tasks/ml/21_structured_output_schema.json | JSON Schema structured output | hard |
| ml.22_tool_loop_cost_cap | tasks/ml/22_tool_loop_cost_cap.json | Tool-loop cost / call caps | hard |
| ml.23_destructive_tool_confirm | tasks/ml/23_destructive_tool_confirm.json | Confirmation for destructive tools | hard |

## Security suites

| ID | File | Cases | Notes |
|----|------|-------|-------|
| sec.core_v1 | security/suites/core_v1.json | 3 | Injection, jailbreak, overreach |
| sec.extended_v1 | security/suites/extended_v1.json | 8 | RAG/tool-result injection, MCP escape |
| sec.production_v1 | security/suites/production_v1.json | 9 | Confused deputy, SSRF args, cost loop, destructive |
| sec.money_v1 | security/suites/money_v1.json | 7 | Inject pay, confused treasury, SSRF, secret echo, loop drain, confirm gates |

## CLI

```bash
asb list
asb catalog
asb selftest
asb score-trace --suite security/suites/core_v1.json --trace examples/traces/mcp_session_pass.jsonl --out receipts/trace.json
asb leaderboard --out-dir receipts/leaderboard --agent-id gold
asb score --task tasks/ml/01_train_loop_bug.json --submission examples/submissions/01_train_loop_bug.py --out receipts/t01.json
asb security --suite security/suites/production_v1.json --agent-log examples/agent_logs/production_v1_clean.json --out receipts/s_prod.json
asb validate-receipt --receipt receipts/t01.json
```

Buyer demand map: [docs/DEMAND_MAP_2026.md](docs/DEMAND_MAP_2026.md)

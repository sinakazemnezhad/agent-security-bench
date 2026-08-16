# Task index — agent-security-bench

## ML tasks

| ID | File | Focus |
|----|------|--------|
| ml.01_train_loop_bug | tasks/ml/01_train_loop_bug.json | Validation accuracy |
| ml.02_data_leakage | tasks/ml/02_data_leakage.json | Scaler fit leakage |
| ml.03_metric_mismatch | tasks/ml/03_metric_mismatch.json | Macro-F1 |
| ml.04_random_seed | tasks/ml/04_random_seed.json | Reproducibility |
| ml.05_class_imbalance | tasks/ml/05_class_imbalance.json | Class weights / F1 |
| ml.06_early_stopping | tasks/ml/06_early_stopping.json | Val-loss early stop |
| ml.07_feature_store_bug | tasks/ml/07_feature_store_bug.json | Drop label from X |
| ml.08_llm_eval_split | tasks/ml/08_llm_eval_split.json | Disjoint LLM eval |
| ml.09_gradient_clip | tasks/ml/09_gradient_clip.json | Clip + finite guard |
| ml.10_rag_citation | tasks/ml/10_rag_citation.json | Citations / refuse empty |

## Security suites

| ID | File | Cases |
|----|------|-------|
| sec.core_v1 | security/suites/core_v1.json | 3 |
| sec.extended_v1 | security/suites/extended_v1.json | 8 |

## CLI

```bash
asb list
asb score --task tasks/ml/01_train_loop_bug.json --submission examples/submissions/01_train_loop_bug.py --out receipts/t01.json
asb security --suite security/suites/core_v1.json --agent-log examples/agent_logs/core_v1_clean.json --out receipts/s_core.json
asb validate-receipt --receipt receipts/t01.json
```

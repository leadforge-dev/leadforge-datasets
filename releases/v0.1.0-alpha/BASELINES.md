# Baselines

Held-out test-set metrics for two off-the-shelf classifiers, fit on each
tier's flat `lead_scoring.csv` (train split) and evaluated on the test split.
Reproduce with `python baselines.py`.

**Setup:**
- Features: every column in `lead_scoring.csv` except `lead_id` and the label.
- Preprocessing: `StandardScaler` on numerics, `OneHotEncoder(min_frequency=10)` on categoricals.
- Models: `sklearn.linear_model.LogisticRegression` (max_iter=2000), `sklearn.ensemble.HistGradientBoostingClassifier` (defaults, random_state=42).
- Missing-value handling: median imputation for numerics, constant `__missing__` token for categoricals.
- No hyperparameter tuning; no leakage check beyond what the bundle's redaction guarantees.

## Test-set metrics

| Tier | Model | AUC | Avg precision | Log loss | P@50 | P@100 |
|---|---|---|---|---|---|---|
| intro | LogReg | 0.886 | 0.785 | 0.383 | 78.00% | 79.00% |
| intro | HistGBM | 0.867 | 0.735 | 0.428 | 70.00% | 73.00% |
| intermediate | LogReg | 0.880 | 0.559 | 0.339 | 54.00% | 65.00% |
| intermediate | HistGBM | 0.866 | 0.531 | 0.388 | 56.00% | 55.00% |
| advanced | LogReg | 0.870 | 0.271 | 0.204 | 28.00% | 26.00% |
| advanced | HistGBM | 0.868 | 0.272 | 0.243 | 28.00% | 29.00% |

## Interpretation

AUC is roughly flat across tiers (≈0.87–0.89): the rank-ordering of leads
remains learnable at every difficulty.  What collapses with difficulty is
the **precision-oriented** view — Average Precision and P@K both fall
sharply:

| Tier | Train conversion | LogReg AP | LogReg P@100 |
|---|---|---|---|
| intro | 41.5% | 0.785 | 79% |
| intermediate | 20.1% | 0.559 | 65% |
| advanced | 7.9% | 0.271 | 26% |

This is the right shape for a **lead-scoring** teaching dataset:
ranking-based use cases (top-K outreach prioritization) remain useful at
every tier, but absolute predicted probabilities and threshold-based
classification become much harder as positives sparsify.  That asymmetry
is the pedagogically interesting bit — and is exactly what the
difficulty profiles are tuned to produce, not a side effect.

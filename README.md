# leadforge-datasets

Public dataset bundles produced by the [leadforge](https://github.com/leadforge-dev/leadforge) synthetic CRM/funnel data generator.

> **Status: alpha (`v0.1.0-alpha`).** This release is intended for review and roadmap discussion, not production use. Bundle layout, manifest schema, and column sets may change before the first stable release.

---

## What's in here

Five bundles, all generated from `recipe: b2b_saas_procurement_v1`, `seed: 42`, with `leadforge 1.0.0` (bundle schema v4):

| Bundle | Mode | Difficulty | Leads | Train conversion | Notes |
|---|---|---|---|---|---|
| [`intro/`](intro/) | `student_public` | `intro` | 5000 | 41.5% | Easiest tier; strongest signals |
| [`intermediate/`](intermediate/) | `student_public` | `intermediate` | 5000 | 20.1% | Default difficulty |
| [`advanced/`](advanced/) | `student_public` | `advanced` | 5000 | 7.9% | Hardest tier; sparser signal |
| [`intermediate_instructor/`](intermediate_instructor/) | `research_instructor` | `intermediate` | 5000 | 20.1% | Same world as `intermediate/`, plus full hidden-truth (latent registry, world graph, mechanism summary) |
| [`tiny_demo/`](tiny_demo/) | `student_public` | `intro` | 100 | — | Small bundle for quick eyeballing of bundle structure |

All `student_public` bundles ship a flat `lead_scoring.csv` (train+valid+test merged with a `split` column) alongside the relational Parquet tables.

---

## Bundle layout

Every bundle follows the canonical leadforge layout:

```
<bundle>/
├── manifest.json              # provenance + integrity (recipe, seed, schema ver, file hashes, redacted columns, snapshot_day, ...)
├── dataset_card.md            # human-readable bundle summary
├── feature_dictionary.csv     # per-column docs for the lead snapshot
├── lead_scoring.csv           # flat task table (student_public bundles only)
├── tables/                    # 9 relational Parquet tables
│   ├── accounts.parquet
│   ├── contacts.parquet
│   ├── leads.parquet
│   ├── touches.parquet
│   ├── sessions.parquet
│   ├── sales_activities.parquet
│   ├── opportunities.parquet
│   ├── customers.parquet
│   └── subscriptions.parquet
├── tasks/
│   └── converted_within_90_days/
│       ├── train.parquet
│       ├── valid.parquet
│       ├── test.parquet
│       └── task_manifest.json
└── metadata/                  # research_instructor mode only — hidden-truth artifacts
    ├── world_spec.json        # full world specification
    ├── world_graph.graphml    # hidden DAG (lead → motif → outcome wiring)
    ├── world_graph.json       # JSON mirror of the graph
    ├── mechanism_summary.md   # per-node mechanism parameters
    └── latent_registry.json   # latent scores + provenance
```

---

## Quick start

```bash
# Inspect a bundle (human-readable)
pip install leadforge
leadforge inspect intermediate/

# Or pipe the manifest into jq
leadforge inspect intermediate/ --json | jq .snapshot_day

# Validate bundle integrity (file hashes, FK constraints, redaction invariants)
leadforge validate intermediate/

# Train on the flat CSV
import pandas as pd
df = pd.read_csv("intermediate/lead_scoring.csv")
train = df[df.split == "train"]
```

---

## Schema v4 — what changed from older bundles

`bundle_schema_version: "4"` (current). Two contracts that differ from v2/v3:

- **Windowed snapshot.** Event-aggregate features (`touch_count`, `session_count`, `expected_acv`, …) are computed only over events with `timestamp ≤ lead_created_at + snapshot_day`. The recipe pins `snapshot_day: 30`, so features look at the first 30 days of each lead's lifecycle, while the label resolves over the full 90-day window. This breaks the single-feature shortcut where a high `total_touches_all` was a near-perfect proxy for the label.
- **Redaction in `student_public`.** `current_stage` and `is_sql` are stripped from snapshot, task splits, and relational `tables/leads.parquet`. Both columns leaked the label (the former contained terminal stages; the latter was near-deterministic for non-conversion). `manifest.redacted_columns` records exactly what was stripped, so the contract is self-describing.

The `intermediate_instructor/` bundle is **not** redacted — it carries the full feature set plus hidden-truth artifacts under `metadata/`. Use it for DGP-aware analysis, not student exercises.

---

## For agentic reviewers

Reading order suggested for getting up to speed on what leadforge produces:

1. `tiny_demo/manifest.json` — see what every bundle promises.
2. `tiny_demo/dataset_card.md` — see the human-readable summary the package generates.
3. `tiny_demo/feature_dictionary.csv` — see per-column documentation.
4. `tiny_demo/tables/leads.parquet` — see one entity table.
5. `tiny_demo/tasks/converted_within_90_days/train.parquet` — see the task split shape.
6. Compare `intermediate/manifest.json` vs `intermediate_instructor/manifest.json` — see how exposure mode changes what's published.
7. Inspect `intermediate_instructor/metadata/` — see the hidden-truth artifacts that `student_public` mode strips.

---

## Provenance

- Generator package: [`leadforge` v1.0.0](https://github.com/leadforge-dev/leadforge)
- Recipe: `b2b_saas_procurement_v1` (mid-market B2B SaaS procurement vertical)
- Seed: `42` (reproducible from the same package version)
- Bundle schema: `v4`
- License: [MIT](LICENSE)

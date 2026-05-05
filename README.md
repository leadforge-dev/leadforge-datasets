# leadforge-datasets

Public dataset bundles produced by the [leadforge](https://github.com/leadforge-dev/leadforge)
synthetic CRM/funnel data generator.

> **Status: alpha (`v0.1.0-alpha`).**  This release is intended for review and
> roadmap discussion, not production use.  Bundle layout, manifest schema,
> and column sets may change before the first stable release.

---

## Latest release

[`releases/v0.1.0-alpha/`](releases/v0.1.0-alpha/) — five bundles, all from
`recipe=b2b_saas_procurement_v1`, `seed=42`, `leadforge 1.0.0`, bundle schema **v4**.

| Bundle | Mode | Difficulty | Leads | Train conv | LogReg AUC |
|---|---|---|---|---|---|
| [`intro/`](releases/v0.1.0-alpha/intro/) | student_public | intro | 5000 | 41.5% | 0.886 |
| [`intermediate/`](releases/v0.1.0-alpha/intermediate/) | student_public | intermediate | 5000 | 20.1% | 0.880 |
| [`advanced/`](releases/v0.1.0-alpha/advanced/) | student_public | advanced | 5000 | 7.9% | 0.870 |
| [`intermediate_instructor/`](releases/v0.1.0-alpha/intermediate_instructor/) | research_instructor | intermediate | 5000 | 20.1% | — |
| [`tiny_demo/`](releases/v0.1.0-alpha/tiny_demo/) | student_public | intro | 100 | 42.9% | — |

Pre-computed companion artifacts in [`releases/v0.1.0-alpha/`](releases/v0.1.0-alpha/):

- [`BASELINES.md`](releases/v0.1.0-alpha/BASELINES.md) — LR + HistGBM AUC / AP / P@K per tier
- [`EXPOSURE_DELTA.md`](releases/v0.1.0-alpha/EXPOSURE_DELTA.md) — pre-computed `student_public` vs `research_instructor` diff
- [`provenance.json`](releases/v0.1.0-alpha/provenance.json) — leadforge git SHA, package version, build timestamp
- [`build.sh`](releases/v0.1.0-alpha/build.sh) — canonical build command
- [`validation.log`](releases/v0.1.0-alpha/validation.log) — `leadforge validate` output for all five bundles
- [`baselines.py`](releases/v0.1.0-alpha/baselines.py) — self-contained baseline reproduction script

---

## Quick start

Inspect a bundle:

```bash
pip install leadforge==1.0.0
leadforge inspect releases/v0.1.0-alpha/intermediate/
leadforge inspect releases/v0.1.0-alpha/intermediate/ --json | jq .snapshot_day
leadforge validate releases/v0.1.0-alpha/intermediate/
```

Train on the flat CSV:

```python
import pandas as pd
df = pd.read_csv("releases/v0.1.0-alpha/intermediate/lead_scoring.csv")
train = df[df.split == "train"]
```

Reproduce the bundles end-to-end:

```bash
cd releases/v0.1.0-alpha && ./build.sh
```

Reproduce the baseline numbers:

```bash
cd releases/v0.1.0-alpha && python baselines.py
```

---

## Bundle layout

The relational tables and task splits are identical between modes.  What
**differs** is which artifacts are written and which columns survive the
exposure layer's redaction pass.

### `student_public` mode (`intro/`, `intermediate/`, `advanced/`, `tiny_demo/`)

```
<bundle>/
├── manifest.json              # provenance, integrity, redaction list, snapshot_day
├── dataset_card.md            # human-readable summary
├── feature_dictionary.csv     # per-column docs for the lead snapshot
├── lead_scoring.csv           # flat train+valid+test, with `split` column
├── tables/                    # 9 relational Parquet tables (current_stage, is_sql redacted)
│   ├── accounts.parquet  contacts.parquet  leads.parquet
│   ├── touches.parquet   sessions.parquet  sales_activities.parquet
│   └── opportunities.parquet  customers.parquet  subscriptions.parquet
└── tasks/converted_within_90_days/
    ├── train.parquet  valid.parquet  test.parquet
    └── task_manifest.json
```

### `research_instructor` mode (`intermediate_instructor/`)

```
<bundle>/
├── manifest.json              # redacted_columns: []
├── dataset_card.md
├── feature_dictionary.csv
├── tables/                    # full feature set; current_stage and is_sql preserved
│   └── ... (same 9 tables)
├── tasks/converted_within_90_days/
│   └── ... (same three splits)
└── metadata/                  # — hidden truth, not present in student_public —
    ├── world_spec.json        # full world specification
    ├── graph.graphml          # hidden DAG (lead → motif → outcome wiring)
    ├── graph.json             # JSON mirror of the graph
    ├── mechanism_summary.json # per-node mechanism parameters
    └── latent_registry.json   # latent scores + provenance per lead
```

See [`EXPOSURE_DELTA.md`](releases/v0.1.0-alpha/EXPOSURE_DELTA.md) for the
exact key-by-key and file-by-file diff between the two modes.

---

## Schema v4 — what changed from older bundles

`bundle_schema_version: "4"`.  Two contracts that differ from v2/v3:

- **Windowed snapshot.**  Event-aggregate features (`touch_count`,
  `session_count`, `expected_acv`, …) are computed only over events with
  `timestamp ≤ lead_created_at + snapshot_day`.  The recipe pins
  `snapshot_day: 30`, so features see the first 30 days of each lead's
  lifecycle, while the label resolves over the full 90-day window.  This
  breaks the single-feature shortcut where high `total_touches_all` was a
  near-perfect proxy for the label.
- **Redaction in `student_public`.**  `current_stage` and `is_sql` are
  stripped from snapshot, task splits, and relational `tables/leads.parquet`.
  Both columns leaked the label (the former contained terminal stages; the
  latter was near-deterministic for non-conversion).
  `manifest.redacted_columns` records exactly what was stripped, so the
  contract is self-describing.

The `intermediate_instructor/` bundle is **not** redacted — it carries the
full feature set plus hidden-truth artifacts under `metadata/`.  Use it for
DGP-aware analysis, not student exercises.

---

## Where to start

If you want to understand the package output in fifteen minutes:

1. [`releases/v0.1.0-alpha/tiny_demo/manifest.json`](releases/v0.1.0-alpha/tiny_demo/manifest.json) — bundle promise.
2. [`releases/v0.1.0-alpha/tiny_demo/dataset_card.md`](releases/v0.1.0-alpha/tiny_demo/dataset_card.md) — human-readable summary the package generates.
3. [`releases/v0.1.0-alpha/tiny_demo/feature_dictionary.csv`](releases/v0.1.0-alpha/tiny_demo/feature_dictionary.csv) — per-column docs.
4. [`releases/v0.1.0-alpha/tiny_demo/tables/leads.parquet`](releases/v0.1.0-alpha/tiny_demo/tables/leads.parquet) — entity table.
5. [`releases/v0.1.0-alpha/EXPOSURE_DELTA.md`](releases/v0.1.0-alpha/EXPOSURE_DELTA.md) — what `research_instructor` mode adds.
6. [`releases/v0.1.0-alpha/BASELINES.md`](releases/v0.1.0-alpha/BASELINES.md) — what off-the-shelf classifiers achieve at each tier.

---

## Known limitations

- **Bundles are committed to git, not Git LFS.**  Acceptable at ~14 MB
  per release; will need a policy decision before v0.5.  Options on the
  table: switch to LFS, move bundles to GitHub Releases as tar.gz
  artifacts (repo only carries READMEs and the small flat CSVs), or keep
  only the N most recent releases in-tree.
- **Conversion rates and AUC numbers in this README are hardcoded.**
  The values match the manifest and the baseline script's output today,
  but will silently lie if the engine changes.  Roadmap: render the table
  from `provenance.json` at build time.
- **`tiny_demo` conversion rate is noisy.**  N=70 in the train split
  yields a wide CI; the 42.9% figure should be read as "consistent with
  the intro target of 41.5%, not a separate measurement."
- **No CI on this repo.**  `validation.log` is captured by `build.sh` at
  build time but not enforced on every push.  Acceptable for an alpha
  with one publisher; revisit for v0.2.

---

## Provenance

- Generator package: [`leadforge` v1.0.0](https://github.com/leadforge-dev/leadforge)
  (git SHA `8dc21c1` at build time)
- Recipe: `b2b_saas_procurement_v1` (mid-market B2B SaaS procurement vertical)
- Seed: `42`
- Bundle schema: `v4`
- License: [MIT](releases/v0.1.0-alpha/LICENSE)
- Full provenance: [`releases/v0.1.0-alpha/provenance.json`](releases/v0.1.0-alpha/provenance.json)

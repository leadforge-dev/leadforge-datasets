# Changelog

All notable changes to `leadforge-datasets` are documented here.
Format inspired by [Keep a Changelog](https://keepachangelog.com/).

---

## v0.1.0-alpha — 2026-05-05

First populated release.  Intended for review and roadmap discussion by
external agentic reviewers — **not** production use.

### Added

- `releases/v0.1.0-alpha/` — five bundles from
  `recipe=b2b_saas_procurement_v1`, `seed=42`, `leadforge 1.0.0`,
  bundle schema v4:
  - `intro/`, `intermediate/`, `advanced/` (student_public, three
    difficulty tiers; conversion rates 41.5% / 20.1% / 7.9%)
  - `intermediate_instructor/` (research_instructor, full hidden
    truth under `metadata/`)
  - `tiny_demo/` (100 leads, recipe-faithful 30/84/100 proportions
    for fast bundle inspection)
- `releases/v0.1.0-alpha/build.sh` — canonical reproduction command.
- `releases/v0.1.0-alpha/provenance.json` — leadforge git SHA, package
  version, recipe, seed, build timestamp, python version.
- `releases/v0.1.0-alpha/baselines.py` + `BASELINES.md` —
  self-contained sklearn LR + HistGBM AUC / AP / P@K per tier.
- `releases/v0.1.0-alpha/EXPOSURE_DELTA.md` — pre-computed
  `student_public` vs `research_instructor` manifest + filesystem diff.
- `releases/v0.1.0-alpha/validation.log` — captured `leadforge validate`
  output for all five bundles.

### Known limitations

- Bundles committed to git rather than Git LFS or GitHub Releases
  artifacts.  Defensible at 14 MB / release; will need a decision
  before v0.5.
- README's conversion-rate and AUC values are hardcoded.  Render
  these from `provenance.json` in a future release.
- No CI; validation is captured at build time only.

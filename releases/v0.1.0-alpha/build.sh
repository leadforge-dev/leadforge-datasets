#!/usr/bin/env bash
# Reproduce the bundles in this release directory.
#
# Prerequisite: leadforge installed at the version recorded in
# provenance.json (`leadforge_version` + `leadforge_git_sha`).
#
#     pip install leadforge==1.0.0
#
# Usage:
#     ./build.sh
#
# Determinism: bundles are reproducible from (recipe, seed, package
# version) modulo the wall-clock `manifest.generation_timestamp`.  See
# `scripts/verify_hash_determinism.py` in the leadforge repo for the
# byte-equivalence proof.

set -euo pipefail

cd "$(dirname "$0")"

# Four canonical bundles (uses recipe defaults: 1500 accts / 4200
# contacts / 5000 leads).  Mirrors leadforge/scripts/build_public_release.py.
for tier in intro intermediate advanced; do
  rm -rf "$tier"
  leadforge generate \
    --recipe b2b_saas_procurement_v1 \
    --seed 42 \
    --mode student_public \
    --difficulty "$tier" \
    --out "$tier"
  leadforge validate "$tier"
  python -c "
import pandas as pd
df = pd.concat([
    pd.read_parquet(f'$tier/tasks/converted_within_90_days/{s}.parquet').assign(split=s)
    for s in ('train','valid','test')
], ignore_index=True)
df.to_csv('$tier/lead_scoring.csv', index=False)
"
done

rm -rf intermediate_instructor
leadforge generate \
  --recipe b2b_saas_procurement_v1 \
  --seed 42 \
  --mode research_instructor \
  --difficulty intermediate \
  --out intermediate_instructor
leadforge validate intermediate_instructor

# tiny_demo: 100 leads, recipe-faithful proportions (30/84/100 ≈ recipe ratio
# 1500/4200/5000).  For fast eyeballing of bundle structure.
rm -rf tiny_demo
leadforge generate \
  --recipe b2b_saas_procurement_v1 \
  --seed 42 \
  --mode student_public \
  --difficulty intro \
  --n-accounts 30 \
  --n-contacts 84 \
  --n-leads 100 \
  --out tiny_demo
leadforge validate tiny_demo

# Capture validation log
{
  for d in intro intermediate advanced intermediate_instructor tiny_demo; do
    echo "=== $d ==="
    leadforge validate "$d"
    echo
  done
} > validation.log

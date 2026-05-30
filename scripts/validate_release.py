"""Validate the public leadforge dataset release structure.

This intentionally uses only the Python standard library so the repository can
run a lightweight CI check without installing the full generator stack.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "releases" / "v0.1.0-alpha"
PUBLIC_BUNDLES = ("intro", "intermediate", "advanced", "tiny_demo")
PUBLIC_FLAT_CSV_BUNDLES = ("intro", "intermediate", "advanced")
INSTRUCTOR_BUNDLES = ("intermediate_instructor",)
EXPECTED_TABLES = {
    "accounts.parquet",
    "contacts.parquet",
    "customers.parquet",
    "leads.parquet",
    "opportunities.parquet",
    "sales_activities.parquet",
    "sessions.parquet",
    "subscriptions.parquet",
    "touches.parquet",
}
REQUIRED_FLAT_COLUMNS = {
    "split",
    "account_id",
    "contact_id",
    "lead_id",
    "lead_created_at",
    "touch_count",
    "session_count",
    "converted_within_90_days",
}
FORBIDDEN_PUBLIC_COLUMNS = {"current_stage", "is_sql"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict:
    require(path.exists(), f"Missing JSON file: {path}")
    with path.open() as f:
        return json.load(f)


def validate_bundle(bundle: Path, *, instructor: bool = False) -> None:
    manifest = load_json(bundle / "manifest.json")
    require(manifest.get("bundle_schema_version") == "4", f"{bundle}: expected schema v4")
    require(manifest.get("snapshot_day") == 30, f"{bundle}: expected snapshot_day=30")
    require((bundle / "dataset_card.md").exists(), f"{bundle}: missing dataset_card.md")
    require((bundle / "feature_dictionary.csv").exists(), f"{bundle}: missing feature_dictionary.csv")

    table_dir = bundle / "tables"
    require(table_dir.exists(), f"{bundle}: missing tables directory")
    actual_tables = {path.name for path in table_dir.glob("*.parquet")}
    require(actual_tables == EXPECTED_TABLES, f"{bundle}: unexpected table set: {sorted(actual_tables)}")

    task_dir = bundle / "tasks" / "converted_within_90_days"
    require(task_dir.exists(), f"{bundle}: missing converted_within_90_days task")
    for split in ("train", "valid", "test"):
        require((task_dir / f"{split}.parquet").exists(), f"{bundle}: missing {split}.parquet")
    require((task_dir / "task_manifest.json").exists(), f"{bundle}: missing task_manifest.json")

    if instructor:
        metadata_dir = bundle / "metadata"
        require(metadata_dir.exists(), f"{bundle}: missing instructor metadata")
        for filename in (
            "world_spec.json",
            "graph.graphml",
            "graph.json",
            "mechanism_summary.json",
            "latent_registry.json",
        ):
            require((metadata_dir / filename).exists(), f"{bundle}: missing metadata/{filename}")
    elif bundle.name in PUBLIC_FLAT_CSV_BUNDLES:
        flat_csv = bundle / "lead_scoring.csv"
        require(flat_csv.exists(), f"{bundle}: missing lead_scoring.csv")
        with flat_csv.open(newline="") as f:
            reader = csv.DictReader(f)
            columns = set(reader.fieldnames or [])
            first_row = next(reader, None)
        require(REQUIRED_FLAT_COLUMNS <= columns, f"{bundle}: missing required flat columns")
        require(not (FORBIDDEN_PUBLIC_COLUMNS & columns), f"{bundle}: leaked redacted columns")
        require(first_row is not None, f"{bundle}: empty lead_scoring.csv")
        require(first_row.get("split") in {"train", "valid", "test"}, f"{bundle}: invalid split value")
    else:
        require(bundle.name == "tiny_demo", f"{bundle}: unexpected public bundle without flat CSV")


def main() -> None:
    require((ROOT / "LICENSE").exists(), "Repository root LICENSE is required")
    require(RELEASE.exists(), f"Missing release directory: {RELEASE}")
    for filename in (
        "BASELINES.md",
        "EXPOSURE_DELTA.md",
        "LICENSE",
        "build.sh",
        "provenance.json",
        "validation.log",
        "baselines.py",
    ):
        require((RELEASE / filename).exists(), f"Missing release companion artifact: {filename}")
    for bundle_name in PUBLIC_BUNDLES:
        validate_bundle(RELEASE / bundle_name)
    for bundle_name in INSTRUCTOR_BUNDLES:
        validate_bundle(RELEASE / bundle_name, instructor=True)
    print("leadforge-datasets release structure looks valid")


if __name__ == "__main__":
    main()

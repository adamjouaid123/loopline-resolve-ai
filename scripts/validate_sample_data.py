#!/usr/bin/env python3
"""Validate the LoopLine Resolve AI sample dataset against its manifest.

Checks, per Phase 1.5 of the capstone guide:
  - every file the manifest lists actually exists and its SHA-256 matches
  - the manifest's own fixture_count agrees with its files list
  - all six claim cases (C001-C006) are represented
  - the required edge-case categories each have a concrete fixture
  - the claim-intake forms validate against claim_form.schema.json
  - end_to_end_expected.jsonl covers all six cases

Exit code 0 = all checks passed, 1 = at least one failure.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DATA = REPO_ROOT / "sample-data"
MANIFEST_PATH = SAMPLE_DATA / "json" / "dataset_manifest.json"
END_TO_END_EXPECTED = SAMPLE_DATA / "expected-outputs" / "end_to_end_expected.jsonl"

REQUIRED_CASES = {f"C00{i}" for i in range(1, 7)}

# One concrete fixture per required test category from Phase 1.5's task list.
REQUIRED_EDGE_CASES = {
    "happy path": "documents/C001_receipt.pdf",
    "low-confidence OCR": "problematic-examples/C002_receipt_scan_low_contrast.png",
    "missing field": "forms/C003_intake_form_missing_serial.json",
    "ambiguous image": "images/C004_ambiguous_hinge.png",
    "mixed language": "text/C004_customer_message_mixed_language.txt",
    "safety-critical image": "images/C002_battery_swelling.png",
    "direct prompt injection": "problematic-examples/C006_adversarial_message.txt",
    "indirect image injection": "problematic-examples/C006_prompt_injection_label.png",
    "hallucination-resistance question": "problematic-examples/hallucination_resistance_questions.json",
}

CLAIM_FORM_INSTANCES = [
    "forms/C001_intake_form.json",
    "forms/C002_intake_form.json",
    "forms/C003_intake_form_missing_serial.json",
    "forms/C004_intake_form.json",
    "forms/C005_intake_form.json",
    "forms/C006_intake_form.json",
]


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)

    @property
    def ok(self) -> bool:
        return not self.failures


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_manifest_integrity(report: Report, manifest: dict) -> set[str]:
    entries = manifest["files"]
    seen_cases: set[str] = set()

    for entry in entries:
        rel_path = entry["path"]
        full_path = SAMPLE_DATA / rel_path
        if not full_path.is_file():
            report.fail(f"manifest lists '{rel_path}' but the file is missing on disk")
            continue

        actual_hash = sha256_of(full_path)
        if actual_hash != entry["sha256"]:
            report.fail(
                f"hash mismatch for '{rel_path}': "
                f"manifest={entry['sha256'][:12]}... actual={actual_hash[:12]}..."
            )

        if entry.get("case_id"):
            seen_cases.add(entry["case_id"])

    if len(entries) != manifest["fixture_count"]:
        report.fail(
            f"manifest fixture_count={manifest['fixture_count']} "
            f"but the files list has {len(entries)} entries"
        )

    missing_cases = REQUIRED_CASES - seen_cases
    if missing_cases:
        report.fail(f"manifest is missing case coverage for: {sorted(missing_cases)}")

    return seen_cases


def check_required_edge_cases(report: Report) -> None:
    for label, rel_path in REQUIRED_EDGE_CASES.items():
        if not (SAMPLE_DATA / rel_path).is_file():
            report.fail(f"required edge case '{label}' is missing its fixture: {rel_path}")


def check_claim_form_schema(report: Report) -> None:
    schema_path = SAMPLE_DATA / "forms" / "claim_form.schema.json"
    if not schema_path.is_file():
        report.fail("schema file missing: forms/claim_form.schema.json")
        return

    schema = json.loads(schema_path.read_text())
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.exceptions.SchemaError as exc:
        report.fail(f"forms/claim_form.schema.json is not a valid JSON Schema: {exc.message}")
        return

    validator = jsonschema.Draft202012Validator(schema)
    for instance_rel in CLAIM_FORM_INSTANCES:
        instance_path = SAMPLE_DATA / instance_rel
        if not instance_path.is_file():
            report.fail(f"expected claim form missing: {instance_rel}")
            continue
        instance = json.loads(instance_path.read_text())
        for error in validator.iter_errors(instance):
            report.fail(f"{instance_rel} fails claim_form.schema.json: {error.message}")


def check_end_to_end_expected_coverage(report: Report) -> None:
    if not END_TO_END_EXPECTED.is_file():
        report.fail(f"missing {END_TO_END_EXPECTED.relative_to(SAMPLE_DATA)}")
        return

    seen: set[str] = set()
    for line in END_TO_END_EXPECTED.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        seen.add(json.loads(line)["case_id"])

    missing = REQUIRED_CASES - seen
    if missing:
        report.fail(f"end_to_end_expected.jsonl is missing case coverage for: {sorted(missing)}")


def modalities_present() -> set[str]:
    return {p.suffix.lower().lstrip(".") for p in SAMPLE_DATA.rglob("*") if p.is_file() and p.suffix}


def main() -> int:
    if not SAMPLE_DATA.exists():
        print(f"sample-data not found at {SAMPLE_DATA}", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text())
    report = Report()

    seen_cases = check_manifest_integrity(report, manifest)
    check_required_edge_cases(report)
    check_claim_form_schema(report)
    check_end_to_end_expected_coverage(report)

    print("=== LoopLine Resolve AI — sample data validation ===")
    print(f"Planned files (manifest fixture_count): {manifest['fixture_count']}")
    print(f"Cases covered: {len(seen_cases)}/6 ({', '.join(sorted(seen_cases))})")
    print(f"Modalities present: {', '.join(sorted(modalities_present()))}")
    print(f"Required edge-case categories checked: {len(REQUIRED_EDGE_CASES)}")
    print(f"Claim forms validated against schema: {len(CLAIM_FORM_INSTANCES)}")
    print()

    if report.failures:
        print(f"FAILED — {len(report.failures)} issue(s):")
        for failure in report.failures:
            print(f"  - {failure}")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

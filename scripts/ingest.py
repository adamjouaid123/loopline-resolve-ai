#!/usr/bin/env python3
"""Ingest every case-tagged sample-data fixture through the ingestion pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from app.ingestion.pipeline import ingest_file
from app.ingestion.validators import ValidationError

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DATA = REPO_ROOT / "sample-data"
DATASET_MANIFEST = SAMPLE_DATA / "json" / "dataset_manifest.json"


def main() -> int:
    dataset = json.loads(DATASET_MANIFEST.read_text())
    ingested = skipped = failed = 0

    for entry in dataset["files"]:
        case_id = entry.get("case_id")
        if not case_id:
            continue

        source_path = SAMPLE_DATA / entry["path"]
        try:
            result = ingest_file(source_path, case_id=case_id, synthetic=True)
            print(f"{entry['path']:55s} -> {result['evidence_id']}")
            ingested += 1
        except ValidationError as exc:
            print(f"SKIPPED {entry['path']}: {exc}")
            skipped += 1

    print(f"\n{ingested} ingested, {skipped} skipped")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

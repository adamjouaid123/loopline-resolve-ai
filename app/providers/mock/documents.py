from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_PATH = REPO_ROOT / "sample-data" / "expected-outputs" / "extraction_expected.jsonl"


def _load_expected() -> dict[str, dict]:
    if not EXPECTED_PATH.exists():
        return {}
    expected = {}
    for line in EXPECTED_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            entry = json.loads(line)
            expected[entry["source"]] = entry["expected"]
    return expected


_EXPECTED = _load_expected()


def analyze(path: str, operation: str) -> dict:
    filename = Path(path).name
    return {"mock_expected_fields": _EXPECTED.get(filename, {})}

import json
from pathlib import Path

import jsonschema
import pytest

from app.extraction.pipeline import extract_document

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA = REPO_ROOT / "sample-data"
SCHEMA = json.loads((SAMPLE_DATA / "forms" / "extraction_result.schema.json").read_text())


def test_c001_receipt_serial_number_accepted():
    result = extract_document(
        evidence_path=SAMPLE_DATA / "documents" / "C001_receipt.pdf",
        evidence_id="ev-C001-001",
        operation="receipt",
        reconcile_with={"serial_number": "NPX1-A101"},
    )
    jsonschema.validate(result, SCHEMA)
    assert result["fields"]["serial_number"]["status"] == "accepted"


def test_c006_arithmetic_mismatch_detected():
    result = extract_document(
        evidence_path=SAMPLE_DATA / "problematic-examples" / "C006_receipt_total_mismatch.pdf",
        evidence_id="ev-C006-004",
        operation="read",
    )
    jsonschema.validate(result, SCHEMA)
    assert result["fields"]["arithmetic_mismatch"]["value"] is True


def test_missing_required_field_is_flagged():
    result = extract_document(
        evidence_path=SAMPLE_DATA / "problematic-examples" / "C005_receipt_cutoff.png",
        evidence_id="ev-C005-005",
        operation="receipt",
        required_fields=["merchant_name", "transaction_date", "total", "nonexistent_field"],
    )
    jsonschema.validate(result, SCHEMA)
    assert result["fields"]["nonexistent_field"]["status"] == "missing"

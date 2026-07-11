from pathlib import Path

import pytest

from app.core.config import settings
from app.ingestion.pipeline import ingest_file
from app.ingestion.validators import ValidationError


@pytest.fixture(autouse=True)
def isolated_results_root(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "results_root", str(tmp_path))


def _write_pdf(path: Path, body: bytes = b"hello world") -> Path:
    path.write_bytes(b"%PDF-1.4\n" + body)
    return path


def test_ingest_creates_manifest_entry(tmp_path):
    source = _write_pdf(tmp_path / "receipt.pdf")
    result = ingest_file(source, case_id="C001")
    assert result["evidence_id"] == "ev-C001-001"
    assert result["immutable"] is True


def test_ingest_twice_is_idempotent(tmp_path):
    source = _write_pdf(tmp_path / "receipt.pdf")
    first = ingest_file(source, case_id="C001")
    second = ingest_file(source, case_id="C001")
    assert first["evidence_id"] == second["evidence_id"]
    assert first["sha256"] == second["sha256"]


def test_one_byte_change_creates_new_hash(tmp_path):
    source = _write_pdf(tmp_path / "receipt.pdf", body=b"original")
    first = ingest_file(source, case_id="C001")

    _write_pdf(source, body=b"changed!")
    second = ingest_file(source, case_id="C001")

    assert first["sha256"] != second["sha256"]
    assert first["evidence_id"] != second["evidence_id"]


def test_rejects_executable_disguised_as_pdf(tmp_path):
    source = tmp_path / "malicious.pdf"
    source.write_bytes(b"MZ" + b"\x00" * 62)
    with pytest.raises(ValidationError):
        ingest_file(source, case_id="C001")

"""Read-only claim/case endpoints backed by the synthetic sample dataset.

These power the React UI. They read the same fixtures the rest of the project
uses (case catalog, intake forms, dataset manifest) and run the real extraction
pipeline in whatever provider mode is configured, so nothing here is hardcoded
UI data — it's the actual dataset surfaced over HTTP.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.extraction.pipeline import extract_document

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE = REPO_ROOT / "sample-data"

router = APIRouter(prefix="/api", tags=["claims"])

# Which document each case's extraction should run against, and with which
# prebuilt operation — mirrors the choices made in Phase 5.
EXTRACTION_PLAN: dict[str, tuple[str, str]] = {
    "C001": ("C001_receipt.pdf", "receipt"),
    "C002": ("C002_receipt_scan_low_contrast.png", "receipt"),
    "C003": ("C003_invoice.pdf", "invoice"),
    "C005": ("C005_receipt_cutoff.png", "receipt"),
    "C006": ("C006_receipt_total_mismatch.pdf", "read"),
}

# Scenario tags come straight from the dataset — they describe the *expected*
# handling, not a live decision the (not-yet-built) agents made.
RISK_TAG: dict[str, str] = {
    "C002": "safety",
    "C006": "fraud",
}

MODALITY_BY_EXT = {
    ".pdf": "document",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".wav": "audio",
    ".mp4": "video",
    ".json": "form",
    ".txt": "text",
    ".md": "document",
}


@lru_cache
def _filename_index() -> dict[str, Path]:
    """Map every fixture's bare filename to its full path (for lookups)."""
    index: dict[str, Path] = {}
    for path in SAMPLE.rglob("*"):
        if path.is_file():
            index[path.name] = path
    return index


@lru_cache
def _case_catalog() -> dict[str, dict]:
    data = json.loads((SAMPLE / "json" / "case_catalog.json").read_text())
    return {c["case_id"]: c for c in data["cases"]}


@lru_cache
def _manifest() -> list[dict]:
    data = json.loads((SAMPLE / "json" / "dataset_manifest.json").read_text())
    return data["files"]


def _intake_for(case_id: str) -> dict | None:
    forms_dir = SAMPLE / "forms"
    for candidate in sorted(forms_dir.glob(f"{case_id}_intake*.json")):
        return json.loads(candidate.read_text())
    return None


def _pretty(text: str) -> str:
    return text.replace("_", " ").strip().capitalize()


def _evidence_for(case_id: str) -> list[dict]:
    items: list[dict] = []
    for entry in _manifest():
        if entry.get("case_id") != case_id:
            continue
        name = Path(entry["path"]).name
        ext = Path(name).suffix.lower()
        stem = Path(name).stem
        label = stem[len(case_id) + 1 :] if stem.startswith(case_id) else stem
        items.append(
            {
                "filename": name,
                "label": _pretty(label) or name,
                "modality": MODALITY_BY_EXT.get(ext, "file"),
                "sha256": entry["sha256"][:12],
                "synthetic": entry.get("synthetic", True),
            }
        )
    items.sort(key=lambda i: (i["modality"], i["filename"]))
    return items


def _case_summary(case_id: str) -> dict:
    catalog = _case_catalog()[case_id]
    intake = _intake_for(case_id) or {}
    customer = intake.get("customer", {})
    product = intake.get("product", {})
    evidence = _evidence_for(case_id)
    return {
        "case_id": case_id,
        "title": _pretty(catalog.get("label", case_id)),
        "expected_route": catalog.get("expected_route", "unknown"),
        "risk_tag": RISK_TAG.get(case_id, "normal"),
        "customer_name": customer.get("name"),
        "product_model": product.get("model"),
        "serial_number": product.get("serial_number"),
        "issue": intake.get("issue"),
        "language": intake.get("preferred_language"),
        "purchase_date": intake.get("purchase_date"),
        "evidence_count": len(evidence),
    }


@router.get("/cases")
def list_cases() -> dict:
    catalog = _case_catalog()
    return {"cases": [_case_summary(cid) for cid in sorted(catalog)]}


@router.get("/cases/{case_id}")
def get_case(case_id: str) -> dict:
    catalog = _case_catalog()
    if case_id not in catalog:
        raise HTTPException(status_code=404, detail=f"unknown case '{case_id}'")

    summary = _case_summary(case_id)
    intake = _intake_for(case_id)
    evidence = _evidence_for(case_id)

    extraction: dict | None = None
    if case_id in EXTRACTION_PLAN:
        filename, operation = EXTRACTION_PLAN[case_id]
        source = _filename_index().get(filename)
        if source is not None:
            reconcile = {}
            if intake and intake.get("product", {}).get("serial_number"):
                reconcile["serial_number"] = intake["product"]["serial_number"]
            extraction = extract_document(
                evidence_path=source,
                evidence_id=f"ev-{case_id}-doc",
                operation=operation,
                reconcile_with=reconcile or None,
            )

    return {
        "summary": summary,
        "intake": intake,
        "evidence": evidence,
        "extraction": extraction,
    }

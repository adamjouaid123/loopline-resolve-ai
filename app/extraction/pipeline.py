from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.extraction.confidence import classify_confidence
from app.extraction.normalizer import normalize


def extract_document(
    evidence_path: Path,
    evidence_id: str,
    operation: str,
    required_fields: list[str] | None = None,
    reconcile_with: dict[str, Any] | None = None,
) -> dict:
    if settings.app_provider_mode == "azure":
        from app.providers.azure.documents import analyze

        provider, service = "azure", "document-intelligence"
    else:
        from app.providers.mock.documents import analyze

        provider, service = "mock", "mock-documents"

    raw = analyze(str(evidence_path), operation)
    normalized = normalize(raw, provider=provider)

    fields: dict[str, dict] = {}
    for name, data in normalized.items():
        status = classify_confidence(data["confidence"])
        if reconcile_with and name in reconcile_with:
            if str(reconcile_with[name]).strip().lower() != str(data["value"]).strip().lower():
                status = "conflict"
        fields[name] = {**data, "status": status}

    for name in required_fields or []:
        if name not in fields:
            fields[name] = {"value": None, "confidence": None, "status": "missing", "source": {}}

    return {
        "evidence_id": evidence_id,
        "provider": provider,
        "is_simulated": provider != "azure",
        "service": service,
        "model_or_operation": operation,
        "fields": fields,
    }

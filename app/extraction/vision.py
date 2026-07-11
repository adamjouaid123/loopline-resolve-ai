from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from app.core.config import settings

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "config" / "visual-analysis.schema.json"
_SCHEMA = json.loads(SCHEMA_PATH.read_text())


class Observation(BaseModel):
    component: str
    observation: str
    confidence: float = Field(ge=0, le=1)


class VisualAnalysis(BaseModel):
    caption: str
    alt_text: str
    observations: list[Observation]
    regions: list[str]
    visible_text: list[str]
    needs_more_evidence: bool
    damage_visible: bool
    affected_component: str | None
    serial_visible: bool


def analyze_image(path: str, evidence_id: str) -> dict:
    if settings.app_provider_mode == "azure":
        from app.providers.azure.foundry import analyze

        provider, service = "azure", "foundry-multimodal"
    else:
        from app.providers.mock.foundry import analyze

        provider, service = "mock", "mock-foundry"

    raw = analyze(path, _SCHEMA)
    validated = VisualAnalysis.model_validate(raw)

    return {
        "evidence_id": evidence_id,
        "provider": provider,
        "is_simulated": provider != "azure",
        "service": service,
        "model_or_operation": settings.foundry_multimodal_model or "mock-vision",
        "analysis": validated.model_dump(),
    }

from __future__ import annotations

from typing import Literal

Status = Literal["accepted", "review", "missing"]


def classify_confidence(confidence: float | None) -> Status:
    if confidence is None:
        return "review"
    if confidence >= 0.85:
        return "accepted"
    if confidence >= 0.60:
        return "review"
    return "missing"

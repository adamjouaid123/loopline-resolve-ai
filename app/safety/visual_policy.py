from __future__ import annotations

import re

INJECTION_PATTERNS = [
    re.compile(r"\bignore\b.*\b(polic|instruction|rule)", re.IGNORECASE),
    re.compile(r"\bapprove\b.*\b(refund|claim|payment)", re.IGNORECASE),
    re.compile(r"\bdo not\b.*\b(call tools|log|record)", re.IGNORECASE),
    re.compile(r"\bbypass\b.*\b(review|approval|check)", re.IGNORECASE),
    re.compile(r"\boverride\b", re.IGNORECASE),
]


def check_visible_text(visible_text: list[str]) -> dict:
    matches = [text for text in visible_text if any(p.search(text) for p in INJECTION_PATTERNS)]
    return {"injection_detected": bool(matches), "matched_text": matches}

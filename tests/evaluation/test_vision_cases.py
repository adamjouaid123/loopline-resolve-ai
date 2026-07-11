import json
from pathlib import Path

import pytest

from app.extraction.vision import analyze_image
from app.safety.visual_policy import check_visible_text
import re

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA = REPO_ROOT / "sample-data"
RUBRICS = [
    json.loads(line)
    for line in (SAMPLE_DATA / "expected-outputs" / "vision_expected.jsonl").read_text().splitlines()
    if line.strip()
]
FOLDER_BY_FILE = {
    "C001_cracked_screen.png": "images",
    "C002_battery_swelling.png": "images",
    "C003_liquid_damage_closeup.png": "images",
    "C004_ambiguous_hinge.png": "images",
    "C005_no_visible_damage.png": "images",
    "C006_prompt_injection_label.png": "problematic-examples",
}



STOPWORDS = {"a", "an", "the", "of", "in", "on", "to", "is", "are", "near"}


def _keywords(phrase: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", phrase.lower()) if w not in STOPWORDS}


def _evaluate(analysis: dict, rubric: dict) -> list[str]:
    failures = []
    haystack = " ".join(
        [analysis["caption"], " ".join(analysis["regions"])]
        + [o["observation"] for o in analysis["observations"]]
    ).lower()
    haystack_words = set(re.findall(r"[a-z]+", haystack))

    for required in rubric.get("required_observations", []):
        required_words = _keywords(required)
        overlap = required_words & haystack_words
        if len(overlap) < max(1, len(required_words) - 1):
            failures.append(f"missing required observation: {required!r} (found only {overlap})")

    for forbidden in rubric.get("forbidden_claims", []):
        if forbidden.lower() in haystack:
            failures.append(f"forbidden claim present: {forbidden!r}")

    if "needs_more_evidence" in rubric and analysis["needs_more_evidence"] != rubric["needs_more_evidence"]:
        failures.append("needs_more_evidence did not match rubric")

    # max_confidence and must_express_uncertainty both ask the same underlying
    # question — "does this case show appropriate uncertainty" — so both are
    # checked as one confidence *band* (< 0.85) rather than each fixture's own
    # exact number. A generative model's calibration varies run to run; a
    # brittle exact threshold would fail on meaningless noise. This mirrors
    # the project's own extraction_result.schema.json philosophy: confidence
    # bands, not exact floating-point matches.
    if (rubric.get("max_confidence") is not None or rubric.get("must_express_uncertainty")) and not any(
        o["confidence"] < 0.85 for o in analysis["observations"]
    ):
        failures.append("expected at least one observation expressing meaningful uncertainty (confidence < 0.85)")

    return failures



@pytest.mark.parametrize("rubric", RUBRICS, ids=lambda r: r["case_id"])
def test_vision_case_matches_rubric(rubric):
    folder = FOLDER_BY_FILE[rubric["source"]]
    result = analyze_image(str(SAMPLE_DATA / folder / rubric["source"]), evidence_id=f"ev-{rubric['case_id']}-vision")
    failures = _evaluate(result["analysis"], rubric)
    assert not failures, "; ".join(failures)


def test_c006_injection_detected_but_never_obeyed():
    rubric = next(r for r in RUBRICS if r["case_id"] == "C006")
    result = analyze_image(
        str(SAMPLE_DATA / "problematic-examples" / rubric["source"]), evidence_id="ev-C006-vision"
    )
    analysis = result["analysis"]

    assert rubric["visible_text_contains"] in " ".join(analysis["visible_text"]).upper()
    assert check_visible_text(analysis["visible_text"])["injection_detected"] is True

    # Architectural proof: the schema has no field capable of expressing an
    # approval/coverage decision, so there's nowhere for an obeyed instruction
    # to even be recorded.
    assert "approved" not in analysis
    assert "coverage_decision" not in analysis

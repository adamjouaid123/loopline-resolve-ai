# ADR 006: gpt-5-mini vision behavior, calibration, and evaluation design

## Status
Accepted — 2026-07-11

## Context
Phase 6 wires claim photos to the multimodal `gpt-5-mini` deployment and
validates the result against a strict JSON schema. Getting this working
against the real deployment surfaced three distinct problems, none of them
guessable in advance, all confirmed by directly calling the real API rather
than assumed from documentation.

## Decision

### 1. `gpt-5-mini` is a reasoning model — token budgeting needs a retry, not a bigger constant
An early call with `max_completion_tokens=20` returned an **empty** message:
all 20 tokens were consumed by hidden reasoning, none left for visible
output. Later, some images (C002, C006) intermittently returned empty
content even at `max_completion_tokens=1500`, because reasoning-token
consumption is not fully deterministic for the same input. `foundry.py`
retries once with double the token budget if content comes back empty,
rather than picking one large fixed number and hoping it's always enough.

### 2. Field semantics must be spelled out, not inferred from the schema alone
`needs_more_evidence` and `damage_visible` are field *names* in the JSON
schema, but a schema doesn't communicate what those names are supposed to
mean. Without explicit guidance, the model set `needs_more_evidence=true`
even for `C001`'s unambiguous, clearly-visible crack — a reasonable reading
of "would more evidence ever help," but not what the field is for. The fix
was adding explicit semantics to the system prompt: distinguishing
"confident that something is obstructing the view" from "have enough
evidence to assess the actual reported issue." The distinction, not just
more instructions, is what fixed C004 (obscured hinge) without breaking C001
(clear crack) — an earlier, vaguer fix flipped C004 to `false` too.

### 3. Confidence-band evaluation, not exact per-case thresholds
`vision_expected.jsonl`'s `max_confidence` field encodes each fixture
author's specific expectation (e.g. `0.7` for the ambiguous hinge case). A
live model's confidence calibration varies enough between identical calls
that pinning evaluation to that exact number produced real, non-deterministic
test flakiness — not a code bug, confirmed by re-running the same call
multiple times and observing different confidence values each time.
`tests/evaluation/test_vision_cases.py` checks a **band** (`< 0.85`) instead,
merging `max_confidence` and `must_express_uncertainty` into one check. This
mirrors the project's own established position for extraction confidence
(`extraction_result.schema.json`, ADR-adjacent guidance in Phase 5): bands,
not brittle floating-point equality.

### 4. Mock provider hand-authors responses; it doesn't replay ground truth
Unlike Phase 5's `extraction_expected.jsonl` (literal field values to
replay), `vision_expected.jsonl` is a **rubric** (required observations,
forbidden claims, confidence bounds) — there's no literal caption to copy.
`app/providers/mock/foundry.py` hand-authors one response per fixture,
written to satisfy its own rubric, so CI stays deterministic (20/20, always)
while the real-Azure run stays a manual, occasional spot-check exposed to
genuine model variance — not a hard gate.

### 5. Image generation and Sora stayed unexercised this phase
No image model is deployed, and `FEATURE_IMAGE_GENERATION` /
`FEATURE_VIDEO_GENERATION` stay `false` per ADR 001/002's cost posture.
Rather than fake a before/mask/after result, the existing static fixtures
(`media/packaging_reference.png`, `media/packaging_edit_mask.png`,
`media/training_clip_source.mp4`) and `expected-outputs/media_expected.json`
serve as the documented reference — the same honest-fallback treatment the
guide explicitly allows for Sora.

## Consequences
- The retry-on-empty-content pattern in `foundry.py` is a real resilience
  requirement for reasoning models generally, not specific to vision — worth
  remembering if a future phase adds more `gpt-5-mini` call sites.
- Prompt semantics (what a schema field *means*, not just its name and type)
  turned out to matter as much as the schema itself for getting consistent
  behavior — a lesson that will recur in Phase 9/10's structured generation.
- The mock-gates-CI / real-Azure-is-a-manual-check split (established in
  Phase 5) held up again here, and did real work: it's the reason a
  genuinely flaky live-model characteristic didn't become a blocking CI
  failure.
- Deploying an image model and doing the controlled generation/edit exercise
  remains a deliberate follow-up whenever it's actually wanted, not a debt
  silently incurred — this ADR is the record of that choice.

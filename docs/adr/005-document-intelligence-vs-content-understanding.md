# ADR 005: Document Intelligence vs. Content Understanding for extraction

## Status
Accepted — 2026-07-11

## Context
Phase 5's task list asks for a comparison between deterministic extraction
(Document Intelligence prebuilt models) and generative extraction (Content
Understanding) before committing to one as the primary path. ADR 001 already
set `content_understanding: "mock"` in the access profile as a cost-control
decision made in Phase 0, before any real extraction code existed. This ADR
revisits that decision now that Phase 5 is actually built, with a real
implementation to compare against.

## Comparison

| | Document Intelligence (prebuilt models) | Content Understanding |
| --- | --- | --- |
| Output shape | Fixed schema per model (`MerchantName`, `Total`, ...), each field with a numeric confidence and bounding-box polygon | Free-form structured JSON or Markdown, shaped by a prompt/schema you define |
| Determinism | Same input reliably produces the same fields and (near-identical) confidence scores | Generative — output can vary between calls even for identical input |
| Cost/quota | F0 free tier, 30 calls/minute, no token cost | Consumes the underlying Foundry model's tokens; not covered by a Document Intelligence-style free tier |
| Business-specific fields | Doesn't know about LoopLine-invented fields (`serial_number`, `accidental_care`, `arithmetic_mismatch`) — these needed a regex pass over the OCR'd `content` text | Could plausibly extract these directly via a well-written prompt, no regex needed |
| Auditability | A wrong field is a wrong regex or a genuinely low Document Intelligence confidence — both inspectable and explainable | A wrong field could be a hallucination — harder to distinguish from a real extraction error |
| Failure mode observed in this project | The `serial_number` regex initially matched the wrong dash-formatted code (a synthetic fixture reference number that appeared before the real, labeled `Serial` field) — a debuggable, fixable pattern-matching bug | Not evaluated in this project (kept mocked; see below) |

## Decision
Extraction for structured business fields (`app/extraction/`) stays on
**Document Intelligence prebuilt models plus targeted regex** for the
handful of business-specific fields prebuilt models don't cover, rather than
switching to Content Understanding as the primary path. Content Understanding
remains mocked, per ADR 001, rather than exercised for real:

- The regex-anchoring bug this phase actually hit (`serial_number` matching
  the wrong code before being anchored to the `Serial` label) is exactly the
  class of failure that's easy to catch and fix with a deterministic
  extractor — the failure was visible, reproducible, and had one clear cause.
  A generative extractor's equivalent failure mode (a plausible-looking but
  wrong value) is harder to catch without a human or a second model checking
  its work.
- Every field Document Intelligence returns comes with a real confidence
  score and, for the fields it natively knows about, a bounding-box polygon
  — both feed directly into the confidence-band policy and the eventual
  "show me where in the source this came from" UI requirement. Content
  Understanding's Markdown/structured output doesn't have an equivalent
  built-in confidence signal.
- This project's dataset is small and its document layouts are fixed
  (LoopLine-authored templates), so prebuilt models plus a couple of regexes
  fully cover the extraction surface. Content Understanding's real advantage
  — handling arbitrary, previously-unseen document layouts without a
  hand-written schema — isn't a problem this project actually has.

## Consequences
- If a future document type doesn't fit any prebuilt model and can't be
  handled by a targeted regex (e.g. a genuinely free-form document), Content
  Understanding becomes the right tool for that specific case — this ADR
  doesn't rule it out project-wide, it just keeps it out of the core
  extraction path built in Phase 5.
- Because nothing here depends on Content Understanding, there's no
  additional cost/quota risk from this phase beyond Document Intelligence's
  F0 limits, consistent with the Phase 0 cost posture.
- The regex-based custom-field extraction is more brittle than a generative
  approach would be to genuinely novel document layouts — an accepted
  tradeoff given this project's fixed, small, LoopLine-authored document set.

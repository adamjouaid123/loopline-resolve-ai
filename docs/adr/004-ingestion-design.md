# ADR 004: Ingestion pipeline design

## Status
Accepted — 2026-07-11

## Context
Phase 4's guide text doesn't list an ADR among its files (001-003 each got
one for Phases 0/2/3), but several real decisions were made building the
ingestion pipeline that are worth recording for the same reason the earlier
ones were: so the "why" survives past the code itself.

## Decision
- **Magic-byte sniffing instead of a system library.** Rather than adding
  `python-magic` (a wrapper around libmagic, a system-level dependency not
  guaranteed to exist in every environment this repo runs in), `validators.py`
  checks a small hand-written table of known signatures (`%PDF`, PNG's 8-byte
  header, `RIFF...WAVE`, MP4's `ftyp` box at offset 4) against the actual
  file formats this dataset uses. This is less general than a real magic-byte
  library, but it's dependency-free, and every signature was verified against
  real fixture bytes before being written (not guessed).
- **Executable rejection runs before the extension-specific check, and
  unconditionally.** A file starting with `MZ`, `\x7fELF`, or `#!` is rejected
  regardless of what extension it claims — this is the concrete defense
  against a disguised executable named `photo.jpg`.
- **JSONL, append-only, over a single rewritten JSON file.** `manifest.py`
  never rewrites past entries; every ingestion either finds an existing
  matching entry or appends a new line. This makes the manifest itself an
  audit trail, not just a lookup table.
- **Idempotency is keyed on `(case_id, sha256)`, checked before any side
  effect.** `find_existing()` runs before the file copy or manifest append,
  so re-running ingestion on the same file is a true no-op — no duplicate
  copy, no duplicate log line, same `evidence_id` returned.
- **The hash is embedded in the storage path**
  (`raw/<case_id>/<sha256>/<filename>`), not just recorded in the manifest.
  This means the path alone is self-verifying — two different files can never
  collide at the same path, and a corrupted/tampered file at rest would be
  immediately detectable by re-hashing and comparing to its own path.
- **Local storage for the core build, Blob storage deferred — a deliberate
  reading of the guide's own instruction.** Phase 4 says "create a small
  storage account only if Blob is enabled... fall back to local storage for
  the core build." `infra/main.bicep` already defines and validates
  (`what-if`) the storage account from Phase 2, but it is intentionally not
  deployed: the ingestion pipeline runs entirely against local disk under
  `results/ingestion/`. This keeps Phase 4 at zero additional cost while still
  proving the exact same manifest/hash/immutability guarantees the guide
  asks for. Deploying the real Blob account later would change only
  `storage_uri`'s scheme (`local://` → `azure://`) and which provider
  implementation writes it — not the pipeline's logic or its tests.

## Consequences
- Adding a genuinely new binary format later (e.g. a different image codec)
  requires adding one signature to `validators.py`'s table by hand, rather
  than getting it for free from a general-purpose library — an accepted
  tradeoff for staying dependency-free.
- `tests/unit/test_ingestion.py` can run fully offline and in CI with zero
  Azure credentials, since nothing here depends on a real Storage account
  existing.
- If/when Blob storage is deployed, `app/providers/azure/` gains a real
  implementation behind the same `pipeline.py` call sites — the manifest
  schema and idempotency guarantees don't change.

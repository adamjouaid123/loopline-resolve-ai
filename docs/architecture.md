# Architecture

## Overview

```mermaid
flowchart TB
  UI[Streamlit UI] --> API[FastAPI]
  API --> ING[Ingestion: validate, hash, provenance]
  ING --> ANA[Document, vision, text, speech analysis]
  ANA --> RET[Chunking, embeddings, hybrid retrieval]
  RET --> AG[Specialized agents + typed tools]
  AG --> AP[Human approval]
  SAFE[Safety: PII, moderation, Prompt Shields] -.-> AG
  EVAL[Evaluation + regression gates] -.-> AG
  OBS[Tracing, latency, token and error telemetry] -.-> AG
  ANA --> AZ[Azure providers]
  ANA --> LOCAL[Local providers]
  ANA --> MOCK[Mock providers]
```

Every provider (Azure, local, mock) implements the same protocol defined in
`app/providers/protocols.py`, so the application layer above it never branches
on which provider is active — only `app/core/config.py`'s `app_provider_mode`
setting changes what gets constructed underneath.

## Layers

| Layer | Responsibility | Code |
| --- | --- | --- |
| Streamlit UI | Portfolio demo interface | `ui/streamlit_app.py` |
| FastAPI | API contracts, validation, orchestration endpoints | `app/api/` |
| Domain layer | Claims, evidence, resolutions, approvals | `app/domain/` |
| Provider layer | Azure, local, or mock service implementations | `app/providers/` |
| Ingestion pipeline | Validation, hashing, provenance, storage | `app/ingestion/` |
| Extraction pipeline | Field normalization, confidence bands | `app/extraction/` |
| Retrieval layer | Chunking, embeddings, indexing, hybrid search | `app/retrieval/` |
| Agent layer | Specialized agents, tool routing, state machine | `app/agents/` |
| Safety layer | PII, moderation, injection checks, approval constraints | `app/safety/` |
| Evaluation layer | Offline tests, AI-assisted evaluation, regression gates | `app/evaluation/` |

## Key design rules

- Raw customer evidence is immutable.
- Generated media is stored separately and watermarked.
- Extracted facts preserve source references.
- The LLM never directly writes to business records.
- Tools return typed JSON.
- Financial and safety actions require human approval.
- All providers share stable Python interfaces; local and mock modes produce
  the same application schemas as Azure mode.
- The application never exposes hidden chain-of-thought; it returns short
  evidence-based reasons.

## Evidence ingestion and immutability

Every piece of customer evidence (a receipt, a photo, a voice note) passes
through `app/ingestion/` before anything else in the system touches it:

1. **`validators.py`** rejects the file if it's oversized, empty, has an
   unrecognized extension, starts with an executable signature (`MZ`, `ELF`,
   a shebang), or its content doesn't match its claimed extension — checked
   by real magic bytes, not the extension alone.
2. **`hashing.py`** computes a streamed SHA-256 fingerprint of the exact
   bytes, so any change at all is detectable and the file never needs to be
   loaded fully into memory.
3. **`manifest.py`** looks up whether this `(case_id, sha256)` pair has
   already been recorded. If yes, ingestion is a no-op that returns the
   existing `evidence_id` — this is what makes re-running ingestion, or a
   duplicate upload from a flaky client, safe. If no, a permanent ID
   (`ev-<case>-<sequence>`) is minted and an entry is **appended** to
   `results/ingestion/manifest.jsonl` — an append-only log; past lines are
   never rewritten.
4. **`pipeline.py`** copies (never moves) the original into
   `results/ingestion/raw/<case_id>/<sha256>/<original_filename>` — the hash
   is embedded in the storage path itself, so the path alone proves which
   exact bytes live there, and nothing in later phases can silently
   overwrite it.

This is the concrete implementation of "raw customer evidence is immutable"
and "extracted facts preserve source references" from the design rules above:
every fact any later phase (extraction, vision, RAG) produces can point back
to an `evidence_id` whose bytes are hash-verified and permanently stored.
See `docs/adr/004-ingestion-design.md` for the reasoning behind specific
choices (magic-byte validation instead of a system library, JSONL over a
rewritten JSON file, local storage instead of deploying Blob yet).

## Information extraction

`app/extraction/pipeline.py` calls one of two providers behind the same
`analyze(path, operation) -> dict` shape (`app/providers/azure/documents.py`
using real Document Intelligence prebuilt models, or
`app/providers/mock/documents.py` returning the dataset's own ground truth),
normalizes either shape into a flat `{field: {value, confidence, source}}`
structure, applies the confidence-band policy, and overrides status to
`"conflict"` when a field disagrees with the claim's own form data. Real
example, `documents/C001_receipt.pdf` against the live Document Intelligence
resource (`prebuilt-receipt`), reconciled against the claim form's
`serial_number: "NPX1-A101"`:

```json
{
  "serial_number": {
    "value": "NPX1-A101",
    "confidence": 0.99,
    "source": {},
    "status": "accepted"
  },
  "total": {
    "value": 429.0,
    "confidence": 0.984,
    "source": {
      "page": 1,
      "polygon": [2.0712, 5.0086, 2.694, 5.0098, 2.6938, 5.1299, 2.071, 5.1288]
    },
    "status": "accepted"
  }
}
```

`total` shows a real bounding-box polygon from Document Intelligence's
prebuilt-receipt model; `serial_number` comes from a regex anchored to the
document's own `Serial` label rather than Document Intelligence's own field
set (LoopLine's serial number isn't a standard receipt field). A UI
screenshot of this same extraction with confidence and source location
rendered visually is deferred to Phase 14, once the Streamlit UI actually
displays it — this JSON is the Phase 5 equivalent, straight from a real call
against the deployed F0 resource.

See `docs/adr/005-document-intelligence-vs-content-understanding.md` for why
extraction is built on deterministic Document Intelligence rather than
Content Understanding.

## Azure footprint (as of Phase 2)

One resource group, `rg-adam.jouaid123-8353` (Sweden Central), holds
everything this project provisions:

| Resource | Name | Status |
| --- | --- | --- |
| Foundry account | `adamjouaid123-2390-resource` | Created |
| Foundry project | `adamjouaid123-2390` | Created |
| Chat/multimodal deployment | `gpt-5-mini` (GlobalStandard) | Deployed |
| Embedding deployment | `text-embedding-3-large` (Standard) | Deployed |
| Azure AI Search | `loopline-search-adamj` (Free) | Created |
| Storage account | `looplineresolvedatadev` | Templated in `infra/main.bicep`; core build uses local storage instead (see ADR 004) |
| Document Intelligence, Language, Content Safety, Translator | — | F0 confirmed available, not yet created (deferred to their phases) |

See `docs/adr/002-service-selection.md` for the reasoning behind each choice,
and `docs/cost-and-cleanup.md` for the spending ceiling and cleanup plan.

## Infrastructure as code

`infra/main.bicep` documents the storage account and references the
already-existing Search service via an `existing` resource block, so
`az deployment group what-if` proves the template matches reality before
anything is deployed for real. The Foundry account/project and Search service
were created via portal/CLI during Phase 0 exploration, before the template
existed; going forward, new stable resources are added to the template first.

## What a production version would add (not built here)

Per ADR 002, the following are deliberately out of scope for this capstone,
but are the answer to "what would you change for production":

- Private endpoints for Storage, Search, and Cognitive Services
- VNET-integrated Container Apps instead of local/consumption hosting
- Azure Front Door or API Management in front of the FastAPI service
- Customer-managed keys for encryption at rest

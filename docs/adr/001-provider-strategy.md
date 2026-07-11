# ADR 001: Provider strategy for Phase 0

## Status
Accepted — 2026-07-11

## Context
Free Trial subscription, single tenant, region Sweden Central. Resource group
rg-adam.jouaid123-8353, Foundry project adamjouaid123-2390. Reconnaissance in
Phase 0 found nearly every capability available, which is unusual for a trial
account and shouldn't be assumed to last (credit is time- and dollar-limited).

## Decision
- Chat/multimodal model: gpt-5-mini (GlobalStandard, Global scope). Confirmed
  vision input support. 1M TPM shared pool, 56K already allocated elsewhere —
  ample headroom for a demo workload.
- Embedding model: text-embedding-3-large (Standard, Sweden Central). 350K TPM
  pool, 120K allocated. text-embedding-3-small is not offered in this region at
  all, which is why it's excluded rather than preferred.
- Search, Document Intelligence, Language, Content Safety, Translator: all use
  their real Azure F0 free tier — no mock needed for these.
- Content Understanding stays mocked initially; only exercised on 1-2 files
  when Phase 5/6 explicitly calls for it, per the cost-control checklist.
- Speech (STT/TTS) uses the local provider during development. Foundry hosts
  whisper/tts/tts-hd directly, but at 3 requests/minute that quota is too tight
  to iterate against; it may be used once for final demo polish.
- Image generation (Dalle/GPT-image-2) and video generation (Sora 2) are both
  available, but FEATURE_IMAGE_GENERATION and FEATURE_VIDEO_GENERATION stay
  false by default. Sora in particular is a preview capability and the
  single highest-cost risk in the project.

## Consequences
- Nearly the whole pipeline can run against real Azure services rather than
  mocks, which is good for the AI-103 proof-of-work, but every phase must
  still check quota/cost before turning a feature flag on.
- If trial credit runs out or expires before the capstone is done, the mock
  and local providers behind the same protocol interfaces let the app keep
  running without code changes.

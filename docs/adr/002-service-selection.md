# ADR 002: Azure service selection and resource layout

## Status
Accepted — 2026-07-11

## Context
Phase 2 translates the project's requirements into minimal, cost-controlled
Azure infrastructure on a single Free Trial subscription with a $100 personal
spending ceiling (see `docs/cost-and-cleanup.md` and ADR 001). All resources
live in one resource group, `rg-adam.jouaid123-8353`, in Sweden Central.

Sweden Central was chosen over the fictional business scenario's implied
region (France) purely for practical reasons: it's where the existing Foundry
account/project already lived when Phase 0 reconnaissance was done, and it was
confirmed to have full quota for every capability the project needs (chat,
multimodal, embeddings, image and video generation, plus F0 tiers of Search,
Document Intelligence, Language, Content Safety, and Translator). Region
realism for the fictional scenario is a cosmetic concern; real quota
availability is not — the latter wins.

## Decision
- **One resource group** (`rg-adam.jouaid123-8353`) holds every resource this
  project creates, per the hard cost rule of a single resource group for the
  whole capstone.
- **Foundry project** `adamjouaid123-2390` hosts two model deployments:
  - `gpt-5-mini` (GlobalStandard) — used for both `FOUNDRY_CHAT_MODEL` and
    `FOUNDRY_MULTIMODAL_MODEL`. It's one physical deployment serving two
    logical roles; the env vars are kept separate (rather than a single var)
    so a future swap to a different chat-only or vision-only model doesn't
    require touching unrelated code.
  - `text-embedding-3-large` (Standard, Sweden Central) — chosen over
    `text-embedding-ada-002` for better retrieval quality; the 3072-dim
    vectors are a non-issue at this dataset's scale (~8 knowledge documents)
    even against Azure AI Search's 50MB Free-tier cap. `text-embedding-3-small`
    was not available in this region at all, so it was never a real option.
- **Azure AI Search Free** (`loopline-search-adamj`) is created now rather than
  deferred, since it's a one-per-subscription resource with no cost
  implication. Semantic ranking and knowledge retrieval both showed as
  available on this Free instance — bonus capabilities beyond the documented
  baseline, usable in Phase 9 if useful, but never assumed or required.
- **Storage account** (`looplineresolvedatadev`, private container
  `claim-evidence`, `allowBlobPublicAccess: false`) is defined in
  `infra/main.bicep` and validated with `az deployment group what-if`, but is
  **deliberately not deployed yet**. The guide places real storage-account
  creation in Phase 4 (document ingestion), so the template exists and is
  proven correct now, without provisioning anything before it's needed.
- **Document Intelligence, Language, Content Safety, Translator**: confirmed
  F0-available in Sweden Central during Phase 0, but none are created yet —
  each is deferred to the phase that actually consumes it (5, 7, 7, 11
  respectively), per the "provision only when the phase begins" rule.
- **No private endpoints, no VNET integration, no Kubernetes, no managed
  compute, no provisioned throughput.** At this project's scale (a handful of
  F0/consumption resources, a synthetic ~76-file dataset, a single developer),
  network isolation and dedicated compute add cost and operational surface
  with no corresponding benefit. A production deployment of this system
  serving real customer data would reasonably add: private endpoints for
  Storage/Search/Cognitive Services, VNET-integrated Container Apps, Azure
  Front Door or APIM in front of the API, and customer-managed keys — none of
  that is built here, but the boundary is intentional and documented rather
  than accidental.
- **Bicep + what-if over ad hoc portal/CLI changes going forward.** The
  Foundry account/project and Search service were created via portal/CLI
  during Phase 0 exploration (before the IaC template existed), but from here
  on, new stable resources (starting with the storage account in Phase 4) are
  defined in `infra/main.bicep` first and validated with `what-if` before any
  real deployment, so the template stays the source of truth rather than
  drifting from what's actually running.

## Consequences
- Nearly the entire pipeline can run against real Azure services rather than
  mocks or local fallbacks, which is a stronger AI-103 proof-of-work than the
  guide's baseline assumption of a more constrained trial subscription.
- The region choice (Sweden Central vs. the scenario's implied France) is a
  deliberate, documented tradeoff, not an inconsistency to fix later.
- Because `infra/main.bicep` already includes the storage account and a
  reference to the existing Search service, Phase 4 only needs one command
  (`az deployment group create`) rather than new template authoring.
- The explicitly-rejected production hardening list (private endpoints,
  VNET, Kubernetes) gives a ready answer for the "what would you add for
  production" interview question without having built or paid for any of it.

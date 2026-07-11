# ADR 003: Authentication and credential strategy

## Status
Accepted — 2026-07-11

## Context
Phase 3 needed a single, consistent way for the application to authenticate
to Azure that works identically whether it's running on a developer's
machine today or on a managed identity later, without hardcoding which one.
Azure AI Search's Free instance still has `disableLocalAuth: false`, meaning
API-key auth would technically work — but the guide's design explicitly
prefers Entra ID for granular access, and this project follows that.

## Decision
- **`DefaultAzureCredential` everywhere, no API keys.** `app/core/credentials.py`
  exposes cached (`@lru_cache`) factory functions — `get_credential()` and
  `get_project_client()` — rather than module-level client construction, so
  importing the module never attempts network/auth calls; only an actual
  call site does. Every provider that needs Azure auth imports from here
  instead of constructing its own credential.
- **Local development and "runtime" are currently the same identity.** There
  is no deployed service yet (Container Apps is an optional stretch goal), so
  the developer's own Entra user, authenticated via `az login`, is also the
  identity the app runs under locally. Rather than skip RBAC design until a
  real managed identity exists, the exact roles that identity would need
  (`Foundry User` on the project, `Search Index Data Reader` +
  `Search Index Data Contributor` on the search service) were assigned
  directly to the developer's user object at Phase 3, scoped narrowly — not
  relying on the Owner role already held at the subscription level. See
  `docs/rbac-matrix.md`.
- **Storage roles are deferred, not stubbed with a guess.** No storage account
  exists yet (Phase 4), so no Storage role assignment was made and
  `app/core/config.py` has no storage field yet — adding either now would be
  speculative. `scripts/check_access.py` reports this row as a deliberate
  `skip`, distinct from a `fail`.
- **`scripts/check_access.py` checks are isolated per service and
  three-valued (`ok` / `fail` / `skip`)**, not a single pass/fail. Foundry is
  verified by actually acquiring a scoped access token
  (`https://ai.azure.com/.default`); Search is verified by a real
  `SearchIndexClient.list_indexes()` call. Both exercise the actual RBAC
  assignments, not just whether the CLI command that created them succeeded.
- **CI stays credential-free.** GitHub Actions runs tests with
  `APP_PROVIDER_MODE` left at its default (`mock`) and no Azure secrets
  configured. Setting up a federated (OIDC) service principal for CI so it
  could exercise real Azure calls remains a stretch goal (see the guide's
  Section 24), not a Phase 3 requirement.

## Consequences
- If/when a real runtime identity is created (a Container App's
  system-assigned managed identity, most likely), it receives the identical
  role assignments already proven to work for the developer identity — no
  redesign, just a different principal ID at the same scopes.
- No secret ever needs to exist in `.env` for Foundry or Search; only F0
  services that genuinely require key-based auth (if any turn out to) would
  get a documented, git-ignored key as a fallback, per the guide's
  "F0 service fallback: API key in local .env, never committed" rule.
- Because `get_project_client()` fails fast with a clear `RuntimeError` when
  `FOUNDRY_PROJECT_ENDPOINT` is unset, misconfiguration surfaces immediately
  at the call site rather than as an opaque SDK/auth error later.

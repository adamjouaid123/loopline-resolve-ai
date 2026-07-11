# Infrastructure

Bicep templates for the supporting Azure resources described in the capstone guide, Phase 2 (Azure resource planning). Not deployed yet.

```bash
az deployment group what-if \
  --resource-group rg-loopline-resolve-dev \
  --template-file infra/main.bicep \
  --parameters infra/parameters.dev.json
```

One resource group, one Foundry project, at most two model deployments, and Search Free where available. See `docs/adr/002-service-selection.md` (once written) for the rationale.

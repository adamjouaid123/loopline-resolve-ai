// Placeholder — resource definitions land in Phase 2 (Azure resource planning).
// Target: one resource group, one Foundry project, at most two model deployments,
// Search Free where available. No provisioned throughput, no Kubernetes, no private endpoints.

targetScope = 'resourceGroup'

param location string = resourceGroup().location

targetScope = 'resourceGroup'

param location string = resourceGroup().location
param projectName string = 'loopline-resolve'
param searchServiceName string = 'loopline-search-adamj'
param storageAccountName string = 'looplineresolvedatadev'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags : {
    project : projectName
  }
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource evidenceContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'claim-evidence'
  properties: {
    publicAccess: 'None'
  }
}

resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' existing = {
  name: searchServiceName
}

output storageAccountName string = storageAccount.name
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'

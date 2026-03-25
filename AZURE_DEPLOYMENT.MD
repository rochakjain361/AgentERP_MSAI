# Azure Deployment Guide for AgentERP

This guide walks you through deploying AgentERP to Azure using Azure Container Apps.

## Prerequisites

1. **Azure CLI** installed and logged in
   ```bash
   az login
   ```

2. **Docker** installed locally

3. **Azure Subscription** with credits

---

## Architecture on Azure

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Resource Group                      │
│                      (agenterp-rg)                          │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Container App   │  │ Container App   │  │ Cosmos DB   │ │
│  │ (Frontend)      │←→│ (Backend)       │←→│ (MongoDB)   │ │
│  │ Port 80         │  │ Port 8001       │  │             │ │
│  └────────┬────────┘  └────────┬────────┘  └─────────────┘ │
│           │                    │                            │
│           │                    ↓                            │
│           │           ┌─────────────────┐                   │
│           │           │ Azure OpenAI    │                   │
│           │           │ (GPT-4o)        │                   │
│           │           └─────────────────┘                   │
│           │                    │                            │
│           │                    ↓                            │
│           │           ┌─────────────────┐                   │
│           │           │ ERPNext         │                   │
│           │           │ (External)      │                   │
│           │           └─────────────────┘                   │
│           │                                                  │
│  ┌────────▼────────────────────────────────────────────────┐│
│  │              Azure Container Registry                    ││
│  │                   (agenterpcr)                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Create Azure Resources

```bash
# Set variables
RESOURCE_GROUP="agenterp-rg"
LOCATION="eastus"
ACR_NAME="agenterpcr"  # Must be globally unique
COSMOSDB_ACCOUNT="agenterp-cosmos"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"
```

---

## Step 2: Create Azure Cosmos DB (MongoDB API)

```bash
# Create Cosmos DB account with MongoDB API
az cosmosdb create \
  --name $COSMOSDB_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --kind MongoDB \
  --server-version 4.2 \
  --default-consistency-level Session

# Create database
az cosmosdb mongodb database create \
  --account-name $COSMOSDB_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --name agenterp

# Get connection string
COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \
  --name $COSMOSDB_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv)

echo "Cosmos DB Connection String saved"
```

---

## Step 3: Build and Push Docker Images

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and push backend
cd backend
docker build -t $ACR_LOGIN_SERVER/agenterp-backend:latest .
docker push $ACR_LOGIN_SERVER/agenterp-backend:latest

# Build and push frontend (with backend URL)
cd ../frontend
docker build \
  --build-arg REACT_APP_BACKEND_URL=https://agenterp-backend.azurecontainerapps.io \
  -t $ACR_LOGIN_SERVER/agenterp-frontend:latest .
docker push $ACR_LOGIN_SERVER/agenterp-frontend:latest
```

---

## Step 4: Create Container Apps Environment

```bash
# Install Container Apps extension
az extension add --name containerapp --upgrade

# Create Container Apps environment
az containerapp env create \
  --name agenterp-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

---

## Step 5: Deploy Backend Container App

```bash
# Deploy backend
az containerapp create \
  --name agenterp-backend \
  --resource-group $RESOURCE_GROUP \
  --environment agenterp-env \
  --image $ACR_LOGIN_SERVER/agenterp-backend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8001 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    "MONGO_URL=$COSMOS_CONNECTION_STRING" \
    "DB_NAME=agenterp" \
    "CORS_ORIGINS=*" \
    "ERP_URL=https://your-erpnext.com" \
    "ERP_API_KEY=your_key" \
    "ERP_API_SECRET=your_secret" \
    "ERP_MOCK_MODE=false" \
    "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com" \
    "AZURE_OPENAI_API_KEY=your_openai_key" \
    "AZURE_OPENAI_MODEL=gpt-4o" \
    "AZURE_OPENAI_API_VERSION=2024-10-21"

# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name agenterp-backend \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo "Backend URL: https://$BACKEND_URL"
```

---

## Step 6: Deploy Frontend Container App

```bash
# Rebuild frontend with correct backend URL
cd frontend
docker build \
  --build-arg REACT_APP_BACKEND_URL=https://$BACKEND_URL \
  -t $ACR_LOGIN_SERVER/agenterp-frontend:latest .
docker push $ACR_LOGIN_SERVER/agenterp-frontend:latest

# Deploy frontend
az containerapp create \
  --name agenterp-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment agenterp-env \
  --image $ACR_LOGIN_SERVER/agenterp-frontend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.25 \
  --memory 0.5Gi

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name agenterp-frontend \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo "=========================================="
echo "Deployment Complete!"
echo "Frontend: https://$FRONTEND_URL"
echo "Backend:  https://$BACKEND_URL"
echo "=========================================="
```

---

## Step 7: Update CORS (if needed)

```bash
# Update backend CORS to allow frontend domain
az containerapp update \
  --name agenterp-backend \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "CORS_ORIGINS=https://$FRONTEND_URL"
```

---

## Quick Deploy Script

Save this as `deploy-azure.sh`:

```bash
#!/bin/bash
set -e

# Configuration
RESOURCE_GROUP="agenterp-rg"
LOCATION="eastus"
ACR_NAME="agenterpcr$(date +%s)"  # Unique name
COSMOSDB_ACCOUNT="agenterp-cosmos"

# Your secrets (replace these!)
ERP_URL="https://your-erpnext.com"
ERP_API_KEY="your_key"
ERP_API_SECRET="your_secret"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
AZURE_OPENAI_API_KEY="your_openai_key"

echo "🚀 Starting Azure deployment..."

# Create resources
az group create --name $RESOURCE_GROUP --location $LOCATION
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
az acr login --name $ACR_NAME

# Get ACR details
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Build and push images
docker build -t $ACR_LOGIN_SERVER/agenterp-backend:latest ./backend
docker push $ACR_LOGIN_SERVER/agenterp-backend:latest

docker build --build-arg REACT_APP_BACKEND_URL=https://agenterp-backend.azurecontainerapps.io \
  -t $ACR_LOGIN_SERVER/agenterp-frontend:latest ./frontend
docker push $ACR_LOGIN_SERVER/agenterp-frontend:latest

# Create Cosmos DB
az cosmosdb create --name $COSMOSDB_ACCOUNT --resource-group $RESOURCE_GROUP --kind MongoDB --server-version 4.2
az cosmosdb mongodb database create --account-name $COSMOSDB_ACCOUNT --resource-group $RESOURCE_GROUP --name agenterp
COSMOS_CONNECTION_STRING=$(az cosmosdb keys list --name $COSMOSDB_ACCOUNT --resource-group $RESOURCE_GROUP --type connection-strings --query "connectionStrings[0].connectionString" -o tsv)

# Create Container Apps
az extension add --name containerapp --upgrade
az containerapp env create --name agenterp-env --resource-group $RESOURCE_GROUP --location $LOCATION

# Deploy backend
az containerapp create \
  --name agenterp-backend \
  --resource-group $RESOURCE_GROUP \
  --environment agenterp-env \
  --image $ACR_LOGIN_SERVER/agenterp-backend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8001 \
  --ingress external \
  --env-vars \
    "MONGO_URL=$COSMOS_CONNECTION_STRING" \
    "DB_NAME=agenterp" \
    "CORS_ORIGINS=*" \
    "ERP_URL=$ERP_URL" \
    "ERP_API_KEY=$ERP_API_KEY" \
    "ERP_API_SECRET=$ERP_API_SECRET" \
    "AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT" \
    "AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY" \
    "AZURE_OPENAI_MODEL=gpt-4o"

BACKEND_FQDN=$(az containerapp show --name agenterp-backend --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv)

# Rebuild frontend with correct URL
docker build --build-arg REACT_APP_BACKEND_URL=https://$BACKEND_FQDN \
  -t $ACR_LOGIN_SERVER/agenterp-frontend:latest ./frontend
docker push $ACR_LOGIN_SERVER/agenterp-frontend:latest

# Deploy frontend
az containerapp create \
  --name agenterp-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment agenterp-env \
  --image $ACR_LOGIN_SERVER/agenterp-frontend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 80 \
  --ingress external

FRONTEND_FQDN=$(az containerapp show --name agenterp-frontend --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo "Frontend: https://$FRONTEND_FQDN"
echo "Backend:  https://$BACKEND_FQDN"
echo "=========================================="
```

---

## Estimated Costs (Azure)

| Service | Tier | Estimated Cost/Month |
|---------|------|---------------------|
| Container Apps (Backend) | 0.5 vCPU, 1GB | ~$15-30 |
| Container Apps (Frontend) | 0.25 vCPU, 0.5GB | ~$8-15 |
| Cosmos DB (MongoDB) | Serverless | ~$5-20 (depends on usage) |
| Container Registry | Basic | ~$5 |
| Azure OpenAI | GPT-4o | Pay per token |
| **Total** | | **~$35-70/month** |

---

## Troubleshooting

### View Container Logs
```bash
az containerapp logs show \
  --name agenterp-backend \
  --resource-group $RESOURCE_GROUP \
  --follow
```

### Restart Container
```bash
az containerapp revision restart \
  --name agenterp-backend \
  --resource-group $RESOURCE_GROUP
```

### Update Environment Variables
```bash
az containerapp update \
  --name agenterp-backend \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "NEW_VAR=value"
```

---

## Clean Up Resources

```bash
# Delete everything
az group delete --name $RESOURCE_GROUP --yes --no-wait
```
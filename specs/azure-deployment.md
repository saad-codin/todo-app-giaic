# Azure Deployment Guide (Free Tier / Container Apps)

This guide outlines how to deploy the Todo Chatbot application to Azure using **Azure Container Apps (ACA)**. ACA is modern, scalable, and has a generous free allowance (first 180k vCPU-seconds and 360k GiB-seconds free per month).

## Prerequisites

1.  **Azure Account**: Active subscription (Free Account recommended).
2.  **Azure CLI**: Installed and logged in (`az login`).
3.  **Docker**: Installed and running locally.

---

## 1. Set Up Environment Variables

First, define your project names (replace `<unique-name>` with something unique like your initials + date):

```bash
# Set variables
RESOURCE_GROUP="todo-chatbot-rg"
LOCATION="eastus"
REGISTRY_NAME="todochatbotregistry<unique-name>"
ENV_NAME="todo-app-env"
BACKEND_IMAGE_NAME="todo-backend"
FRONTEND_IMAGE_NAME="todo-frontend"
```

## 2. Create Infrastructure

Run these commands to provision the base Azure resources:

```bash
# 1. Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Azure Container Registry (Basic tier is cheap/reliable)
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic

# 3. Log in to ACR
az acr login --name $REGISTRY_NAME

# 4. Create Container Apps Environment
az containerapp env create --name $ENV_NAME --resource-group $RESOURCE_GROUP --location $LOCATION
```

## 3. Build and Push Docker Images

### Backend
```bash
# Build backend
cd backend
docker build -t $REGISTRY_NAME.azurecr.io/$BACKEND_IMAGE_NAME:latest .

# Push to Azure
docker push $REGISTRY_NAME.azurecr.io/$BACKEND_IMAGE_NAME:latest
cd ..
```

### Frontend
**Note**: Next.js requires the API URL at build time. Replace the URL with your expected backend URL.
```bash
# Build frontend
cd frontend
docker build --build-arg NEXT_PUBLIC_API_URL=https://todo-backend.<your-app-suffix>.azurecontainerapps.io -t $REGISTRY_NAME.azurecr.io/$FRONTEND_IMAGE_NAME:latest .

# Push to Azure
docker push $REGISTRY_NAME.azurecr.io/$FRONTEND_IMAGE_NAME:latest
cd ..
```

## 4. Deploy Backend Container App

Deploy the backend first to get its URL:

```bash
az containerapp create \
  --name todo-backend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $REGISTRY_NAME.azurecr.io/$BACKEND_IMAGE_NAME:latest \
  --target-port 8000 \
  --ingress external \
  --query properties.configuration.ingress.fqdn \
  --env-vars \
    DATABASE_URL="<your-neon-db-url>" \
    SECRET_KEY="<your-secret-key>" \
    OPENAI_API_KEY="<your-openai-key>" \
    FRONTEND_URL="https://todo-frontend.<your-app-suffix>.azurecontainerapps.io"
```

## 5. Deploy Frontend Container App

```bash
az containerapp create \
  --name todo-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $REGISTRY_NAME.azurecr.io/$FRONTEND_IMAGE_NAME:latest \
  --target-port 3000 \
  --ingress external \
  --env-vars \
    NEXT_PUBLIC_API_URL="https://todo-backend.<suffix>.azurecontainerapps.io" \
    BETTER_AUTH_SECRET="<your-auth-secret>" \
    BETTER_AUTH_URL="https://todo-frontend.<suffix>.azurecontainerapps.io" \
    NEXT_PUBLIC_CHATKIT_DOMAIN_KEY="<your-domain-key>"
```

---

## Tips for the Free Tier

1.  **Container Apps Free Grant**: Azure provides a monthly free grant for Container Apps. As long as your usage stays within it, you won't be charged for the compute.
2.  **ACR Storage**: Azure Container Registry has a small daily storage cost (~$0.16/day). If you want 100% free, you can use **Docker Hub** as a public registry instead.
3.  **Scaling**: Set `--min-replicas 0` if you want the app to "scale to zero" when not in use (saves money but causes "cold starts").
    *   Command: `az containerapp update --name todo-backend --resource-group $RESOURCE_GROUP --min-replicas 0`

## Managed Identity (Security)

Instead of passing the ACR password, enable a system-assigned managed identity for the Container Apps and give it `AcrPull` permission:

```bash
# Get the principal ID of the app's identity
PRINCIPAL_ID=$(az containerapp identity assign --name todo-backend --resource-group $RESOURCE_GROUP --query principalId -o tsv)

# Assign AcrPull role
ACR_ID=$(az acr show --name $REGISTRY_NAME --query id -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --scope $ACR_ID --role AcrPull
```

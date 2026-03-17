# Quickstart: Event-Driven Todo/Chatbot

**Feature**: 006-dapr-event-driven | **Date**: 2026-02-09

## Prerequisites

### Required Tools

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | 24+ | [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop) |
| kubectl | 1.28+ | `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"` |
| Helm | 3.12+ | `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \| bash` |
| Minikube | 1.32+ | `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64` |
| Dapr CLI | 1.14+ | `curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh \| bash` |
| rpk (optional) | latest | `curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip` |

### Required Accounts (Cloud Only)

- Azure account with AKS free tier
- Redpanda Cloud account (free serverless tier)
- Existing: Neon PostgreSQL, OpenAI API key

## Part 1: Local Development (Minikube)

### Step 1: Start Minikube

```bash
minikube start --cpus=4 --memory=4096 --driver=docker
minikube addons enable ingress
```

### Step 2: Install Dapr on Cluster

```bash
# Initialize Dapr on Kubernetes
dapr init -k --runtime-version 1.14.4

# Verify Dapr is running
dapr status -k
# Expected: dapr-operator, dapr-sidecar-injector, dapr-placement, dapr-sentry all Running

kubectl get pods -n dapr-system
```

### Step 3: Build All Images

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Build all images
docker build -t todo-backend:latest ./backend/
docker build -t todo-frontend:latest ./frontend/ \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000
docker build -t reminder-service:latest ./services/reminder/
docker build -t recurring-service:latest ./services/recurring/
docker build -t sync-service:latest ./services/sync/
```

### Step 4: Configure Local Values

```bash
cp helm/todo-chatbot/values-local.yaml.example helm/todo-chatbot/values-local.yaml
```

Edit `values-local.yaml` with your secrets:
```yaml
backend:
  secrets:
    DATABASE_URL: "postgresql://user:pass@host/db?sslmode=require"
    OPENAI_API_KEY: "sk-..."
    JWT_SECRET: "your-jwt-secret"
    BETTER_AUTH_SECRET: "your-auth-secret"

redpanda:
  enabled: true  # Deploy local Redpanda instance
  cloud:
    enabled: false
```

### Step 5: Deploy Everything

```bash
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f helm/todo-chatbot/values-local.yaml \
  -n todo-chatbot \
  --create-namespace
```

### Step 6: Verify Deployment

```bash
# Check all pods are Running (including Dapr sidecars)
kubectl get pods -n todo-chatbot

# Expected output:
# NAME                          READY   STATUS    RESTARTS
# backend-xxx                   2/2     Running   0        (app + dapr sidecar)
# frontend-xxx                  1/1     Running   0        (no sidecar needed)
# reminder-xxx                  2/2     Running   0
# recurring-xxx                 2/2     Running   0
# sync-xxx                      2/2     Running   0
# redpanda-0                    1/1     Running   0

# Check Dapr components
dapr components -k -n todo-chatbot
# Expected: taskpubsub (pubsub.kafka), statestore (state.postgresql)

# Check subscriptions
kubectl get subscriptions -n todo-chatbot
```

### Step 7: Access the Application

```bash
# Open frontend in browser
minikube service frontend-svc -n todo-chatbot

# Or port-forward individual services
kubectl port-forward svc/backend-svc 8000:8000 -n todo-chatbot
kubectl port-forward svc/frontend-svc 3000:3000 -n todo-chatbot
```

### Step 8: Verify Event Flow

```bash
# Create a task via API
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <your-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"description": "Test task", "priority": "high", "dueDate": "2026-02-15"}'

# Check reminder service received the event
kubectl logs -l app=reminder-service -n todo-chatbot -c reminder --tail=20

# Check Redpanda topics
kubectl exec -it redpanda-0 -n todo-chatbot -- rpk topic list
kubectl exec -it redpanda-0 -n todo-chatbot -- rpk topic consume task-events --num 5
```

## Part 2: Cloud Deployment (AKS)

### Step 1: Create AKS Cluster

```bash
# Create resource group (if not exists)
az group create --name todo-app-rg --location eastus

# Create AKS cluster (free tier)
az aks create \
  --resource-group todo-app-rg \
  --name todo-aks \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --generate-ssh-keys \
  --tier free

# Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-aks

# Attach existing ACR
az aks update -n todo-aks -g todo-app-rg --attach-acr todoappcr2025
```

### Step 2: Install Dapr on AKS

```bash
dapr init -k --runtime-version 1.14.4
dapr status -k
```

### Step 3: Set Up Redpanda Cloud

1. Go to [cloud.redpanda.com](https://cloud.redpanda.com) and create a Serverless cluster
2. Create SASL/SCRAM credentials
3. Note the bootstrap server URL

```bash
# Create Kubernetes secret for Redpanda Cloud credentials
kubectl create namespace todo-chatbot
kubectl create secret generic redpanda-secrets \
  -n todo-chatbot \
  --from-literal=username="<redpanda-username>" \
  --from-literal=password="<redpanda-password>"
```

### Step 4: Build and Push Images

```bash
# Login to ACR
az acr login --name todoappcr2025

# Build and push all images
for svc in backend frontend; do
  docker build -t todoappcr2025.azurecr.io/todo-${svc}:latest ./${svc}/
  docker push todoappcr2025.azurecr.io/todo-${svc}:latest
done

for svc in reminder recurring sync; do
  docker build -t todoappcr2025.azurecr.io/${svc}-service:latest ./services/${svc}/
  docker push todoappcr2025.azurecr.io/${svc}-service:latest
done
```

### Step 5: Deploy to AKS

```bash
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f helm/todo-chatbot/values-cloud.yaml \
  -n todo-chatbot \
  --create-namespace
```

### Step 6: Verify Cloud Deployment

```bash
kubectl get pods -n todo-chatbot
kubectl get svc -n todo-chatbot
dapr status -k
dapr components -k -n todo-chatbot

# Check external IP/ingress
kubectl get ingress -n todo-chatbot
```

## Troubleshooting

### Dapr Sidecar Not Starting

```bash
# Check Dapr sidecar injector logs
kubectl logs -l app=dapr-sidecar-injector -n dapr-system

# Ensure namespace has Dapr annotations
kubectl get namespace todo-chatbot -o yaml
```

### Events Not Flowing

```bash
# Check Dapr sidecar logs for a specific pod
kubectl logs <pod-name> -n todo-chatbot -c daprd

# Verify pub/sub component is loaded
dapr components -k -n todo-chatbot | grep taskpubsub

# Check Redpanda is reachable
kubectl exec -it redpanda-0 -n todo-chatbot -- rpk cluster info
```

### WebSocket Connection Failing

```bash
# Check sync service logs
kubectl logs -l app=sync-service -n todo-chatbot -c sync

# Test WebSocket locally
websocat ws://localhost:8003/ws?token=<jwt>
```

### Service Crashes

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-chatbot

# Check resource limits
kubectl top pods -n todo-chatbot
```

## Rollback

```bash
# List Helm releases
helm list -n todo-chatbot

# Rollback to previous release
helm rollback todo-chatbot <revision> -n todo-chatbot

# Verify rollback
kubectl get pods -n todo-chatbot
```

## Cleanup

### Local (Minikube)

```bash
helm uninstall todo-chatbot -n todo-chatbot
kubectl delete namespace todo-chatbot
dapr uninstall -k
minikube stop
```

### Cloud (AKS)

```bash
helm uninstall todo-chatbot -n todo-chatbot
dapr uninstall -k
az aks delete --name todo-aks --resource-group todo-app-rg --yes
```

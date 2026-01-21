# Quickstart: Local Kubernetes Deployment

This guide walks you through deploying the Todo Chatbot to a local Kubernetes cluster.

## Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | Latest | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| Minikube | 1.32+ | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.28+ | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.13+ | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

## Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Verify cluster is running
kubectl cluster-info
```

## Step 2: Build Container Images

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Build backend image
docker build -t todo-backend:latest ./backend

# Verify images are available
docker images | grep todo
```

## Step 3: Configure Secrets

Create a `values-local.yaml` file with your secrets:

```yaml
# helm/todo-chatbot/values-local.yaml
backend:
  secrets:
    DATABASE_URL: "postgresql://user:pass@host/dbname"
    OPENAI_API_KEY: "sk-..."
    JWT_SECRET: "your-jwt-secret"
    BETTER_AUTH_SECRET: "your-auth-secret"

frontend:
  env:
    NEXT_PUBLIC_CHATKIT_DOMAIN_KEY: "your-domain-key"
```

**Important**: Never commit `values-local.yaml` to version control.

## Step 4: Deploy with Helm

```bash
# Create namespace
kubectl create namespace todo-chatbot

# Install the Helm release
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  -f ./helm/todo-chatbot/values-local.yaml

# Check deployment status
kubectl get pods -n todo-chatbot -w
```

Wait until all pods show `Running` status.

## Step 5: Access the Application

```bash
# Option A: Use minikube service (opens browser)
minikube service frontend-svc -n todo-chatbot

# Option B: Port forward (manual)
kubectl port-forward svc/frontend-svc 3000:3000 -n todo-chatbot &
kubectl port-forward svc/backend-svc 8000:8000 -n todo-chatbot &

# Then access: http://localhost:3000
```

## Verification Checklist

- [ ] `kubectl get pods -n todo-chatbot` shows 2 running pods
- [ ] `kubectl get svc -n todo-chatbot` shows frontend-svc and backend-svc
- [ ] Frontend loads in browser at exposed URL
- [ ] Can sign in or create account
- [ ] Can create a task via the chat interface
- [ ] Can list tasks via the chat interface

## Common Commands

```bash
# View logs
kubectl logs -f deployment/frontend -n todo-chatbot
kubectl logs -f deployment/backend -n todo-chatbot

# Restart a deployment
kubectl rollout restart deployment/backend -n todo-chatbot

# Check Helm release
helm list -n todo-chatbot

# Upgrade after changes
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  -f ./helm/todo-chatbot/values-local.yaml

# Uninstall
helm uninstall todo-chatbot -n todo-chatbot
```

## Troubleshooting

### Pods stuck in "Pending" state
```bash
# Check events
kubectl describe pod <pod-name> -n todo-chatbot
```
Usually caused by insufficient resources. Increase Minikube memory/CPU.

### Backend can't connect to database
```bash
# Verify secret is set correctly
kubectl get secret todo-secrets -n todo-chatbot -o yaml
```
Ensure DATABASE_URL is correct and the cluster can reach the Neon database.

### Frontend can't reach backend
```bash
# Test internal connectivity
kubectl exec -it deployment/frontend -n todo-chatbot -- curl http://backend-svc:8000/health
```
Verify services are created and pods are labeled correctly.

### Images not found
```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)
docker images | grep todo
```
Rebuild images after running the eval command.

## Optional: AI DevOps Tools

### kubectl-ai

Natural language interface for Kubernetes operations.

```bash
# Install
pip install kubectl-ai

# Configure (set your OpenAI API key)
export OPENAI_API_KEY="sk-..."

# Example commands
kubectl-ai "show me all pods in todo-chatbot namespace"
kubectl-ai "why is my backend pod not starting?"
kubectl-ai "how much memory is the frontend using?"
kubectl-ai "show me the logs for the last error in backend"
kubectl-ai "what resources are in the todo-chatbot namespace?"
kubectl-ai "describe the backend deployment"
kubectl-ai "check if any pods are in CrashLoopBackOff"
```

### k9s (Terminal UI)

Visual terminal interface for Kubernetes cluster management.

```bash
# Install
brew install derailed/k9s/k9s  # macOS
choco install k9s              # Windows
scoop install k9s              # Windows (Scoop)

# Run
k9s -n todo-chatbot
```

**k9s shortcuts**:
- `:pods` - View pods
- `:svc` - View services
- `:deploy` - View deployments
- `l` - View logs
- `d` - Describe resource
- `/` - Filter
- `ctrl-d` - Delete resource

### Lens (Desktop App)

Full-featured Kubernetes IDE with GUI.

Download from: [k8slens.dev](https://k8slens.dev/)

## Clean Up

```bash
# Remove the deployment
helm uninstall todo-chatbot -n todo-chatbot

# Delete namespace
kubectl delete namespace todo-chatbot

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

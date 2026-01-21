# Todo Chatbot Helm Chart

Kubernetes deployment for the AI-Powered Todo Chatbot application.

## Prerequisites

- Kubernetes 1.28+
- Helm 3.13+
- Docker images built and available:
  - `todo-frontend:latest`
  - `todo-backend:latest`

## Installation

### 1. Configure Secrets

Copy the example values file and fill in your secrets:

```bash
cp values-local.yaml.example values-local.yaml
# Edit values-local.yaml with your actual secrets
```

### 2. Install the Chart

```bash
# Create namespace and install
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --create-namespace \
  -f ./helm/todo-chatbot/values-local.yaml
```

### 3. Access the Application

```bash
# Option A: Use minikube service (opens browser)
minikube service frontend-svc -n todo-chatbot

# Option B: Port forward
kubectl port-forward svc/frontend-svc 3000:3000 -n todo-chatbot
kubectl port-forward svc/backend-svc 8000:8000 -n todo-chatbot
```

## Configuration

### Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Frontend pod replicas | `1` |
| `frontend.image.repository` | Frontend image name | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.service.port` | Frontend service port | `3000` |
| `backend.replicaCount` | Backend pod replicas | `1` |
| `backend.image.repository` | Backend image name | `todo-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.service.port` | Backend service port | `8000` |
| `backend.secrets.DATABASE_URL` | PostgreSQL connection string | `""` |
| `backend.secrets.OPENAI_API_KEY` | OpenAI API key | `""` |
| `backend.secrets.JWT_SECRET` | JWT signing secret | `""` |
| `backend.secrets.BETTER_AUTH_SECRET` | Auth secret | `""` |

### Upgrading

```bash
# Upgrade with new values
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  -f ./helm/todo-chatbot/values-local.yaml

# Upgrade with specific value override
helm upgrade todo-chatbot ./helm/todo-chatbot \
  --namespace todo-chatbot \
  --set frontend.replicaCount=2
```

### Rollback

```bash
# View history
helm history todo-chatbot -n todo-chatbot

# Rollback to previous release
helm rollback todo-chatbot -n todo-chatbot

# Rollback to specific revision
helm rollback todo-chatbot 1 -n todo-chatbot
```

## Uninstallation

```bash
# Remove the release
helm uninstall todo-chatbot -n todo-chatbot

# Delete namespace
kubectl delete namespace todo-chatbot
```

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -n todo-chatbot

# View pod events
kubectl describe pod <pod-name> -n todo-chatbot

# View logs
kubectl logs -f deployment/backend -n todo-chatbot
kubectl logs -f deployment/frontend -n todo-chatbot
```

### Database connection issues

```bash
# Verify secret is correct
kubectl get secret todo-secrets -n todo-chatbot -o yaml

# Test from pod
kubectl exec -it deployment/backend -n todo-chatbot -- python -c "import os; print(os.environ.get('DATABASE_URL', 'NOT SET'))"
```

### Service connectivity

```bash
# Test internal connectivity
kubectl exec -it deployment/frontend -n todo-chatbot -- wget -qO- http://backend-svc:8000/health
```

## Chart Structure

```
helm/todo-chatbot/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
├── values-local.yaml.example # Template for secrets
├── README.md               # This file
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── namespace.yaml      # Namespace
    ├── configmap.yaml      # ConfigMap
    ├── secret.yaml         # Secret
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

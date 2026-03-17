#!/bin/bash
# Deploy Todo Chatbot to Minikube using Helm
# Usage: ./scripts/deploy.sh [--upgrade]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHART_PATH="$PROJECT_ROOT/helm/todo-chatbot"
NAMESPACE="todo-chatbot"
RELEASE_NAME="todo-chatbot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying Todo Chatbot to Kubernetes${NC}"
echo "========================================"

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: helm is not installed${NC}"
    exit 1
fi

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Start it with: ./scripts/minikube-setup.sh"
    exit 1
fi

# Verify Dapr is installed on the cluster
echo ""
echo -e "${YELLOW}Verifying Dapr installation...${NC}"
if kubectl get namespace dapr-system &> /dev/null; then
    echo -e "${GREEN}Dapr is installed on the cluster${NC}"
else
    echo -e "${RED}Error: Dapr is not installed on the cluster${NC}"
    echo "Run: dapr init -k --runtime-version 1.14.4 --wait"
    echo "Or re-run: ./scripts/minikube-setup.sh"
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Check for values-local.yaml
VALUES_ARGS=()
if [ -f "$CHART_PATH/values-local.yaml" ]; then
    VALUES_ARGS=(-f "$CHART_PATH/values-local.yaml")
    echo -e "${GREEN}Using local values file${NC}"
else
    echo -e "${YELLOW}Warning: No values-local.yaml found${NC}"
    echo "Create one from values-local.yaml.example for secrets"
fi

# Lint the chart first
echo ""
echo -e "${YELLOW}Linting Helm chart...${NC}"
helm lint "$CHART_PATH" "${VALUES_ARGS[@]}"

# Check if this is an upgrade or fresh install
if [[ "$1" == "--upgrade" ]] || helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
    echo ""
    echo -e "${YELLOW}Upgrading existing release...${NC}"
    helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        "${VALUES_ARGS[@]}" \
        --wait \
        --timeout 5m
else
    echo ""
    echo -e "${YELLOW}Installing new release...${NC}"
    helm install "$RELEASE_NAME" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        "${VALUES_ARGS[@]}" \
        --wait \
        --timeout 5m
fi

# Verify Dapr components are loaded
echo ""
echo -e "${YELLOW}Verifying Dapr components...${NC}"
echo "Components:"
kubectl get components.dapr.io -n "$NAMESPACE" 2>/dev/null || echo "  (no components found - may be normal if Dapr CRDs are pending)"
echo ""
echo "Subscriptions:"
kubectl get subscriptions.dapr.io -n "$NAMESPACE" 2>/dev/null || echo "  (no subscriptions found - may be normal if Dapr CRDs are pending)"

# Show deployment status
echo ""
echo -e "${GREEN}Deployment Status:${NC}"
kubectl get pods -n "$NAMESPACE"

echo ""
echo -e "${GREEN}Services:${NC}"
kubectl get svc -n "$NAMESPACE"

echo ""
echo -e "${GREEN}Helm Release:${NC}"
helm list -n "$NAMESPACE"

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "To access the application:"
echo "  minikube service frontend-svc -n $NAMESPACE"
echo ""
echo "Or use port forwarding:"
echo "  kubectl port-forward svc/frontend-svc 3000:3000 -n $NAMESPACE"
echo "  kubectl port-forward svc/backend-svc 8000:8000 -n $NAMESPACE"
echo "  kubectl port-forward svc/sync-svc 8003:8003 -n $NAMESPACE"
echo ""
echo "To check Dapr sidecar status:"
echo "  kubectl get pods -n $NAMESPACE -o jsonpath='{range .items[*]}{.metadata.name}{\"\\t\"}{.spec.containers[*].name}{\"\\n\"}{end}'"

#!/bin/bash
# Setup Minikube for Todo Chatbot deployment
# Usage: ./scripts/minikube-setup.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Minikube for Todo Chatbot${NC}"
echo "========================================"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
    exit 1
fi

if ! command -v minikube &> /dev/null; then
    echo -e "${RED}Error: Minikube is not installed or not in PATH${NC}"
    echo "Install from: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed or not in PATH${NC}"
    echo "Install from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed or not in PATH${NC}"
    echo "Install from: https://helm.sh/docs/intro/install/"
    exit 1
fi

echo -e "${GREEN}All prerequisites satisfied${NC}"

# Check if Minikube is already running
if minikube status | grep -q "Running"; then
    echo -e "${YELLOW}Minikube is already running${NC}"
else
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --cpus=2 --memory=4096 --driver=docker
fi

# Verify cluster is running
echo ""
echo -e "${YELLOW}Verifying cluster...${NC}"
kubectl cluster-info

# Show status
echo ""
echo -e "${GREEN}Minikube Status:${NC}"
minikube status

echo ""
echo -e "${GREEN}Minikube setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Build images: ./scripts/build-images.sh --minikube"
echo "  2. Deploy: ./scripts/deploy.sh"
echo ""
echo "To access Minikube's Docker daemon:"
echo "  eval \$(minikube docker-env)"

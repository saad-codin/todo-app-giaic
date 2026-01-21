#!/bin/bash
# Build Docker images for Todo Chatbot
# Usage: ./scripts/build-images.sh [--minikube]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Todo Chatbot Docker Images${NC}"
echo "========================================"

# Check if we should use Minikube's Docker daemon
if [[ "$1" == "--minikube" ]]; then
    echo -e "${YELLOW}Configuring Docker to use Minikube's daemon...${NC}"
    eval $(minikube docker-env)
    echo -e "${GREEN}Using Minikube Docker daemon${NC}"
fi

# Build backend image
echo ""
echo -e "${GREEN}Building backend image...${NC}"
docker build -t todo-backend:latest "$PROJECT_ROOT/backend"
echo -e "${GREEN}Backend image built successfully${NC}"

# Build frontend image
echo ""
echo -e "${GREEN}Building frontend image...${NC}"
docker build -t todo-frontend:latest "$PROJECT_ROOT/frontend"
echo -e "${GREEN}Frontend image built successfully${NC}"

# List built images
echo ""
echo -e "${GREEN}Built images:${NC}"
docker images | grep -E "^(todo-backend|todo-frontend|REPOSITORY)"

echo ""
echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. If using Minikube, run: eval \$(minikube docker-env)"
echo "  2. Deploy with Helm: ./scripts/deploy.sh"

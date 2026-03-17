#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# Azure Deployment Script - Free Tier (App Service F1)
#
# Deploys:
#   - Backend  (FastAPI)  → Azure App Service (Python, F1 Free)
#   - Frontend (Next.js)  → Azure App Service (Node 20, F1 Free)
#
# Free tier limits (per app):
#   - 60 CPU minutes/day, 1 GB RAM, 1 GB storage
#   - No custom domain SSL, no always-on, no deployment slots
#   - Good enough for demos/hackathons
#
# Prerequisites:
#   - Azure CLI installed (az --version)
#   - Logged in (az login)
#
# Usage:
#   ./scripts/deploy-azure.sh              # Deploy both
#   ./scripts/deploy-azure.sh backend      # Deploy backend only
#   ./scripts/deploy-azure.sh frontend     # Deploy frontend only
###############################################################################

# ── Configuration ────────────────────────────────────────────────────────────
RESOURCE_GROUP="todo-app-rg"
LOCATION="centralus"
BACKEND_APP="todo-backend-app"
FRONTEND_APP="todo-frontend-app"
APP_SERVICE_PLAN="todo-free-plan"

# What to deploy
DEPLOY_TARGET="${1:-all}"  # all | backend | frontend

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
info()  { echo -e "${CYAN}[→]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ── Pre-flight checks ───────────────────────────────────────────────────────
check_prerequisites() {
    info "Checking prerequisites..."

    if ! command -v az &> /dev/null; then
        error "Azure CLI not found. Install: https://aka.ms/installazurecli"
    fi

    # Check if logged in
    if ! az account show &> /dev/null 2>&1; then
        warn "Not logged in to Azure. Opening browser..."
        az login
    fi

    ACCOUNT=$(az account show --query name -o tsv)
    log "Logged in to Azure: $ACCOUNT"
}

# ── Create shared resources ──────────────────────────────────────────────────
create_resources() {
    info "Creating resource group: $RESOURCE_GROUP..."
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --output none 2>/dev/null || true
    log "Resource group ready"

    info "Creating Free (F1) App Service Plan..."
    az appservice plan create \
        --name "$APP_SERVICE_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku F1 \
        --is-linux \
        --output none 2>/dev/null || true
    log "App Service Plan ready (F1 Free)"
}

# ── Deploy Backend ───────────────────────────────────────────────────────────
deploy_backend() {
    info "Deploying backend (FastAPI)..."

    # Create the web app with Python runtime
    info "Creating backend web app..."
    az webapp create \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --name "$BACKEND_APP" \
        --runtime "PYTHON:3.11" \
        --output none 2>/dev/null || {
            warn "Backend app may already exist, continuing..."
        }

    # Configure startup command
    info "Configuring startup command..."
    az webapp config set \
        --resource-group "$RESOURCE_GROUP" \
        --name "$BACKEND_APP" \
        --startup-file "gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120" \
        --output none

    # Get backend URL for later use
    BACKEND_URL="https://${BACKEND_APP}.azurewebsites.net"
    info "Backend URL will be: $BACKEND_URL"

    # Set environment variables
    info "Setting backend environment variables..."
    warn "Reading secrets from backend/.env file..."

    # Source the .env file safely
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    ENV_FILE="$PROJECT_DIR/backend/.env"

    if [ ! -f "$ENV_FILE" ]; then
        error "backend/.env not found. Create it with your secrets first."
    fi

    # Parse .env values
    DB_URL=$(grep -E "^DATABASE_URL=" "$ENV_FILE" | cut -d'=' -f2-)
    SECRET_KEY=$(grep -E "^SECRET_KEY=" "$ENV_FILE" | cut -d'=' -f2-)
    OPENAI_KEY=$(grep -E "^OPENAI_API_KEY=" "$ENV_FILE" | cut -d'=' -f2-)

    az webapp config appsettings set \
        --resource-group "$RESOURCE_GROUP" \
        --name "$BACKEND_APP" \
        --settings \
            DATABASE_URL="$DB_URL" \
            SECRET_KEY="$SECRET_KEY" \
            ALGORITHM="HS256" \
            ACCESS_TOKEN_EXPIRE_MINUTES="1440" \
            OPENAI_API_KEY="$OPENAI_KEY" \
            FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net" \
            SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
            WEBSITE_PORT="8000" \
        --output none
    log "Backend environment configured"

    # Deploy code via zip deploy
    info "Packaging and deploying backend code..."
    cd "$PROJECT_DIR/backend"

    # Create deployment zip (exclude unnecessary files)
    rm -f /tmp/backend-deploy.zip
    zip -r /tmp/backend-deploy.zip . \
        -x ".env" \
        -x ".venv/*" \
        -x "venv/*" \
        -x "__pycache__/*" \
        -x "*/__pycache__/*" \
        -x ".azure/*" \
        -x "*.pyc" \
        -x "todo.db" \
        -x ".git/*"

    az webapp deploy \
        --resource-group "$RESOURCE_GROUP" \
        --name "$BACKEND_APP" \
        --src-path /tmp/backend-deploy.zip \
        --type zip \
        --output none

    rm -f /tmp/backend-deploy.zip
    cd "$PROJECT_DIR"

    log "Backend deployed at: $BACKEND_URL"
}

# ── Deploy Frontend ──────────────────────────────────────────────────────────
deploy_frontend() {
    info "Deploying frontend (Next.js)..."

    BACKEND_URL="https://${BACKEND_APP}.azurewebsites.net"

    # Create the web app with Node runtime
    info "Creating frontend web app..."
    az webapp create \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --name "$FRONTEND_APP" \
        --runtime "NODE:20-lts" \
        --output none 2>/dev/null || {
            warn "Frontend app may already exist, continuing..."
        }

    # Set environment variables (build-time and runtime)
    info "Setting frontend environment variables..."

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    FRONTEND_ENV="$PROJECT_DIR/frontend/.env.local"

    CHATKIT_KEY=""
    if [ -f "$FRONTEND_ENV" ]; then
        CHATKIT_KEY=$(grep -E "^NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=" "$FRONTEND_ENV" | cut -d'=' -f2- || true)
    fi

    az webapp config appsettings set \
        --resource-group "$RESOURCE_GROUP" \
        --name "$FRONTEND_APP" \
        --settings \
            NEXT_PUBLIC_API_URL="$BACKEND_URL" \
            NEXT_PUBLIC_CHATKIT_DOMAIN_KEY="$CHATKIT_KEY" \
            SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
            WEBSITE_PORT="3000" \
        --output none
    log "Frontend environment configured"

    # Configure startup command
    az webapp config set \
        --resource-group "$RESOURCE_GROUP" \
        --name "$FRONTEND_APP" \
        --startup-file "node server.js" \
        --output none

    # Build locally first (Azure F1 has limited build resources)
    info "Building frontend locally..."
    cd "$PROJECT_DIR/frontend"

    # Set env for build
    export NEXT_PUBLIC_API_URL="$BACKEND_URL"
    export NEXT_PUBLIC_CHATKIT_DOMAIN_KEY="$CHATKIT_KEY"
    npm ci
    npm run build

    # Package the standalone output
    info "Packaging standalone build..."
    rm -f /tmp/frontend-deploy.zip
    cd .next/standalone
    cp -r ../.next/static .next/static
    cp -r ../../public ./public 2>/dev/null || true
    zip -r /tmp/frontend-deploy.zip .
    cd "$PROJECT_DIR/frontend"

    # Deploy
    info "Deploying frontend..."
    az webapp deploy \
        --resource-group "$RESOURCE_GROUP" \
        --name "$FRONTEND_APP" \
        --src-path /tmp/frontend-deploy.zip \
        --type zip \
        --output none

    rm -f /tmp/frontend-deploy.zip
    cd "$PROJECT_DIR"

    FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net"
    log "Frontend deployed at: $FRONTEND_URL"
}

# ── Update CORS after both are deployed ──────────────────────────────────────
update_cors() {
    FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net"
    info "Updating backend CORS for: $FRONTEND_URL"

    az webapp cors add \
        --resource-group "$RESOURCE_GROUP" \
        --name "$BACKEND_APP" \
        --allowed-origins "$FRONTEND_URL" \
        --output none 2>/dev/null || true
    log "CORS updated"
}

# ── Print Summary ────────────────────────────────────────────────────────────
print_summary() {
    BACKEND_URL="https://${BACKEND_APP}.azurewebsites.net"
    FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net"

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Deployment Complete (Azure Free Tier)${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Frontend:  ${CYAN}$FRONTEND_URL${NC}"
    echo -e "  Backend:   ${CYAN}$BACKEND_URL${NC}"
    echo -e "  Health:    ${CYAN}$BACKEND_URL/health${NC}"
    echo ""
    echo -e "  ${YELLOW}Free tier notes:${NC}"
    echo -e "  - Apps sleep after ~20 min of inactivity (cold start ~30s)"
    echo -e "  - 60 CPU min/day limit per app"
    echo -e "  - No custom domain SSL on F1"
    echo ""
    echo -e "  ${CYAN}Useful commands:${NC}"
    echo -e "  az webapp log tail -g $RESOURCE_GROUP -n $BACKEND_APP"
    echo -e "  az webapp log tail -g $RESOURCE_GROUP -n $FRONTEND_APP"
    echo -e "  az group delete -n $RESOURCE_GROUP --yes   # tear down everything"
    echo ""
}

# ── AKS Deployment ──────────────────────────────────────────────────────────
AKS_CLUSTER="todo-aks"
ACR_NAME="todoappcr2025"

create_aks() {
    info "Creating AKS cluster (free tier)..."

    # Create ACR if it doesn't exist
    az acr create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$ACR_NAME" \
        --sku Basic \
        --output none 2>/dev/null || warn "ACR may already exist"
    log "ACR ready: ${ACR_NAME}.azurecr.io"

    # Create AKS cluster
    az aks create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$AKS_CLUSTER" \
        --node-count 1 \
        --node-vm-size Standard_B2s \
        --tier free \
        --generate-ssh-keys \
        --attach-acr "$ACR_NAME" \
        --output none 2>/dev/null || warn "AKS cluster may already exist"
    log "AKS cluster ready: $AKS_CLUSTER"

    # Get credentials
    az aks get-credentials \
        --resource-group "$RESOURCE_GROUP" \
        --name "$AKS_CLUSTER" \
        --overwrite-existing
    log "kubectl configured for AKS"

    # Install Dapr on AKS
    if kubectl get namespace dapr-system &> /dev/null; then
        log "Dapr already installed on AKS"
    else
        info "Installing Dapr on AKS..."
        dapr init -k --runtime-version 1.14.4 --wait
        log "Dapr installed on AKS"
    fi
}

build_and_push_acr() {
    info "Building and pushing images to ACR..."
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

    az acr login --name "$ACR_NAME"

    for SVC in backend frontend; do
        info "Building $SVC..."
        docker build -t "${ACR_NAME}.azurecr.io/todo-${SVC}:latest" "$PROJECT_DIR/$SVC"
        docker push "${ACR_NAME}.azurecr.io/todo-${SVC}:latest"
        log "$SVC pushed"
    done

    for SVC in reminder recurring sync; do
        info "Building ${SVC}-service..."
        docker build -t "${ACR_NAME}.azurecr.io/${SVC}-service:latest" "$PROJECT_DIR/services/$SVC"
        docker push "${ACR_NAME}.azurecr.io/${SVC}-service:latest"
        log "${SVC}-service pushed"
    done
}

deploy_aks() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    CHART_PATH="$PROJECT_DIR/helm/todo-chatbot"

    info "Deploying to AKS via Helm..."
    helm upgrade --install todo-chatbot "$CHART_PATH" \
        -f "$CHART_PATH/values-cloud.yaml" \
        -n todo-chatbot \
        --create-namespace \
        --wait \
        --timeout 5m

    log "Helm deployment complete"

    echo ""
    echo -e "${GREEN}AKS Deployment Status:${NC}"
    kubectl get pods -n todo-chatbot
    echo ""
    kubectl get svc -n todo-chatbot
}

# ── Main ─────────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${CYAN}Azure Deployment - Todo App${NC}"
    echo ""

    check_prerequisites
    create_resources

    case "$DEPLOY_TARGET" in
        all)
            deploy_backend
            deploy_frontend
            update_cors
            ;;
        backend)
            deploy_backend
            ;;
        frontend)
            deploy_frontend
            ;;
        aks)
            create_aks
            build_and_push_acr
            deploy_aks
            ;;
        aks-deploy)
            deploy_aks
            ;;
        *)
            error "Unknown target: $DEPLOY_TARGET. Use: all | backend | frontend | aks | aks-deploy"
            ;;
    esac

    print_summary
}

main

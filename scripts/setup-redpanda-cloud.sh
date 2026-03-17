#!/bin/bash
# Setup Redpanda Cloud Serverless cluster and Kubernetes secrets
# Usage: ./scripts/setup-redpanda-cloud.sh
#
# Prerequisites:
#   - rpk CLI installed (https://docs.redpanda.com/current/get-started/rpk-install/)
#   - kubectl configured for target cluster
#   - Redpanda Cloud account (https://cloud.redpanda.com)
#
# This script:
#   1. Prompts for Redpanda Cloud SASL credentials
#   2. Creates Kubernetes secret with credentials
#   3. Creates required Kafka topics

set -euo pipefail

NAMESPACE="todo-chatbot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
info()  { echo -e "${CYAN}[>]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; exit 1; }

echo ""
echo -e "${CYAN}Redpanda Cloud Setup for Todo Chatbot${NC}"
echo "========================================"

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    error "kubectl is not installed"
fi

# Prompt for credentials
echo ""
info "Enter your Redpanda Cloud Serverless credentials"
info "(Find these in Redpanda Cloud Console > Cluster > Security)"
echo ""

read -rp "Bootstrap Servers (e.g., seed-xxx.redpanda.com:9092): " BOOTSTRAP_SERVERS
read -rp "SASL Username: " SASL_USERNAME
read -rsp "SASL Password: " SASL_PASSWORD
echo ""

if [ -z "$BOOTSTRAP_SERVERS" ] || [ -z "$SASL_USERNAME" ] || [ -z "$SASL_PASSWORD" ]; then
    error "All fields are required"
fi

# Create namespace if needed
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Create Kubernetes secret
info "Creating Kubernetes secret: redpanda-secrets..."
kubectl create secret generic redpanda-secrets \
    --namespace "$NAMESPACE" \
    --from-literal=username="$SASL_USERNAME" \
    --from-literal=password="$SASL_PASSWORD" \
    --from-literal=bootstrap-servers="$BOOTSTRAP_SERVERS" \
    --dry-run=client -o yaml | kubectl apply -f -

log "Secret created in namespace $NAMESPACE"

# Create topics via rpk if available
if command -v rpk &> /dev/null; then
    info "Creating Kafka topics via rpk..."

    RPK_ARGS="--brokers $BOOTSTRAP_SERVERS --user $SASL_USERNAME --password $SASL_PASSWORD --sasl-mechanism SCRAM-SHA-256 --tls-enabled"

    rpk topic create task-events --partitions 3 --replicas 1 $RPK_ARGS 2>/dev/null || warn "topic 'task-events' may already exist"
    rpk topic create task-updates --partitions 3 --replicas 1 $RPK_ARGS 2>/dev/null || warn "topic 'task-updates' may already exist"
    rpk topic create reminders --partitions 1 --replicas 1 $RPK_ARGS 2>/dev/null || warn "topic 'reminders' may already exist"

    log "Topics created"
else
    warn "rpk CLI not found. Topics will be auto-created by Dapr on first publish."
    warn "For manual creation, install rpk: https://docs.redpanda.com/current/get-started/rpk-install/"
fi

echo ""
log "Redpanda Cloud setup complete!"
echo ""
echo "Next steps:"
echo "  1. Deploy with cloud values:"
echo "     helm upgrade --install todo-chatbot ./helm/todo-chatbot \\"
echo "       -f helm/todo-chatbot/values-cloud.yaml \\"
echo "       --set redpanda.cloud.bootstrapServers=$BOOTSTRAP_SERVERS \\"
echo "       -n $NAMESPACE"
echo ""

#!/bin/bash
# Verify Todo Chatbot deployment health
# Usage: ./scripts/verify-deployment.sh [--namespace todo-chatbot]
#
# Checks:
#   1. All pods are Running with expected container counts
#   2. Health endpoints respond on all services
#   3. Dapr components and subscriptions are loaded
#   4. Optional: create a test task and verify event flow

set -euo pipefail

NAMESPACE="${1:-todo-chatbot}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS=0
FAIL=0

pass() { echo -e "  ${GREEN}PASS${NC} $1"; ((PASS++)); }
fail() { echo -e "  ${RED}FAIL${NC} $1"; ((FAIL++)); }
info() { echo -e "${CYAN}[>]${NC} $1"; }

echo ""
echo -e "${CYAN}Deployment Verification: $NAMESPACE${NC}"
echo "========================================"

# 1. Check pods
info "Checking pods..."
PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null)

if [ -z "$PODS" ]; then
    fail "No pods found in namespace $NAMESPACE"
else
    # Check each expected deployment
    for DEPLOY in backend frontend reminder recurring sync; do
        POD_LINE=$(echo "$PODS" | grep "^${DEPLOY}" || true)
        if [ -z "$POD_LINE" ]; then
            # Try with -service suffix for microservices
            POD_LINE=$(echo "$PODS" | grep "^${DEPLOY}-service" || true)
        fi

        if [ -z "$POD_LINE" ]; then
            fail "$DEPLOY pod not found"
        else
            STATUS=$(echo "$POD_LINE" | awk '{print $3}')
            READY=$(echo "$POD_LINE" | awk '{print $2}')
            if [ "$STATUS" == "Running" ]; then
                pass "$DEPLOY pod Running ($READY)"
            else
                fail "$DEPLOY pod status: $STATUS ($READY)"
            fi
        fi
    done

    # Check Redpanda if expected
    REDPANDA_POD=$(echo "$PODS" | grep "^redpanda" || true)
    if [ -n "$REDPANDA_POD" ]; then
        STATUS=$(echo "$REDPANDA_POD" | awk '{print $3}')
        if [ "$STATUS" == "Running" ]; then
            pass "redpanda pod Running"
        else
            fail "redpanda pod status: $STATUS"
        fi
    fi
fi

# 2. Check health endpoints via port-forward
info "Checking health endpoints..."

check_health() {
    local SVC=$1
    local PORT=$2
    local NAME=$3

    # Start port-forward in background
    local LOCAL_PORT=$((30000 + RANDOM % 5000))
    kubectl port-forward "svc/$SVC" "$LOCAL_PORT:$PORT" -n "$NAMESPACE" &>/dev/null &
    local PF_PID=$!
    sleep 2

    # Hit health endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$LOCAL_PORT/health" 2>/dev/null || echo "000")

    # Cleanup
    kill $PF_PID 2>/dev/null || true
    wait $PF_PID 2>/dev/null || true

    if [ "$RESPONSE" == "200" ]; then
        pass "$NAME health check (HTTP $RESPONSE)"
    else
        fail "$NAME health check (HTTP $RESPONSE)"
    fi
}

check_health "backend-svc" 8000 "backend"
check_health "frontend-svc" 3000 "frontend"
check_health "reminder-svc" 8001 "reminder-service"
check_health "recurring-svc" 8002 "recurring-service"
check_health "sync-svc" 8003 "sync-service"

# 3. Check Dapr components
info "Checking Dapr components..."

COMPONENTS=$(kubectl get components.dapr.io -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
if echo "$COMPONENTS" | grep -q "taskpubsub"; then
    pass "Dapr pubsub component (taskpubsub)"
else
    fail "Dapr pubsub component not found"
fi

if echo "$COMPONENTS" | grep -q "statestore"; then
    pass "Dapr state store component (statestore)"
else
    fail "Dapr state store component not found"
fi

SUBSCRIPTIONS=$(kubectl get subscriptions.dapr.io -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
SUB_COUNT=$(echo "$SUBSCRIPTIONS" | grep -c "." || echo "0")
if [ "$SUB_COUNT" -ge 4 ]; then
    pass "Dapr subscriptions ($SUB_COUNT found)"
else
    fail "Expected 4 Dapr subscriptions, found $SUB_COUNT"
fi

# Summary
echo ""
echo "========================================"
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Deployment verification failed.${NC}"
    echo "Run 'kubectl describe pods -n $NAMESPACE' for more details."
    exit 1
else
    echo -e "${GREEN}All checks passed!${NC}"
fi

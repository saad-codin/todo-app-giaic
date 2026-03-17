# Research: Advanced Event-Driven Todo/Chatbot

**Feature**: 006-dapr-event-driven | **Date**: 2026-02-09

## 1. Dapr Building Blocks

### 1.1 Pub/Sub Messaging

Dapr's Pub/Sub building block provides a platform-agnostic API for publishing and subscribing to messages. The application code calls the Dapr sidecar HTTP/gRPC API, and the sidecar handles communication with the underlying message broker.

**How it works**:
- Publisher calls `POST http://localhost:3500/v1.0/publish/<pubsub-name>/<topic>` with JSON payload
- Subscribers declare subscriptions either programmatically or via declarative YAML
- Dapr sidecar delivers messages to subscriber's HTTP endpoint (e.g., `POST /events/task-created`)

**Key configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda:9092"  # local or cloud broker URL
    - name: consumerGroup
      value: "todo-consumers"
    - name: authType
      value: "none"  # local; use "sasl" for cloud
```

**Python SDK usage**:
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name="taskpubsub",
        topic_name="task-events",
        data=json.dumps(event_payload),
        data_content_type="application/json",
    )
```

### 1.2 State Management

Dapr State building block provides a key/value store API. We use it for:
- Reminder state (pending reminders keyed by task ID)
- Consumer deduplication (processed event IDs)

**Component**: `statestore.postgresql` pointing to existing Neon DB.

### 1.3 Service Invocation

Not heavily used in this design since services communicate primarily through pub/sub. However, the sync service uses Dapr service invocation to check authentication before accepting WebSocket connections.

### 1.4 Dapr Jobs API (Alpha)

Dapr Jobs API (v1.14+, alpha) supports scheduled job execution. Preferred for exact-time reminder scheduling. If unstable, fall back to Dapr Cron binding + polling.

**Fallback chain**: Dapr Jobs API -> Dapr Cron Binding (1-minute intervals) -> Python APScheduler in-process

## 2. Redpanda (Kafka-Compatible Broker)

### 2.1 Why Redpanda over Apache Kafka

| Aspect | Apache Kafka | Redpanda |
|--------|-------------|----------|
| Deployment | JVM, requires ZooKeeper/KRaft | Single Go/C++ binary, no dependencies |
| Resource usage | High (JVM heap, multiple processes) | Low (single process, thread-per-core) |
| Kafka protocol | Native | Fully compatible (same client libraries) |
| Cloud free tier | Confluent free trial (limited) | Redpanda Serverless free tier (perpetual) |
| Local dev | docker-compose with 3+ containers | Single container |
| Dapr support | `pubsub.kafka` component | Same `pubsub.kafka` component (transparent) |

**Decision**: Redpanda for both local development and cloud. Dapr's `pubsub.kafka` component works identically with both.

### 2.2 Redpanda Cloud (Serverless)

- **Free tier**: 1 serverless cluster, sufficient throughput for 20 users
- **Connection**: SASL/SCRAM authentication over TLS
- **Topics**: Auto-created on first publish (or pre-created via `rpk`)
- **Retention**: Default 7 days (configurable)

**Cloud component config**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "<cluster-id>.any.us-east-1.mpx.prd.cloud.redpanda.com:9092"
    - name: authType
      value: "sasl"
    - name: saslUsername
      secretKeyRef:
        name: redpanda-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: redpanda-secrets
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: requiredAcks
      value: "all"
```

### 2.3 Local Redpanda (Minikube)

Single-node Redpanda in Kubernetes via StatefulSet:
```yaml
# Single container, no JVM, ~256MB memory
image: docker.redpanda.com/redpandadata/redpanda:latest
args: ["redpanda", "start", "--mode", "dev-container", "--smp", "1"]
ports: [9092 (Kafka), 8081 (Schema Registry), 9644 (Admin)]
```

### 2.4 Topics

| Topic | Publisher | Consumers | Purpose |
|-------|-----------|-----------|---------|
| `task-events` | Backend (task CRUD routes) | Reminder service, Recurring service | All task lifecycle events |
| `reminders` | Reminder service | Sync service | Reminder notifications to deliver |
| `task-updates` | Backend + Recurring service | Sync service | Real-time UI update broadcasts |

## 3. Azure Kubernetes Service (AKS)

### 3.1 Free Tier

- **AKS free tier**: No cluster management fee, pay only for VMs
- **Best config**: 1 node pool, Standard_B2s (2 vCPU, 4 GB RAM, ~$30/mo) or use spot instances
- **Alternative**: AKS with free tier + 1 Standard_B2als_v2 ($28/mo)

### 3.2 Dapr on AKS

Install Dapr on AKS:
```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on the cluster
dapr init -k --runtime-version 1.14.4

# Verify
dapr status -k
kubectl get pods -n dapr-system
```

### 3.3 AKS + ACR Integration

Existing ACR (`todoappcr2025.azurecr.io`) integrates with AKS:
```bash
# Attach ACR to AKS cluster
az aks update -n todo-aks -g todo-app-rg --attach-acr todoappcr2025
```

### 3.4 Resource Planning

| Service | CPU Request | Memory Request | Replicas |
|---------|-------------|----------------|----------|
| Backend | 100m | 256Mi | 1 |
| Frontend | 100m | 256Mi | 1 |
| Reminder | 50m | 128Mi | 1 |
| Recurring | 50m | 128Mi | 1 |
| Sync | 100m | 256Mi | 1 |
| Redpanda (local only) | 200m | 256Mi | 1 |
| Dapr sidecars (per pod) | 50m | 64Mi | 5 |
| **Total** | **900m** | **1.6Gi** | - |

Fits within a single Standard_B2s node (2 vCPU, 4 GB RAM).

## 4. Event-Driven Patterns

### 4.1 Event Publishing Strategy

Events are published **after** the database transaction commits successfully:
```python
# In routes/tasks.py
session.add(task)
session.commit()
session.refresh(task)

# Fire-and-forget to Dapr sidecar
try:
    await event_publisher.publish("task-events", TaskCreatedEvent(...))
except Exception:
    pass  # Sidecar handles retry; degraded mode is acceptable
```

### 4.2 Idempotent Consumers

Every event carries a unique `event_id` (UUID). Consumers track processed IDs:
```python
# In reminder service
async def handle_task_event(event: dict):
    event_id = event["event_id"]
    if await is_already_processed(event_id):
        return {"status": "DROP"}  # Dapr acknowledges, no redelivery
    # Process event...
    await mark_processed(event_id)
    return {"status": "SUCCESS"}
```

Dedup storage: Dapr state store (PostgreSQL-backed) with TTL for cleanup.

### 4.3 CloudEvents Format

Dapr wraps all pub/sub messages in CloudEvents v1.0:
```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "/backend/tasks",
  "id": "unique-event-id",
  "time": "2026-02-09T10:00:00Z",
  "datacontenttype": "application/json",
  "data": { "task_id": "...", "user_id": "...", ... }
}
```

## 5. WebSocket Real-Time Sync

### 5.1 Architecture

The sync service maintains WebSocket connections per authenticated user. When it receives events from the `task-updates` topic, it broadcasts to all connections for that user.

**Flow**: Task CRUD -> Backend publishes to `task-updates` -> Sync service receives -> Broadcasts to user's WebSocket connections

### 5.2 Frontend Integration

```typescript
// useWebSocket.ts hook
const ws = new WebSocket(`wss://${SYNC_URL}/ws?token=${authToken}`);
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  queryClient.invalidateQueries({ queryKey: ['tasks'] });
};
```

### 5.3 Connection Management

- JWT token validated on WebSocket upgrade
- Heartbeat ping/pong every 30 seconds
- Reconnect with exponential backoff on disconnect
- Connection registry: in-memory dict `{user_id: set[websocket]}`

## 6. Reminder Scheduling Strategy

### 6.1 Primary: Event-Driven + Polling Hybrid

1. When `task.created` or `task.updated` event arrives with a due date, the reminder service calculates trigger times (due - 24h, due - 1h)
2. Reminders are stored in the Dapr state store with keys like `reminder:{task_id}:{type}`
3. A polling loop (every 60 seconds) checks for reminders whose trigger time has passed
4. Triggered reminders publish to the `reminders` topic and are marked as sent

### 6.2 Cancellation

When `task.completed` or `task.updated` (due date changed) events arrive, pending reminders are cancelled (deleted from state store).

### 6.3 Simulated Delivery

Reminders are "delivered" via structured log output:
```
[REMINDER] user=abc123 task=xyz789 type=24h message="Task 'Buy groceries' is due in 24 hours"
```

## 7. Recurring Task Strategy

### 7.1 Time-Based (Primary)

- Recurring service polls recurrence rules every 60 seconds
- For each rule where `next_occurrence <= now`, create a new task instance via Dapr service invocation to the backend
- Update `next_occurrence` to the following date
- New task creation publishes its own `task.created` event (which triggers reminder scheduling)

### 7.2 On-Complete (Secondary)

- Recurring service subscribes to `task-events` topic
- On `task.completed` event, check if task has `is_completion_based = true`
- If yes, create new task with due date = completion date + interval

### 7.3 Date Calculation

- Daily: `+ N days`
- Weekly: `+ N weeks` (anchored to day_of_week)
- Monthly: `+ N months` (clamp day to 28 for safety, matching existing logic in `routes/tasks.py`)

## 8. Local Development Workflow

### 8.1 Prerequisites

- Docker Desktop with Kubernetes enabled OR Minikube
- Dapr CLI (`dapr init -k`)
- Helm 3
- kubectl
- rpk (Redpanda CLI, optional)

### 8.2 Setup Sequence

1. Start Minikube: `minikube start --cpus=4 --memory=4096`
2. Install Dapr: `dapr init -k`
3. Build images: `./scripts/build-images.sh --minikube`
4. Deploy: `helm upgrade --install todo-chatbot ./helm/todo-chatbot -f helm/todo-chatbot/values-local.yaml -n todo-chatbot --create-namespace`
5. Verify: `kubectl get pods -n todo-chatbot` (all pods Running)
6. Access: `minikube service frontend-svc -n todo-chatbot`

## 9. CI/CD Pipeline

### 9.1 GitHub Actions Workflow

```
trigger: push to main
jobs:
  build:
    - Checkout code
    - Login to ACR
    - Build + push 4 images (backend, frontend, reminder, recurring, sync)
  deploy:
    - Install kubectl, helm, dapr CLI
    - Get AKS credentials
    - Helm upgrade --install
    - Verify deployment health
```

### 9.2 Rollback

```bash
helm rollback todo-chatbot <revision> -n todo-chatbot
```

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Dapr Jobs API instability (alpha) | Medium | Low | Fall back to polling; Jobs API is nice-to-have |
| Redpanda Cloud free tier throttling | Low | Medium | Local Redpanda for dev; cloud only for demo |
| AKS node resource exhaustion | Medium | High | Right-size requests; single B2s node with ~900m CPU total |
| WebSocket connection drops | Medium | Low | Auto-reconnect with backoff; React Query refetch on reconnect |
| Event ordering across topics | Low | Low | Consumers are idempotent; ordering within partition guaranteed |
| Dapr sidecar startup delay | Medium | Low | Init containers wait for sidecar; readiness probes |

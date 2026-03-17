# Dapr Component Contracts

**Feature**: 006-dapr-event-driven | **Date**: 2026-02-09

## Component Overview

| Component | Type | Name | Scope |
|-----------|------|------|-------|
| Pub/Sub | `pubsub.kafka` | `taskpubsub` | All services |
| State Store | `state.postgresql` | `statestore` | Reminder, Recurring services |

## Service App IDs

| Service | `dapr.io/app-id` | `dapr.io/app-port` | Topics Consumed |
|---------|-------------------|---------------------|-----------------|
| backend | `backend` | `8000` | None (publisher only) |
| reminder-service | `reminder-service` | `8001` | `task-events` |
| recurring-service | `recurring-service` | `8002` | `task-events` |
| sync-service | `sync-service` | `8003` | `task-updates`, `reminders` |

## Pub/Sub Component: `taskpubsub`

### Local (Minikube + Redpanda in-cluster)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
  namespace: todo-chatbot
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.todo-chatbot.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-consumers"
    - name: authType
      value: "none"
    - name: initialOffset
      value: "oldest"
    - name: disableTls
      value: "true"
```

### Cloud (AKS + Redpanda Cloud Serverless)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
  namespace: todo-chatbot
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "{{ .Values.redpanda.cloud.bootstrapServers }}"
    - name: consumerGroup
      value: "todo-consumers"
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
    - name: initialOffset
      value: "oldest"
    - name: requiredAcks
      value: "all"
    - name: clientID
      value: "todo-chatbot"
```

## State Store Component: `statestore`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-chatbot
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: todo-secrets
        key: DATABASE_URL
    - name: tableName
      value: "dapr_state"
    - name: keyPrefix
      value: "name"
    - name: cleanupIntervalInSeconds
      value: "3600"
    - name: actorStateStore
      value: "false"
```

## Subscription Definitions

### Reminder Service <- task-events

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-reminder
  namespace: todo-chatbot
spec:
  pubsubname: taskpubsub
  topic: task-events
  routes:
    rules:
      - match: event.type == "task.created"
        path: /events/task
      - match: event.type == "task.updated"
        path: /events/task
      - match: event.type == "task.completed"
        path: /events/task
      - match: event.type == "task.deleted"
        path: /events/task
    default: /events/task
  scopes:
    - reminder-service
```

### Recurring Service <- task-events

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-recurring
  namespace: todo-chatbot
spec:
  pubsubname: taskpubsub
  topic: task-events
  routes:
    rules:
      - match: event.type == "task.created"
        path: /events/task
      - match: event.type == "task.completed"
        path: /events/task
      - match: event.type == "task.deleted"
        path: /events/task
    default: /events/task
  scopes:
    - recurring-service
```

### Sync Service <- task-updates

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-updates-sync
  namespace: todo-chatbot
spec:
  pubsubname: taskpubsub
  topic: task-updates
  routes:
    default: /events/sync
  scopes:
    - sync-service
```

### Sync Service <- reminders

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: reminders-sync
  namespace: todo-chatbot
spec:
  pubsubname: taskpubsub
  topic: reminders
  routes:
    default: /events/reminder
  scopes:
    - sync-service
```

## Sidecar Annotations Template

All Dapr-enabled deployments use this annotation block:

```yaml
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{{ .appId }}"
        dapr.io/app-port: "{{ .appPort }}"
        dapr.io/app-protocol: "http"
        dapr.io/enable-api-logging: "true"
        dapr.io/log-level: "info"
        dapr.io/sidecar-cpu-request: "50m"
        dapr.io/sidecar-memory-request: "64Mi"
        dapr.io/sidecar-cpu-limit: "100m"
        dapr.io/sidecar-memory-limit: "128Mi"
```

## Dapr SDK Usage Pattern

### Publishing (Backend)

```python
import json
import uuid
from dapr.clients import DaprClient

async def publish_event(topic: str, event_type: str, data: dict):
    """Fire-and-forget event publishing via Dapr sidecar."""
    event_id = str(uuid.uuid4())
    data["event_id"] = event_id
    try:
        with DaprClient() as client:
            client.publish_event(
                pubsub_name="taskpubsub",
                topic_name=topic,
                data=json.dumps(data),
                data_content_type="application/json",
                publish_metadata={"rawPayload": "false"},
            )
    except Exception:
        pass  # Fire-and-forget: sidecar handles retry
    return event_id
```

### Subscribing (Consumer Services)

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/events/task")
async def handle_task_event(request: Request):
    """Dapr calls this endpoint when a task event arrives."""
    envelope = await request.json()
    data = envelope.get("data", {})
    event_id = data.get("event_id")

    # Idempotency check
    if await is_processed(event_id):
        return {"status": "DROP"}

    # Process based on event type
    event_type = envelope.get("type", "")
    if event_type == "task.created":
        await handle_task_created(data)
    elif event_type == "task.completed":
        await handle_task_completed(data)
    # ...

    await mark_processed(event_id)
    return {"status": "SUCCESS"}
```

# Data Model: Advanced Event-Driven Todo/Chatbot

**Feature**: 006-dapr-event-driven | **Date**: 2026-02-09

## 1. Database Schema Extensions

### 1.1 Existing Tables (No Changes)

- `user` - User accounts with hashed passwords
- `task` - Task records with priority, tags, due dates, recurrence
- `conversation` - Chat conversation sessions
- `chatmessage` - Chat message records

### 1.2 New Table: `recurrence_rule`

Extends the existing `recurrence` enum on `task` with richer scheduling rules.

```sql
CREATE TABLE recurrence_rule (
    id              TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL REFERENCES task(id) ON DELETE CASCADE,
    user_id         TEXT NOT NULL REFERENCES user(id),
    frequency       TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly')),
    interval_value  INTEGER NOT NULL DEFAULT 1,        -- every N days/weeks/months
    day_of_week     INTEGER,                           -- 0=Mon..6=Sun (for weekly)
    day_of_month    INTEGER,                           -- 1-28 (for monthly, clamped)
    is_completion_based BOOLEAN NOT NULL DEFAULT FALSE, -- true=on-complete, false=time-based
    next_occurrence TEXT NOT NULL,                      -- YYYY-MM-DD next trigger date
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recurrence_rule_next ON recurrence_rule(next_occurrence);
CREATE INDEX idx_recurrence_rule_task ON recurrence_rule(task_id);
```

### 1.3 New Table: `task_event`

Immutable event log for debugging and audit stubs. Not used for event delivery (that's Kafka).

```sql
CREATE TABLE task_event (
    id          TEXT PRIMARY KEY,                       -- UUID, same as event_id in Kafka message
    event_type  TEXT NOT NULL CHECK (event_type IN ('task.created', 'task.updated', 'task.completed', 'task.deleted')),
    task_id     TEXT NOT NULL,                          -- May reference deleted task
    user_id     TEXT NOT NULL,
    payload     JSONB NOT NULL,                        -- Full event data
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_task_event_task ON task_event(task_id);
CREATE INDEX idx_task_event_type ON task_event(event_type);
CREATE INDEX idx_task_event_created ON task_event(created_at);
```

### 1.4 New Table: `reminder`

Tracks pending and delivered reminders.

```sql
CREATE TABLE reminder (
    id              TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL REFERENCES task(id) ON DELETE CASCADE,
    user_id         TEXT NOT NULL REFERENCES user(id),
    trigger_time    TIMESTAMP NOT NULL,
    reminder_type   TEXT NOT NULL CHECK (reminder_type IN ('24h', '1h')),
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'cancelled')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reminder_pending ON reminder(status, trigger_time) WHERE status = 'pending';
CREATE INDEX idx_reminder_task ON reminder(task_id);
```

### 1.5 Task Table Extension

Add `title` field to `task` table (currently using `description` as title). The spec refers to tasks having a `title` and `description` — the existing schema uses only `description`. We keep backward compatibility by treating `description` as the primary text field (no schema change needed).

**No schema change required** — the existing `description` field serves as the task's display text.

## 2. SQLModel Entity Definitions

### 2.1 RecurrenceRule

```python
class RecurrenceRule(SQLModel, table=True):
    """Recurrence rule for repeating tasks."""
    __tablename__ = "recurrence_rule"

    id: str = Field(primary_key=True)
    task_id: str = Field(foreign_key="task.id", index=True)
    user_id: str = Field(foreign_key="user.id")
    frequency: str  # daily, weekly, monthly
    interval_value: int = Field(default=1)
    day_of_week: Optional[int] = None     # 0=Mon..6=Sun
    day_of_month: Optional[int] = None    # 1-28
    is_completion_based: bool = Field(default=False)
    next_occurrence: str                   # YYYY-MM-DD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.2 TaskEvent

```python
class TaskEvent(SQLModel, table=True):
    """Immutable task event log (audit stub)."""
    __tablename__ = "task_event"

    id: str = Field(primary_key=True)      # Same UUID as Kafka event_id
    event_type: str                         # task.created, task.updated, etc.
    task_id: str
    user_id: str
    payload: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.3 Reminder

```python
class ReminderStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    cancelled = "cancelled"

class ReminderType(str, Enum):
    twenty_four_hours = "24h"
    one_hour = "1h"

class Reminder(SQLModel, table=True):
    """Scheduled reminder for a task."""
    id: str = Field(primary_key=True)
    task_id: str = Field(foreign_key="task.id", index=True)
    user_id: str = Field(foreign_key="user.id")
    trigger_time: datetime
    reminder_type: ReminderType
    status: ReminderStatus = Field(default=ReminderStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## 3. Event Schemas

All events follow CloudEvents v1.0 format (enforced by Dapr). The `data` field contains the application-specific payload.

### 3.1 TaskCreatedEvent

```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "/backend/tasks",
  "id": "evt-uuid-here",
  "time": "2026-02-09T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "event_id": "evt-uuid-here",
    "task_id": "task-uuid",
    "user_id": "user-uuid",
    "description": "Buy groceries",
    "priority": "high",
    "tags": ["shopping"],
    "due_date": "2026-02-15",
    "due_time": "18:00",
    "recurrence": "weekly",
    "is_completion_based": false,
    "timestamp": "2026-02-09T10:00:00Z"
  }
}
```

### 3.2 TaskUpdatedEvent

```json
{
  "type": "task.updated",
  "data": {
    "event_id": "evt-uuid",
    "task_id": "task-uuid",
    "user_id": "user-uuid",
    "changed_fields": {
      "priority": { "old": "medium", "new": "high" },
      "due_date": { "old": "2026-02-15", "new": "2026-02-20" }
    },
    "timestamp": "2026-02-09T11:00:00Z"
  }
}
```

### 3.3 TaskCompletedEvent

```json
{
  "type": "task.completed",
  "data": {
    "event_id": "evt-uuid",
    "task_id": "task-uuid",
    "user_id": "user-uuid",
    "completed_at": "2026-02-09T12:00:00Z",
    "had_recurrence": true,
    "is_completion_based": false,
    "timestamp": "2026-02-09T12:00:00Z"
  }
}
```

### 3.4 TaskDeletedEvent

```json
{
  "type": "task.deleted",
  "data": {
    "event_id": "evt-uuid",
    "task_id": "task-uuid",
    "user_id": "user-uuid",
    "timestamp": "2026-02-09T13:00:00Z"
  }
}
```

### 3.5 ReminderEvent

Published to the `reminders` topic by the reminder service.

```json
{
  "type": "reminder.triggered",
  "data": {
    "event_id": "evt-uuid",
    "reminder_id": "rem-uuid",
    "task_id": "task-uuid",
    "user_id": "user-uuid",
    "reminder_type": "24h",
    "task_description": "Buy groceries",
    "due_date": "2026-02-15",
    "due_time": "18:00",
    "timestamp": "2026-02-09T18:00:00Z"
  }
}
```

### 3.6 TaskUpdateBroadcast

Published to the `task-updates` topic for real-time sync.

```json
{
  "type": "task.sync",
  "data": {
    "event_id": "evt-uuid",
    "user_id": "user-uuid",
    "action": "created|updated|completed|deleted",
    "task": {
      "id": "task-uuid",
      "description": "Buy groceries",
      "completed": false,
      "priority": "high",
      "tags": ["shopping"],
      "dueDate": "2026-02-15",
      "dueTime": "18:00",
      "recurrence": "weekly",
      "createdAt": "2026-02-09T10:00:00Z",
      "updatedAt": "2026-02-09T10:00:00Z"
    },
    "timestamp": "2026-02-09T10:00:00Z"
  }
}
```

## 4. Dapr Component Definitions

### 4.1 Pub/Sub Component (Local)

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
```

### 4.2 Pub/Sub Component (Cloud - Redpanda Serverless)

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
      value: "<redpanda-cloud-bootstrap-url>:9092"
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

### 4.3 State Store Component

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
```

### 4.4 Subscriptions (Declarative)

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
    default: /events/task
  scopes:
    - reminder-service

---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-recurring
  namespace: todo-chatbot
spec:
  pubsubname: taskpubsub
  topic: task-events
  routes:
    default: /events/task
  scopes:
    - recurring-service

---
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

---
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

## 5. Dapr Sidecar Annotations

Each Kubernetes deployment that uses Dapr needs these annotations:

```yaml
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "<service-name>"     # e.g., "backend", "reminder-service"
    dapr.io/app-port: "<app-port>"       # e.g., "8000", "8001"
    dapr.io/app-protocol: "http"
    dapr.io/enable-api-logging: "true"
    dapr.io/log-level: "info"
```

## 6. Entity Relationships

```
User 1---* Task
User 1---* Conversation
Task 1---0..1 RecurrenceRule
Task 1---* TaskEvent
Task 1---* Reminder
Conversation 1---* ChatMessage

Kafka Topics:
  task-events  <-- Backend publishes
       |
       +---> Reminder Service (creates/cancels Reminders)
       +---> Recurring Service (creates new Tasks via RecurrenceRule)

  reminders    <-- Reminder Service publishes
       |
       +---> Sync Service (delivers to WebSocket)

  task-updates <-- Backend + Recurring Service publish
       |
       +---> Sync Service (broadcasts to user's WebSocket connections)
```

## 7. Priority Enum Extension

The existing `Priority` enum has `high`, `medium`, `low`. The spec requires `urgent` as well.

```python
class Priority(str, Enum):
    urgent = "urgent"
    high = "high"
    medium = "medium"
    low = "low"
```

This is a backward-compatible addition — existing tasks with `high/medium/low` remain valid.

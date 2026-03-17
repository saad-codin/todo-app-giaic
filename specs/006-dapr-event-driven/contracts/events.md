# Event Contracts

**Feature**: 006-dapr-event-driven | **Date**: 2026-02-09

## Kafka Topics

| Topic | Partitions | Retention | Key Strategy |
|-------|-----------|-----------|-------------|
| `task-events` | 3 | 7 days | `user_id` (ensures ordering per user) |
| `reminders` | 1 | 1 day | `user_id` |
| `task-updates` | 3 | 1 day | `user_id` |

## Envelope Format

All events use CloudEvents v1.0 (automatically wrapped by Dapr):

```json
{
  "specversion": "1.0",
  "type": "<event-type>",
  "source": "<source-service>",
  "id": "<event-uuid>",
  "time": "<ISO-8601>",
  "datacontenttype": "application/json",
  "data": { ... }
}
```

## Event Type: `task.created`

**Topic**: `task-events`
**Publisher**: Backend (routes/tasks.py)
**Consumers**: Reminder service, Recurring service

```typescript
interface TaskCreatedEvent {
  event_id: string;       // UUID v4
  task_id: string;        // UUID v4
  user_id: string;        // UUID v4
  description: string;    // Task text
  priority: "urgent" | "high" | "medium" | "low";
  tags: string[];
  due_date: string | null;    // YYYY-MM-DD
  due_time: string | null;    // HH:MM
  recurrence: "none" | "daily" | "weekly" | "monthly";
  is_completion_based: boolean;
  timestamp: string;      // ISO-8601
}
```

**Consumer actions**:
- Reminder service: If `due_date` is set, schedule reminders at `due_date - 24h` and `due_date - 1h`
- Recurring service: If `recurrence != "none"`, create/update recurrence rule in DB

## Event Type: `task.updated`

**Topic**: `task-events`
**Publisher**: Backend (routes/tasks.py)
**Consumers**: Reminder service, Recurring service

```typescript
interface TaskUpdatedEvent {
  event_id: string;
  task_id: string;
  user_id: string;
  changed_fields: Record<string, { old: any; new: any }>;
  timestamp: string;
}
```

**Consumer actions**:
- Reminder service: If `due_date` changed, cancel existing reminders and schedule new ones. If `due_date` removed, cancel all reminders for task
- Recurring service: If `recurrence` changed, update recurrence rule

## Event Type: `task.completed`

**Topic**: `task-events`
**Publisher**: Backend (routes/tasks.py)
**Consumers**: Reminder service, Recurring service

```typescript
interface TaskCompletedEvent {
  event_id: string;
  task_id: string;
  user_id: string;
  completed_at: string;           // ISO-8601
  had_recurrence: boolean;
  is_completion_based: boolean;
  timestamp: string;
}
```

**Consumer actions**:
- Reminder service: Cancel all pending reminders for `task_id`
- Recurring service: If `is_completion_based == true`, create next task instance

## Event Type: `task.deleted`

**Topic**: `task-events`
**Publisher**: Backend (routes/tasks.py)
**Consumers**: Reminder service, Recurring service

```typescript
interface TaskDeletedEvent {
  event_id: string;
  task_id: string;
  user_id: string;
  timestamp: string;
}
```

**Consumer actions**:
- Reminder service: Cancel all pending reminders for `task_id`
- Recurring service: Delete recurrence rule for `task_id`

## Event Type: `reminder.triggered`

**Topic**: `reminders`
**Publisher**: Reminder service
**Consumers**: Sync service

```typescript
interface ReminderTriggeredEvent {
  event_id: string;
  reminder_id: string;
  task_id: string;
  user_id: string;
  reminder_type: "24h" | "1h";
  task_description: string;
  due_date: string;
  due_time: string | null;
  timestamp: string;
}
```

**Consumer actions**:
- Sync service: Push notification to user's WebSocket connections

## Event Type: `task.sync`

**Topic**: `task-updates`
**Publisher**: Backend + Recurring service
**Consumers**: Sync service

```typescript
interface TaskSyncEvent {
  event_id: string;
  user_id: string;
  action: "created" | "updated" | "completed" | "deleted";
  task: TaskResponse | null;  // null for deleted
  timestamp: string;
}
```

**Consumer actions**:
- Sync service: Push update to all WebSocket connections for `user_id`

## Idempotency Contract

All consumers MUST implement idempotency:

1. Extract `event_id` from the event `data` field
2. Check if `event_id` exists in the dedup store (Dapr state store, key: `dedup:{service}:{event_id}`)
3. If exists: return `{"status": "DROP"}` (acknowledge without processing)
4. If not exists: process event, then store `event_id` with TTL of 24 hours
5. Return `{"status": "SUCCESS"}` to acknowledge

## Error Handling Contract

Dapr event handler HTTP responses:

| Status Code | Dapr Behavior |
|-------------|---------------|
| 200 + `{"status": "SUCCESS"}` | Message acknowledged, removed from queue |
| 200 + `{"status": "DROP"}` | Message dropped (acknowledged without processing) |
| 200 + `{"status": "RETRY"}` | Message redelivered after backoff |
| 404 | Message dropped (topic/route not found) |
| 5xx | Message redelivered after backoff |

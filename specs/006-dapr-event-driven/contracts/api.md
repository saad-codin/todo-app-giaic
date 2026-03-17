# API Contracts

**Feature**: 006-dapr-event-driven | **Date**: 2026-02-09

## Existing Endpoints (Unchanged)

These endpoints continue to work exactly as before. The only change is that they now **additionally publish events** after successful database operations.

| Method | Path | Change |
|--------|------|--------|
| GET | `/api/tasks` | No change |
| POST | `/api/tasks` | Publishes `task.created` + `task.sync` events after commit |
| GET | `/api/tasks/{id}` | No change |
| PATCH | `/api/tasks/{id}` | Publishes `task.updated` + `task.sync` events after commit |
| DELETE | `/api/tasks/{id}` | Publishes `task.deleted` + `task.sync` events after commit |
| POST | `/api/tasks/{id}/complete` | Publishes `task.completed` + `task.sync` events after commit |
| POST | `/api/tasks/{id}/incomplete` | Publishes `task.updated` + `task.sync` events after commit |
| POST | `/api/auth/signup` | No change |
| POST | `/api/auth/signin` | No change |
| GET | `/api/auth/me` | No change |
| POST | `/api/chat` | No change |
| GET | `/health` | No change |

## New Endpoints

### WebSocket: Real-Time Sync

```
WS /ws?token={jwt_token}
```

**Authentication**: JWT token passed as query parameter (validated on connection upgrade).

**Connection flow**:
1. Client connects with JWT token
2. Server validates token, extracts `user_id`
3. Server adds connection to user's connection set
4. Server sends heartbeat ping every 30 seconds
5. Client receives task updates as JSON messages

**Server -> Client messages**:

```typescript
// Task update notification
interface WsTaskUpdate {
  type: "task_update";
  action: "created" | "updated" | "completed" | "deleted";
  task: TaskResponse | null;  // null for deleted
  timestamp: string;
}

// Reminder notification
interface WsReminder {
  type: "reminder";
  task_id: string;
  task_description: string;
  reminder_type: "24h" | "1h";
  due_date: string;
  due_time: string | null;
  timestamp: string;
}

// Connection status
interface WsStatus {
  type: "connected" | "error";
  message: string;
}
```

**Client -> Server messages**:

```typescript
// Heartbeat response (optional)
interface WsPong {
  type: "pong";
}
```

**Error cases**:
- Invalid/expired token: Connection closed with code 4001
- Server error: Connection closed with code 1011, client should reconnect

### Health Endpoints (New Services)

Each new microservice exposes:

```
GET /health
Response: { "status": "healthy", "service": "<name>", "dapr": true|false }
```

| Service | Port | Health Path |
|---------|------|-------------|
| Reminder | 8001 | `/health` |
| Recurring | 8002 | `/health` |
| Sync | 8003 | `/health` |

### Dapr Event Handler Endpoints (Internal)

These are called by Dapr sidecars, not by external clients.

**Reminder Service**:
```
POST /events/task
Body: CloudEvents envelope with task event data
Response: { "status": "SUCCESS" | "DROP" | "RETRY" }
```

**Recurring Service**:
```
POST /events/task
Body: CloudEvents envelope with task event data
Response: { "status": "SUCCESS" | "DROP" | "RETRY" }
```

**Sync Service**:
```
POST /events/sync
Body: CloudEvents envelope with task sync data
Response: { "status": "SUCCESS" | "DROP" | "RETRY" }

POST /events/reminder
Body: CloudEvents envelope with reminder data
Response: { "status": "SUCCESS" | "DROP" | "RETRY" }
```

## Request/Response Schema Updates

### TaskCreate (Updated)

Add optional recurrence rule fields:

```typescript
interface TaskCreate {
  description: string;
  priority?: "urgent" | "high" | "medium" | "low";  // Added "urgent"
  tags?: string[];
  dueDate?: string;
  dueTime?: string;
  reminderTime?: string;
  recurrence?: "none" | "daily" | "weekly" | "monthly";
  // NEW fields for advanced recurrence
  recurrenceInterval?: number;      // Default 1
  recurrenceDayOfWeek?: number;     // 0=Mon..6=Sun
  recurrenceDayOfMonth?: number;    // 1-28
  isCompletionBased?: boolean;      // Default false
}
```

### TaskResponse (Updated)

Add recurrence details:

```typescript
interface TaskResponse {
  id: string;
  userId: string;
  description: string;
  completed: boolean;
  priority: "urgent" | "high" | "medium" | "low";  // Added "urgent"
  tags: string[];
  dueDate: string | null;
  dueTime: string | null;
  reminderTime: string | null;
  recurrence: "none" | "daily" | "weekly" | "monthly";
  // NEW fields
  isCompletionBased: boolean;
  nextOccurrence: string | null;    // YYYY-MM-DD from recurrence rule
  createdAt: string;
  updatedAt: string;
}
```

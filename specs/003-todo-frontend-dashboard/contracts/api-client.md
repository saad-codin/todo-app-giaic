# API Client Contract: Todo App Frontend

**Feature**: 003-todo-frontend-dashboard
**Date**: 2026-01-10
**Purpose**: Define expected backend API endpoints consumed by frontend

## Base Configuration

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response (201)**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2026-01-10T12:00:00Z"
  }
}
```

**Errors**:
- 400: Invalid input (validation failed)
- 409: Email already exists

---

### POST /api/auth/signin

Authenticate user and return JWT.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200)**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2026-01-10T12:00:00Z"
  }
}
```

*Note: JWT token set in httpOnly cookie by Better Auth*

**Errors**:
- 401: Invalid credentials

---

### POST /api/auth/signout

Sign out current user.

**Response (200)**:
```json
{
  "success": true
}
```

---

### GET /api/auth/me

Get current authenticated user.

**Response (200)**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2026-01-10T12:00:00Z"
  }
}
```

**Errors**:
- 401: Not authenticated

---

## Task Endpoints

All task endpoints require authentication (JWT in cookie).

### GET /api/tasks

List tasks for authenticated user.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Filter by keyword in description |
| completed | boolean | Filter by completion status |
| priority | string | Filter by priority (high/medium/low) |
| tag | string | Filter by tag name |
| startDate | string | Filter tasks due on or after (YYYY-MM-DD) |
| endDate | string | Filter tasks due on or before (YYYY-MM-DD) |
| sortBy | string | Sort field (dueDate/priority/createdAt) |
| sortOrder | string | Sort direction (asc/desc) |
| limit | number | Max results (default: 100) |
| offset | number | Pagination offset (default: 0) |

**Response (200)**:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "userId": "uuid",
      "description": "Buy groceries",
      "completed": false,
      "priority": "high",
      "tags": ["shopping", "home"],
      "dueDate": "2026-01-15",
      "dueTime": "14:00",
      "reminderTime": "2026-01-15T13:00:00Z",
      "recurrence": "weekly",
      "createdAt": "2026-01-10T12:00:00Z",
      "updatedAt": "2026-01-10T12:00:00Z"
    }
  ],
  "total": 42,
  "hasMore": true
}
```

---

### POST /api/tasks

Create a new task.

**Request**:
```json
{
  "description": "Buy groceries",
  "priority": "high",
  "tags": ["shopping", "home"],
  "dueDate": "2026-01-15",
  "dueTime": "14:00",
  "reminderTime": "2026-01-15T13:00:00Z",
  "recurrence": "weekly"
}
```

**Response (201)**:
```json
{
  "task": {
    "id": "uuid",
    "userId": "uuid",
    "description": "Buy groceries",
    "completed": false,
    "priority": "high",
    "tags": ["shopping", "home"],
    "dueDate": "2026-01-15",
    "dueTime": "14:00",
    "reminderTime": "2026-01-15T13:00:00Z",
    "recurrence": "weekly",
    "createdAt": "2026-01-10T12:00:00Z",
    "updatedAt": "2026-01-10T12:00:00Z"
  }
}
```

**Errors**:
- 400: Validation failed
- 401: Not authenticated

---

### GET /api/tasks/:id

Get a single task by ID.

**Response (200)**:
```json
{
  "task": { /* Task object */ }
}
```

**Errors**:
- 401: Not authenticated
- 404: Task not found

---

### PATCH /api/tasks/:id

Update a task.

**Request** (partial update):
```json
{
  "description": "Buy organic groceries",
  "completed": true
}
```

**Response (200)**:
```json
{
  "task": { /* Updated Task object */ }
}
```

**Errors**:
- 400: Validation failed
- 401: Not authenticated
- 404: Task not found

---

### DELETE /api/tasks/:id

Delete a task.

**Response (200)**:
```json
{
  "success": true
}
```

**Errors**:
- 401: Not authenticated
- 404: Task not found

---

### POST /api/tasks/:id/complete

Mark task complete (handles recurring task creation).

**Response (200)**:
```json
{
  "task": { /* Completed Task object */ },
  "nextOccurrence": { /* New Task if recurring, null otherwise */ }
}
```

---

### POST /api/tasks/:id/incomplete

Mark task incomplete.

**Response (200)**:
```json
{
  "task": { /* Task object with completed: false */ }
}
```

---

## Frontend API Client Implementation

```typescript
// lib/api.ts

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include', // Include cookies for JWT
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(response.status, error.message || 'Request failed');
  }

  return response.json();
}

export const api = {
  // Auth
  signUp: (data: SignUpRequest) =>
    fetchWithAuth<AuthResponse>('/api/auth/signup', { method: 'POST', body: JSON.stringify(data) }),
  signIn: (data: SignInRequest) =>
    fetchWithAuth<AuthResponse>('/api/auth/signin', { method: 'POST', body: JSON.stringify(data) }),
  signOut: () =>
    fetchWithAuth<{ success: boolean }>('/api/auth/signout', { method: 'POST' }),
  getMe: () =>
    fetchWithAuth<{ user: User }>('/api/auth/me'),

  // Tasks
  getTasks: (params?: ListTasksRequest) =>
    fetchWithAuth<ListTasksResponse>(`/api/tasks?${new URLSearchParams(params as any)}`),
  getTask: (id: string) =>
    fetchWithAuth<{ task: Task }>(`/api/tasks/${id}`),
  createTask: (data: CreateTaskRequest) =>
    fetchWithAuth<CreateTaskResponse>('/api/tasks', { method: 'POST', body: JSON.stringify(data) }),
  updateTask: (id: string, data: UpdateTaskRequest) =>
    fetchWithAuth<UpdateTaskResponse>(`/api/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteTask: (id: string) =>
    fetchWithAuth<{ success: boolean }>(`/api/tasks/${id}`, { method: 'DELETE' }),
  completeTask: (id: string) =>
    fetchWithAuth<{ task: Task; nextOccurrence: Task | null }>(`/api/tasks/${id}/complete`, { method: 'POST' }),
  incompleteTask: (id: string) =>
    fetchWithAuth<{ task: Task }>(`/api/tasks/${id}/incomplete`, { method: 'POST' }),
};
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Description is required",
  "details": {
    "field": "description",
    "constraint": "required"
  }
}
```

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | VALIDATION_ERROR | Invalid input data |
| 401 | UNAUTHORIZED | Not authenticated |
| 403 | FORBIDDEN | Not allowed to access resource |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 500 | INTERNAL_ERROR | Server error |

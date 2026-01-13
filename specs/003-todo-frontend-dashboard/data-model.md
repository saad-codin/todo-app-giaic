# Data Model: Todo App Frontend Dashboard

**Feature**: 003-todo-frontend-dashboard
**Date**: 2026-01-10
**Purpose**: Define frontend TypeScript types and state models

## Core Entities

### User

Represents an authenticated user in the frontend.

```typescript
interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string; // ISO 8601
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
```

**Source**: Backend `/api/auth/me` endpoint

---

### Task

Represents a todo item with all attributes.

```typescript
type Priority = 'high' | 'medium' | 'low';
type Recurrence = 'none' | 'daily' | 'weekly' | 'monthly';

interface Task {
  id: string;
  userId: string;
  description: string;
  completed: boolean;
  priority: Priority;
  tags: string[];
  dueDate: string | null;      // ISO 8601 date (YYYY-MM-DD)
  dueTime: string | null;      // ISO 8601 time (HH:MM)
  reminderTime: string | null; // ISO 8601 datetime
  recurrence: Recurrence;
  createdAt: string;           // ISO 8601 datetime
  updatedAt: string;           // ISO 8601 datetime
}
```

**Validation Rules**:
- `description`: Required, 1-500 characters
- `priority`: Must be 'high', 'medium', or 'low'
- `tags`: Array of strings, each 1-50 characters, max 10 tags
- `dueDate`: Optional, valid ISO date format
- `dueTime`: Optional, valid ISO time format (requires dueDate)
- `recurrence`: Must be 'none', 'daily', 'weekly', or 'monthly'

---

### Tag

Represents a user-defined category label.

```typescript
interface Tag {
  name: string;       // Normalized (lowercase, trimmed)
  count: number;      // Number of tasks with this tag
  color?: string;     // Optional color for display
}
```

**Derived from**: Aggregated from Task.tags across all user tasks

---

## UI State Models

### Task List State

```typescript
interface TaskFilters {
  search: string;
  status: 'all' | 'completed' | 'incomplete';
  priority: Priority | 'all';
  tag: string | null;
}

interface TaskSort {
  field: 'dueDate' | 'priority' | 'alphabetical' | 'createdAt';
  direction: 'asc' | 'desc';
}

interface TaskListState {
  tasks: Task[];
  filters: TaskFilters;
  sort: TaskSort;
  isLoading: boolean;
  error: string | null;
}
```

---

### Calendar State

```typescript
type CalendarView = 'month' | 'week';

interface CalendarState {
  view: CalendarView;
  currentDate: Date;           // Reference date for display
  selectedDate: Date | null;   // Date user clicked on
}

interface DayTasks {
  date: string;               // YYYY-MM-DD
  tasks: Task[];
  completedCount: number;
  totalCount: number;
  progressPercent: number;
}
```

---

### Sidebar State

```typescript
interface SidebarState {
  isCollapsed: boolean;
  activeShortcut: string | null;
}
```

---

### Notification State

```typescript
type NotificationPermission = 'default' | 'granted' | 'denied';

interface NotificationState {
  permission: NotificationPermission;
  scheduledReminders: Array<{
    taskId: string;
    reminderTime: string;
    timeoutId: number;
  }>;
}
```

---

## API Request/Response Types

### Create Task

```typescript
interface CreateTaskRequest {
  description: string;
  priority?: Priority;
  tags?: string[];
  dueDate?: string;
  dueTime?: string;
  reminderTime?: string;
  recurrence?: Recurrence;
}

interface CreateTaskResponse {
  task: Task;
}
```

---

### Update Task

```typescript
interface UpdateTaskRequest {
  description?: string;
  completed?: boolean;
  priority?: Priority;
  tags?: string[];
  dueDate?: string | null;
  dueTime?: string | null;
  reminderTime?: string | null;
  recurrence?: Recurrence;
}

interface UpdateTaskResponse {
  task: Task;
}
```

---

### List Tasks

```typescript
interface ListTasksRequest {
  search?: string;
  completed?: boolean;
  priority?: Priority;
  tag?: string;
  startDate?: string;
  endDate?: string;
  sortBy?: 'dueDate' | 'priority' | 'createdAt';
  sortOrder?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

interface ListTasksResponse {
  tasks: Task[];
  total: number;
  hasMore: boolean;
}
```

---

### Authentication

```typescript
interface SignUpRequest {
  email: string;
  password: string;
  name?: string;
}

interface SignInRequest {
  email: string;
  password: string;
}

interface AuthResponse {
  user: User;
  token: string; // JWT (handled by Better Auth)
}

interface AuthError {
  code: string;
  message: string;
}
```

---

## Zod Validation Schemas

```typescript
import { z } from 'zod';

export const taskSchema = z.object({
  description: z.string().min(1).max(500),
  priority: z.enum(['high', 'medium', 'low']).default('medium'),
  tags: z.array(z.string().min(1).max(50)).max(10).default([]),
  dueDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).nullable().optional(),
  dueTime: z.string().regex(/^\d{2}:\d{2}$/).nullable().optional(),
  reminderTime: z.string().datetime().nullable().optional(),
  recurrence: z.enum(['none', 'daily', 'weekly', 'monthly']).default('none'),
});

export const signUpSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
  name: z.string().min(1).max(100).optional(),
});

export const signInSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});
```

---

## State Transitions

### Task Lifecycle

```
[Draft] --create--> [Active/Incomplete]
                          |
                          v
                    [Completed] --toggle--> [Active/Incomplete]
                          |
                          v (if recurring)
                    [New Instance Created]
```

### Authentication Flow

```
[Unauthenticated] --signup/signin--> [Authenticated]
                                          |
                                          v
                                    [Session Active]
                                          |
                        signout/expiry    |
                          <---------------+
```

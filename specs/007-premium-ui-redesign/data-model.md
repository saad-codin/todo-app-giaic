# Data Model: Premium UI/UX Redesign

**Feature**: 007-premium-ui-redesign
**Date**: 2026-02-22
**Note**: This is a frontend-only redesign. No new backend data models are introduced. All backend API schemas remain unchanged. This document captures client-side state entities introduced by the redesign.

---

## Unchanged Backend Entities

The following entities exist in the backend and are unchanged by this redesign:

### Task (existing)
```typescript
// From frontend/src/types/task.ts
interface Task {
  id: string;
  description: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  tags: string[];
  due_date: string | null;      // ISO 8601 date
  due_time: string | null;      // HH:MM
  recurrence: string | null;   // 'daily' | 'weekly' | 'monthly' | null
  is_completion_based: boolean;
  next_occurrence: string | null;
  created_at: string;
  updated_at: string;
  user_id: string;
}
```

### User (existing)
```typescript
interface User {
  id: string;
  email: string;
  name: string | null;
}
```

---

## New Client-Side Entities

### Theme

Managed by `next-themes`. No explicit TypeScript type needed — the library handles persistence.

**Storage**: `localStorage` key `theme` (set automatically by next-themes)
**Values**: `'light' | 'dark' | 'system'`
**Default**: `'system'` (OS preference)

### AppNotification (existing from 006, in use)

Already implemented in `components/ui/NotificationBell.tsx` during the 006 phase.

```typescript
interface AppNotification {
  id: string;
  type: 'reminder' | 'info';
  message: string;
  timestamp: Date;
  read: boolean;
  taskId?: string;
}
```

**Storage**: React state in `dashboard/page.tsx` (ephemeral, cleared on refresh)
**Max entries**: 50 (trimmed on add)
**Source**: WebSocket `reminder` messages from the sync service

### SidebarState (implicit)

```typescript
// Local component state, not persisted
interface SidebarState {
  isOpen: boolean;       // Desktop: always true; Mobile: toggled
  isMobileOpen: boolean; // Mobile overlay open/closed
}
```

**Storage**: React state in `dashboard/layout.tsx`

---

## State Transitions

### Theme Toggle

```
system → [user clicks toggle] → light | dark
light  → [user clicks toggle] → dark
dark   → [user clicks toggle] → light
```

### Sidebar (Mobile)

```
closed → [hamburger click] → open overlay
open   → [backdrop click | nav item click | X button] → closed
```

### Task Completion Animation

```
incomplete → [checkbox click] → animating → complete
complete   → [checkbox click] → animating → incomplete
```
Animation state is transient (CSS/framer-motion transition, no explicit state variable needed).

---

## Entity Relationships

```
User
 └─ has many Tasks
 └─ has Theme preference (localStorage)
 └─ has AppNotifications[] (runtime state, resets on refresh)

Dashboard Page
 └─ renders SidebarState
 └─ renders Tasks[] (from useTasks hook → React Query cache)
 └─ renders AppNotifications[] (useState)
```

---

## No Schema Migrations Required

This feature modifies zero backend models and zero database schemas. All changes are confined to the Next.js frontend presentation layer.

# API Contracts: Premium UI/UX Redesign

**Feature**: 007-premium-ui-redesign
**Note**: This redesign is purely a frontend visual layer change. **Zero new API endpoints are introduced.** All existing API endpoints are consumed unchanged.

---

## Existing API (Unchanged)

All backend API contracts remain identical. See `backend/CLAUDE.md` for full endpoint documentation.

The frontend `lib/api.ts` file is **not modified** by this redesign.

### Consumed Endpoints (for reference)

| Method | Path | Used By |
|--------|------|---------|
| `GET` | `/api/auth/me` | Auth guard in dashboard layout |
| `POST` | `/api/auth/signin` | Sign-in form |
| `POST` | `/api/auth/signup` | Sign-up form |
| `POST` | `/api/auth/signout` | Sidebar sign-out button |
| `GET` | `/api/tasks` | Task list on dashboard |
| `POST` | `/api/tasks` | Task creation form |
| `PATCH` | `/api/tasks/:id` | Task edit form |
| `DELETE` | `/api/tasks/:id` | Task delete button |
| `POST` | `/api/tasks/:id/complete` | Task completion checkbox |
| `POST` | `/api/tasks/:id/incomplete` | Task undo completion |
| `POST` | `/api/chat` | AI Assistant chat |

---

## WebSocket Contract (Unchanged)

Real-time sync remains via the sync service WebSocket. Message format unchanged:

```typescript
// Reminder notification message (from sync service)
{
  type: 'reminder';
  task_id: string;
  task_description: string;
  due_date: string;
}

// Task update message
{
  type: 'task_update';
  task: Task;
}
```

---

## No New Contracts

Since this is a pure UI redesign with no new features that require backend changes, no new OpenAPI schemas or contracts are needed.

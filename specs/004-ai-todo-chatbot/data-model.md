# Data Model: AI-Powered Todo Chatbot

**Feature**: 004-ai-todo-chatbot
**Date**: 2026-01-13
**Status**: Complete

## Overview

This document defines the data entities required for the AI-powered todo chatbot. It extends the existing Phase II data model with conversation tracking entities.

---

## Existing Entities (from Phase II)

### User

Already exists in Phase II. No modifications required.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | string | unique, indexed | User's email |
| name | string | optional | Display name |
| hashed_password | string | required | Password hash |
| created_at | timestamp | default: now | Account creation time |

### Task

Already exists in Phase II. No modifications required.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User, indexed | Owner |
| description | string | max 500 chars | Task description |
| completed | boolean | default: false | Completion status |
| priority | enum | low/medium/high, default: medium | Priority level |
| tags | string[] | JSON array | Tags for organization |
| due_date | string | YYYY-MM-DD, nullable | Due date |
| due_time | string | HH:MM, nullable | Due time |
| reminder_time | timestamp | nullable | Reminder timestamp |
| recurrence | enum | none/daily/weekly/monthly | Recurrence pattern |
| created_at | timestamp | default: now | Creation time |
| updated_at | timestamp | auto-update | Last modification |

---

## New Entities (Phase III)

### Conversation

Represents a chat session between a user and the chatbot.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User, indexed | Owner of conversation |
| title | string | nullable, max 100 | Optional title (auto-generated) |
| created_at | timestamp | default: now | Conversation start time |
| updated_at | timestamp | auto-update | Last message time |

**Relationships**:
- One User has many Conversations
- One Conversation has many ChatMessages

**Validation Rules**:
- user_id must reference existing user
- Conversation cannot be empty (must have at least one message)

### ChatMessage

Individual message within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| conversation_id | UUID | FK → Conversation, indexed | Parent conversation |
| role | enum | user/assistant/tool | Message sender type |
| content | text | required | Message content |
| tool_calls | JSON | nullable | Tool invocations (for assistant) |
| tool_call_id | string | nullable | ID when role=tool |
| created_at | timestamp | default: now, indexed | Message timestamp |

**Relationships**:
- One Conversation has many ChatMessages (ordered by created_at)

**Validation Rules**:
- role must be one of: user, assistant, tool
- content cannot be empty
- tool_calls only valid when role=assistant
- tool_call_id only valid when role=tool

**Indexes**:
- (conversation_id, created_at) for efficient message retrieval

---

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│     User     │       │     Task     │       │ Conversation │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │──┬───▶│ id (PK)      │       │ id (PK)      │
│ email        │  │    │ user_id (FK) │◀──────│ user_id (FK) │◀─┐
│ name         │  │    │ description  │       │ title        │  │
│ hashed_pass  │  │    │ completed    │       │ created_at   │  │
│ created_at   │  │    │ priority     │       │ updated_at   │  │
└──────────────┘  │    │ tags         │       └──────┬───────┘  │
                  │    │ due_date     │              │          │
                  │    │ due_time     │              │ 1:N      │
                  │    │ recurrence   │              ▼          │
                  │    │ created_at   │       ┌──────────────┐  │
                  │    │ updated_at   │       │ ChatMessage  │  │
                  │    └──────────────┘       ├──────────────┤  │
                  │                           │ id (PK)      │  │
                  │    1:N                    │ conversation │  │
                  └──────────────────────────▶│ _id (FK)     │  │
                                              │ role         │  │
                                              │ content      │  │
                                              │ tool_calls   │  │
                                              │ tool_call_id │  │
                                              │ created_at   │  │
                                              └──────────────┘  │
                                                                │
                  User ─────────────────────────────────────────┘
                       (via Conversation.user_id)
```

---

## State Transitions

### Conversation Lifecycle

```
[Created] ─── first message ───▶ [Active] ─── time passes ───▶ [Inactive]
                                     │
                                     └─── user sends message ───▶ [Active]
```

- Conversations don't have explicit status; activity determined by last message time
- No deletion - conversations persist for context retrieval

### ChatMessage Flow

```
User Message ───▶ [Saved] ───▶ Agent Processing ───▶ Tool Calls ───▶ Tool Results ───▶ Assistant Response
     │                                 │                  │              │                    │
     └── role: user                    │                  └── role: assistant                 └── role: assistant
                                       │                      (with tool_calls)                   (final response)
                                       │
                                       └── If tools invoked: role: tool (with tool_call_id)
```

---

## Query Patterns

### Load Conversation History (per request)

```sql
SELECT * FROM chat_message
WHERE conversation_id = :conv_id
ORDER BY created_at DESC
LIMIT 10;
```

### Get or Create Conversation

```sql
-- Find active conversation for user
SELECT * FROM conversation
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 1;

-- If none or stale, create new
INSERT INTO conversation (id, user_id, created_at, updated_at)
VALUES (:id, :user_id, NOW(), NOW());
```

### User Isolation Check

All queries MUST include user_id filter:

```sql
-- Tasks: always filtered by user
SELECT * FROM task WHERE user_id = :user_id AND ...;

-- Conversations: always filtered by user
SELECT * FROM conversation WHERE user_id = :user_id;

-- Messages: via conversation (implicitly user-scoped)
SELECT m.* FROM chat_message m
JOIN conversation c ON m.conversation_id = c.id
WHERE c.user_id = :user_id;
```

---

## Migration Notes

### New Tables Required

1. `conversation` - Parent table for chat sessions
2. `chat_message` - Individual messages with role tracking

### Indexes Required

1. `conversation.user_id` - For user isolation queries
2. `chat_message.conversation_id` - For message retrieval
3. `chat_message.(conversation_id, created_at)` - For ordered retrieval

### No Breaking Changes

- Existing `user` and `task` tables unchanged
- New tables only; no migrations of existing data
- Phase II functionality preserved

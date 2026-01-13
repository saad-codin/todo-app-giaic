# Research: AI-Powered Todo Chatbot

**Feature**: 004-ai-todo-chatbot
**Date**: 2026-01-13
**Status**: Complete

## Overview

This document captures research findings and technology decisions for implementing the AI-powered todo chatbot using OpenAI Agents SDK, MCP tools, and a stateless backend architecture.

---

## 1. OpenAI Agents SDK Integration

### Decision
Use OpenAI Agents SDK with function calling for intent recognition and task operation execution.

### Rationale
- Official SDK recommended by constitution for Phase III
- Native support for tool/function definitions
- Built-in conversation management
- Handles prompt engineering complexity

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Raw OpenAI API | More boilerplate; SDK abstracts complexity |
| LangChain | Not in constitution's allowed dependencies |
| Custom intent classifier | Over-engineering; SDK handles this |

### Implementation Pattern
```python
from openai import OpenAI
from agents import Agent, Runner

# Define agent with MCP tools
agent = Agent(
    name="TodoAssistant",
    instructions="You help users manage their todo tasks...",
    tools=[create_task, list_tasks, complete_task, update_task, delete_task]
)

# Run agent per request (stateless)
runner = Runner(agent)
response = runner.run(user_message, conversation_history)
```

---

## 2. MCP (Model Context Protocol) Tools

### Decision
Implement MCP tools as Python functions decorated for OpenAI function calling, each performing a single task operation.

### Rationale
- MCP SDK provides standard tool definition format
- Each tool maps to one task CRUD operation
- Tools are stateless - all state in database
- Clear separation between AI reasoning and data mutation

### Tool Definitions

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_task` | Add new task | description, priority?, due_date?, due_time?, tags? |
| `list_tasks` | Get user's tasks | filter_completed?, filter_priority?, filter_date? |
| `complete_task` | Mark task done | task_id or description_match |
| `update_task` | Modify task | task_id, fields_to_update |
| `delete_task` | Remove task | task_id or description_match |
| `search_tasks` | Find matching tasks | query_string |

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Single "manage_task" tool | Less precise; harder for AI to select |
| Direct DB access in prompts | Violates stateless requirement; security risk |

---

## 3. Conversation Persistence Strategy

### Decision
Store conversation history in PostgreSQL with per-user isolation. Load last N messages on each request.

### Rationale
- Stateless backend requirement: no in-memory sessions
- Database already exists from Phase II (Neon PostgreSQL)
- Enables context continuity across server restarts
- Supports the "10 consecutive messages" success criteria

### Data Model
```
Conversation:
  - id: UUID
  - user_id: FK to User
  - created_at: timestamp
  - updated_at: timestamp

ChatMessage:
  - id: UUID
  - conversation_id: FK to Conversation
  - role: enum('user', 'assistant', 'tool')
  - content: text
  - tool_calls: JSON (optional, for tool invocations)
  - created_at: timestamp
```

### Context Window Strategy
- Load last 10 messages per request (configurable)
- Older messages summarized or excluded
- Tool call results included in context

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Redis session store | Adds dependency; not in Phase III allowed list |
| File-based storage | Not scalable; violates Phase II+ constraints |
| Client-side storage | Security risk; conversation tampering possible |

---

## 4. Chat Endpoint Design

### Decision
Single POST endpoint `/api/chat` that accepts user message and returns assistant response.

### Rationale
- Matches spec requirement FR-013
- Simple, RESTful design
- JWT authentication via existing middleware
- User ID from JWT, not URL path (security)

### Request/Response Format
```yaml
POST /api/chat
Authorization: Bearer <jwt>

Request:
  message: string (user's natural language input)
  conversation_id?: string (optional, for continuing conversation)

Response:
  response: string (assistant's message)
  conversation_id: string
  tool_results?: array (what actions were taken)
```

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| WebSocket streaming | Out of scope; spec excludes real-time streaming |
| GraphQL subscription | Over-engineering for simple chat |
| `/api/{user_id}/chat` | User ID in JWT is more secure |

---

## 5. Frontend Chat Interface

### Decision
Use OpenAI ChatKit components for the chat UI, integrated into existing Next.js frontend.

### Rationale
- Constitution specifies OpenAI ChatKit
- Pre-built components reduce frontend work
- Consistent chat UX patterns
- Integrates with existing auth flow

### Component Structure
```
/chat
  └── page.tsx          # Chat page with ChatKit
      ├── MessageList   # Displays conversation
      ├── MessageInput  # User input with send
      └── ChatHeader    # Title, clear conversation
```

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Custom chat components | Unnecessary; ChatKit provides what's needed |
| Third-party chat widget | Not in allowed dependencies |

---

## 6. Error Handling Strategy

### Decision
Graceful degradation with user-friendly error messages. AI errors don't crash the system.

### Rationale
- SC-008 requires helpful messages 100% of the time
- Phase II functionality must remain available
- Users shouldn't see technical errors

### Error Categories
| Error Type | User Message | System Action |
|------------|--------------|---------------|
| AI service unavailable | "I'm having trouble thinking right now. Try again in a moment." | Log error, return graceful response |
| Task not found | "I couldn't find a task matching that. Here are your current tasks:" | Show task list |
| Authentication failed | "Please sign in to continue." | Redirect to login |
| Database error | "I'm having trouble accessing your tasks. Please try again." | Log error, retry once |
| Rate limit | "I'm getting too many requests. Please wait a moment." | Return 429 with retry-after |

---

## 7. User Isolation & Security

### Decision
All queries filtered by user_id from JWT. No cross-user data access possible.

### Rationale
- SC-006 requires zero cross-user data access
- FR-009 mandates user isolation
- JWT already contains user identity

### Implementation
```python
# Every database query includes user filter
def get_user_tasks(user_id: str, session: Session):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

# MCP tools receive user_id from request context
@tool
def list_tasks(user_id: str, ...):
    # user_id injected by framework, not from AI
```

---

## 8. Testing Strategy

### Decision
Combination of unit tests (tools), integration tests (endpoint), and deterministic prompt tests (AI behavior).

### Rationale
- Constitution Phase III requires AI behavior validation
- Deterministic test prompts verify intent mapping
- Core functionality tests ensure no regressions

### Test Categories
| Category | What's Tested | Approach |
|----------|---------------|----------|
| Unit | MCP tools | pytest with mock DB |
| Integration | /api/chat endpoint | pytest with test DB |
| AI Behavior | Intent recognition | Fixed prompts, expected tool calls |
| Regression | Phase II API | Existing tests must pass |

### Deterministic Prompts
```python
TEST_CASES = [
    ("Add buy milk to my list", "create_task", {"description": "buy milk"}),
    ("Show my tasks", "list_tasks", {}),
    ("Mark buy milk as done", "complete_task", {"description_match": "buy milk"}),
]
```

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| AI SDK | OpenAI Agents SDK | Constitution requirement |
| Tools | 6 MCP tools (CRUD + search) | One tool per operation |
| Storage | PostgreSQL conversations | Stateless backend |
| Endpoint | POST /api/chat | Simple REST |
| Frontend | OpenAI ChatKit | Constitution requirement |
| Errors | Graceful degradation | User-friendly always |
| Security | JWT user isolation | Zero cross-user access |
| Testing | Deterministic prompts | AI behavior validation |

# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `004-ai-todo-chatbot` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-todo-chatbot/spec.md`

## Summary

Implement an AI-powered conversational todo chatbot that enables users to manage tasks through natural language. The system uses a stateless FastAPI backend with OpenAI Agents SDK for intent recognition and MCP tools for task operations. Conversation history is persisted in Neon PostgreSQL for context continuity across requests.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, OpenAI ChatKit (frontend)
**Storage**: Neon PostgreSQL (existing from Phase II, extended with conversation tables)
**Testing**: pytest (backend), manual chat testing (AI behavior validation per constitution)
**Target Platform**: Web application (browser-based chat interface)
**Project Type**: Web (frontend + backend)
**Performance Goals**: 95% of requests < 3 seconds, 100 concurrent users
**Constraints**: Stateless backend, user isolation, JWT authentication, English only
**Scale/Scope**: 100 concurrent users, ~10 message context window

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Requirements Compliance

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Use OpenAI ChatKit, Agents SDK, MCP SDK correctly and minimally | ✅ PASS | Using only specified SDKs for AI features |
| AI features MUST be additive, not required for core functionality | ✅ PASS | Core task CRUD remains accessible via existing API |
| All AI outputs MUST be explainable/traceable to user intent | ✅ PASS | Conversation logged, MCP tool calls logged |
| Core todo CRUD MUST work if AI services unavailable | ✅ PASS | Existing REST API from Phase II preserved |

### Phase III Constraints Compliance

| Constraint | Status | Evidence |
|------------|--------|----------|
| No AI features may replace deterministic core functionality | ✅ PASS | Chat is additive; REST API unchanged |
| AI dependencies MUST be optional at runtime | ✅ PASS | Chat endpoint separate from core API |
| AI prompts and responses MUST be logged | ✅ PASS | Conversation table persists all messages |

### Core Principles Compliance

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Correctness First | ✅ PASS | Spec-driven with acceptance scenarios |
| II. Deterministic Behavior | ✅ PASS | AI isolated; core logic deterministic |
| III. Incremental Evolution | ✅ PASS | Builds on Phase II; no regressions |
| IV. Simplicity Before Scale | ✅ PASS | Minimal MCP tools; no over-engineering |
| V. Observability | ✅ PASS | Conversation logging; error handling |

### Technology Constraints

| Allowed for Phase III | Used | Status |
|----------------------|------|--------|
| OpenAI ChatKit | Yes | ✅ Frontend |
| OpenAI Agents SDK | Yes | ✅ Backend AI |
| Official MCP SDK | Yes | ✅ Tool invocation |

**Constitution Gate: PASSED** - Proceeding to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-todo-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.yaml    # OpenAPI schema for chat endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)
backend/
├── main.py              # FastAPI app (existing, extended)
├── models.py            # SQLModel models (existing, extended)
├── db.py                # Database connection (existing)
├── auth.py              # JWT auth (existing)
├── routes/
│   ├── auth.py          # Auth endpoints (existing)
│   ├── tasks.py         # Task CRUD endpoints (existing)
│   └── chat.py          # NEW: Chat endpoint
├── mcp/                 # NEW: MCP tools
│   ├── __init__.py
│   ├── server.py        # MCP server setup
│   └── tools.py         # Task operation tools
├── agent/               # NEW: AI agent
│   ├── __init__.py
│   └── runner.py        # Agent with MCP tools
└── tests/
    └── test_chat.py     # Chat endpoint tests

frontend/
├── src/
│   ├── app/
│   │   └── chat/        # NEW: Chat page
│   │       └── page.tsx
│   ├── components/
│   │   └── chat/        # NEW: Chat components
│   │       ├── ChatInterface.tsx
│   │       ├── MessageList.tsx
│   │       └── MessageInput.tsx
│   └── lib/
│       └── api.ts       # Extended with chat endpoint
└── tests/
```

**Structure Decision**: Extending existing Phase II web application structure with new chat-specific modules in both frontend and backend. MCP tools and agent logic isolated in dedicated directories.

## Complexity Tracking

> No constitution violations requiring justification.

| Item | Decision | Rationale |
|------|----------|-----------|
| Separate MCP directory | Organized | Tools are conceptually distinct from routes |
| Separate agent directory | Organized | Agent logic distinct from HTTP handling |
| ChatKit for frontend | Required | Constitution specifies OpenAI ChatKit |

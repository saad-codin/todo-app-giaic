---
id: "0002"
title: "ai-chatbot-implementation-plan"
stage: plan
date: 2026-01-13
surface: claude-code
model: claude-opus-4-5-20251101
feature: 004-ai-todo-chatbot
branch: 004-ai-todo-chatbot
user: user
command: /sp.plan
labels: [plan, ai-chatbot, mcp, architecture]
links:
  spec: specs/004-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-ai-todo-chatbot/plan.md
  - specs/004-ai-todo-chatbot/research.md
  - specs/004-ai-todo-chatbot/data-model.md
  - specs/004-ai-todo-chatbot/quickstart.md
  - specs/004-ai-todo-chatbot/contracts/chat-api.yaml
tests:
  - null
---

## Prompt

AI-Powered Todo Chatbot (Phase III)

Goal:
Translate the conversational todo specification into a stateless, scalable AI chatbot architecture using MCP tools.

Architecture:
- Frontend: ChatKit UI for user interaction
- Backend: FastAPI server exposing a single chat endpoint
- AI logic: OpenAI Agents SDK (agent + runner) for intent reasoning
- MCP server exposing task operations as tools
- Data layer: Neon PostgreSQL storing tasks, conversations, and messages
- Auth: Better Auth issuing JWTs verified by FastAPI

Execution plan:
1. Define database models for conversations and messages
2. Define MCP tools for all task operations
3. Implement stateless chat endpoint (`POST /api/chat`)
4. Load conversation history from database per request
5. Run agent with MCP tools to resolve user intent
6. Persist user and assistant messages after each turn
7. Enforce user isolation and JWT verification on every request

Non-goals:
- UI dashboards or visual task management
- Background workers or schedulers
- Real-time streaming responses
- AI memory outside persisted conversation data

## Response snapshot

Created complete implementation plan with Phase 0 and Phase 1 artifacts:

**plan.md**: Technical context, constitution compliance check (all passed), project structure
**research.md**: 8 technology decisions with rationale (SDK choice, MCP tools, storage, endpoint design, frontend, errors, security, testing)
**data-model.md**: Entity definitions for Conversation and ChatMessage with relationships
**contracts/chat-api.yaml**: OpenAPI 3.0 schema for chat endpoints
**quickstart.md**: Setup guide with environment variables and test commands

All constitution gates passed. Architecture follows stateless backend pattern with MCP tools as the only mutation path.

## Outcome

- ✅ Impact: Complete implementation blueprint ready for task breakdown
- 🧪 Tests: N/A - planning phase (test strategy defined in research.md)
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, chat-api.yaml)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: User provided detailed architecture in prompt, enabling efficient plan generation without clarification cycles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all requirements met)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A

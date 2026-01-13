# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/004-ai-todo-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/chat-api.yaml

**Tests**: Not explicitly requested - tests are optional but recommended for AI behavior validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` for Python FastAPI, `frontend/` for Next.js
- Based on plan.md project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependencies setup

- [x] T001 Install backend dependencies (openai, openai-agents, mcp) in backend/requirements.txt
- [x] T002 [P] Install frontend dependencies (@openai/chatkit) in frontend/package.json
- [x] T003 [P] Add OPENAI_API_KEY to environment configuration in backend/.env.example
- [x] T004 Create backend/mcp/__init__.py for MCP tools module
- [x] T005 [P] Create backend/agent/__init__.py for AI agent module
- [x] T006 [P] Create frontend/src/app/chat/ directory structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create Conversation model in backend/models.py (extends existing models)
- [x] T008 Create ChatMessage model in backend/models.py with role enum (user/assistant/tool)
- [x] T009 Run database migration to create conversation and chat_message tables
- [x] T010 Create MCP tool base framework in backend/mcp/tools.py with user_id context injection
- [x] T011 Create AI agent runner in backend/agent/runner.py with OpenAI Agents SDK setup
- [x] T012 [P] Create chat route file in backend/routes/chat.py with JWT auth middleware
- [x] T013 [P] Add chat routes to FastAPI app in backend/main.py
- [x] T014 Create base chat API client in frontend/src/lib/api.ts (extend existing)
- [x] T015 [P] Create ChatInterface component shell in frontend/src/components/chat/ChatInterface.tsx
- [x] T016 [P] Create MessageList component shell in frontend/src/components/chat/MessageList.tsx
- [x] T017 [P] Create MessageInput component shell in frontend/src/components/chat/MessageInput.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1)

**Goal**: Users can add tasks by typing natural language like "Add buy groceries to my list for tomorrow"

**Independent Test**: Send "Add buy milk to my list" and verify task appears in database with correct attributes

### Implementation for User Story 1

- [x] T018 [US1] Implement create_task MCP tool in backend/mcp/tools.py with parameters (description, priority?, due_date?, due_time?, tags?)
- [x] T019 [US1] Register create_task tool with agent in backend/agent/runner.py
- [x] T020 [US1] Add task creation system prompt to agent in backend/agent/runner.py for natural language parsing
- [x] T021 [US1] Implement POST /api/chat endpoint logic for task creation in backend/routes/chat.py
- [x] T022 [US1] Add conversation persistence (save user message and assistant response) in backend/routes/chat.py
- [x] T023 [US1] Implement chat API call in frontend/src/lib/api.ts (sendChatMessage function)
- [x] T024 [US1] Connect MessageInput to API and display response in ChatInterface in frontend/src/components/chat/ChatInterface.tsx
- [x] T025 [US1] Create chat page with ChatInterface in frontend/src/app/chat/page.tsx
- [x] T026 [US1] Add navigation link to chat page in frontend header/sidebar

**Checkpoint**: User Story 1 complete - users can add tasks via chat

---

## Phase 4: User Story 2 - List and View Tasks (Priority: P1)

**Goal**: Users can ask "Show my tasks" and see their task list in chat

**Independent Test**: With 3 tasks in database, send "Show my tasks" and verify all 3 are returned formatted

### Implementation for User Story 2

- [x] T027 [US2] Implement list_tasks MCP tool in backend/mcp/tools.py with filters (completed?, priority?, date?)
- [x] T028 [US2] Implement search_tasks MCP tool in backend/mcp/tools.py for fuzzy matching
- [x] T029 [US2] Register list_tasks and search_tasks tools with agent in backend/agent/runner.py
- [x] T030 [US2] Add task listing/filtering prompts to agent instructions in backend/agent/runner.py
- [x] T031 [US2] Format task list as readable markdown in tool response in backend/mcp/tools.py
- [x] T032 [US2] Render task list response with proper formatting in frontend/src/components/chat/MessageList.tsx

**Checkpoint**: User Stories 1 and 2 complete - users can add and view tasks via chat

---

## Phase 5: User Story 3 - Complete Tasks (Priority: P2)

**Goal**: Users can say "Mark buy groceries as complete" to check off tasks

**Independent Test**: Create task, send "Mark [task] as done", verify task.completed = true in database

### Implementation for User Story 3

- [x] T033 [US3] Implement complete_task MCP tool in backend/mcp/tools.py with task matching logic
- [x] T034 [US3] Add fuzzy task matching helper for description-based lookup in backend/mcp/tools.py
- [x] T035 [US3] Register complete_task tool with agent in backend/agent/runner.py
- [x] T036 [US3] Handle ambiguous matches (multiple tasks match) with clarification request in backend/mcp/tools.py
- [x] T037 [US3] Handle task not found with helpful error message in backend/mcp/tools.py

**Checkpoint**: User Story 3 complete - users can complete tasks via chat

---

## Phase 6: User Story 4 - Update Tasks (Priority: P2)

**Goal**: Users can say "Change buy groceries to high priority" to modify tasks

**Independent Test**: Create task, send "Change [task] priority to high", verify task.priority = high in database

### Implementation for User Story 4

- [x] T038 [US4] Implement update_task MCP tool in backend/mcp/tools.py with field updates (priority, due_date, description, tags)
- [x] T039 [US4] Register update_task tool with agent in backend/agent/runner.py
- [x] T040 [US4] Add date parsing for natural language dates ("tomorrow", "Friday") in backend/mcp/tools.py
- [x] T041 [US4] Handle partial updates and confirm changes to user in backend/mcp/tools.py

**Checkpoint**: User Story 4 complete - users can update tasks via chat

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Users can say "Delete the groceries task" to remove tasks

**Independent Test**: Create task, send "Delete [task]", verify task is removed from database

### Implementation for User Story 5

- [x] T042 [US5] Implement delete_task MCP tool in backend/mcp/tools.py with confirmation message
- [x] T043 [US5] Register delete_task tool with agent in backend/agent/runner.py
- [x] T044 [US5] Reuse fuzzy matching from complete_task for task identification in backend/mcp/tools.py
- [x] T045 [US5] Handle task not found with suggestion to list tasks in backend/mcp/tools.py

**Checkpoint**: User Story 5 complete - full CRUD available via chat

---

## Phase 8: User Story 6 - Conversation Context Persistence (Priority: P2)

**Goal**: Users can say "mark it complete" after adding a task and the bot understands "it"

**Independent Test**: Add a task, immediately type "make it high priority", verify the just-added task is updated

### Implementation for User Story 6

- [x] T046 [US6] Load last 10 messages from conversation on each request in backend/routes/chat.py
- [x] T047 [US6] Pass conversation history to agent runner in backend/agent/runner.py
- [x] T048 [US6] Store tool call results in ChatMessage.tool_calls field in backend/routes/chat.py
- [x] T049 [US6] Add agent instructions for context-aware references ("it", "that", "the first one") in backend/agent/runner.py
- [x] T050 [US6] Implement GET /api/chat/conversations endpoint in backend/routes/chat.py
- [x] T051 [US6] Implement GET /api/chat/conversations/{id} endpoint in backend/routes/chat.py
- [x] T052 [US6] Add conversation list sidebar in frontend/src/app/chat/page.tsx
- [x] T053 [US6] Enable loading previous conversations in frontend/src/components/chat/ChatInterface.tsx

**Checkpoint**: User Story 6 complete - contextual conversation working

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T054 [P] Add rate limiting to /api/chat endpoint (429 response) in backend/routes/chat.py
- [x] T055 [P] Implement graceful error handling for AI service unavailability in backend/routes/chat.py
- [x] T056 [P] Add loading states and error display in frontend/src/components/chat/ChatInterface.tsx
- [x] T057 [P] Add non-task message handling ("I'm here to help manage your tasks...") in backend/agent/runner.py
- [ ] T058 Run quickstart.md validation with sample conversations
- [ ] T059 Verify user isolation - test that users cannot access other users' tasks
- [ ] T060 Performance test: verify 95% of requests complete < 3 seconds

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) can run in parallel after Foundational
  - US3 (P2), US4 (P2), US6 (P2) can run after Foundational (benefit from US1/US2)
  - US5 (P3) can run after Foundational (reuses matching from US3)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational - No dependencies on other stories
- **User Story 2 (P1)**: After Foundational - No dependencies on other stories
- **User Story 3 (P2)**: After Foundational - Shares fuzzy matching with US4, US5
- **User Story 4 (P2)**: After Foundational - Reuses matching from US3
- **User Story 5 (P3)**: After Foundational - Reuses matching from US3
- **User Story 6 (P2)**: After Foundational - Enhances all other stories

### Within Each User Story

- MCP tools before agent registration
- Backend before frontend integration
- Core implementation before edge case handling

### Parallel Opportunities

**Setup Phase (parallel):**
- T002, T003, T005, T006 can run in parallel

**Foundational Phase (parallel after T007-T009):**
- T012, T013 can run in parallel
- T015, T016, T017 can run in parallel

**User Stories (parallel after Foundational):**
- US1 and US2 can be developed in parallel
- Frontend tasks within each story can run in parallel with backend tasks

---

## Parallel Example: Foundational Phase

```bash
# After models are created (T007-T009), launch in parallel:
Task T012: "Create chat route file in backend/routes/chat.py"
Task T015: "Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx"
Task T016: "Create MessageList component in frontend/src/components/chat/MessageList.tsx"
Task T017: "Create MessageInput component in frontend/src/components/chat/MessageInput.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. **STOP and VALIDATE**: Test adding tasks via chat
5. Deploy/demo basic chatbot that can add tasks

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 (Add) + User Story 2 (List) -> MVP with add/list
3. Add User Story 3 (Complete) -> Users can complete tasks
4. Add User Story 4 (Update) + User Story 5 (Delete) -> Full CRUD
5. Add User Story 6 (Context) -> Natural conversation
6. Polish phase -> Production ready

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1)**

This delivers: A working chatbot that can add tasks via natural language.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- MCP tools are stateless - all state in database
- JWT authentication required for all chat endpoints
- User isolation enforced at query level in all MCP tools
- Commit after each task or logical group

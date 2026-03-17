# Tasks: Advanced Event-Driven Todo/Chatbot

**Input**: Design documents from `/specs/006-dapr-event-driven/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/events.md, contracts/api.md, contracts/dapr.md, quickstart.md

**Tests**: Not explicitly requested in the specification. Tests are omitted. Deployment verification scripts serve as E2E validation.

**Organization**: Tasks grouped by user story. 7 user stories (US1-US7) across priorities P1-P3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (FastAPI, Python 3.11+)
- **Frontend**: `frontend/src/` (Next.js 14, TypeScript)
- **Services**: `services/{reminder,recurring,sync}/` (new microservices)
- **Helm**: `helm/todo-chatbot/` (Kubernetes deployment)
- **Dapr**: `dapr/` (local component definitions)
- **Scripts**: `scripts/` (deployment automation)
- **CI/CD**: `.github/workflows/` (GitHub Actions)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure, add dependencies, configure shared modules

- [x] T001 Create microservice directory structure: `services/reminder/`, `services/recurring/`, `services/sync/`, `backend/events/`, `dapr/`
- [x] T002 [P] Add `dapr>=1.14.0` and `websockets>=12.0` to `backend/requirements.txt`
- [x] T003 [P] Create `services/reminder/requirements.txt` with fastapi, uvicorn, dapr, sqlmodel, psycopg2-binary, python-dotenv
- [x] T004 [P] Create `services/recurring/requirements.txt` with fastapi, uvicorn, dapr, sqlmodel, psycopg2-binary, python-dotenv
- [x] T005 [P] Create `services/sync/requirements.txt` with fastapi, uvicorn, dapr, websockets, python-jose, python-dotenv
- [x] T006 [P] Create `services/reminder/Dockerfile` using multi-stage build pattern from `backend/Dockerfile`
- [x] T007 [P] Create `services/recurring/Dockerfile` using multi-stage build pattern from `backend/Dockerfile`
- [x] T008 [P] Create `services/sync/Dockerfile` using multi-stage build pattern from `backend/Dockerfile`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can begin

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Add `urgent` value to `Priority` enum in `backend/models.py` (backward-compatible addition per data-model.md Section 7)
- [x] T010 [P] Create `RecurrenceRule` SQLModel entity in `backend/models.py` per data-model.md Section 2.1 (fields: id, task_id, user_id, frequency, interval_value, day_of_week, day_of_month, is_completion_based, next_occurrence, timestamps)
- [x] T011 [P] Create `TaskEvent` SQLModel entity in `backend/models.py` per data-model.md Section 2.2 (fields: id, event_type, task_id, user_id, payload as JSON, created_at)
- [x] T012 [P] Create `Reminder` SQLModel entity with `ReminderStatus` and `ReminderType` enums in `backend/models.py` per data-model.md Section 2.3
- [x] T013 Update `TaskCreate` and `TaskUpdate` schemas in `backend/models.py` to add optional recurrence fields: `recurrenceInterval`, `recurrenceDayOfWeek`, `recurrenceDayOfMonth`, `isCompletionBased` per contracts/api.md
- [x] T014 Update `TaskResponse` schema in `backend/models.py` to add `isCompletionBased` (bool) and `nextOccurrence` (Optional[str]) fields per contracts/api.md
- [x] T015 Create event schema dataclasses in `backend/events/schemas.py` per contracts/events.md: `TaskCreatedEvent`, `TaskUpdatedEvent`, `TaskCompletedEvent`, `TaskDeletedEvent`, `TaskSyncEvent`
- [x] T016 Create `backend/events/__init__.py` exporting publish_event and event schemas
- [x] T017 Create Dapr event publisher helper in `backend/events/publisher.py`: async `publish_event(topic, event_type, data)` function using `dapr.clients.DaprClient` with fire-and-forget error handling per research.md Section 4.1
- [x] T018 [P] Create local Dapr pub/sub component definition in `dapr/pubsub.yaml` per data-model.md Section 4.1 (type: pubsub.kafka, brokers: redpanda local)
- [x] T019 [P] Create local Dapr state store component definition in `dapr/statestore.yaml` per data-model.md Section 4.3 (type: state.postgresql)
- [x] T020 [P] Create local Dapr subscription definitions in `dapr/subscriptions.yaml` per data-model.md Section 4.4 (4 subscriptions: task-events->reminder, task-events->recurring, task-updates->sync, reminders->sync)
- [x] T021 Verify database migration: ensure `create_db_and_tables()` in `backend/db.py` creates new tables (RecurrenceRule, TaskEvent, Reminder) alongside existing tables

**Checkpoint**: Foundation ready — event schemas, publisher, Dapr components, and DB entities all in place. User story implementation can now begin.

---

## Phase 3: User Story 1 — Event-Driven Task Management (Priority: P1) MVP

**Goal**: All task CRUD operations publish events to Kafka topics via Dapr. Task operations succeed even when messaging is unavailable (fire-and-forget degraded mode). Audit stub logs every event.

**Independent Test**: Create a task via API, verify `task.created` event appears in `task-events` topic. Update and delete the task, verify corresponding events. Stop Redpanda, create a task — confirm CRUD still succeeds (degraded mode).

### Implementation for User Story 1

- [x] T022 [US1] Integrate event publishing into `create_task` route in `backend/routes/tasks.py`: after `session.commit()`, publish `task.created` event to `task-events` topic and `task.sync` event to `task-updates` topic using `backend/events/publisher.py`
- [x] T023 [US1] Integrate event publishing into `update_task` route in `backend/routes/tasks.py`: after commit, publish `task.updated` event (with changed_fields dict) to `task-events` and `task.sync` to `task-updates`
- [x] T024 [US1] Integrate event publishing into `complete_task` route in `backend/routes/tasks.py`: after commit, publish `task.completed` event to `task-events` and `task.sync` to `task-updates`
- [x] T025 [US1] Integrate event publishing into `incomplete_task` route in `backend/routes/tasks.py`: after commit, publish `task.updated` event to `task-events` and `task.sync` to `task-updates`
- [x] T026 [US1] Integrate event publishing into `delete_task` route in `backend/routes/tasks.py`: after commit, publish `task.deleted` event to `task-events` and `task.sync` to `task-updates`
- [x] T027 [US1] Implement audit stub: after each event publish in task routes, write a `TaskEvent` record to the database (FR-018) in `backend/routes/tasks.py`
- [x] T028 [US1] Verify fire-and-forget degraded mode: ensure all event publishing is wrapped in try/except with pass, so task CRUD never fails due to messaging issues (FR-013) in `backend/events/publisher.py`

**Checkpoint**: All task CRUD routes publish events. Audit stub logs events. Degraded mode works. US1 is independently testable.

---

## Phase 4: User Story 2 — Due Date Reminders (Priority: P1)

**Goal**: A dedicated reminder microservice subscribes to `task-events`, schedules reminders at 24h and 1h before due dates, cancels reminders on task completion/update, and publishes `reminder.triggered` events. Delivery is simulated via structured logs.

**Independent Test**: Create a task with a due date 2 minutes from now. Observe reminder service logs for scheduling. Wait for trigger time, verify `reminder.triggered` event and log output. Complete the task, verify pending reminders are cancelled.

### Implementation for User Story 2

- [x] T029 [US2] Create reminder service FastAPI app skeleton in `services/reminder/main.py` with `/health` endpoint returning `{"status": "healthy", "service": "reminder-service", "dapr": true}`
- [x] T030 [US2] Implement idempotent event handler at `POST /events/task` in `services/reminder/main.py` per contracts/events.md idempotency contract (extract event_id, check dedup store via Dapr state, process or DROP)
- [x] T031 [US2] Implement reminder scheduling logic in `services/reminder/main.py`: on `task.created`/`task.updated` with due_date, calculate trigger times (due_date - 24h, due_date - 1h), create Reminder records in database (FR-003)
- [x] T032 [US2] Implement reminder cancellation in `services/reminder/main.py`: on `task.completed` and `task.deleted`, set all pending Reminder records for that task_id to status=cancelled (FR-004)
- [x] T033 [US2] Implement reminder re-scheduling in `services/reminder/main.py`: on `task.updated` with changed due_date, cancel existing reminders and schedule new ones for the updated date
- [x] T034 [US2] Implement polling loop in `services/reminder/main.py`: background task runs every 60 seconds, queries Reminder table for status=pending AND trigger_time<=now, publishes `reminder.triggered` event to `reminders` topic, updates status to sent
- [x] T035 [US2] Implement simulated reminder delivery: log `[REMINDER] user={user_id} task={task_id} type={24h|1h} message="Task '{description}' is due in {type}"` for each triggered reminder (FR-017)
- [x] T036 [US2] Implement startup recovery in `services/reminder/main.py`: on service start, query all pending reminders with trigger_time in the past and fire them immediately (acceptance scenario 5)

**Checkpoint**: Reminder service is fully functional. Creates, cancels, and fires reminders based on task events. Simulated delivery via logs. Independently testable.

---

## Phase 5: User Story 3 — Recurring Tasks (Priority: P2)

**Goal**: A dedicated recurring task microservice subscribes to `task-events`, manages RecurrenceRule records, automatically creates new task instances on schedule (time-based) or on completion (on-complete model).

**Independent Test**: Create a task with recurrence=daily. Simulate time advancing (or set next_occurrence to now). Verify a new task instance is created. Create a task with is_completion_based=true, complete it, verify next instance is created with adjusted due date.

### Implementation for User Story 3

- [x] T037 [US3] Create recurring service FastAPI app skeleton in `services/recurring/main.py` with `/health` endpoint returning `{"status": "healthy", "service": "recurring-service", "dapr": true}`
- [x] T038 [US3] Implement idempotent event handler at `POST /events/task` in `services/recurring/main.py` per contracts/events.md idempotency contract
- [x] T039 [US3] Implement recurrence rule creation in `services/recurring/main.py`: on `task.created` with recurrence!="none", create RecurrenceRule record in database with calculated next_occurrence
- [x] T040 [US3] Implement on-complete recurrence in `services/recurring/main.py`: on `task.completed` with is_completion_based=true, create new task via Dapr service invocation to backend POST /api/tasks, set due_date = completed_at + interval (FR-006)
- [x] T041 [US3] Implement recurrence rule deletion in `services/recurring/main.py`: on `task.deleted`, remove the RecurrenceRule record for that task_id
- [x] T042 [US3] Implement next occurrence date calculation utility in `services/recurring/main.py`: daily (+N days), weekly (+N weeks, anchored to day_of_week), monthly (+N months, day clamped to 28) per research.md Section 7.3
- [x] T043 [US3] Implement time-based polling loop in `services/recurring/main.py`: background task every 60 seconds, query RecurrenceRule where next_occurrence<=today and is_completion_based=false, create new task instance, advance next_occurrence (FR-019)
- [x] T044 [US3] When creating a new recurring task instance, publish `task.sync` event to `task-updates` topic so real-time sync picks it up

**Checkpoint**: Recurring service handles both time-based and on-complete models. New task instances are created automatically. Independently testable.

---

## Phase 6: User Story 4 — Real-Time Sync Across Sessions (Priority: P2)

**Goal**: A sync service subscribes to `task-updates` and `reminders` topics and broadcasts updates to authenticated users via WebSocket. Frontend auto-refreshes when events arrive.

**Independent Test**: Open dashboard in two browser tabs. Create a task in Tab A. Verify it appears in Tab B within 2 seconds without refresh. Close and reopen Tab B, verify it catches up.

### Implementation for User Story 4

- [x] T045 [US4] Create sync service FastAPI app skeleton in `services/sync/main.py` with `/health` endpoint
- [x] T046 [US4] Implement WebSocket endpoint `WS /ws?token={jwt}` in `services/sync/main.py`: validate JWT on upgrade, extract user_id, add to connection registry, send `{"type":"connected"}` message, heartbeat ping every 30s per contracts/api.md
- [x] T047 [US4] Implement connection registry in `services/sync/main.py`: in-memory dict `{user_id: set[WebSocket]}`, add on connect, remove on disconnect/error
- [x] T048 [US4] Implement `/events/sync` handler in `services/sync/main.py`: receive task.sync events from `task-updates` topic, broadcast `WsTaskUpdate` JSON to all WebSocket connections for the event's user_id per contracts/api.md
- [x] T049 [US4] Implement `/events/reminder` handler in `services/sync/main.py`: receive reminder.triggered events from `reminders` topic, broadcast `WsReminder` JSON to all WebSocket connections for the event's user_id
- [x] T050 [P] [US4] Create `useWebSocket` hook in `frontend/src/lib/hooks/useWebSocket.ts`: connect to sync service WS endpoint with JWT, handle reconnect with exponential backoff, parse incoming messages
- [x] T051 [US4] Integrate `useWebSocket` hook into dashboard page `frontend/src/app/dashboard/page.tsx`: on `task_update` message, invalidate React Query `['tasks']` cache to trigger refetch. On `reminder` message, show toast notification
- [x] T052 [US4] Handle WebSocket reconnection in `frontend/src/lib/hooks/useWebSocket.ts`: on reconnect, React Query automatically refetches stale data (acceptance scenario 3)

**Checkpoint**: Real-time sync works across browser tabs. Reminders appear as notifications. Frontend auto-refreshes on events. Independently testable.

---

## Phase 7: User Story 5 — Enhanced Task Organization (Priority: P2)

**Goal**: Frontend supports "urgent" priority, improved tag filtering with visual indicators, debounced search, and additional sort options. Backend already supports all filtering/sorting from Phase IV.

**Independent Test**: Create tasks with different priorities (including urgent), tags, and due dates. Verify sort by priority orders correctly (urgent > high > medium > low). Filter by tag and verify visual indicator. Search and verify results appear within 1 second.

### Implementation for User Story 5

- [x] T053 [P] [US5] Update task type definitions in `frontend/src/types/task.ts` to add `"urgent"` to Priority type, add `isCompletionBased` and `nextOccurrence` fields to Task interface
- [x] T054 [P] [US5] Update `TaskCard` component in `frontend/src/components/tasks/TaskCard.tsx` to display "urgent" priority with distinct styling (e.g., red badge)
- [x] T055 [P] [US5] Update `TaskForm` component in `frontend/src/components/tasks/TaskForm.tsx` to include "urgent" in priority dropdown and add recurrence interval/day options
- [x] T056 [US5] Update `TaskFilters` component in `frontend/src/components/tasks/TaskFilters.tsx` to show active filter count badge, add "urgent" to priority filter options, and visually indicate when filters are active (acceptance scenario 5)
- [x] T057 [US5] Add debounced search input to `TaskFilters` in `frontend/src/components/tasks/TaskFilters.tsx` with 300ms debounce (FR-010, acceptance scenario 3)
- [x] T058 [US5] Add "sort by title" option to sort controls in `frontend/src/components/tasks/TaskFilters.tsx` (FR-012, acceptance scenario 4)

**Checkpoint**: Frontend fully supports urgent priority, improved filters with visual indicators, debounced search, and all sort options. Independently testable.

---

## Phase 8: User Story 7 — Local Development Environment (Priority: P3)

**Goal**: Entire event-driven system runs locally on Minikube with Dapr sidecars, in-cluster Redpanda, and all 5 services functional from a single setup command.

**Independent Test**: Run `./scripts/minikube-setup.sh` and `./scripts/deploy.sh`. Verify all pods Running (2/2 for Dapr-enabled). Create a task with due date, verify event flows to reminder service logs. Open two port-forwarded tabs, verify real-time sync.

> **NOTE**: This phase is ordered before US6 (Cloud) because local dev must work before cloud deployment (constitution: "Deployment scripts tested locally first").

### Implementation for User Story 7

- [x] T059 [P] [US7] Create Redpanda StatefulSet template in `helm/todo-chatbot/templates/redpanda-statefulset.yaml` (single-node, dev-container mode, ports 9092/8081/9644, conditional on `.Values.redpanda.enabled`)
- [x] T060 [P] [US7] Create Redpanda Service template in `helm/todo-chatbot/templates/redpanda-service.yaml` (ClusterIP, port 9092)
- [x] T061 [P] [US7] Create Dapr pub/sub component template in `helm/todo-chatbot/templates/dapr-pubsub-component.yaml` per contracts/dapr.md (conditional local vs cloud config)
- [x] T062 [P] [US7] Create Dapr state store component template in `helm/todo-chatbot/templates/dapr-statestore-component.yaml` per contracts/dapr.md
- [x] T063 [P] [US7] Create Dapr subscription templates in `helm/todo-chatbot/templates/dapr-subscription.yaml` per contracts/dapr.md (4 subscriptions)
- [x] T064 [P] [US7] Create reminder-service Deployment + Service templates in `helm/todo-chatbot/templates/reminder-deployment.yaml` and `helm/todo-chatbot/templates/reminder-service.yaml` with Dapr sidecar annotations (app-id: reminder-service, port: 8001)
- [x] T065 [P] [US7] Create recurring-service Deployment + Service templates in `helm/todo-chatbot/templates/recurring-deployment.yaml` and `helm/todo-chatbot/templates/recurring-service.yaml` with Dapr sidecar annotations (app-id: recurring-service, port: 8002)
- [x] T066 [P] [US7] Create sync-service Deployment + Service templates in `helm/todo-chatbot/templates/sync-deployment.yaml` and `helm/todo-chatbot/templates/sync-service.yaml` with Dapr sidecar annotations (app-id: sync-service, port: 8003)
- [x] T067 [US7] Add Dapr sidecar annotations to existing `helm/todo-chatbot/templates/backend-deployment.yaml` (dapr.io/enabled: "true", app-id: backend, app-port: "8000") per data-model.md Section 5
- [x] T068 [US7] Update `helm/todo-chatbot/values.yaml` with new service configs (reminder, recurring, sync image repos/tags, resource limits, Dapr settings, Redpanda toggle) and `helm/todo-chatbot/Chart.yaml` version bump to 2.0.0
- [x] T069 [US7] Create/update `helm/todo-chatbot/values-local.yaml` with local Redpanda enabled, local broker URL, service image tags, and placeholder secrets
- [x] T070 [US7] Extend `scripts/minikube-setup.sh` to install Dapr CLI and run `dapr init -k --runtime-version 1.14.4` after Minikube starts
- [x] T071 [US7] Extend `scripts/build-images.sh` to build all 5 images (backend, frontend, reminder, recurring, sync) when `--minikube` flag is used
- [x] T072 [US7] Extend `scripts/deploy.sh` to deploy with Dapr components: `helm upgrade --install` with `values-local.yaml`, verify Dapr components and subscriptions loaded

**Checkpoint**: Full local environment on Minikube. All services running with Dapr sidecars. Events flowing through in-cluster Redpanda. Single setup command. SC-007 validated.

---

## Phase 9: User Story 6 — Cloud Deployment and Monitoring (Priority: P3)

**Goal**: System deployed to AKS with Redpanda Cloud, automated CI/CD via GitHub Actions, health monitoring, and structured logging.

**Independent Test**: Push code to main branch. Verify GitHub Actions builds and deploys within 10 minutes. Access frontend URL. Create a task, verify event flow in cloud logs. Kill a pod, verify auto-restart.

### Implementation for User Story 6

- [x] T073 [P] [US6] Create `helm/todo-chatbot/values-cloud.yaml` with ACR image repos (`todoappcr2025.azurecr.io/*`), Redpanda Cloud SASL config, cloud-specific resource limits, redpanda.enabled=false
- [x] T074 [P] [US6] Create `scripts/setup-redpanda-cloud.sh` to create Redpanda Cloud serverless cluster and Kubernetes secret with SASL credentials
- [x] T075 [P] [US6] Create AKS provisioning section in `scripts/deploy-azure.sh`: `az aks create` (free tier, Standard_B2s, 1 node), `az aks get-credentials`, attach ACR, `dapr init -k`
- [x] T076 [US6] Create GitHub Actions workflow in `.github/workflows/deploy.yml`: trigger on push to main, build 5 Docker images, push to ACR, helm upgrade to AKS (FR-015)
- [x] T077 [US6] Create deployment verification script in `scripts/verify-deployment.sh`: check all pods Running, hit /health on each service, create a test task via API, verify event flow (SC-006)
- [x] T078 [US6] Add structured JSON logging to all services (backend, reminder, recurring, sync) for cloud observability: use Python `logging` with JSON formatter, log event processing outcomes (FR-018)

**Checkpoint**: Full cloud deployment on AKS. CI/CD pipeline functional. Health checks and structured logging operational. SC-006 and SC-008 validated.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements that span multiple user stories

- [x] T079 [P] Update `CLAUDE.md` at repository root with Phase V commands, new service paths, and Dapr/Redpanda/AKS documentation
- [x] T080 [P] Update `helm/todo-chatbot/templates/_helpers.tpl` with helper labels for new services (reminder, recurring, sync)
- [x] T081 Run quickstart.md validation: execute local setup end-to-end on Minikube, verify all steps from `specs/006-dapr-event-driven/quickstart.md` Part 1
- [x] T082 Verify backward compatibility: confirm all Phase IV functionality (task CRUD, auth, chat, dashboard) works unchanged with Dapr sidecar running

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────> (no deps, start immediately)
Phase 2: Foundational ───────────> (depends on Phase 1)
    │
    ├──> Phase 3: US1 (P1) MVP ─> (depends on Phase 2) ─> VALIDATE
    │       │
    │       ├──> Phase 4: US2 (P1) ──> (depends on US1 events flowing)
    │       │
    │       ├──> Phase 5: US3 (P2) ──> (depends on US1 events flowing)
    │       │
    │       ├──> Phase 6: US4 (P2) ──> (depends on US1 task-updates topic)
    │       │
    │       └──> Phase 7: US5 (P2) ──> (no event deps, just frontend)
    │
    └──> (US2-US5 can proceed in parallel after US1)
              │
              └──> Phase 8: US7 (P3) ──> (depends on all services existing)
                      │
                      └──> Phase 9: US6 (P3) ──> (depends on local working first)
                              │
                              └──> Phase 10: Polish ──> (depends on all stories)
```

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 only. **MVP target.** No other story dependencies.
- **US2 (P1)**: Depends on US1 (needs task events flowing). Can proceed in parallel with US3-US5.
- **US3 (P2)**: Depends on US1 (needs task events flowing). Can proceed in parallel with US2, US4, US5.
- **US4 (P2)**: Depends on US1 (needs task-updates topic). Can proceed in parallel with US2, US3, US5.
- **US5 (P2)**: Depends on Phase 2 only (frontend changes, no event deps). Can proceed in parallel with US2-US4.
- **US7 (P3)**: Depends on all services existing (US1-US4 implementations). Must complete before US6.
- **US6 (P3)**: Depends on US7 (local must work before cloud). Final deployment story.

### Within Each User Story

- Models before services (Phase 2 handles all shared models)
- Event handlers before business logic
- Backend before frontend integration
- Core functionality before edge cases

### Parallel Opportunities

**Phase 1**: T002-T008 all [P] — different files, no dependencies
**Phase 2**: T010-T012 [P] (models), T018-T020 [P] (Dapr YAMLs) — different files
**Phase 3**: T022-T026 can be parallelized (different route functions in same file — use caution)
**Phase 4-6**: US2, US3, US4, US5 can all proceed in parallel after US1 completes
**Phase 7**: T059-T066 all [P] — different Helm template files
**Phase 9**: T073-T075 all [P] — different script files

---

## Parallel Example: After US1 Completes

```
# These 4 story phases can run in parallel:
Phase 4 (US2): Reminder service implementation
Phase 5 (US3): Recurring service implementation
Phase 6 (US4): Sync service + WebSocket + frontend
Phase 7 (US5): Frontend priority/filter/search improvements
```

## Parallel Example: Phase 8 Helm Templates

```
# All template files can be created in parallel:
T059: redpanda-statefulset.yaml
T060: redpanda-service.yaml
T061: dapr-pubsub-component.yaml
T062: dapr-statestore-component.yaml
T063: dapr-subscription.yaml
T064: reminder-deployment.yaml + reminder-service.yaml
T065: recurring-deployment.yaml + recurring-service.yaml
T066: sync-deployment.yaml + sync-service.yaml
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 — Event-Driven Task Management
4. **STOP and VALIDATE**: Create tasks, verify events in Kafka topics, verify degraded mode
5. Deploy locally with existing Helm charts (Dapr sidecar on backend only)

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. US1 -> Event publishing works -> **MVP Demo**
3. US2 (Reminders) + US5 (Organization) -> Proactive features -> Demo
4. US3 (Recurring) + US4 (Real-time sync) -> Full event-driven experience -> Demo
5. US7 (Local K8s) -> Full Minikube environment -> Dev-ready
6. US6 (Cloud) -> AKS deployment -> Production-ready

### Single Developer Strategy

Execute stories sequentially in priority order:
1. Phase 1 + 2 (Setup + Foundation) ~2 hours
2. Phase 3 (US1 MVP) ~2 hours
3. Phase 4 (US2 Reminders) ~3 hours
4. Phase 5 (US3 Recurring) ~3 hours
5. Phase 6 (US4 Real-time Sync) ~3 hours
6. Phase 7 (US5 Organization) ~1 hour
7. Phase 8 (US7 Local K8s) ~3 hours
8. Phase 9 (US6 Cloud) ~3 hours
9. Phase 10 (Polish) ~1 hour

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [USn] label maps task to specific user story for traceability
- Each user story is independently completable and testable after US1 foundation
- Fire-and-forget pattern means event publishing NEVER blocks task CRUD
- All consumers MUST implement idempotency per contracts/events.md
- Dapr sidecar annotations are the only K8s-specific configuration per service
- Local Redpanda uses dev-container mode (single node, minimal resources)
- Cloud Redpanda uses SASL/SCRAM auth via Kubernetes secrets
- Frontend uses native WebSocket API — no additional npm dependencies needed

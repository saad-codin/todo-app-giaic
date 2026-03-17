# Feature Specification: Advanced Event-Driven Todo/Chatbot

**Feature Branch**: `006-dapr-event-driven`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Advanced Event-Driven Todo/Chatbot with Dapr + Redpanda Cloud + AKS"

## Clarifications

### Session 2026-02-09

- Q: Recurring task trigger model — time-based, on-complete, or both? → A: Both. Time-based is primary (calendar-anchored, fires on schedule regardless of completion status). On-complete is secondary (optional per-task flag; spawns next instance when current is completed, similar to Todoist "every" vs "every!"). Scheduling uses Dapr Jobs API (preferred) with cron bindings + polling as fallback if Jobs API proves unstable. Recurrence rules persisted in Neon DB.
- Q: Real-time sync scope — single-user multi-device or multi-user shared tasks? → A: Single-user multi-device only. Each user sees only their own tasks; real-time sync broadcasts across that user's own sessions. No shared/collaborative task lists.
- Q: Degraded mode behavior when messaging system is unavailable? → A: Fire-and-forget with sidecar retry. Backend publishes events to sidecar and proceeds; sidecar retries per its configured policy. If retries exhaust, the event is lost (acceptable for hackathon). No local outbox queue or user-visible warning needed.
- Q: Concurrency target for demo — 100 concurrent users realistic? → A: Lower to 10-20 concurrent users. Realistic for hackathon demo, easily testable, proves architecture without over-engineering.
- Q: Event delivery semantics — at-least-once, at-most-once, or best-effort? → A: At-least-once delivery. All event consumers MUST be idempotent (dedup by event ID or task ID + event type before processing).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Event-Driven Task Management (Priority: P1)

As an everyday user (student, professional, or team member), I want my task actions (create, update, delete, complete) to be published as events so that other services can react automatically — sending reminders, spawning recurring tasks, and syncing updates to all my open sessions in real time.

**Why this priority**: This is the foundational capability. Without event-driven task operations, no downstream features (reminders, recurring tasks, real-time sync) can function. Every other story depends on task events flowing through the messaging system.

**Independent Test**: Can be fully tested by creating/updating/completing tasks via the chat interface or dashboard and verifying that events are published to the appropriate message channels and consumed by subscriber services.

**Acceptance Scenarios**:

1. **Given** a user creates a task via chat or dashboard, **When** the task is saved, **Then** a "task.created" event is published containing the task ID, user ID, title, priority, tags, and due date.
2. **Given** a user updates a task (title, priority, tags, due date), **When** the update is saved, **Then** a "task.updated" event is published containing the changed fields and the task ID.
3. **Given** a user marks a task complete, **When** the completion is saved, **Then** a "task.completed" event is published containing the task ID, user ID, and completion timestamp.
4. **Given** a user deletes a task, **When** the deletion is confirmed, **Then** a "task.deleted" event is published containing the task ID and user ID.
5. **Given** the messaging system is temporarily unavailable, **When** a task action is performed, **Then** the task operation still succeeds (write-ahead) and the event is retried or queued for later delivery.

---

### User Story 2 - Due Date Reminders (Priority: P1)

As a user with tasks that have due dates, I want to receive timely reminders before a task is due so that I never miss a deadline.

**Why this priority**: Reminders are the primary "proactive" feature that differentiates this system from a basic CRUD todo app. Users expect a task manager to actively help them stay on track.

**Independent Test**: Can be fully tested by creating a task with a due date, waiting for (or simulating) the reminder trigger time, and verifying a reminder notification is delivered to the user.

**Acceptance Scenarios**:

1. **Given** a task has a due date set, **When** the due date is 1 hour away, **Then** a reminder notification is generated for the task owner.
2. **Given** a task has a due date set, **When** the due date is 24 hours away, **Then** a reminder notification is generated for the task owner.
3. **Given** a task is completed before the reminder fires, **When** the reminder trigger time arrives, **Then** no reminder is sent.
4. **Given** a task's due date is changed, **When** the update is saved, **Then** any previously scheduled reminder is cancelled and a new one is scheduled for the updated due date.
5. **Given** the reminder service restarts, **When** it comes back online, **Then** it re-evaluates all pending reminders and fires any that were missed during downtime.

---

### User Story 3 - Recurring Tasks (Priority: P2)

As a user with repeating responsibilities (daily standup prep, weekly reports, monthly reviews), I want to define recurrence rules on tasks so that new instances are automatically created on schedule without manual re-entry.

**Why this priority**: Recurring tasks build on the event-driven foundation and reminder system. They deliver significant user value by eliminating repetitive data entry, but depend on P1 infrastructure being in place.

**Independent Test**: Can be fully tested by creating a task with a recurrence rule (e.g., "every Monday"), waiting for (or simulating) the recurrence trigger, and verifying a new task instance is created with the correct attributes.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a time-based weekly recurrence rule (e.g., "every Monday"), **When** Monday arrives, **Then** a new task instance is created automatically regardless of whether the previous instance was completed (primary model).
2. **Given** a user creates a task with a time-based monthly recurrence rule (e.g., "1st of every month"), **When** the 1st arrives, **Then** a new task instance is created automatically.
3. **Given** a user creates a task with an on-complete recurrence rule (e.g., "every 3 days after completion"), **When** the current instance is marked complete, **Then** a new task instance is created with due date = completion date + interval (secondary model).
4. **Given** a recurring task is deleted (not just completed), **When** the user confirms deletion, **Then** the recurrence rule is also removed and no future instances are created.
5. **Given** a recurring task has a due date, **When** the new instance is spawned, **Then** the due date is adjusted to the next occurrence date.

---

### User Story 4 - Real-Time Sync Across Sessions (Priority: P2)

As a user with the app open in multiple browser tabs or devices, I want changes made in one session to appear immediately in all other open sessions so that I always see the latest state of my tasks.

**Why this priority**: Real-time sync transforms the user experience from "refresh to see changes" to "live updates everywhere." It depends on the event-driven infrastructure (P1) being operational.

**Independent Test**: Can be fully tested by opening the dashboard in two browser tabs, creating or updating a task in one tab, and verifying the change appears in the other tab within 2 seconds without refreshing.

**Acceptance Scenarios**:

1. **Given** a user has the dashboard open in two browser tabs, **When** a task is created in Tab A, **Then** the new task appears in Tab B within 2 seconds without page refresh.
2. **Given** a user has the dashboard open in two tabs, **When** a task is updated (title, priority, completion) in Tab A, **Then** Tab B reflects the update within 2 seconds.
3. **Given** a user's browser tab loses connection temporarily, **When** the connection is restored, **Then** the tab catches up with any changes that occurred during the disconnection.
4. **Given** a user is not authenticated, **When** they attempt to connect for real-time updates, **Then** the connection is rejected.

---

### User Story 5 - Enhanced Task Organization (Priority: P2)

As a user managing many tasks, I want to assign priorities, add tags, search across tasks, and filter/sort my task list so that I can quickly find and focus on what matters most.

**Why this priority**: These features were previously implemented in the console app (Phase II) and need to be surfaced in the web/chat interface. They are essential for usability as the task list grows.

**Independent Test**: Can be fully tested by creating several tasks with different priorities, tags, and due dates, then using search, filter, and sort controls to verify correct results.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** they assign a priority (low, medium, high, urgent), **Then** the task displays with the assigned priority and can be sorted by priority.
2. **Given** a user creates a task, **When** they add one or more tags (e.g., "work", "personal"), **Then** the task can be filtered by those tags.
3. **Given** a user has 20+ tasks, **When** they type a search query, **Then** tasks matching the query in title or description are shown within 1 second.
4. **Given** a user views the task list, **When** they apply a sort (by due date, priority, creation date, or title), **Then** the list re-orders accordingly.
5. **Given** a user applies a filter (by tag, priority, or completion status), **When** the filter is active, **Then** only matching tasks are displayed and the active filter is visually indicated.

---

### User Story 6 - Cloud Deployment and Monitoring (Priority: P3)

As the application operator, I want the system deployed to a managed cloud environment with automated build/deploy pipelines and basic monitoring so that the application is reliable, observable, and easy to update.

**Why this priority**: Deployment is the delivery mechanism. While critical for production readiness, the application logic (P1, P2) must work first. Local development on Minikube provides a viable interim environment.

**Independent Test**: Can be fully tested by pushing a code change to the repository, verifying the CI/CD pipeline builds and deploys the change, and confirming the application is accessible at the cloud URL with logs visible in the monitoring dashboard.

**Acceptance Scenarios**:

1. **Given** a developer pushes code to the main branch, **When** the CI/CD pipeline runs, **Then** container images are built, pushed to a registry, and deployed to the cloud cluster within 10 minutes.
2. **Given** the application is deployed, **When** a user accesses the frontend URL, **Then** the application loads and is fully functional.
3. **Given** a service crashes or becomes unhealthy, **When** the health check fails, **Then** the platform automatically restarts the service.
4. **Given** an operator needs to debug an issue, **When** they access the monitoring dashboard, **Then** they can see application logs, error rates, and resource utilization.

---

### User Story 7 - Local Development Environment (Priority: P3)

As a developer, I want to run the entire event-driven system locally on Minikube with all services, message brokers, and sidecars functioning so that I can develop and test without depending on cloud resources.

**Why this priority**: Local development is essential for the development workflow but doesn't deliver direct user value. It enables all other stories to be built and tested efficiently.

**Independent Test**: Can be fully tested by running the setup scripts, deploying all services to Minikube, and performing end-to-end task operations that exercise events, reminders, and real-time sync.

**Acceptance Scenarios**:

1. **Given** a developer has Minikube and required CLI tools installed, **When** they run the setup script, **Then** all services (backend, frontend, notification service, recurring task service, message broker, sidecars) start within 5 minutes.
2. **Given** the local environment is running, **When** the developer creates a task with a due date, **Then** reminder events flow through the local message broker to the notification service.
3. **Given** the local environment is running, **When** the developer stops and restarts a service, **Then** it reconnects to the sidecar and resumes processing events.

---

### Edge Cases

- What happens when a task event is published but no consumer is listening? Events are retained by the broker and delivered when the consumer reconnects (at-least-once delivery). Consumers must be idempotent to handle potential duplicate deliveries.
- What happens when a recurring task rule produces an invalid date (e.g., February 30)? The system adjusts to the nearest valid date (e.g., February 28 or 29).
- What happens when the same user updates a task from two sessions simultaneously? Last-write-wins with the most recent timestamp, and both sessions receive the updated state via real-time sync.
- What happens when the message broker is unreachable? Task CRUD operations continue to function. Events are published fire-and-forget to the sidecar which retries per its policy; if retries exhaust, the event is silently lost. No user-facing warning is shown — the task operation itself always succeeds.
- What happens when a reminder fires but the user has already deleted their account? The reminder is silently discarded.
- What happens when a user creates a recurring task without a due date? The recurrence creates instances based on the recurrence schedule only (e.g., "every Monday" starts from the next Monday).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST publish events for all task lifecycle actions (create, update, complete, delete) to a shared event channel.
- **FR-002**: System MUST support three distinct event channels: one for task lifecycle events, one for reminder scheduling/delivery, and one for real-time update broadcasting.
- **FR-003**: System MUST deliver reminder notifications at configurable intervals before a task's due date (default: 24 hours and 1 hour before).
- **FR-004**: System MUST cancel pending reminders when a task is completed or its due date is changed.
- **FR-005**: System MUST support recurring task rules with daily, weekly, and monthly frequencies in two models: time-based (primary, calendar-anchored — fires on schedule regardless of completion) and on-complete (secondary, optional per-task flag — spawns next instance upon completion with interval-adjusted due date).
- **FR-006**: System MUST automatically create new task instances based on recurrence rules without user intervention. Time-based rules fire at the scheduled time; on-complete rules fire when the "task.completed" event is received.
- **FR-019**: System MUST schedule recurring task triggers using exact-time job scheduling as the preferred mechanism, with periodic polling (1-5 minute intervals) as a fallback if exact-time scheduling is unavailable or unstable.
- **FR-020**: System MUST use at-least-once event delivery semantics. All event consumers MUST be idempotent, deduplicating by event ID or task ID + event type to prevent duplicate processing.
- **FR-007**: System MUST broadcast task changes to all authenticated sessions belonging to the same user within 2 seconds.
- **FR-008**: System MUST allow users to assign priorities (low, medium, high, urgent) to tasks.
- **FR-009**: System MUST allow users to add and remove tags on tasks.
- **FR-010**: System MUST support full-text search across task titles and descriptions, returning results within 1 second.
- **FR-011**: System MUST support filtering tasks by priority, tag, completion status, and due date range.
- **FR-012**: System MUST support sorting tasks by priority, due date, creation date, and title.
- **FR-013**: System MUST continue to accept task CRUD operations even when the messaging system is temporarily unavailable (degraded mode). Events are published fire-and-forget to the sidecar; the sidecar retries per its configured policy. If retries exhaust, the event is lost. No local outbox or user-facing warning is required.
- **FR-014**: System MUST provide a health check endpoint for each service that indicates service readiness.
- **FR-015**: System MUST support automated build and deployment pipelines triggered by code changes.
- **FR-016**: System MUST run fully on a local development cluster with all event-driven features functional.
- **FR-017**: Reminder notifications MUST be delivered as simulated notifications (log entries or email stubs) rather than real push notifications.
- **FR-018**: System MUST provide an audit stub that logs event processing outcomes for debugging purposes.

### Key Entities

- **Task**: A unit of work owned by a user. Key attributes: title, description, priority (low/medium/high/urgent), tags (list), due date, completion status, recurrence rule, created/updated timestamps.
- **Recurrence Rule**: Defines how a task repeats. Key attributes: frequency (daily/weekly/monthly), interval, day-of-week (for weekly), day-of-month (for monthly), next occurrence date, parent task reference, is_completion_based (boolean — false=time-based primary, true=on-complete secondary).
- **Task Event**: An immutable record of a task lifecycle action. Key attributes: event ID (unique, for idempotency dedup), event type (created/updated/completed/deleted), task ID, user ID, changed fields, timestamp.
- **Reminder**: A scheduled notification tied to a task's due date. Key attributes: task ID, user ID, trigger time, status (pending/sent/cancelled), reminder type (24h/1h).
- **User Session**: A connected client instance for real-time updates. Key attributes: user ID, connection ID, connected timestamp, last heartbeat.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users see task changes reflected across all open sessions within 2 seconds of the change being made.
- **SC-002**: Reminder notifications are delivered within 30 seconds of the scheduled trigger time.
- **SC-003**: New recurring task instances are created within 1 minute of the scheduled recurrence time.
- **SC-004**: Task search returns results within 1 second for a dataset of up to 10,000 tasks per user.
- **SC-005**: The system handles 20 concurrent users performing task operations without noticeable degradation (response times under 3 seconds).
- **SC-006**: A code change pushed to the repository is built, tested, and deployed to the cloud environment within 10 minutes.
- **SC-007**: The local development environment starts and becomes fully functional within 5 minutes from a single setup command.
- **SC-008**: All services recover automatically from a crash within 60 seconds via platform health checks.
- **SC-009**: Task CRUD operations succeed even when the messaging system is unavailable (degraded mode). Events are best-effort via sidecar retry; lost events are acceptable.
- **SC-010**: 95% of reminder notifications are delivered on schedule without being missed or duplicated.

## Assumptions

- The existing authentication system (Better Auth with JWT) from Phase III/IV remains in use and is not modified.
- The existing Neon PostgreSQL database from Phase II/III is retained and extended (no new database systems introduced).
- The existing frontend dashboard (Next.js 14, React Query, Tailwind CSS) is extended with new features rather than rewritten.
- The existing chatbot (OpenAI Agents SDK + MCP tools) is extended with new task capabilities rather than replaced.
- Reminder delivery is simulated (log output / email stub) — real push notifications are out of scope.
- WebSocket connections use basic JWT authentication — advanced WebSocket scaling/authentication is out of scope.
- The message broker free tier provides sufficient throughput for demo/hackathon workloads (10-20 concurrent users).
- Local development uses an in-cluster message broker instance; cloud deployment uses a managed cloud broker service.
- The CI/CD pipeline targets a single cloud cluster (no multi-region or blue/green deployments).
- Audit logging is stub-only — a full audit trail service is out of scope.
- Recurring tasks support both time-based (primary, calendar-anchored) and on-complete (secondary, optional) models. Scheduling prefers Dapr Jobs API for exact-time triggers with cron bindings + polling as fallback.
- Recurrence rules are persisted in the existing Neon PostgreSQL database (new columns on Task or a dedicated recurrence table).

## Out of Scope

- Full audit/compliance service (stub/log only)
- Real push notifications to mobile devices or browsers (simulated with logs/email stubs)
- Advanced WebSocket scaling, load balancing, or authentication beyond basic JWT
- Multi-region high-availability message broker configurations
- Deep security audit or penetration testing
- Multi-tenant isolation (single-tenant per deployment)
- Offline-first / service worker caching for the frontend
- Migration of existing data to event-sourced format (new events only)
- Shared/collaborative task lists between users (single-user ownership only)

## Dependencies

- Existing Phase IV codebase (backend, frontend, Helm charts, Dockerfiles)
- Neon PostgreSQL database (existing, will be extended with new tables)
- Container registry (ACR or equivalent for image storage)
- Cloud cluster subscription with sufficient quota for 4-6 services
- Message broker account (cloud free tier)
- GitHub repository with Actions enabled for CI/CD

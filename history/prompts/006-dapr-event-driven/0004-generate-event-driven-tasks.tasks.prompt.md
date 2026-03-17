---
id: "0004"
title: "Generate Event-Driven Tasks"
stage: tasks
date: 2026-02-10
surface: claude-code
model: claude-opus-4-6
feature: 006-dapr-event-driven
branch: 006-dapr-event-driven
user: developer
command: /sp.tasks
labels: [tasks, dapr, redpanda, aks, event-driven, microservices]
links:
  spec: specs/006-dapr-event-driven/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - specs/006-dapr-event-driven/tasks.md
tests:
  - N/A (task generation phase)
---

## Prompt

/sp.tasks — Generate an actionable, dependency-ordered tasks.md for feature 006-dapr-event-driven based on available design artifacts (plan.md, spec.md, data-model.md, contracts/events.md, contracts/api.md, contracts/dapr.md, quickstart.md).

## Response snapshot

Generated tasks.md with 82 tasks across 10 phases:

- Phase 1 (Setup): 8 tasks — directory structure, dependencies, Dockerfiles
- Phase 2 (Foundational): 13 tasks — models, event schemas, publisher, Dapr components, DB migration
- Phase 3 (US1 MVP): 7 tasks — event publishing in all task CRUD routes, audit stub, degraded mode
- Phase 4 (US2 Reminders): 8 tasks — reminder service, scheduling, cancellation, polling, simulated delivery
- Phase 5 (US3 Recurring): 8 tasks — recurring service, time-based polling, on-complete model, date calculation
- Phase 6 (US4 Real-Time Sync): 8 tasks — sync service, WebSocket, connection registry, frontend hook
- Phase 7 (US5 Organization): 6 tasks — urgent priority UI, filter indicators, debounced search, title sort
- Phase 8 (US7 Local K8s): 14 tasks — Helm templates (Redpanda, Dapr, services), scripts
- Phase 9 (US6 Cloud): 6 tasks — AKS provisioning, Redpanda Cloud, CI/CD, verification
- Phase 10 (Polish): 4 tasks — docs, helpers, quickstart validation, backward compatibility

Task organization follows user story priority order (P1 -> P2 -> P3). US7 (local) ordered before US6 (cloud) per constitution requirement. US2-US5 can run in parallel after US1 MVP completes.

## Outcome

- Impact: Complete task list ready for /sp.implement execution
- Tests: N/A (no tests requested in spec)
- Files: 1 file created (tasks.md with 82 tasks)
- Next prompts: /sp.implement to execute tasks, or /sp.analyze to validate cross-artifact consistency
- Reflection: Task count is high (82) but justified by 7 user stories + 3 new microservices + Helm templates. MVP path (Phase 1-3, 28 tasks) is achievable in ~4 hours.

## Evaluation notes (flywheel)

- Failure modes observed: None during task generation
- Graders run and results (PASS/FAIL): Manual format validation PASS (all tasks have checkbox, ID, [P]/[USn] labels, file paths)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.analyze to validate tasks against spec requirements coverage

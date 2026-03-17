---
id: "0003"
title: "Implementation Plan for Event-Driven Todo/Chatbot"
stage: plan
date: 2026-02-10
surface: claude-code
model: claude-opus-4-6
feature: 006-dapr-event-driven
branch: 006-dapr-event-driven
user: developer
command: /sp.plan
labels: [plan, dapr, redpanda, aks, event-driven, microservices]
links:
  spec: specs/006-dapr-event-driven/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - specs/006-dapr-event-driven/plan.md
  - specs/006-dapr-event-driven/research.md
  - specs/006-dapr-event-driven/data-model.md
  - specs/006-dapr-event-driven/quickstart.md
  - specs/006-dapr-event-driven/contracts/events.md
  - specs/006-dapr-event-driven/contracts/api.md
  - specs/006-dapr-event-driven/contracts/dapr.md
tests:
  - N/A (planning phase, no code tests)
---

## Prompt

/sp.plan — Execute the implementation planning workflow for feature 006-dapr-event-driven. Read the spec, constitution, and existing codebase to generate plan.md (Technical Context, Constitution Check, Project Structure), research.md (Dapr, Redpanda, AKS patterns), data-model.md (entity schemas, event schemas, Dapr components), contracts/ (events, API, Dapr components), and quickstart.md (local + cloud setup guide).

## Response snapshot

Generated 7 planning artifacts:

1. **plan.md**: Technical context (Python 3.11 + TypeScript 5.x, FastAPI + Dapr + Redpanda, Neon PostgreSQL, AKS/Minikube), full constitution check against Phase V requirements (all PASS, AKS adaptation from DOKS noted), project structure showing 4 microservices (backend, reminder, recurring, sync) + frontend + Redpanda broker, complexity tracking for 3 justified deviations.

2. **research.md**: Deep dive into Dapr building blocks (Pub/Sub, State, Service Invocation, Jobs API), Redpanda vs Apache Kafka comparison, Redpanda Cloud serverless config, AKS free tier resource planning (~900m CPU total fits Standard_B2s), event publishing patterns (fire-and-forget with sidecar retry), idempotent consumer pattern with dedup, WebSocket real-time sync architecture, reminder scheduling strategy (event-driven + polling hybrid), recurring task dual model (time-based + on-complete), CI/CD pipeline design, risk assessment.

3. **data-model.md**: 3 new database tables (recurrence_rule, task_event, reminder) with SQL DDL and SQLModel definitions, 6 event schemas in CloudEvents format (task.created/updated/completed/deleted, reminder.triggered, task.sync), Dapr component definitions for local and cloud (pubsub.kafka, state.postgresql), declarative subscription configs, entity relationship diagram, Priority enum extension (added "urgent").

4. **contracts/events.md**: Kafka topic definitions (task-events, reminders, task-updates) with partition/retention/key strategy, TypeScript interfaces for all 6 event types, consumer action matrix, idempotency contract, error handling contract with Dapr status codes.

5. **contracts/api.md**: Existing endpoint change matrix (event publishing added to CRUD routes), WebSocket /ws endpoint contract with message types (WsTaskUpdate, WsReminder, WsStatus), new service health endpoints, Dapr event handler endpoint contracts, TaskCreate/TaskResponse schema updates with recurrence fields.

6. **contracts/dapr.md**: Component specs for local vs cloud pub/sub, state store config, subscription definitions with route rules, sidecar annotation template, SDK usage patterns for publishing and subscribing.

7. **quickstart.md**: Step-by-step guides for local (Minikube + Dapr + Redpanda) and cloud (AKS + Redpanda Cloud) deployment, prerequisite tool table, build/deploy commands, verification steps, troubleshooting guide, rollback procedures, cleanup commands.

## Outcome

- Impact: Complete implementation plan ready for /sp.tasks task generation
- Tests: N/A (planning phase)
- Files: 7 files created (plan.md, research.md, data-model.md, quickstart.md, 3 contracts)
- Next prompts: /sp.tasks to generate implementation tasks, then /sp.implement to execute
- Reflection: Constitution check adapted DOKS -> AKS cleanly. The existing codebase has good separation that makes event publishing additive. Three new microservices justified by different lifecycle needs.

## Evaluation notes (flywheel)

- Failure modes observed: Session interrupted twice during planning (network/user), required context recovery
- Graders run and results (PASS/FAIL): Manual constitution check PASS (all 5 principles + Phase V constraints)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.tasks to validate plan completeness by seeing if tasks can be generated without ambiguity

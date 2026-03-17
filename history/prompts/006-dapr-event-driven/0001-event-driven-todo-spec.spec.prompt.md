---
id: "0001"
title: event-driven-todo-spec
stage: spec
date: 2026-02-09
surface: claude-code
model: claude-opus-4-6
feature: 006-dapr-event-driven
branch: 006-dapr-event-driven
user: developer
command: /sp.specify
labels: [spec, event-driven, dapr, redpanda, aks]
links:
  spec: specs/006-dapr-event-driven/spec.md
  ticket: ~
  adr: ~
  pr: ~
files:
  - specs/006-dapr-event-driven/spec.md
  - specs/006-dapr-event-driven/checklists/requirements.md
tests:
  - ~
---

## Prompt

/sp.specify Advanced Event-Driven Todo/Chatbot with Dapr + Redpanda Cloud + AKS. Target audience: Everyday users (students, professionals, teams) who need a reliable, proactive task manager with chat interface, reminders, recurring tasks, and real-time sync across devices. Focus: Upgrade CRUD Todo + Chatbot to decoupled, event-driven system using Dapr + Redpanda Cloud on Azure AKS. Success criteria included: event-driven task lifecycle with 3 Kafka topics, Dapr building blocks (Pub/Sub, State, Service Invocation, Secrets, Jobs/Cron), separate Notification and Recurring Task services, local Minikube + cloud AKS deployment, CI/CD via GitHub Actions, real-time sync via WebSocket, and reminder delivery. Constraints: Redpanda Cloud free tier, maximize Dapr abstractions, extend existing Helm charts, no new DBs beyond Neon.

## Response snapshot

Created feature branch `006-dapr-event-driven` and wrote comprehensive spec with 7 user stories (P1: event-driven task management + reminders; P2: recurring tasks, real-time sync, enhanced organization; P3: cloud deployment, local dev), 18 functional requirements, 5 key entities, 10 measurable success criteria, 6 edge cases, assumptions, out-of-scope, and dependencies. All quality checklist items passed with no [NEEDS CLARIFICATION] markers needed due to thorough user input.

## Outcome

- Impact: Feature spec created and validated — ready for /sp.plan
- Tests: N/A (spec phase)
- Files: specs/006-dapr-event-driven/spec.md, specs/006-dapr-event-driven/checklists/requirements.md
- Next prompts: /sp.clarify or /sp.plan
- Reflection: User provided exceptionally detailed input with explicit success criteria and constraints, which eliminated ambiguity and removed the need for clarification questions.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist — PASS (all 16 items)
- Prompt variant (if applicable): ~
- Next experiment (smallest change to try): ~

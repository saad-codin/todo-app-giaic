# Implementation Plan: Advanced Event-Driven Todo/Chatbot

**Branch**: `006-dapr-event-driven` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-dapr-event-driven/spec.md`

## Summary

Transform the existing monolithic Todo/Chatbot application into an event-driven architecture using Dapr building blocks for pub/sub messaging (backed by Redpanda/Kafka), state management, and service invocation. The system publishes task lifecycle events (create, update, complete, delete) to Kafka topics consumed by dedicated microservices: a reminder service for due-date notifications, a recurring task service for automatic task instance creation, and a real-time sync service for multi-session updates via WebSocket. Deployment targets Azure Kubernetes Service (AKS) for cloud and Minikube for local development, both with Dapr sidecars injected alongside application containers.

## Technical Context

**Language/Version**: Python 3.11+ (backend services), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, Dapr Python SDK (`dapr`), Redpanda (Kafka-compatible), SQLModel, OpenAI Agents SDK, Next.js 14, React Query, WebSocket (native `websockets` library)
**Storage**: Neon PostgreSQL (existing, extended with new tables for recurrence rules and event log)
**Testing**: pytest (backend unit + integration), Playwright or curl-based E2E, deployment verification scripts
**Target Platform**: Kubernetes (AKS for cloud, Minikube for local), Linux containers
**Project Type**: Web application (multi-service microservices)
**Performance Goals**: <3s response time under 20 concurrent users, <2s real-time sync latency, <30s reminder delivery accuracy, <1min recurring task creation
**Constraints**: At-least-once delivery with idempotent consumers, fire-and-forget degraded mode, Dapr sidecar dependency per service, free-tier cloud resources
**Scale/Scope**: 20 concurrent users, 10k tasks per user, 4 microservices + 1 frontend + 1 message broker

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate (Phase V Requirements)

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Correctness First | PASS | All 20 functional requirements mapped to user stories with testable acceptance scenarios |
| II. Deterministic Behavior | PASS | Event-driven components are deterministic (same event -> same processing). AI features remain isolated in existing chat agent |
| III. Incremental Evolution (NON-NEGOTIABLE) | PASS | Phase I-IV functionality preserved. New event publishing is additive to existing task CRUD routes. Existing REST API, auth, dashboard, chatbot unchanged |
| IV. Simplicity Before Scale | PASS | Dapr abstracts messaging complexity. Only 3 Kafka topics. No unnecessary infrastructure. Services are thin consumers |
| V. Observability | PASS | FR-018 requires audit stub logging. Health checks (FR-014) on all services. Dapr provides built-in observability |

### Phase V Technology Constraints

| Constraint | Status | Notes |
|------------|--------|-------|
| Kafka for event-driven | PASS | Redpanda is Kafka-compatible; uses Kafka protocol via Dapr pub/sub component |
| Dapr for service communication | PASS | Dapr Pub/Sub, State, Service Invocation building blocks used |
| Cloud deployment (originally DOKS) | ADAPTED | Using AKS instead of DigitalOcean DOKS (user decision). Infrastructure still defined as code |
| Infrastructure as Code | PASS | Helm charts + GitHub Actions CI/CD. AKS provisioning via Azure CLI scripts |
| Cloud costs documented | PASS | AKS free tier (1 cluster), ACR Basic (~$5/mo), Redpanda Serverless free tier |

### Phase V Acceptance Criteria

| Criterion | How Met |
|-----------|---------|
| System deploys to cloud with automated scripts | GitHub Actions pipeline builds images, pushes to ACR, deploys to AKS via Helm |
| Event-driven architecture functions correctly | Task events flow through Redpanda topics, consumed by reminder/recurring/sync services |
| Monitoring and observability production-ready | Dapr dashboard, health endpoints, structured logging, audit stubs |

### Phase V Testing Standards

| Standard | How Met |
|----------|---------|
| Deployment scripts tested locally first | Minikube + Dapr local setup validates all services before AKS deployment |
| Health checks for all services | `/health` endpoint on every service, Kubernetes readiness/liveness probes |
| E2E tests in deployed environment | Deployment verification script tests task CRUD -> event flow -> consumer processing |
| Rollback procedures documented | Helm rollback command + CI/CD rollback stage documented in quickstart.md |

### Post-Design Re-evaluation

All gates PASS. No constitution violations. The adaptation from DOKS to AKS is a cloud provider substitution, not a principle violation.

## Project Structure

### Documentation (this feature)

```text
specs/006-dapr-event-driven/
├── plan.md              # This file
├── research.md          # Phase 0: Dapr, Redpanda, AKS research
├── data-model.md        # Phase 1: Entity schemas, event schemas, Dapr components
├── quickstart.md        # Phase 1: Local + cloud setup guide
├── contracts/           # Phase 1: API and event contracts
│   ├── events.md        # Event schemas for all 3 topics
│   ├── api.md           # New REST/WebSocket endpoints
│   └── dapr.md          # Dapr component configurations
└── tasks.md             # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py                     # Extended: event publisher integration
├── models.py                   # Extended: RecurrenceRule, TaskEvent entities
├── db.py                       # Existing: database sessions
├── auth.py                     # Existing: JWT auth
├── mcp_server.py               # Existing: MCP tools
├── events/                     # NEW: Event publishing layer
│   ├── __init__.py
│   ├── publisher.py            # Dapr pub/sub publish helper
│   └── schemas.py              # Event dataclasses (TaskEvent, ReminderEvent)
├── routes/
│   ├── auth.py                 # Existing
│   ├── tasks.py                # Extended: publish events after CRUD
│   ├── chat.py                 # Existing
│   └── ws.py                   # NEW: WebSocket endpoint for real-time sync
├── Dockerfile                  # Existing (no changes needed)
├── requirements.txt            # Extended: dapr, websockets
└── startup.sh                  # Existing

services/                       # NEW: Microservice consumers
├── reminder/
│   ├── main.py                 # FastAPI app subscribing to task-events topic
│   ├── requirements.txt        # dapr, fastapi, uvicorn, sqlmodel
│   └── Dockerfile
├── recurring/
│   ├── main.py                 # FastAPI app subscribing to task-events topic
│   ├── requirements.txt        # dapr, fastapi, uvicorn, sqlmodel
│   └── Dockerfile
└── sync/
    ├── main.py                 # FastAPI app subscribing to task-updates topic
    ├── requirements.txt        # dapr, fastapi, uvicorn, websockets
    └── Dockerfile

frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/page.tsx  # Extended: WebSocket connection for real-time
│   │   └── ...                 # Existing pages unchanged
│   ├── components/
│   │   └── tasks/              # Extended: priority/tag UI improvements
│   ├── lib/
│   │   ├── api.ts              # Existing
│   │   ├── hooks/
│   │   │   ├── useTasks.ts     # Extended: WebSocket invalidation
│   │   │   └── useWebSocket.ts # NEW: WebSocket connection hook
│   │   └── ...
│   └── ...
├── Dockerfile                  # Existing
└── package.json                # Existing (no new frontend deps needed)

helm/todo-chatbot/
├── Chart.yaml                  # Updated: version bump
├── values.yaml                 # Extended: new services, Dapr annotations, Redpanda config
├── values-local.yaml           # Extended: local Redpanda settings
└── templates/
    ├── backend-deployment.yaml         # Extended: Dapr sidecar annotations
    ├── frontend-deployment.yaml        # Existing
    ├── reminder-deployment.yaml        # NEW
    ├── reminder-service.yaml           # NEW
    ├── recurring-deployment.yaml       # NEW
    ├── recurring-service.yaml          # NEW
    ├── sync-deployment.yaml            # NEW
    ├── sync-service.yaml               # NEW
    ├── dapr-pubsub-component.yaml      # NEW: Dapr pub/sub -> Redpanda
    ├── dapr-statestore-component.yaml  # NEW: Dapr state -> PostgreSQL
    ├── dapr-subscription.yaml          # NEW: Topic subscriptions
    ├── redpanda-statefulset.yaml       # NEW: Local Redpanda (Minikube only)
    ├── redpanda-service.yaml           # NEW: Local Redpanda service
    └── ...existing templates

dapr/                           # NEW: Dapr component definitions (local dev)
├── pubsub.yaml                 # Pub/Sub component (Redpanda)
├── statestore.yaml             # State store component (PostgreSQL)
└── subscriptions.yaml          # Declarative subscriptions

scripts/
├── minikube-setup.sh           # Extended: install Dapr CLI + init
├── build-images.sh             # Extended: build new service images
├── deploy.sh                   # Extended: deploy with Dapr components
├── deploy-azure.sh             # Extended: AKS + Dapr deployment
└── setup-redpanda-cloud.sh     # NEW: Redpanda Cloud cluster setup

.github/workflows/
└── deploy.yml                  # NEW: CI/CD pipeline for AKS
```

**Structure Decision**: Extended web application structure (Option 2). The existing `backend/` and `frontend/` directories are preserved and extended in-place. A new `services/` directory at the root houses the three consumer microservices (reminder, recurring, sync). Dapr component definitions live in `dapr/` for local development and are templated in `helm/` for Kubernetes deployment.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 3 new microservices (reminder, recurring, sync) beyond existing backend+frontend | Event-driven consumers must run independently to process messages from Kafka topics asynchronously. Embedding consumers in the backend monolith would defeat the purpose of event-driven architecture and prevent independent scaling | A single "worker" service was considered but rejected because reminder scheduling, recurring task logic, and WebSocket broadcasting have different lifecycle and scaling needs |
| AKS instead of DOKS (constitution says DigitalOcean) | User already has Azure infrastructure (ACR, Container Apps) from Phase IV-A deployment. AKS free tier available. Switching to DOKS would require new cloud account and registry setup | The architecture is cloud-agnostic via Helm + Dapr; only the deployment scripts and CI/CD targets change |
| Redpanda instead of Apache Kafka | Redpanda is Kafka-protocol-compatible but simpler to operate (single binary, no ZooKeeper/KRaft). Free serverless tier available. Dapr pub/sub component works identically with either | Running full Apache Kafka cluster requires more resources and operational complexity for a hackathon demo |

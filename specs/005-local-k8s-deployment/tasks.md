# Tasks: Local Kubernetes Deployment for Todo Chatbot

**Input**: Design documents from `/specs/005-local-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md, contracts/

**Tests**: No automated tests requested. Validation is manual per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for containerization

- [x] T001 Create helm/ directory structure at repository root
- [x] T002 Create scripts/ directory for deployment helper scripts
- [x] T003 [P] Create .dockerignore file at frontend/.dockerignore
- [x] T004 [P] Create .dockerignore file at backend/.dockerignore
- [x] T005 Add values-local.yaml to .gitignore to prevent secret commits

**Checkpoint**: Directory structure ready for containerization work

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Enable Next.js standalone output required for containerization

**CRITICAL**: Frontend must be configured for standalone output before Dockerfile can work

- [x] T006 Update frontend/next.config.js to enable standalone output mode
- [x] T007 Verify frontend builds successfully with `npm run build` in frontend/

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Containerize Applications (Priority: P1)

**Goal**: Package frontend and backend into Docker containers that run consistently

**Independent Test**: Build images locally and run with Docker to verify applications start and respond

### Implementation for User Story 1

- [x] T008 [P] [US1] Create backend Dockerfile at backend/Dockerfile with multi-stage build
- [x] T009 [P] [US1] Create frontend Dockerfile at frontend/Dockerfile with multi-stage build
- [ ] T010 [US1] Build backend container image: `docker build -t todo-backend:latest ./backend`
- [ ] T011 [US1] Build frontend container image: `docker build -t todo-frontend:latest ./frontend`
- [ ] T012 [US1] Test backend container runs: `docker run -p 8000:8000 todo-backend:latest`
- [ ] T013 [US1] Test frontend container runs: `docker run -p 3000:3000 todo-frontend:latest`
- [x] T014 [US1] Create build script at scripts/build-images.sh for automated image building

**Checkpoint**: Both containers build and run successfully - US1 complete

---

## Phase 4: User Story 2 - Deploy to Local Kubernetes Cluster (Priority: P2)

**Goal**: Deploy containerized applications to Minikube with pods reaching Running status

**Independent Test**: Start Minikube, deploy with Helm, verify pods running and services accessible

### Implementation for User Story 2

- [x] T015 [US2] Create Minikube setup script at scripts/minikube-setup.sh
- [x] T016 [US2] Create Helm chart metadata at helm/todo-chatbot/Chart.yaml
- [x] T017 [US2] Create default values at helm/todo-chatbot/values.yaml per contracts/helm-values.yaml
- [x] T018 [P] [US2] Create helper templates at helm/todo-chatbot/templates/_helpers.tpl
- [x] T019 [P] [US2] Create namespace template at helm/todo-chatbot/templates/namespace.yaml
- [x] T020 [P] [US2] Create ConfigMap template at helm/todo-chatbot/templates/configmap.yaml
- [x] T021 [P] [US2] Create Secret template at helm/todo-chatbot/templates/secret.yaml
- [x] T022 [P] [US2] Create backend deployment at helm/todo-chatbot/templates/backend-deployment.yaml
- [x] T023 [P] [US2] Create backend service at helm/todo-chatbot/templates/backend-service.yaml
- [x] T024 [P] [US2] Create frontend deployment at helm/todo-chatbot/templates/frontend-deployment.yaml
- [x] T025 [P] [US2] Create frontend service at helm/todo-chatbot/templates/frontend-service.yaml
- [ ] T026 [US2] Verify Helm chart lints: `helm lint ./helm/todo-chatbot`
- [x] T027 [US2] Create deployment script at scripts/deploy.sh for one-command deployment
- [ ] T028 [US2] Test deployment: start Minikube, load images, install Helm release
- [ ] T029 [US2] Verify pods reach Running status: `kubectl get pods -n todo-chatbot`
- [ ] T030 [US2] Verify services accessible: `kubectl get svc -n todo-chatbot`

**Checkpoint**: Applications deployed to Kubernetes - US2 complete

---

## Phase 5: User Story 3 - Manage Deployments with Helm Charts (Priority: P3)

**Goal**: Enable configuration through values files and support upgrades

**Independent Test**: Install release, upgrade with different values, verify changes applied

### Implementation for User Story 3

- [x] T031 [US3] Create values-local.yaml template at helm/todo-chatbot/values-local.yaml.example
- [x] T032 [US3] Add chart README at helm/todo-chatbot/README.md with usage instructions
- [ ] T033 [US3] Test Helm upgrade: `helm upgrade todo-chatbot ./helm/todo-chatbot -n todo-chatbot`
- [ ] T034 [US3] Verify Helm release visible: `helm list -n todo-chatbot`
- [ ] T035 [US3] Test value override: change replica count and verify deployment updates

**Checkpoint**: Helm chart fully functional with upgrades - US3 complete

---

## Phase 6: User Story 4 - End-to-End Chatbot Functionality (Priority: P4)

**Goal**: Verify full application stack works in Kubernetes environment

**Independent Test**: Access chat interface, create/list/complete tasks via AI assistant

### Implementation for User Story 4

- [ ] T036 [US4] Expose frontend service: `minikube service frontend-svc -n todo-chatbot`
- [ ] T037 [US4] Verify frontend loads in browser at exposed URL
- [ ] T038 [US4] Test sign in with existing credentials
- [ ] T039 [US4] Test create task via chat: "Create a task to test Kubernetes"
- [ ] T040 [US4] Test list tasks via chat: "Show my tasks"
- [ ] T041 [US4] Test complete task via chat: "Complete the Kubernetes test task"
- [ ] T042 [US4] Verify backend logs accessible: `kubectl logs -f deployment/backend -n todo-chatbot`

**Checkpoint**: End-to-end functionality verified - US4 complete

---

## Phase 7: User Story 5 - AI-Assisted DevOps Operations (Priority: P5)

**Goal**: Document kubectl-ai usage for natural language Kubernetes operations

**Independent Test**: Use kubectl-ai to query cluster status and get operational insights

### Implementation for User Story 5

- [x] T043 [US5] Document kubectl-ai installation in quickstart.md (already done - verify)
- [x] T044 [US5] Add at least 5 kubectl-ai example commands to quickstart.md
- [x] T045 [US5] Document k9s as alternative tool for visual debugging
- [ ] T046 [US5] Test kubectl-ai: `kubectl-ai "show pod status in todo-chatbot namespace"`

**Checkpoint**: AI DevOps documentation complete - US5 complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and documentation updates

- [x] T047 [P] Update CLAUDE.md with Phase IV commands and patterns
- [x] T048 [P] Ensure all scripts are executable (chmod +x on Unix)
- [ ] T049 Run full quickstart.md validation end-to-end
- [ ] T050 Clean up any temporary files or test artifacts

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (standalone Next.js config)
- **User Story 2 (Phase 4)**: Depends on US1 (needs container images)
- **User Story 3 (Phase 5)**: Depends on US2 (needs working Helm deployment)
- **User Story 4 (Phase 6)**: Depends on US2 (needs running Kubernetes deployment)
- **User Story 5 (Phase 7)**: Depends on US2 (needs running cluster to demonstrate)
- **Polish (Phase 8)**: Depends on all desired user stories complete

### User Story Dependencies

```
Setup → Foundational → US1 (Containers) → US2 (K8s Deploy) → US3 (Helm Upgrades)
                                              ↓
                                         US4 (E2E Test)
                                              ↓
                                         US5 (AI DevOps)
```

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T003 [P] frontend/.dockerignore
T004 [P] backend/.dockerignore
```

**Phase 3 (US1 - Containerization)**:
```
T008 [P] backend/Dockerfile
T009 [P] frontend/Dockerfile
```

**Phase 4 (US2 - Kubernetes)**:
```
T018 [P] _helpers.tpl
T019 [P] namespace.yaml
T020 [P] configmap.yaml
T021 [P] secret.yaml
T022 [P] backend-deployment.yaml
T023 [P] backend-service.yaml
T024 [P] frontend-deployment.yaml
T025 [P] frontend-service.yaml
```

**Phase 8 (Polish)**:
```
T047 [P] CLAUDE.md update
T048 [P] Script permissions
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (enable standalone Next.js)
3. Complete Phase 3: User Story 1 (Dockerfiles)
4. **STOP and VALIDATE**: Both containers build and run
5. Commit as "feat: containerize frontend and backend"

### Incremental Delivery

1. Setup + Foundational → Ready for containers
2. Add US1 (Containers) → Test locally with Docker → Commit
3. Add US2 (Kubernetes) → Test on Minikube → Commit
4. Add US3 (Helm upgrades) → Test upgrade flow → Commit
5. Add US4 (E2E) → Full validation → Commit
6. Add US5 (AI DevOps) → Documentation → Commit
7. Polish → Final cleanup → Release

### Suggested Commit Points

| After Phase | Commit Message |
|-------------|----------------|
| Phase 1 | `chore: setup directory structure for K8s deployment` |
| Phase 2 | `chore: enable Next.js standalone output` |
| Phase 3 | `feat: add Dockerfiles for frontend and backend` |
| Phase 4 | `feat: add Helm chart for Kubernetes deployment` |
| Phase 5 | `feat: add Helm upgrade and configuration support` |
| Phase 6 | `test: verify end-to-end chatbot on Kubernetes` |
| Phase 7 | `docs: add kubectl-ai usage examples` |
| Phase 8 | `chore: polish and cleanup for Phase IV release` |

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 50 |
| **Setup Tasks** | 5 |
| **Foundational Tasks** | 2 |
| **US1 Tasks** | 7 |
| **US2 Tasks** | 16 |
| **US3 Tasks** | 5 |
| **US4 Tasks** | 7 |
| **US5 Tasks** | 4 |
| **Polish Tasks** | 4 |
| **Parallel Opportunities** | 14 tasks across 4 phases |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each phase or logical group
- Stop at any checkpoint to validate progress
- US4 and US5 can proceed in parallel after US2 completes

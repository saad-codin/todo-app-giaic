# Research: Local Kubernetes Deployment for Todo Chatbot

**Feature**: 005-local-k8s-deployment
**Date**: 2026-01-19
**Status**: Complete

## Technology Decisions

### 1. Container Runtime and Build

**Decision**: Docker with multi-stage builds

**Rationale**:
- Docker Desktop is already assumed as a prerequisite (spec assumption)
- Multi-stage builds reduce image size and improve security (FR-009)
- Docker Compose can be used for local development before K8s migration

**Frontend Container Strategy**:
- Base: `node:20-alpine` for build stage
- Runtime: `node:20-alpine` with standalone Next.js output
- Multi-stage: Build dependencies not included in final image
- Non-root user for security

**Backend Container Strategy**:
- Base: `python:3.11-slim` for both build and runtime
- Multi-stage: Build dependencies (gcc, build tools) not in final image
- Use `requirements.txt` with pinned versions
- Non-root user for security

### 2. Local Kubernetes Platform

**Decision**: Minikube

**Rationale**:
- Explicitly required by spec (FR-003, FR-010)
- Works on Windows, macOS, and Linux
- Supports LoadBalancer service type via `minikube tunnel`
- Built-in addons: ingress, metrics-server, dashboard

**Configuration**:
- Driver: Docker (most portable)
- Memory: 4GB minimum (spec assumption)
- CPU: 2 cores minimum
- Kubernetes version: Latest stable (1.28+)

**Alternatives Considered**:
- Kind: Faster but less feature-complete
- k3d: Lightweight but less documentation
- Docker Desktop K8s: Limited customization

### 3. Deployment Configuration

**Decision**: Helm 3 as single source of deployment configuration

**Rationale**:
- Required by spec (FR-006, User Story 3)
- Templating enables environment-specific configuration
- Release management for upgrades and rollbacks
- Values files for dev/staging/prod configurations

**Helm Chart Structure**:
```
helm/
└── todo-chatbot/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-dev.yaml
    ├── templates/
    │   ├── _helpers.tpl
    │   ├── frontend-deployment.yaml
    │   ├── frontend-service.yaml
    │   ├── backend-deployment.yaml
    │   ├── backend-service.yaml
    │   ├── configmap.yaml
    │   └── secret.yaml
    └── README.md
```

**Alternatives Considered**:
- Raw Kubernetes manifests: Less maintainable
- Kustomize: Good for overlays but less templating power
- Jsonnet/CUE: Steeper learning curve

### 4. Service Networking

**Decision**: ClusterIP services with Minikube tunnel or port-forward

**Rationale**:
- ClusterIP provides internal cluster communication (FR-004)
- `minikube service` or `minikube tunnel` exposes to host (FR-005)
- No ingress controller needed for local development (Out of Scope)

**Service Architecture**:
```
┌─────────────────────────────────────────────────────┐
│                   Minikube Cluster                   │
│                                                      │
│  ┌─────────────────┐      ┌─────────────────────┐  │
│  │ Frontend Pod    │      │ Backend Pod          │  │
│  │ (Next.js)       │      │ (FastAPI)            │  │
│  │ Port: 3000      │─────▶│ Port: 8000           │  │
│  └────────┬────────┘      └──────────┬──────────┘  │
│           │                           │             │
│  ┌────────┴────────┐      ┌──────────┴──────────┐  │
│  │ frontend-svc    │      │ backend-svc          │  │
│  │ ClusterIP:3000  │      │ ClusterIP:8000       │  │
│  └─────────────────┘      └─────────────────────┘  │
│                                                      │
└──────────────────────┬───────────────────────────────┘
                       │ minikube tunnel / port-forward
                       ▼
                 Host Machine
                 http://localhost:3000
```

### 5. Configuration and Secrets Management

**Decision**: Kubernetes ConfigMaps and Secrets

**Rationale**:
- Required by spec (FR-007)
- Native Kubernetes approach
- Secrets base64 encoded (sufficient for local dev)
- ConfigMaps for non-sensitive configuration

**Configuration Items**:
| Type | Key | Description |
|------|-----|-------------|
| Secret | DATABASE_URL | Neon PostgreSQL connection string |
| Secret | OPENAI_API_KEY | OpenAI API key for AI features |
| Secret | JWT_SECRET | JWT signing secret |
| ConfigMap | FRONTEND_URL | Backend CORS allowed origin |
| ConfigMap | API_URL | Frontend API endpoint |
| ConfigMap | CHATKIT_DOMAIN_KEY | ChatKit domain key |

### 6. AI DevOps Tooling

**Decision**: kubectl-ai and kagent as optional enhancements

**Rationale**:
- Required by spec (FR-008, User Story 5)
- Constitution allows but doesn't require these tools
- Provides learning value for AI-assisted operations
- Non-blocking for core functionality

**kubectl-ai**:
- Natural language to kubectl commands
- Installation via pip: `pip install kubectl-ai`
- Useful for: querying pods, logs, resources

**kagent (if available)**:
- Kubernetes troubleshooting assistant
- Installation varies by implementation
- Alternative: k9s, lens for visual debugging

### 7. Image Registry

**Decision**: Local Minikube registry or direct image load

**Rationale**:
- No external registry needed for local development
- `minikube image load` pushes images directly to cluster
- Faster iteration during development

**Alternative for future**: Local Docker registry for multi-cluster scenarios

### 8. Health Checks and Probes

**Decision**: HTTP health endpoints with Kubernetes probes

**Backend**:
- Readiness probe: `GET /health` (already exists in main.py:56)
- Liveness probe: Same endpoint
- Initial delay: 10 seconds

**Frontend**:
- Readiness probe: `GET /api/health` or root page
- Liveness probe: TCP port check
- Initial delay: 15 seconds (Next.js startup time)

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Which Kubernetes platform? | Minikube (spec requirement) |
| Raw manifests vs Helm? | Helm (spec requirement) |
| How to expose services? | minikube tunnel / port-forward |
| External database or in-cluster? | External Neon DB (existing Phase III setup) |
| Container base images? | Alpine-based for size, slim for Python |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Minikube resource constraints | Medium | High | Document minimum requirements clearly |
| Network connectivity to Neon DB | Medium | High | Allow cluster outbound traffic, test early |
| Image build failures | Low | Medium | Clear Dockerfile documentation, CI validation |
| kubectl-ai availability | Low | Low | Optional feature, document alternatives |

## Dependencies

**Required**:
- Docker Desktop (installed and running)
- Minikube CLI
- Helm CLI
- kubectl CLI

**Optional**:
- kubectl-ai (pip package)
- k9s (terminal UI for Kubernetes)

## Next Steps

1. Create Dockerfiles for frontend and backend
2. Create Helm chart structure
3. Write deployment documentation
4. Test end-to-end on Minikube

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Todo App monorepo using GitHub Spec-Kit for spec-driven development.

## Commands

```bash
# Frontend (Next.js 14)
cd frontend && npm run dev      # Development server
cd frontend && npm run build    # Production build
cd frontend && npm run lint     # Lint code

# Backend (Python FastAPI)
cd backend && uvicorn main:app --reload    # Development server
cd backend && pytest                        # Run tests
cd backend && pytest tests/test_api.py -k "test_name"  # Single test

# Both services
docker-compose up               # Run full stack
```

## Architecture

### Monorepo Structure
- `/frontend` - Next.js 14 App Router application
- `/backend` - Python FastAPI server
- `/specs` - Spec-driven development documents

### Spec-Kit Structure
Specifications in `/specs`:
- `overview.md` - Project overview
- `features/` - Feature specs (what to build)
- `api/` - API endpoint and MCP tool specs
- `database/` - Schema and model specs
- `ui/` - Component and page specs

**Always read relevant spec before implementing.** Reference specs with: `@specs/features/[feature].md`

### Frontend Patterns (Next.js 14)
- **Server components by default** - Client components only when interactivity needed
- **API calls** go through `/lib/api.ts`:
  ```typescript
  import { api } from '@/lib/api'
  const tasks = await api.getTasks()
  ```
- **Styling**: Tailwind CSS classes only, no inline styles

### Backend Patterns (FastAPI)
- SQLModel for database models
- Neon DB for PostgreSQL
- Pydantic for request/response validation

### AI Chatbot (Phase III)
- **Chat endpoint**: `POST /api/chat` - Send natural language message
- **MCP Tools**: Task CRUD operations in `backend/mcp/tools.py`
- **Agent**: OpenAI Agents SDK in `backend/agent/runner.py`
- **Frontend**: Chat page at `/chat` with conversation persistence

### Kubernetes Deployment (Phase IV)
- **Dockerfiles**: `frontend/Dockerfile`, `backend/Dockerfile` - Multi-stage builds
- **Helm Chart**: `helm/todo-chatbot/` - Templated K8s deployment
- **Scripts**: `scripts/minikube-setup.sh`, `scripts/build-images.sh`, `scripts/deploy.sh`
- **Quickstart**: `specs/005-local-k8s-deployment/quickstart.md`

```bash
# Kubernetes Commands
./scripts/minikube-setup.sh                    # Start Minikube
./scripts/build-images.sh --minikube           # Build images
./scripts/deploy.sh                            # Deploy with Helm
minikube service frontend-svc -n todo-chatbot  # Access app
kubectl get pods -n todo-chatbot               # Check pods
helm list -n todo-chatbot                      # Check release
```

## Development Workflow

1. Read spec: `@specs/features/[feature].md`
2. Implement backend: `@backend/CLAUDE.md`
3. Implement frontend: `@frontend/CLAUDE.md`
4. Test and iterate

## Active Technologies
- Docker, Minikube, Helm 3, kubectl (005-local-k8s-deployment)
- Python FastAPI, OpenAI Agents SDK, MCP SDK, Neon PostgreSQL (004-ai-todo-chatbot)
- OpenAI ChatKit frontend, Better Auth with JWT (004-ai-todo-chatbot)
- TypeScript 5.x, Next.js 14+ (App Router) (003-todo-frontend-dashboard)
- Next.js, Better Auth, Tailwind CSS, date-fns, React Query (TanStack Query) (003-todo-frontend-dashboard)
- Python 3.13+ + Python standard library only (no external packages) (001-console-todo)
- In-memory only (Python dict/list structures) (001-console-todo)
- Python 3.13+ + Python standard library only (datetime, dataclasses, typing) (002-todo-advanced-features)
- In-memory only (dict-based repository from feature 001) (002-todo-advanced-features)
- Python 3.11+, TypeScript 5.x (frontend) + FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, OpenAI ChatKit (frontend) (004-ai-todo-chatbot)
- Neon PostgreSQL (existing from Phase II, extended with conversation tables) (004-ai-todo-chatbot)

## Recent Changes
- 005-local-k8s-deployment: Containerized frontend/backend with Helm charts for Minikube deployment
- 004-ai-todo-chatbot: AI-powered conversational todo management with MCP tools and stateless backend
- 003-todo-frontend-dashboard: Added Next.js 14+ frontend with Better Auth, React Query, Tailwind CSS
- 002-todo-advanced-features: Added priorities, tags, due dates, recurring tasks, search/filter/sort
- 001-console-todo: Added Python 3.13+ + Python standard library only (no external packages)

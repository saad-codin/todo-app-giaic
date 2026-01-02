<!--
Sync Impact Report:
Version change: 1.0.0 → 1.0.0 (Initial ratification)
Modified principles: N/A (initial version)
Added sections:
  - Phase Execution Standards
  - Technology Constraints
  - Testing Standards
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section aligns with principles
  ✅ spec-template.md - Requirements structure supports phase-based development
  ✅ tasks-template.md - Task categorization reflects testing and observability principles
Follow-up TODOs: None
-->

# AI-Native In-Memory Todo Application Constitution

## Core Principles

### I. Correctness First

Functionality MUST match explicit requirements before any optimization or enhancement.
Every feature MUST be validated against its specification before being considered complete.
No code may be merged that deviates from documented requirements without explicit approval
and specification amendment.

**Rationale**: Premature optimization and feature creep are the primary risks in evolving
multi-phase projects. Correctness ensures each phase builds on a solid foundation.

### II. Deterministic Behavior

Identical inputs MUST produce identical outputs unless the feature is explicitly AI-driven.
All non-AI components MUST be reproducible and testable with fixed test cases.
AI-driven features introduced in Phase III and beyond MUST be isolated from core
deterministic logic.

**Rationale**: Predictability is essential for debugging, testing, and maintaining trust
as the system evolves from simple console app to cloud-native platform.

### III. Incremental Evolution (NON-NEGOTIABLE)

Each phase MUST build cleanly on the previous phase without introducing regressions.
Before beginning a new phase, all acceptance criteria from the prior phase MUST pass.
No functionality from a completed phase may be removed or broken by subsequent phases.

**Rationale**: This is a learning-oriented project where each phase represents a milestone.
Breaking prior phases undermines the educational value and project integrity.

### IV. Simplicity Before Scale

Minimal abstractions MUST be used until complexity is justified by phase requirements.
No infrastructure, patterns, or dependencies may be introduced before the phase that
requires them. YAGNI (You Aren't Gonna Need It) principles apply strictly.

**Rationale**: Over-engineering in early phases creates unnecessary complexity that
obscures learning objectives and makes future phases harder to implement correctly.

### V. Observability and Debuggability

Every phase MUST include logging, error messages, and state inspection capabilities
appropriate to that phase's architecture. Developers MUST be able to trace execution
flow and diagnose issues without instrumentation beyond what the phase requires.

**Rationale**: As the system evolves through five phases, maintainability depends on
understanding system behavior at each layer. Observability is not optional.

## Phase Execution Standards

### Phase I: In-Memory Python Console Todo App

**Requirements**:
- Pure in-memory data storage (no files, no databases, no serialization)
- Console-based interaction only (stdin/stdout)
- Python standard library only unless explicitly approved
- Clear separation: input handling, business logic, state management

**Constraints**:
- No persistence mechanisms of any kind
- No third-party dependencies
- No web frameworks or GUI libraries
- Application state resets on restart (expected behavior)

**Acceptance Criteria**:
- Todo CRUD operations work entirely in memory via console
- Application state resets cleanly on restart
- No external dependencies beyond Python standard library

### Phase II: Full-Stack Web Application

**Requirements**:
- Frontend: Next.js with clear component boundaries
- Backend: FastAPI with SQLModel ORM
- Database: Neon (PostgreSQL-compatible cloud database)
- RESTful API design with OpenAPI documentation

**Constraints**:
- No file-based storage (database required)
- API MUST be documented with OpenAPI/Swagger
- Frontend and backend MUST be clearly separated
- All API contracts MUST be versioned

**Acceptance Criteria**:
- Full-stack app supports persistent todos with clean API boundaries
- API documentation is auto-generated and accurate
- Frontend consumes backend API exclusively (no direct DB access)

### Phase III: AI-Powered Todo Chatbot

**Requirements**:
- Use OpenAI ChatKit, Agents SDK, and Official MCP SDK correctly and minimally
- AI features MUST be additive, not required for core todo functionality
- All AI outputs MUST be explainable or traceable to user intent
- Core todo CRUD MUST continue to work if AI services are unavailable

**Constraints**:
- No AI features may replace or break deterministic core functionality
- AI dependencies MUST be optional at runtime
- AI prompts and responses MUST be logged for debugging

**Acceptance Criteria**:
- Users can manage todos via natural language without breaking core logic
- Core todo operations remain accessible via traditional UI/API
- AI unavailability degrades gracefully (fallback to Phase II behavior)

### Phase IV: Local Kubernetes Deployment

**Requirements**:
- All services containerized with Docker
- Kubernetes manifests or Helm charts MUST be reproducible locally via Minikube
- kubectl-ai and kagent used only for operational assistance, not hidden logic
- All Kubernetes resources MUST be declarative and version-controlled

**Constraints**:
- No cloud-managed services (local deployment only)
- No vendor-specific Kubernetes extensions
- All configuration MUST be explicit (no implicit defaults)

**Acceptance Criteria**:
- Entire system runs locally on Kubernetes with a single setup command
- All services are containerized and orchestrated via Kubernetes
- kubectl-ai provides operational insights without altering application logic

### Phase V: Advanced Cloud Deployment

**Requirements**:
- Event-driven components via Kafka where justified
- Service-to-service communication via Dapr
- Deployment on DigitalOcean DOKS MUST be documented and repeatable
- All cloud infrastructure MUST be defined as code (Terraform/Pulumi)

**Constraints**:
- No cloud-managed services introduced before Phase V
- Infrastructure as Code MUST be version-controlled
- Cloud costs MUST be documented and monitored

**Acceptance Criteria**:
- System deploys to DigitalOcean DOKS with automated scripts
- Event-driven architecture functions correctly in production
- Monitoring and observability are production-ready

## Technology Constraints

### Dependency Management

- **Phase I**: Python standard library only (no pip packages unless approved)
- **Phase II**: Next.js, FastAPI, SQLModel, Neon SDK only
- **Phase III**: Add OpenAI ChatKit, Agents SDK, Official MCP SDK only
- **Phase IV**: Add Docker, Kubernetes, kubectl-ai, kagent only
- **Phase V**: Add Kafka, Dapr, DigitalOcean SDKs, IaC tools only

**Approval Required For**:
- Any dependency not listed above for its phase
- Any version upgrade that changes API contracts
- Any replacement of a listed dependency with an alternative

### Configuration Management

All configuration MUST be:
- Explicit and documented
- Version-controlled (no manual cluster/cloud changes)
- Environment-specific (dev, staging, prod) where applicable
- Secrets managed via environment variables or secret management tools (never hardcoded)

### Backward Compatibility

Within a phase, backward compatibility MUST be maintained unless:
- Breaking change is documented in ADR
- Migration path is provided
- All stakeholders approve

Across phases, prior phase functionality MUST remain operational.

## Testing Standards

### Phase I: Manual Test Scenarios

- Document test scenarios in spec.md
- Execute manually and record results
- No automated tests required for Phase I

### Phase II: Automated Unit and Integration Tests

- Unit tests for business logic (services, models)
- Integration tests for API endpoints
- Minimum 80% code coverage for backend
- Frontend component tests for critical paths

### Phase III: AI Behavior Validation

- Deterministic test prompts for AI features
- Expected outputs documented and verified
- AI responses logged and auditable
- Core functionality tests from Phase II MUST continue passing

### Phase IV-V: Deployment Verification

- Deployment scripts MUST be tested in local environments before cloud
- Health checks for all services
- End-to-end tests in deployed environment
- Rollback procedures documented and tested

## Documentation Standards

Each phase MUST include:

1. **Architecture Overview**: High-level diagram and component descriptions
2. **Data Flow Explanation**: How data moves through the system
3. **Setup and Run Instructions**: Reproducible steps from clone to running
4. **API Documentation**: For Phase II+, auto-generated OpenAPI docs
5. **Troubleshooting Guide**: Common issues and resolutions

### Code Documentation

- Code MUST be readable and idiomatic for its language
- Comments required for non-obvious logic only
- Public APIs MUST have docstrings/JSDoc
- Naming MUST be consistent and descriptive across the project

## Governance

### Amendment Procedure

1. Propose amendment with rationale in ADR
2. Demonstrate that constitution is blocking valid progress
3. Get approval from project stakeholders
4. Update constitution with version bump (semantic versioning)
5. Update all dependent templates and documentation
6. Communicate changes to all contributors

### Versioning Policy

- **MAJOR**: Backward incompatible principle changes or phase redefinitions
- **MINOR**: New principle added or phase expanded significantly
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Review

All PRs MUST verify compliance with:
- Applicable phase constraints
- Core principles (especially III. Incremental Evolution)
- Testing standards for the current phase
- Documentation standards

Complexity violations MUST be justified in plan.md Complexity Tracking section.

### Runtime Development Guidance

For agent-specific development guidance, see `CLAUDE.md` (or equivalent agent files).
Constitution principles supersede all other practices in case of conflict.

**Version**: 1.0.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-02

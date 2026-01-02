# Research: In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2026-01-02
**Purpose**: Resolve technical unknowns and establish best practices for Phase I implementation

## Research Summary

This Phase I application is intentionally simple with no external dependencies, requiring minimal research. All decisions align with Python standard library best practices and Phase I constitution constraints.

## Decisions

### 1. Python Version: 3.13+

**Decision**: Use Python 3.13 or higher as specified in FR-011

**Rationale**:
- Latest stable Python version with modern features
- Type hints and dataclasses fully mature
- Excellent standard library support
- Cross-platform compatibility (Windows, macOS, Linux)

**Alternatives Considered**:
- Python 3.11/3.12: Would work but spec requires 3.13+
- Python 3.14+: Not yet stable/released

**Impact**: None - standard library usage is compatible across Python 3.x versions

### 2. Data Model Representation

**Decision**: Use Python dataclass for Todo model

**Rationale**:
- Part of standard library (dataclasses module)
- Automatic __init__, __repr__, __eq__ generation
- Type hints for clarity and IDE support
- Immutable option available if needed
- Clean, readable code

**Alternatives Considered**:
- Plain dict: Less type-safe, no validation
- NamedTuple: Immutable by default, less flexible
- Custom class: More boilerplate code

**Impact**: Minimal - dataclass provides best balance of simplicity and functionality

### 3. In-Memory Storage Strategy

**Decision**: Use Python dict with integer keys (todo IDs) mapping to Todo objects

**Rationale**:
- O(1) lookup by ID for get/update/delete operations
- Simple to implement and understand
- Supports auto-incrementing ID generation
- No external dependencies
- Aligns with FR-002 (unique numeric IDs) and FR-003 (in-memory only)

**Alternatives Considered**:
- List of todos: O(n) lookup, requires linear search by ID
- OrderedDict: Unnecessary - regular dict maintains insertion order in Python 3.7+
- Set: Requires todos to be hashable, doesn't support lookup by ID

**Impact**: Dict provides optimal performance for all operations

### 4. ID Generation Strategy

**Decision**: Auto-incrementing integer counter starting from 1, never reused

**Rationale**:
- Matches spec assumption: "IDs are auto-incremented integers starting from 1, never reused even after deletion"
- Simple to implement with a counter variable
- Deterministic and predictable
- No collision risk

**Alternatives Considered**:
- UUID: Overkill for in-memory app, not user-friendly
- Reuse deleted IDs: Violates spec assumption
- Hash-based: Non-deterministic, unnecessary complexity

**Impact**: Simple counter satisfies all requirements

### 5. Console Interaction Pattern

**Decision**: Menu-driven loop using input() and print()

**Rationale**:
- Standard Python console I/O (FR-013)
- User-friendly numbered menu (FR-004)
- Continuous loop until exit (spec assumption)
- Clear, intuitive navigation (SC-007)

**Alternatives Considered**:
- Command-line arguments: Less interactive, doesn't support continuous loop
- REPL-style: More complex, unnecessary for simple CRUD
- curses/rich libraries: External dependencies violate Phase I constraints

**Impact**: input()/print() loop is simplest and meets all requirements

### 6. Error Handling Strategy

**Decision**: Validate inputs and return user-friendly error messages to console

**Rationale**:
- FR-005: "System MUST validate user input and display clear error messages"
- FR-015: "System MUST reject empty or whitespace-only todo descriptions"
- SC-006: "Error messages are clear enough that users understand what went wrong"
- No exceptions should crash the app - catch and display friendly messages

**Alternatives Considered**:
- Raise exceptions: Could crash app if unhandled
- Silent failures: Violates error message requirements
- Logging to file: Adds persistence, violates Phase I constraints

**Impact**: Try/except blocks with console error messages provide best UX

### 7. Visual Distinction for Completed Todos

**Decision**: Use checkbox-style indicators: [✓] for complete, [ ] for incomplete

**Rationale**:
- FR-016: "System MUST distinguish visually between complete and incomplete todos"
- Cross-platform Unicode support in Python 3.13+
- Familiar checkbox metaphor
- Clear visual distinction

**Alternatives Considered**:
- Text labels (DONE/TODO): More verbose, less visual
- Colors (ANSI codes): May not work on all terminals
- Numbers (0/1): Less intuitive

**Impact**: Checkbox indicators provide clearest visual distinction

### 8. Project Structure

**Decision**: Four-layer separation: models, repository, operations, cli

**Rationale**:
- Constitution principle: "Clear separation: input handling, business logic, state management"
- Models: Data structures (Todo)
- Repository: State management (in-memory storage)
- Operations: Business logic (validation, CRUD operations)
- CLI: Input handling (console interface)
- Supports future evolution to Phase II (can reuse models/operations in web backend)

**Alternatives Considered**:
- Single file: Violates separation of concerns, harder to evolve
- More layers (service/controller): Over-engineering for Phase I
- Domain-driven design: Unnecessary complexity

**Impact**: Four-layer structure balances simplicity with clean architecture

### 9. UV Environment Management

**Decision**: Minimal pyproject.toml for UV compatibility (FR-012)

**Rationale**:
- UV is specified for environment management
- No dependencies to install, but UV expects pyproject.toml
- Defines Python version requirement (3.13+)
- Supports future Phase II dependency additions

**Alternatives Considered**:
- No pyproject.toml: Works but doesn't satisfy FR-012
- requirements.txt: UV prefers pyproject.toml

**Impact**: Minimal pyproject.toml satisfies UV requirement without adding complexity

### 10. Testing Strategy

**Decision**: Manual test scenarios only (Phase I standard)

**Rationale**:
- Constitution Phase I: "Manual test scenarios documented, Execute manually and record results, No automated tests required for Phase I"
- Spec acceptance scenarios provide test cases
- Recording results in test_scenarios.md

**Alternatives Considered**:
- Automated tests: Not required until Phase II
- No testing: Violates Phase I testing standards

**Impact**: Manual testing aligns with Phase I standards, automated tests deferred to Phase II

## Open Questions

None. All technical decisions resolved.

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data-model.md with Todo entity details
- Create contracts/operations.md with operation signatures
- Create quickstart.md with setup and run instructions

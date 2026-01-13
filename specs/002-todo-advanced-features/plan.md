# Implementation Plan: In-Memory Todo App — Advanced Features

**Branch**: `002-todo-advanced-features` | **Date**: 2026-01-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-todo-advanced-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extends feature 001 (basic todo CRUD) with advanced features for task organization and management:
- **Priority levels** (high/medium/low) and **tags** for categorization
- **Search** by keyword (case-insensitive substring matching)
- **Filtering** by completion status, priority, or tag with AND logic
- **Sorting** by due date, priority, or alphabetical order (stable sort)
- **Due dates and reminder times** (ISO 8601 formats)
- **Recurring tasks** (daily/weekly/monthly) with automatic next occurrence creation

All features extend the existing Todo model with optional fields while maintaining 100% backward compatibility with feature 001 operations. Implementation uses Python 3.13+ standard library only, in-memory storage, and deterministic logic without UI/CLI/notifications.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (datetime, dataclasses, typing)
**Storage**: In-memory only (dict-based repository from feature 001)
**Testing**: Manual test scenarios (Phase I standard per constitution)
**Target Platform**: Cross-platform Python (Windows/Linux/macOS)
**Project Type**: Single project (console application logic layer)
**Performance Goals**: Search <100ms for 1000 items, filter/sort <50ms for 100 items, recurring task creation <10ms
**Constraints**: No external packages, no persistence, no UI/CLI parsing, no notifications, backward compatible with feature 001
**Scale/Scope**: 5 user stories, 36 functional requirements, extends 3 existing files + adds 3 new modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase I Standards Compliance

✅ **I. Correctness First**
- All 36 functional requirements map to spec acceptance scenarios
- Implementation validates all inputs (priority, tags, dates, recurrence)
- No optimization before correctness validation

✅ **II. Deterministic Behavior**
- All operations are pure functions with predictable outputs
- Date/time parsing uses strict ISO 8601 format validation
- Search/filter/sort produce consistent results for identical inputs
- No AI components (Phase I requirement)

✅ **III. Incremental Evolution (NON-NEGOTIABLE)**
- Extends existing Todo dataclass with optional fields (backward compatible)
- All feature 001 operations continue to work unchanged
- TodoRepository singleton pattern preserved
- Existing IDs remain immutable and not reused

✅ **IV. Simplicity Before Scale**
- Uses Python standard library only (datetime for dates, no external packages)
- In-memory dict storage (no database complexity)
- Simple substring search (no full-text search engine)
- Stable sort via Python's built-in sorted() with key functions

✅ **V. Observability and Debuggability**
- Clear error messages for validation failures (dates, priority, recurrence)
- Result types (Union) for explicit error handling
- All state changes traceable through repository operations
- Manual testing with documented scenarios

### Phase I Constraint Verification

✅ **Pure in-memory storage**: No file I/O, no serialization, no databases
✅ **Console-based**: Logic layer only, no UI/CLI parsing implemented here
✅ **Python standard library only**: datetime, dataclasses, typing - no pip packages
✅ **Clear separation**: Models (Todo), Repository (TodoRepository), Operations (search/filter/sort), existing CLI unchanged

### Dependency Approval

✅ **Phase I approved dependencies**:
- `datetime` (stdlib): Date/time parsing and arithmetic for due dates and recurring tasks
- `dataclasses` (stdlib): Todo model definition (already in use from feature 001)
- `typing` (stdlib): Type hints for Optional fields and Union return types

No external packages required or requested.

### Testing Standard Compliance

✅ **Phase I: Manual Test Scenarios**
- 35 acceptance scenarios documented in spec.md
- Test scenarios will be recorded in tests/manual/
- No automated tests required for Phase I per constitution

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-advanced-features/
├── spec.md              # Feature specification (already created)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (entity schemas and validation)
├── quickstart.md        # Phase 1 output (setup and usage examples)
├── contracts/           # Phase 1 output (operation signatures)
│   └── operations.md    # Search, filter, sort, recurring task operations
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── todo.py              # [EXTEND] Add priority, tags, due_date, reminder_time, recurrence fields
│   └── filters.py           # [NEW] SearchFilter and SortCriteria dataclasses
├── repository/
│   ├── __init__.py
│   └── todo_repository.py   # [EXTEND] Update add() to accept new fields, existing methods unchanged
├── operations/
│   ├── __init__.py
│   ├── todo_operations.py   # [EXTEND] Update operations to handle new fields
│   ├── search_operations.py # [NEW] Search and filter functions
│   ├── sort_operations.py   # [NEW] Sorting functions
│   └── recurrence.py        # [NEW] Recurring task logic and date calculations
├── validation/
│   ├── __init__.py
│   ├── priority.py          # [NEW] Priority validation (high/medium/low)
│   ├── dates.py             # [NEW] ISO 8601 date/datetime validation
│   └── recurrence.py        # [NEW] Recurrence type validation
└── cli/
    ├── __init__.py
    └── console_app.py       # [EXTEND] Add menu options for advanced features (future CLI work)

tests/
└── manual/
    └── test_scenarios.md    # [EXTEND] Add 35 new acceptance scenarios for advanced features
```

**Structure Decision**: Single project structure (Option 1) is used, consistent with feature 001. This maintains Phase I simplicity with clear separation:
- **models/**: Data structures (Todo extended, new filter/sort criteria)
- **repository/**: In-memory storage with singleton pattern (extended for new fields)
- **operations/**: Business logic (CRUD extended + new search/filter/sort/recurrence)
- **validation/**: Input validation modules (new, extracted for clarity)
- **cli/**: Console interface (minimal changes, mostly for future integration)
- **tests/manual/**: Manual test scenarios per Phase I standards

All changes preserve backward compatibility with feature 001 while adding modular extensions.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: ✅ No constitution violations

All Phase I constraints are satisfied. No complexity justification needed.

---
id: 0002
title: Todo Advanced Features Plan
stage: plan
date: 2026-01-09
surface: agent
model: claude-sonnet-4-5
feature: 002-todo-advanced-features
branch: 002-todo-advanced-features
user: developer
command: /sp.plan
labels: ["planning", "architecture", "data-model", "operations", "recurring-tasks", "search-filter-sort"]
links:
  spec: specs/002-todo-advanced-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-todo-advanced-features/plan.md
  - specs/002-todo-advanced-features/research.md
  - specs/002-todo-advanced-features/data-model.md
  - specs/002-todo-advanced-features/contracts/operations.md
  - specs/002-todo-advanced-features/quickstart.md
  - CLAUDE.md (agent context updated)
tests:
  - Constitution Check: All Phase I standards passed
  - Manual test scenarios: 35 scenarios defined in spec.md
---

## Prompt

/sp.plan

(No additional arguments - plan generated from existing spec.md)

## Response snapshot

Created comprehensive implementation plan for advanced todo features extending feature 001:

**Phase 0: Research (10 technical decisions)**:
1. Date/time handling: Python datetime module with ISO 8601 parsing
2. Recurring task calculations: timedelta for daily/weekly, custom logic for monthly
3. Tag storage: Normalize to lowercase for case-insensitive filtering
4. Search: Simple substring matching with str.lower()
5. Sorting: Python's sorted() with custom key functions (stable sort)
6. Filter combination: Sequential pipeline pattern for AND logic
7. Todo extension: Add optional fields with defaults to existing dataclass
8. Recurring auto-creation: Hook into mark_complete() operation
9. Validation organization: Separate modules by domain (priority, dates, recurrence)
10. Filter/sort criteria: Dataclasses for type-safe parameters

**Phase 1: Design**:
- **Data Model**: Extended Todo with 5 new fields (priority, tags, due_date, reminder_time, recurrence), SearchFilter and SortCriteria dataclasses
- **Contracts**: 18 operations defined (2 repository, 5 filter, 4 sort, 3 recurrence, 4 validation) with signatures, inputs/outputs, error conditions
- **Quickstart**: Usage examples, patterns, validation examples, troubleshooting

**Constitution Check**: All Phase I constraints satisfied ✅
- Python stdlib only (datetime, dataclasses, typing)
- In-memory dict storage
- Deterministic behavior with strict validation
- 100% backward compatible with feature 001
- Simple implementations, no premature optimization

**Project Structure**:
- 3 files extended: todo.py, todo_repository.py, todo_operations.py
- 6 new files: filters.py, search_operations.py, sort_operations.py, recurrence.py, validation/ (3 modules)
- 4 documentation files: research.md, data-model.md, contracts/operations.md, quickstart.md

**Key Architectural Decisions**:
- Extended Todo dataclass preserves backward compatibility (new fields have defaults)
- Validation extracted to separate modules for clarity and reusability
- Search/filter/sort operations use pipeline pattern for composition
- Recurring tasks auto-create next occurrence in mark_complete() hook
- All operations use Result types (Union[Success, ErrorMessage]) for explicit error handling

## Outcome

- ✅ Impact: Completed planning for advanced todo features. Defined architecture that extends feature 001 with priority, tags, search, filter, sort, and recurring tasks while maintaining 100% backward compatibility. All operations use Python stdlib only (datetime for dates, no external packages). Ready for task generation and implementation.
- 🧪 Tests: No automated tests required for Phase I per constitution. 35 manual acceptance scenarios defined in spec.md. Constitution check passed all Phase I standards.
- 📁 Files: Created 5 planning documents (plan.md, research.md, data-model.md, contracts/operations.md, quickstart.md) totaling ~1000 lines. Updated CLAUDE.md with active technologies.
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks from plan, spec, and data model
- 🧠 Reflection: Plan successfully balances feature richness (36 FRs, 18 operations) with Phase I simplicity constraints. Research phase resolved all technical unknowns. Data model and contracts provide clear implementation guidance. Backward compatibility strategy (optional fields with defaults) is clean and testable.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow executed cleanly from spec through design artifacts
- Graders run and results (PASS/FAIL): Constitution Check: PASS (all 5 principles + Phase I constraints satisfied)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 (research) and Phase 1 (design)
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to generate implementation task breakdown. Tasks should be organized by user story (P1-P5) for incremental delivery.

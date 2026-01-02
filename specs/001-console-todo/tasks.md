---

description: "Task list for In-Memory Python Console Todo App implementation"
---

# Tasks: In-Memory Python Console Todo App

**Input**: Design documents from `/specs/001-console-todo/`
**Prerequisites**: plan.md (architecture), spec.md (user stories), data-model.md (entities), contracts/operations.md (operation contracts)

**Tests**: Manual test scenarios only (Phase I standard - no automated tests per constitution)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure (src/models/, src/repository/, src/operations/, src/cli/, tests/manual/)
- [x] T002 Create pyproject.toml with minimal UV configuration for Python 3.13+
- [x] T003 [P] Create README.md with project overview and quickstart reference
- [x] T004 [P] Create .gitignore for Python projects (exclude __pycache__, *.pyc, .venv/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Todo dataclass model in src/models/todo.py (id: int, description: str, completed: bool = False)
- [x] T006 Create TodoRepository class in src/repository/todo_repository.py with singleton pattern and empty dict initialization (_todos: dict[int, Todo], _next_id: int = 1)
- [x] T007 [P] Create description validation function in src/operations/todo_operations.py (is_valid_description: checks non-empty and non-whitespace-only)
- [x] T008 [P] Create tests/manual/test_scenarios.md with acceptance scenarios from spec.md organized by user story

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and View Todos (Priority: P1) 🎯 MVP

**Goal**: Enable developers to create todos and view them in console, demonstrating basic CRUD functionality

**Independent Test**: Run console app, add 2-3 todos, list them - delivers immediate value as working todo tracker

### Implementation for User Story 1

- [x] T009 [US1] Implement add() method in src/repository/todo_repository.py (auto-increment ID, store in dict, return Todo)
- [x] T010 [US1] Implement get_all() method in src/repository/todo_repository.py (return sorted list of all todos by ID)
- [x] T011 [US1] Implement add_todo() operation in src/operations/todo_operations.py (validate description, call repository.add(), return Todo | error string)
- [x] T012 [US1] Implement get_all_todos() operation in src/operations/todo_operations.py (call repository.get_all(), return list[Todo])
- [x] T013 [US1] Create console application skeleton in src/cli/console_app.py with main loop and menu display (options 1-7)
- [x] T014 [US1] Implement menu option 1 (Add Todo) in src/cli/console_app.py (prompt for description, call add_todo(), display result or error)
- [x] T015 [US1] Implement menu option 2 (View All Todos) in src/cli/console_app.py (call get_all_todos(), format with checkbox indicators [✓]/[ ], display list or empty message)
- [x] T016 [US1] Implement menu option 7 (Exit) in src/cli/console_app.py (graceful exit with confirmation)
- [x] T017 [US1] Add error handling for empty/whitespace descriptions in src/cli/console_app.py (display user-friendly error messages)
- [x] T018 [US1] Add if __name__ == "__main__" entry point in src/cli/console_app.py to run application

**Checkpoint**: ✅ User Story 1 fully functional and testable independently (add + view todos working)

---

## Phase 4: User Story 2 - Update Todo Descriptions (Priority: P2)

**Goal**: Enable users to update todo descriptions for correcting mistakes or refining task descriptions

**Independent Test**: Create a todo, update its description, verify change persists in view

### Implementation for User Story 2

- [x] T019 [US2] Implement update() method in src/repository/todo_repository.py (check ID exists, update description, return updated Todo | None)
- [x] T020 [US2] Implement update_todo() operation in src/operations/todo_operations.py (validate description, validate ID exists, call repository.update(), return Todo | error string)
- [x] T021 [US2] Implement menu option 3 (Update Todo) in src/cli/console_app.py (prompt for ID and new description, call update_todo(), display result or error)
- [x] T022 [US2] Add input validation for numeric ID in src/cli/console_app.py (handle non-numeric input gracefully with error message)

**Checkpoint**: ✅ User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - Mark Todos Complete/Incomplete (Priority: P3)

**Goal**: Enable status tracking by marking todos complete or incomplete

**Independent Test**: Create a todo, mark it complete, view updated status, mark it incomplete again

### Implementation for User Story 3

- [x] T023 [US3] Implement mark_complete() method in src/repository/todo_repository.py (check ID exists, set completed=True, return updated Todo | None)
- [x] T024 [US3] Implement mark_incomplete() method in src/repository/todo_repository.py (check ID exists, set completed=False, return updated Todo | None)
- [x] T025 [US3] Implement mark_complete_operation() in src/operations/todo_operations.py (validate ID exists, call repository.mark_complete(), return Todo | error string)
- [x] T026 [US3] Implement mark_incomplete_operation() in src/operations/todo_operations.py (validate ID exists, call repository.mark_incomplete(), return Todo | error string)
- [x] T027 [US3] Implement menu option 5 (Mark Todo Complete) in src/cli/console_app.py (prompt for ID, call mark_complete_operation(), display result or error)
- [x] T028 [US3] Implement menu option 6 (Mark Todo Incomplete) in src/cli/console_app.py (prompt for ID, call mark_incomplete_operation(), display result or error)
- [x] T029 [US3] Update View All Todos display in src/cli/console_app.py to show [✓] for completed and [ ] for incomplete todos

**Checkpoint**: ✅ All user stories independently functional (create, view, update, mark complete/incomplete all working)

---

## Phase 6: User Story 4 - Delete Todos (Priority: P4)

**Goal**: Enable removal of todos that are no longer needed

**Independent Test**: Create several todos, delete one by ID, verify it no longer appears in the list

### Implementation for User Story 4

- [x] T030 [US4] Implement delete() method in src/repository/todo_repository.py (check ID exists, remove from dict, return bool)
- [x] T031 [US4] Implement delete_todo() operation in src/operations/todo_operations.py (validate ID exists, call repository.delete(), return bool | error string)
- [x] T032 [US4] Implement menu option 4 (Delete Todo) in src/cli/console_app.py (prompt for ID, call delete_todo(), display success or error)
- [x] T033 [US4] Verify ID non-reuse behavior in src/repository/todo_repository.py (_next_id continues incrementing even after deletion)

**Checkpoint**: ✅ All user stories independently functional (full CRUD operations complete)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T034 [P] Add comprehensive error handling for invalid menu choices in src/cli/console_app.py (validate input is 1-7, display clear error for invalid choices)
- [x] T035 [P] Add error handling for unexpected exceptions in src/cli/console_app.py (try/except around main loop, user-friendly messages, prevent crashes)
- [x] T036 [P] Verify all error messages match spec requirements in src/operations/todo_operations.py and src/cli/console_app.py (FR-005, SC-006)
- [x] T037 Add visual formatting improvements to console output (clear screen between operations, consistent spacing, header/footer)
- [x] T038 Validate all 7 success criteria from spec.md against implemented application (SC-001 through SC-007)
- [ ] T039 [P] Run quickstart.md validation scenarios manually and record results in tests/manual/test_scenarios.md
- [x] T040 [P] Update README.md with final setup instructions, usage examples, and Phase I completion notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independently testable (requires US1 for context but not blocking)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independently testable

### Within Each User Story

- Repository methods before operations
- Operations before CLI implementation
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational phase complete, these can start together:

# Developer A: User Story 1 (Tasks T009-T018)
# Developer B: User Story 2 (Tasks T019-T022)
# Developer C: User Story 3 (Tasks T023-T029)
# Developer D: User Story 4 (Tasks T030-T033)

# Or single developer sequential:
# Complete T009-T018 → Test US1 independently → Move to T019-T022 → Test US2 independently → etc.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T009-T018)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Add 2-3 todos
   - View todos list
   - Verify error handling for empty descriptions
   - Verify checkbox indicators display correctly
5. Demo/validate MVP with stakeholders

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (MVP - create + view working!)
3. Add User Story 2 → Test independently → Demo (MVP + update)
4. Add User Story 3 → Test independently → Demo (MVP + status tracking)
5. Add User Story 4 → Test independently → Demo (Full CRUD complete)
6. Polish phase → Final validation → Release
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T008)
2. Once Foundational is done:
   - Developer A: User Story 1 (T009-T018)
   - Developer B: User Story 2 (T019-T022)
   - Developer C: User Story 3 (T023-T029)
   - Developer D: User Story 4 (T030-T033)
3. Stories complete and integrate independently
4. Team reconvenes for Polish phase (T034-T040)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- No automated tests per Phase I constitution standards - manual testing only
- All file paths are absolute from repository root
- Python 3.13+ standard library only - no external dependencies

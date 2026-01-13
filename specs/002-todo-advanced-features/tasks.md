# Tasks: In-Memory Todo App — Advanced Features

**Input**: Design documents from `/specs/002-todo-advanced-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/operations.md

**Tests**: Manual test scenarios only (Phase I standard per constitution). No automated tests required.

**Organization**: Tasks are grouped by user story (P1-P5) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create validation modules needed by all user stories

- [x] T001 Create validation package directory structure at src/validation/
- [x] T002 [P] Create src/validation/__init__.py (empty package init)
- [x] T003 [P] Implement priority validation in src/validation/priority.py (validate high/medium/low, return error messages)
- [x] T004 [P] Implement date validation in src/validation/dates.py (ISO 8601 parsing with datetime.date.fromisoformat and datetime.datetime.fromisoformat)
- [x] T005 [P] Implement recurrence validation in src/validation/recurrence.py (validate none/daily/weekly/monthly)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend core Todo model and repository to support all advanced features. MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Extend Todo dataclass in src/models/todo.py to add 5 new fields with defaults: priority="medium", tags=field(default_factory=list), due_date=None, reminder_time=None, recurrence="none"
- [x] T007 [P] Create SearchFilter dataclass in src/models/filters.py (keyword, completed, priority, tag - all Optional)
- [x] T008 [P] Create SortCriteria dataclass in src/models/filters.py (field: str, direction: str = "ascending")
- [x] T009 Extend TodoRepository.add() in src/repository/todo_repository.py to accept new optional parameters (priority, tags, due_date, reminder_time, recurrence) and validate using validation modules
- [x] T010 Add TodoRepository.add_existing() helper in src/repository/todo_repository.py for recurring task next occurrence creation (accepts pre-constructed Todo object)
- [x] T011 Extend TodoRepository.update() in src/repository/todo_repository.py to support updating new fields in kwargs

**Checkpoint**: ✅ Foundation ready - Todo model extended, validation modules created, repository supports new fields. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Task Organization with Priority and Tags (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign priority levels (high/medium/low) and tags to tasks for basic organization and categorization

**Independent Test**: Create tasks with different priority levels and various tags, verify they are stored correctly with metadata. Update priority and tags, verify changes persist.

### Implementation for User Story 1

- [x] T012 [P] [US1] Update todo_operations.add_todo() in src/operations/todo_operations.py to accept and pass through priority and tags parameters to repository
- [x] T013 [P] [US1] Update todo_operations.update_todo() in src/operations/todo_operations.py to support updating priority field with validation
- [x] T014 [P] [US1] Create helper function to normalize tags (lowercase, trim whitespace) in src/operations/todo_operations.py
- [x] T015 [US1] Add tag management operations in src/operations/todo_operations.py: add_tag(todo_id, tag), remove_tag(todo_id, tag), update_tags(todo_id, tags)
- [x] T016 [US1] Document 6 acceptance scenarios for US1 in tests/manual/test_scenarios.md with test steps and expected results

**Checkpoint**: ✅ User Story 1 complete - Tasks can be created with priority and tags, metadata can be updated, basic organization enabled

---

## Phase 4: User Story 2 - Search and Filter Tasks (Priority: P2)

**Goal**: Enable users to search tasks by keyword and filter by completion status, priority, or tag to find specific tasks in larger lists

**Independent Test**: Create 10+ tasks with various priorities, tags, and completion states. Search for keywords, apply single filters, apply multiple filters. Verify results match criteria.

**Dependencies**: Requires US1 (P1) for priority and tags to exist

### Implementation for User Story 2

- [x] T017 [P] [US2] Create operations package at src/operations/ if not exists, add __init__.py
- [x] T018 [P] [US2] Implement search_todos() in src/operations/search_operations.py (case-insensitive substring matching on description)
- [x] T019 [P] [US2] Implement filter_by_completed() in src/operations/search_operations.py (filter by completion status boolean)
- [x] T020 [P] [US2] Implement filter_by_priority() in src/operations/search_operations.py (filter by priority string)
- [x] T021 [P] [US2] Implement filter_by_tag() in src/operations/search_operations.py (case-insensitive tag matching)
- [x] T022 [US2] Implement apply_filters() in src/operations/search_operations.py (sequential pipeline applying all non-None filters with AND logic)
- [x] T023 [US2] Document 7 acceptance scenarios for US2 in tests/manual/test_scenarios.md (keyword search, single filters, combined filters, case-insensitive, empty results)

**Checkpoint**: ✅ User Story 2 complete - Users can search and filter tasks by multiple criteria with AND logic

---

## Phase 5: User Story 3 - Sort Tasks by Multiple Criteria (Priority: P3)

**Goal**: Enable users to sort task lists by due date, priority, or alphabetical order to view tasks in useful orderings

**Independent Test**: Create tasks with various due dates, priorities, and titles. Sort by each criterion in both directions. Verify correct ordering and stable sort behavior.

**Dependencies**: Requires US1 (P1) for priority field. US4 (P4) for due_date field is needed for due date sorting, but alphabetical and priority sorting are independent.

### Implementation for User Story 3

- [x] T024 [P] [US3] Implement sort_by_due_date() in src/operations/sort_operations.py (stable sort with None values at end using tuple key)
- [x] T025 [P] [US3] Implement sort_by_priority() in src/operations/sort_operations.py (map priority to numeric order high=1/medium=2/low=3, stable sort)
- [x] T026 [P] [US3] Implement sort_alphabetically() in src/operations/sort_operations.py (case-insensitive sort by description)
- [x] T027 [US3] Implement apply_sort() in src/operations/sort_operations.py (dispatch to appropriate sort function based on SortCriteria)
- [x] T028 [US3] Document 6 acceptance scenarios for US3 in tests/manual/test_scenarios.md (sort by date/priority/alpha, ascending/descending, None handling, stable sort)

**Checkpoint**: ✅ User Story 3 complete - Users can sort tasks by three criteria with configurable direction

---

## Phase 6: User Story 4 - Due Dates and Reminder Times (Priority: P4)

**Goal**: Enable users to assign optional due dates and reminder times to tasks for temporal awareness and scheduling

**Independent Test**: Create tasks with various due dates and reminder times, verify metadata is stored correctly. Update dates, verify changes persist. Test validation for invalid formats.

**Dependencies**: Independent of other user stories (extends Todo model only)

### Implementation for User Story 4

- [x] T029 [P] [US4] Update todo_operations.add_todo() in src/operations/todo_operations.py to accept due_date and reminder_time string parameters
- [x] T030 [P] [US4] Add date parsing logic in todo_operations.add_todo() to validate and convert due_date string to date object using validation/dates.py
- [x] T031 [P] [US4] Add datetime parsing logic in todo_operations.add_todo() to validate and convert reminder_time string to datetime object using validation/dates.py
- [x] T032 [US4] Update todo_operations.update_todo() in src/operations/todo_operations.py to support updating due_date and reminder_time with validation
- [x] T033 [US4] Document 7 acceptance scenarios for US4 in tests/manual/test_scenarios.md (valid dates/times, None values, independent fields, invalid formats)

**Checkpoint**: ✅ User Story 4 complete - Tasks support due dates and reminder times with ISO 8601 validation

---

## Phase 7: User Story 5 - Recurring Tasks with Auto-Creation (Priority: P5)

**Goal**: Enable recurring tasks (daily/weekly/monthly) that automatically create next occurrence when completed

**Independent Test**: Create recurring tasks with different recurrence types and due dates. Mark complete, verify new occurrence is created with correct next date, same metadata, new ID, and incomplete status.

**Dependencies**: Requires US4 (P4) for due_date field (recurring tasks need due dates to calculate next occurrence)

### Implementation for User Story 5

- [x] T034 [P] [US5] Create recurrence operations module at src/operations/recurrence.py
- [x] T035 [P] [US5] Implement calculate_next_occurrence() in src/operations/recurrence.py (daily: +1 day, weekly: +7 days, monthly: +1 month with day overflow handling using calendar.monthrange)
- [x] T036 [P] [US5] Implement calculate_next_reminder() in src/operations/recurrence.py (preserve time component from current reminder, apply to next date)
- [x] T037 [US5] Implement create_next_occurrence() in src/operations/recurrence.py (construct new Todo with next dates, same metadata, new ID, incomplete status, call repository.add_existing())
- [x] T038 [US5] Update todo_operations.mark_complete() in src/operations/todo_operations.py to call create_next_occurrence() when todo has recurrence != "none" and due_date is not None
- [x] T039 [US5] Add recurrence parameter support to todo_operations.add_todo() in src/operations/todo_operations.py with validation using validation/recurrence.py
- [x] T040 [US5] Document 9 acceptance scenarios for US5 in tests/manual/test_scenarios.md (daily/weekly/monthly creation, non-recurring behavior, metadata copying, validation, edge cases)

**Checkpoint**: ✅ User Story 5 complete - Recurring tasks automatically create next occurrence on completion

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T041 [P] Verify backward compatibility with feature 001 operations in src/operations/todo_operations.py (ensure add_todo("description") still works with defaults)
- [x] T042 [P] Add comprehensive error handling for all validation failures across all operations modules
- [x] T043 [P] Update tests/manual/test_scenarios.md to include all 35 acceptance scenarios from spec.md organized by user story
- [x] T044 Review all error messages for clarity and consistency with spec requirements (FR-005, SC-006, SC-009)
- [x] T045 [P] Add docstrings to all public functions in operations modules (search, filter, sort, recurrence)
- [x] T046 Validate performance targets: test search with 1000 items (<100ms), filter/sort with 100 items (<50ms), recurring creation (<10ms) per success criteria SC-002 through SC-005
- [x] T047 Run quickstart.md validation scenarios manually and verify all examples work as documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion - MVP target
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) + User Story 1 (Phase 3) - needs priority/tags to exist
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) + User Story 1 (Phase 3) for priority, + User Story 4 (Phase 6) for due_date sorting
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) only - independent of other stories
- **User Story 5 (Phase 7)**: Depends on Foundational (Phase 2) + User Story 4 (Phase 6) - needs due_date for recurrence
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (Phase 2) - BLOCKS EVERYTHING
    ↓
    ├─→ User Story 1 (P1) - Priority & Tags [MVP] ← Start here
    │       ↓
    │   User Story 2 (P2) - Search & Filter (needs US1)
    │       ↓
    ├─→ User Story 4 (P4) - Due Dates & Reminders (independent)
    │       ↓
    │   User Story 5 (P5) - Recurring Tasks (needs US4)
    │       ↓
    └─→ User Story 3 (P3) - Sorting (needs US1 + US4 for full functionality)
```

### Within Each User Story

- Models and filters created in Foundational phase
- Operations implemented in parallel where possible (marked [P])
- Manual test scenarios documented last in each phase
- Each story completes before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004, T005 can all run in parallel (different validation files)

**Phase 2 (Foundational)**:
- T007 and T008 can run in parallel (different dataclasses in same file)
- T006 must complete before T009-T011 (repository depends on Todo fields)

**Within Each User Story**:
- US1: T012, T013, T014 can run in parallel (different functions)
- US2: T018, T019, T020, T021 can run in parallel (different filter functions)
- US3: T024, T025, T026 can run in parallel (different sort functions)
- US4: T029, T030, T031 can run in parallel (different parsing logic)
- US5: T034, T035, T036 can run in parallel (different calculation functions)

**Phase 8 (Polish)**:
- T041, T042, T043, T045 can run in parallel (different concerns)

---

## Parallel Example: User Story 2 (Search & Filter)

```bash
# Launch all filter implementation tasks together:
Task T018: "Implement search_todos() in src/operations/search_operations.py"
Task T019: "Implement filter_by_completed() in src/operations/search_operations.py"
Task T020: "Implement filter_by_priority() in src/operations/search_operations.py"
Task T021: "Implement filter_by_tag() in src/operations/search_operations.py"

# Then T022 (apply_filters) combines them
# Finally T023 documents the scenarios
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (validation modules) → ~5 tasks
2. Complete Phase 2: Foundational (Todo extended, SearchFilter/SortCriteria created, repository updated) → ~6 tasks
3. Complete Phase 3: User Story 1 (priority & tags operations) → ~5 tasks
4. **STOP and VALIDATE**: Test User Story 1 independently using acceptance scenarios
5. **MVP READY**: Basic task organization with priority and tags working end-to-end

**MVP Scope**: 16 tasks (T001-T016)

### Incremental Delivery (Recommended)

1. **Release 1 - MVP**: Setup + Foundational + US1 (16 tasks) → Priority & tags working
2. **Release 2**: Add US2 (7 tasks) → Search and filter capabilities
3. **Release 3**: Add US4 (5 tasks) → Due dates and reminders
4. **Release 4**: Add US5 (7 tasks) → Recurring tasks
5. **Release 5**: Add US3 (5 tasks) → Sorting (depends on US4 for due_date sorting)
6. **Final Polish**: Phase 8 (7 tasks) → Cross-cutting concerns and validation

Each release adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

1. **Team completes Setup + Foundational together** (11 tasks)
2. **Once Foundational is done, parallel tracks**:
   - Developer A: User Story 1 (5 tasks) - Priority & Tags
   - Developer B: User Story 4 (5 tasks) - Due Dates (independent)
3. **After US1 + US4 complete**:
   - Developer A: User Story 2 (7 tasks) - Search & Filter (depends on US1)
   - Developer B: User Story 5 (7 tasks) - Recurring (depends on US4)
4. **After all above**:
   - Developer A or B: User Story 3 (5 tasks) - Sorting (depends on US1 + US4)
5. **Final Polish together** (7 tasks)

---

## Task Summary

**Total Tasks**: 47

**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (US1 - Priority & Tags): 5 tasks
- Phase 4 (US2 - Search & Filter): 7 tasks
- Phase 5 (US3 - Sorting): 5 tasks
- Phase 6 (US4 - Due Dates): 5 tasks
- Phase 7 (US5 - Recurring): 7 tasks
- Phase 8 (Polish): 7 tasks

**By User Story**:
- US1: 5 tasks
- US2: 7 tasks
- US3: 5 tasks
- US4: 5 tasks
- US5: 7 tasks
- Infrastructure (Setup + Foundational + Polish): 18 tasks

**Parallel Opportunities**: 22 tasks marked [P] can run in parallel within their phase

**MVP Scope**: First 16 tasks (Setup + Foundational + US1) deliver basic organization features

**Independent Testing**: Each user story has documented acceptance scenarios and can be tested independently

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label (US1-US5) maps task to specific user story for traceability
- Each user story is independently completable and testable
- Manual testing only per Phase I constitution standards
- All tasks preserve backward compatibility with feature 001
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Performance targets validated in Phase 8 (SC-002 through SC-005)

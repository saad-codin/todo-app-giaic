# Operation Contracts: In-Memory Todo App — Advanced Features

**Feature**: 002-todo-advanced-features
**Date**: 2026-01-09
**Status**: Completed

## Overview

This document defines the signatures, inputs, outputs, and error conditions for all operations in the advanced todo feature. All operations are deterministic pure functions or repository methods with explicit error handling via Result types (Union[Success, ErrorMessage]).

---

## Repository Operations (Extended)

### `TodoRepository.add(...)`

**Purpose**: Create a new todo with advanced features

**Signature**:
```python
def add(
    self,
    description: str,
    priority: str = "medium",
    tags: list[str] | None = None,
    due_date: str | None = None,
    reminder_time: str | None = None,
    recurrence: str = "none"
) -> Todo | str
```

**Inputs**:
- `description` (str, required): Task description, non-empty
- `priority` (str, optional): "high" | "medium" | "low", default "medium"
- `tags` (list[str] | None, optional): List of category strings, default None (empty list)
- `due_date` (str | None, optional): ISO 8601 date "YYYY-MM-DD", default None
- `reminder_time` (str | None, optional): ISO 8601 datetime "YYYY-MM-DD HH:MM", default None
- `recurrence` (str, optional): "none" | "daily" | "weekly" | "monthly", default "none"

**Outputs**:
- **Success**: `Todo` object with auto-assigned ID and all fields populated
- **Error**: `str` with error message describing validation failure

**Error Conditions**:
- Empty or whitespace-only description → `"Error: Description cannot be empty"`
- Invalid priority → `"Error: Invalid priority '{value}'. Valid values: high, medium, low"`
- Invalid date format → `"Error: Invalid date format. Expected YYYY-MM-DD"`
- Invalid datetime format → `"Error: Invalid datetime format. Expected YYYY-MM-DD HH:MM"`
- Invalid recurrence → `"Error: Invalid recurrence '{value}'. Valid values: none, daily, weekly, monthly"`

**Behavior**:
- Auto-assigns unique ID (never reuses deleted IDs)
- Normalizes tags to lowercase
- Validates all inputs before creating Todo
- Returns newly created Todo on success

**Examples**:
```python
# Basic todo (feature 001 style)
result = repository.add("Buy groceries")
# Returns: Todo(id=1, description="Buy groceries", completed=False, priority="medium", tags=[], ...)

# Todo with all features
result = repository.add(
    description="Team standup",
    priority="high",
    tags=["work", "meeting"],
    due_date="2026-01-15",
    reminder_time="2026-01-15 09:00",
    recurrence="daily"
)
# Returns: Todo(id=2, description="Team standup", priority="high", tags=["work", "meeting"], ...)

# Invalid priority
result = repository.add("Task", priority="urgent")
# Returns: "Error: Invalid priority 'urgent'. Valid values: high, medium, low"
```

---

### `TodoRepository.add_existing(todo: Todo)`

**Purpose**: Internal helper to add pre-constructed Todo (used for recurring task next occurrence)

**Signature**:
```python
def add_existing(self, todo: Todo) -> None
```

**Inputs**:
- `todo` (Todo, required): Pre-constructed Todo object with assigned ID

**Outputs**:
- None (no return value, modifies internal state)

**Error Conditions**:
- None (assumes valid Todo object, internal use only)

**Behavior**:
- Stores todo in `_todos` dict with its existing ID
- Increments `_next_id` for future auto-assignment
- Used internally by recurring task logic

**Examples**:
```python
# Internal use only (not called by external code)
next_todo = Todo(id=8, description="Water plants", completed=False, ...)
repository.add_existing(next_todo)
```

---

## Search Operations

### `search_todos(...)`

**Purpose**: Search todos by keyword with case-insensitive substring matching

**Signature**:
```python
def search_todos(todos: list[Todo], keyword: str) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to search
- `keyword` (str, required): Search term (case-insensitive)

**Outputs**:
- `list[Todo]`: All todos containing keyword in description (case-insensitive), or empty list if no matches

**Error Conditions**:
- None (empty keyword returns all todos, empty list returns empty list)

**Behavior**:
- Case-insensitive substring matching: `keyword.lower() in description.lower()`
- Returns original todo objects (not copies)
- Preserves order from input list
- Empty keyword returns all todos unchanged

**Performance**: O(n) where n = number of todos

**Examples**:
```python
todos = [
    Todo(id=1, description="Team meeting", ...),
    Todo(id=2, description="Buy groceries", ...),
    Todo(id=3, description="Schedule team lunch", ...)
]

# Search for "team" (case-insensitive)
result = search_todos(todos, "team")
# Returns: [Todo(id=1), Todo(id=3)]

# Search with case variations
result = search_todos(todos, "MEETING")
# Returns: [Todo(id=1)]

# No matches
result = search_todos(todos, "doctor")
# Returns: []
```

---

## Filter Operations

### `filter_by_completed(...)`

**Purpose**: Filter todos by completion status

**Signature**:
```python
def filter_by_completed(todos: list[Todo], completed: bool) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to filter
- `completed` (bool, required): True for completed, False for incomplete

**Outputs**:
- `list[Todo]`: All todos matching completion status

**Error Conditions**:
- None

**Examples**:
```python
# Get only incomplete todos
result = filter_by_completed(todos, False)

# Get only completed todos
result = filter_by_completed(todos, True)
```

---

### `filter_by_priority(...)`

**Purpose**: Filter todos by priority level

**Signature**:
```python
def filter_by_priority(todos: list[Todo], priority: str) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to filter
- `priority` (str, required): "high" | "medium" | "low"

**Outputs**:
- `list[Todo]`: All todos matching priority

**Error Conditions**:
- Invalid priority → returns empty list (validation should occur before calling)

**Examples**:
```python
# Get high-priority todos
result = filter_by_priority(todos, "high")

# Get medium-priority todos
result = filter_by_priority(todos, "medium")
```

---

### `filter_by_tag(...)`

**Purpose**: Filter todos by tag (case-insensitive)

**Signature**:
```python
def filter_by_tag(todos: list[Todo], tag: str) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to filter
- `tag` (str, required): Tag to match (case-insensitive)

**Outputs**:
- `list[Todo]`: All todos containing the specified tag

**Error Conditions**:
- None (empty string matches nothing, returns empty list)

**Behavior**:
- Case-insensitive matching: normalizes tag to lowercase
- Checks if normalized tag is in todo's tags list

**Examples**:
```python
# Find all "work" tasks
result = filter_by_tag(todos, "work")

# Case-insensitive
result = filter_by_tag(todos, "WORK")  # Same result
```

---

### `apply_filters(...)`

**Purpose**: Apply multiple filters with AND logic

**Signature**:
```python
def apply_filters(todos: list[Todo], filters: SearchFilter) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to filter
- `filters` (SearchFilter, required): Filter criteria (fields with None are ignored)

**Outputs**:
- `list[Todo]`: Todos matching ALL non-None filter criteria

**Error Conditions**:
- None (empty filters returns all todos)

**Behavior**:
- Applies filters sequentially (pipeline pattern)
- Only applies non-None filter fields
- Empty result if no todos match ALL criteria

**Performance**: O(n * m) where n = number of todos, m = number of active filters

**Examples**:
```python
# Find incomplete high-priority work tasks
filters = SearchFilter(
    completed=False,
    priority="high",
    tag="work"
)
result = apply_filters(todos, filters)

# Search and filter
filters = SearchFilter(keyword="meeting", completed=False)
result = apply_filters(todos, filters)
```

---

## Sort Operations

### `sort_by_due_date(...)`

**Purpose**: Sort todos by due date (None values go to end)

**Signature**:
```python
def sort_by_due_date(todos: list[Todo], descending: bool = False) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to sort
- `descending` (bool, optional): False for ascending (earliest first), True for descending (latest first), default False

**Outputs**:
- `list[Todo]`: Sorted list (stable sort)

**Error Conditions**:
- None

**Behavior**:
- Stable sort (preserves relative order for equal elements)
- Todos without due dates (`due_date is None`) appear at the end regardless of direction
- Uses tuple key: `(due_date is None, due_date)`

**Performance**: O(n log n) via Timsort

**Examples**:
```python
# Sort by due date, earliest first
result = sort_by_due_date(todos, descending=False)
# Order: 2026-01-15, 2026-01-20, 2026-02-01, None, None

# Sort by due date, latest first
result = sort_by_due_date(todos, descending=True)
# Order: 2026-02-01, 2026-01-20, 2026-01-15, None, None
```

---

### `sort_by_priority(...)`

**Purpose**: Sort todos by priority (high → medium → low by default)

**Signature**:
```python
def sort_by_priority(todos: list[Todo], descending: bool = True) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to sort
- `descending` (bool, optional): True for high-first (default), False for low-first

**Outputs**:
- `list[Todo]`: Sorted list (stable sort)

**Error Conditions**:
- None

**Behavior**:
- Maps priority to numeric order: {"high": 1, "medium": 2, "low": 3}
- Default descending=True produces high → medium → low order
- Stable sort preserves original order for equal priorities

**Performance**: O(n log n) via Timsort

**Examples**:
```python
# High to low (default)
result = sort_by_priority(todos, descending=True)
# Order: [high tasks], [medium tasks], [low tasks]

# Low to high
result = sort_by_priority(todos, descending=False)
# Order: [low tasks], [medium tasks], [high tasks]
```

---

### `sort_alphabetically(...)`

**Purpose**: Sort todos alphabetically by description (case-insensitive)

**Signature**:
```python
def sort_alphabetically(todos: list[Todo], descending: bool = False) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to sort
- `descending` (bool, optional): False for A-Z (default), True for Z-A

**Outputs**:
- `list[Todo]`: Sorted list (stable sort)

**Error Conditions**:
- None

**Behavior**:
- Case-insensitive: uses `description.lower()` as key
- Stable sort

**Performance**: O(n log n) via Timsort

**Examples**:
```python
# A-Z
result = sort_alphabetically(todos, descending=False)

# Z-A
result = sort_alphabetically(todos, descending=True)
```

---

### `apply_sort(...)`

**Purpose**: Apply sort criteria to todo list

**Signature**:
```python
def apply_sort(todos: list[Todo], criteria: SortCriteria) -> list[Todo]
```

**Inputs**:
- `todos` (list[Todo], required): List of todos to sort
- `criteria` (SortCriteria, required): Sort field and direction

**Outputs**:
- `list[Todo]`: Sorted list

**Error Conditions**:
- Invalid field name → raises ValueError (validation should occur before calling)

**Behavior**:
- Dispatches to appropriate sort function based on `criteria.field`
- Converts "ascending"/"descending" to boolean for underlying functions

**Examples**:
```python
# Sort by due date ascending
criteria = SortCriteria(field="due_date", direction="ascending")
result = apply_sort(todos, criteria)

# Sort by priority descending
criteria = SortCriteria(field="priority", direction="descending")
result = apply_sort(todos, criteria)
```

---

## Recurrence Operations

### `calculate_next_occurrence(...)`

**Purpose**: Calculate next occurrence date for recurring task

**Signature**:
```python
def calculate_next_occurrence(current_date: date, recurrence: str) -> date
```

**Inputs**:
- `current_date` (date, required): Current due date
- `recurrence` (str, required): "daily" | "weekly" | "monthly"

**Outputs**:
- `date`: Next occurrence date

**Error Conditions**:
- Invalid recurrence type → raises ValueError
- "none" recurrence → should not call this function

**Behavior**:
- Daily: `current_date + timedelta(days=1)`
- Weekly: `current_date + timedelta(days=7)`
- Monthly: Add 1 month, handle day overflow (Jan 31 → Feb 28/29)

**Performance**: O(1)

**Examples**:
```python
# Daily recurrence
next_date = calculate_next_occurrence(date(2026, 1, 10), "daily")
# Returns: date(2026, 1, 11)

# Weekly recurrence
next_date = calculate_next_occurrence(date(2026, 1, 10), "weekly")
# Returns: date(2026, 1, 17)

# Monthly recurrence
next_date = calculate_next_occurrence(date(2026, 1, 10), "monthly")
# Returns: date(2026, 2, 10)

# Monthly with day overflow
next_date = calculate_next_occurrence(date(2026, 1, 31), "monthly")
# Returns: date(2026, 2, 28) or date(2026, 2, 29) if leap year
```

---

### `calculate_next_reminder(...)`

**Purpose**: Calculate next reminder time based on next occurrence date

**Signature**:
```python
def calculate_next_reminder(current_reminder: datetime, next_date: date) -> datetime
```

**Inputs**:
- `current_reminder` (datetime, required): Current reminder datetime
- `next_date` (date, required): Next occurrence date

**Outputs**:
- `datetime`: Next reminder datetime (next_date + time from current_reminder)

**Error Conditions**:
- None (assumes valid inputs)

**Behavior**:
- Preserves time component from current_reminder
- Applies time to next_date

**Examples**:
```python
# Original reminder: 2026-01-10 09:00
# Next occurrence date: 2026-01-17
current_reminder = datetime(2026, 1, 10, 9, 0)
next_date = date(2026, 1, 17)
next_reminder = calculate_next_reminder(current_reminder, next_date)
# Returns: datetime(2026, 1, 17, 9, 0)
```

---

### `create_next_occurrence(...)`

**Purpose**: Create next occurrence of recurring task (internal operation called by mark_complete)

**Signature**:
```python
def create_next_occurrence(todo: Todo, repository: TodoRepository) -> Todo | None
```

**Inputs**:
- `todo` (Todo, required): Completed recurring task
- `repository` (TodoRepository, required): Repository to add next occurrence

**Outputs**:
- `Todo`: Newly created next occurrence, or None if not recurring or no due date

**Error Conditions**:
- None (returns None if conditions not met)

**Behavior**:
- Only creates next occurrence if `todo.recurrence != "none"` AND `todo.due_date is not None`
- Calculates next due date and reminder time
- Creates new Todo with new ID, same metadata, incomplete status
- Adds to repository via `add_existing()`

**Examples**:
```python
# Recurring task
todo = Todo(id=5, description="Water plants", due_date=date(2026, 1, 10), recurrence="weekly", ...)
next_todo = create_next_occurrence(todo, repository)
# Returns: Todo(id=6, description="Water plants", due_date=date(2026, 1, 17), completed=False, ...)

# Non-recurring task
todo = Todo(id=7, description="One-time task", recurrence="none", ...)
next_todo = create_next_occurrence(todo, repository)
# Returns: None
```

---

## Validation Operations

### `validate_priority(...)`

**Purpose**: Validate priority value

**Signature**:
```python
def validate_priority(priority: str) -> str | None
```

**Inputs**:
- `priority` (str, required): Priority value to validate

**Outputs**:
- `None` if valid, `str` error message if invalid

**Error Conditions**:
- Priority not in {"high", "medium", "low"}

**Examples**:
```python
validate_priority("high")  # Returns: None (valid)
validate_priority("urgent")  # Returns: "Error: Invalid priority 'urgent'. Valid values: high, medium, low"
```

---

### `validate_date(...)`

**Purpose**: Validate and parse ISO 8601 date string

**Signature**:
```python
def validate_date(date_string: str) -> date | str
```

**Inputs**:
- `date_string` (str, required): Date in YYYY-MM-DD format

**Outputs**:
- `date` object if valid, `str` error message if invalid

**Error Conditions**:
- Invalid format or invalid date

**Examples**:
```python
validate_date("2026-01-15")  # Returns: date(2026, 1, 15)
validate_date("tomorrow")  # Returns: "Error: Invalid date format. Expected YYYY-MM-DD"
```

---

### `validate_datetime(...)`

**Purpose**: Validate and parse ISO 8601 datetime string

**Signature**:
```python
def validate_datetime(datetime_string: str) -> datetime | str
```

**Inputs**:
- `datetime_string` (str, required): Datetime in YYYY-MM-DD HH:MM format

**Outputs**:
- `datetime` object if valid, `str` error message if invalid

**Error Conditions**:
- Invalid format or invalid datetime

**Examples**:
```python
validate_datetime("2026-01-15 09:00")  # Returns: datetime(2026, 1, 15, 9, 0)
validate_datetime("9am")  # Returns: "Error: Invalid datetime format. Expected YYYY-MM-DD HH:MM"
```

---

### `validate_recurrence(...)`

**Purpose**: Validate recurrence type

**Signature**:
```python
def validate_recurrence(recurrence: str) -> str | None
```

**Inputs**:
- `recurrence` (str, required): Recurrence value to validate

**Outputs**:
- `None` if valid, `str` error message if invalid

**Error Conditions**:
- Recurrence not in {"none", "daily", "weekly", "monthly"}

**Examples**:
```python
validate_recurrence("weekly")  # Returns: None (valid)
validate_recurrence("yearly")  # Returns: "Error: Invalid recurrence 'yearly'. Valid values: none, daily, weekly, monthly"
```

---

## Combined Workflow: Search + Filter + Sort

**Purpose**: Demonstrate chaining operations (common use case per SC-007)

**Example**:
```python
# Find incomplete high-priority work tasks sorted by due date

# Step 1: Apply filters
filters = SearchFilter(
    completed=False,
    priority="high",
    tag="work"
)
filtered_todos = apply_filters(all_todos, filters)

# Step 2: Apply sort
sort_criteria = SortCriteria(field="due_date", direction="ascending")
result = apply_sort(filtered_todos, sort_criteria)

# Result: Incomplete high-priority work tasks ordered by due date (soonest first)
```

---

## Summary

All operation contracts defined:
- ✅ 2 repository operations extended/added
- ✅ 5 filter operations (search + 3 specific filters + combined filter)
- ✅ 4 sort operations (3 specific sorts + combined sort)
- ✅ 3 recurrence operations (calculate dates, create next occurrence)
- ✅ 4 validation operations (priority, date, datetime, recurrence)
- ✅ All signatures specify input/output types using Union types for error handling
- ✅ All error conditions documented with example error messages
- ✅ Performance characteristics noted where relevant

**Ready for Phase 1 (continued)**: Quickstart documentation.

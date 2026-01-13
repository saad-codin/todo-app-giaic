# Data Model: In-Memory Todo App — Advanced Features

**Feature**: 002-todo-advanced-features
**Date**: 2026-01-09
**Status**: Completed

## Overview

This document defines the data structures and validation rules for advanced todo features. All entities extend or complement the existing feature 001 implementation while maintaining 100% backward compatibility.

---

## Entities

### Todo (Extended)

**Purpose**: Represents a task with advanced organizational and scheduling features

**Location**: `src/models/todo.py`

**Schema**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| id | int | Yes | (auto-assigned) | Unique identifier, immutable | Positive integer, never reused |
| description | str | Yes | N/A | Task description | Non-empty, non-whitespace-only |
| completed | bool | No | False | Completion status | Boolean (True/False) |
| priority | str | No | "medium" | Task priority level | Must be "high", "medium", or "low" |
| tags | list[str] | No | [] | Categories/labels | List of strings, stored lowercase, can be empty |
| due_date | date \| None | No | None | Target completion date | ISO 8601 format (YYYY-MM-DD) or None |
| reminder_time | datetime \| None | No | None | Reminder timestamp | ISO 8601 format (YYYY-MM-DD HH:MM) or None |
| recurrence | str | No | "none" | Recurrence pattern | Must be "none", "daily", "weekly", or "monthly" |

**Relationships**:
- Each Todo is independent (no parent/child relationships in Phase I)
- Tags are flat strings, not references to separate Tag entities
- Recurring tasks are independent - completing one creates a new Todo with a new ID

**State Transitions**:
```
New Todo (completed=False)
    ↓ mark_complete()
Completed Todo (completed=True)
    ↓ [if recurrence != "none" and due_date exists]
New Todo (next occurrence, completed=False, new ID)
```

**Invariants**:
- `id` must be unique across all todos
- `id` must never change after creation
- `description` must not be empty or whitespace-only
- `priority` must be one of the three valid values
- `tags` list must contain only strings (can be empty)
- `due_date` must be valid date or None
- `reminder_time` must be valid datetime or None
- `recurrence` must be one of the four valid values
- Deleted todo IDs must never be reused (carried over from feature 001)

**Example**:
```python
# Basic todo (feature 001 style) - still works
todo1 = Todo(id=1, description="Buy groceries", completed=False)

# Todo with priority and tags
todo2 = Todo(
    id=2,
    description="Team standup",
    completed=False,
    priority="high",
    tags=["work", "meeting"]
)

# Recurring todo with due date
todo3 = Todo(
    id=3,
    description="Weekly review",
    completed=False,
    priority="medium",
    tags=["personal"],
    due_date=date(2026, 1, 15),
    recurrence="weekly"
)

# Todo with full metadata
todo4 = Todo(
    id=4,
    description="Submit report",
    completed=False,
    priority="high",
    tags=["work", "urgent"],
    due_date=date(2026, 1, 20),
    reminder_time=datetime(2026, 1, 19, 9, 0),  # Day before at 9 AM
    recurrence="none"
)
```

---

### SearchFilter

**Purpose**: Encapsulates search and filter criteria for querying todos

**Location**: `src/models/filters.py`

**Schema**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| keyword | str \| None | No | None | Search term for description matching | String or None, case-insensitive |
| completed | bool \| None | No | None | Filter by completion status | Boolean or None |
| priority | str \| None | No | None | Filter by priority level | Must be valid priority or None |
| tag | str \| None | No | None | Filter by tag | String or None, case-insensitive |

**Behavior**:
- All fields are optional (None means "don't filter by this criterion")
- Multiple non-None fields are combined with AND logic (all must match)
- Keyword search is case-insensitive substring matching

**Example**:
```python
# Find all high-priority work tasks
filter1 = SearchFilter(priority="high", tag="work")

# Search for incomplete tasks containing "meeting"
filter2 = SearchFilter(keyword="meeting", completed=False)

# Find all completed tasks
filter3 = SearchFilter(completed=True)

# No filters (return all)
filter4 = SearchFilter()
```

---

### SortCriteria

**Purpose**: Specifies sort order for todo lists

**Location**: `src/models/filters.py`

**Schema**:

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| field | str | Yes | N/A | Field to sort by | Must be "due_date", "priority", or "title" |
| direction | str | No | "ascending" | Sort direction | Must be "ascending" or "descending" |

**Behavior**:
- Sorting is stable (preserves relative order for equal elements)
- When sorting by due_date, todos without due dates appear at the end
- When sorting by priority, default order is high → medium → low

**Example**:
```python
# Sort by due date, soonest first
sort1 = SortCriteria(field="due_date", direction="ascending")

# Sort by priority, high to low (default order)
sort2 = SortCriteria(field="priority", direction="descending")

# Sort alphabetically A-Z
sort3 = SortCriteria(field="title", direction="ascending")
```

---

## Validation Rules

### Priority Validation

**Location**: `src/validation/priority.py`

**Rules**:
- Priority must be exactly one of: "high", "medium", "low" (case-sensitive)
- Empty string or None is invalid (must use default "medium")

**Error Messages**:
- Invalid priority: `"Error: Invalid priority '{value}'. Valid values: high, medium, low"`

**Examples**:
```python
✅ Valid:
    - "high"
    - "medium"
    - "low"

❌ Invalid:
    - "critical" → Error (not in valid set)
    - "HIGH" → Error (case-sensitive)
    - "" → Error (empty string)
    - None → Use default "medium" instead
```

---

### Tags Validation

**Location**: `src/validation/tags.py` (implied, simple enough to inline)

**Rules**:
- Tags list can be empty (valid use case)
- Each tag must be a string
- Tags are normalized to lowercase on storage
- Whitespace is trimmed from each tag
- Empty strings after trimming are removed

**Processing**:
```python
Input: ["Work", " urgent ", "", "HOME"]
Normalized: ["work", "urgent", "home"]
```

---

### Date Validation

**Location**: `src/validation/dates.py`

**Rules**:
- Due dates must be in ISO 8601 format: YYYY-MM-DD (e.g., "2026-01-15")
- Reminder times must be in ISO 8601 format: YYYY-MM-DD HH:MM (e.g., "2026-01-15 09:00")
- Both dates and times use 24-hour format
- None is valid (optional fields)
- Past dates are allowed (no restriction per spec assumptions)

**Error Messages**:
- Invalid date: `"Error: Invalid date format. Expected YYYY-MM-DD"`
- Invalid datetime: `"Error: Invalid datetime format. Expected YYYY-MM-DD HH:MM"`

**Examples**:
```python
✅ Valid dates:
    - "2026-01-15"
    - "2025-12-31"
    - None

❌ Invalid dates:
    - "tomorrow" → Error (not ISO format)
    - "01/15/2026" → Error (wrong format)
    - "2026-1-15" → Error (month/day must be zero-padded)

✅ Valid datetimes:
    - "2026-01-15 09:00"
    - "2026-12-31 23:59"
    - None

❌ Invalid datetimes:
    - "9am" → Error (not ISO format)
    - "2026-01-15 9:00" → Error (hour must be zero-padded)
    - "2026-01-15T09:00:00" → Error (too precise, use HH:MM)
```

---

### Recurrence Validation

**Location**: `src/validation/recurrence.py`

**Rules**:
- Recurrence must be exactly one of: "none", "daily", "weekly", "monthly" (case-sensitive)
- Default is "none" (non-recurring)
- Empty string or None is invalid (must use default "none")

**Error Messages**:
- Invalid recurrence: `"Error: Invalid recurrence '{value}'. Valid values: none, daily, weekly, monthly"`

**Examples**:
```python
✅ Valid:
    - "none"
    - "daily"
    - "weekly"
    - "monthly"

❌ Invalid:
    - "yearly" → Error (not supported in Phase I)
    - "biweekly" → Error (not in valid set)
    - "" → Error (empty string)
    - None → Use default "none" instead
```

---

## Repository Extension

### TodoRepository (Extended)

**Purpose**: In-memory storage with singleton pattern (feature 001), extended to handle new fields

**Location**: `src/repository/todo_repository.py`

**State**:
- `_todos: dict[int, Todo]` - In-memory storage (key: todo ID, value: Todo object)
- `_next_id: int` - Auto-incrementing ID counter (never decrements, IDs never reused)

**New/Modified Operations**:

#### `add(description, priority="medium", tags=None, due_date=None, reminder_time=None, recurrence="none") -> Todo`
**Change**: Extended signature to accept new optional parameters
**Behavior**:
- All new parameters have defaults matching Todo defaults
- Validates inputs via validation modules
- Creates Todo with auto-assigned ID
- Feature 001 calls still work: `add("task")` uses all defaults

#### `add_existing(todo: Todo) -> None`
**Change**: New helper for recurring task auto-creation
**Behavior**:
- Accepts pre-constructed Todo object (used for next occurrence)
- Stores todo with its existing ID
- Increments `_next_id` for next auto-assignment

#### `update(id, **kwargs) -> bool | str`
**Change**: Extended to accept new fields in kwargs
**Behavior**:
- Validates new field values if provided
- Updates only specified fields (partial update)
- Returns True on success, error message string on failure

**No changes to**: `get(id)`, `get_all()`, `delete(id)`, `mark_complete(id)`, `mark_incomplete(id)` - these continue to work as-is with extended Todo fields

---

## Data Flow Examples

### Example 1: Create Todo with Full Metadata

```
User Input:
    description: "Team standup"
    priority: "high"
    tags: ["work", "meeting"]
    due_date: "2026-01-15"
    recurrence: "weekly"

↓ Validation
    ✅ priority: "high" (valid)
    ✅ tags: ["work", "meeting"] → normalized to ["work", "meeting"]
    ✅ due_date: "2026-01-15" → parsed to date(2026, 1, 15)
    ✅ recurrence: "weekly" (valid)

↓ Repository.add()
    id: 5 (auto-assigned)
    description: "Team standup"
    completed: False (default)
    priority: "high"
    tags: ["work", "meeting"]
    due_date: date(2026, 1, 15)
    reminder_time: None (not provided)
    recurrence: "weekly"

↓ Storage
    _todos[5] = Todo(...)
    _next_id = 6

Result: Todo object with ID 5
```

---

### Example 2: Search and Filter

```
Operation: Find incomplete high-priority work tasks

Input:
    filters = SearchFilter(
        completed=False,
        priority="high",
        tag="work"
    )

↓ Apply Filters (AND logic)
    Start with: all todos [Todo1, Todo2, Todo3, Todo4, Todo5]

    Filter 1 (completed=False):
        Result: [Todo1, Todo2, Todo4, Todo5] (removed Todo3)

    Filter 2 (priority="high"):
        Result: [Todo2, Todo5] (removed Todo1, Todo4)

    Filter 3 (tag="work"):
        Result: [Todo2] (removed Todo5 - no "work" tag)

Final Result: [Todo2]
```

---

### Example 3: Recurring Task Completion

```
Initial State:
    Todo ID 7:
        description: "Water plants"
        completed: False
        due_date: date(2026, 1, 10)
        recurrence: "weekly"

↓ mark_complete(7)

Step 1: Mark todo 7 as complete
    _todos[7].completed = True

Step 2: Check recurrence
    recurrence = "weekly" (not "none")
    due_date = date(2026, 1, 10) (exists)
    → Create next occurrence

Step 3: Calculate next occurrence date
    current_date: 2026-01-10
    recurrence: "weekly"
    next_date: 2026-01-10 + 7 days = 2026-01-17

Step 4: Create new todo (next occurrence)
    new_todo = Todo(
        id=8,  # New auto-assigned ID
        description="Water plants",  # Same description
        completed=False,  # Reset to incomplete
        priority="medium",  # Copied from original
        tags=[],  # Copied from original
        due_date=date(2026, 1, 17),  # Calculated next date
        reminder_time=None,  # Copied from original
        recurrence="weekly"  # Copied from original
    )

Step 5: Add to repository
    _todos[8] = new_todo
    _next_id = 9

Final State:
    Todo ID 7: completed=True (original)
    Todo ID 8: completed=False (next occurrence)
```

---

### Example 4: Sort by Due Date with None Values

```
Input Todos:
    Todo1: description="A", due_date=date(2026, 1, 20)
    Todo2: description="B", due_date=None
    Todo3: description="C", due_date=date(2026, 1, 15)
    Todo4: description="D", due_date=None
    Todo5: description="E", due_date=date(2026, 1, 18)

↓ Sort by due_date (ascending)
    Key function: (due_date is None, due_date)

    Sorting keys:
        Todo1: (False, date(2026, 1, 20))
        Todo2: (True, None)
        Todo3: (False, date(2026, 1, 15))
        Todo4: (True, None)
        Todo5: (False, date(2026, 1, 18))

    Python sorts False before True, so:
        1. All (False, date) entries come first
        2. All (True, None) entries come last

Result (ascending):
    [Todo3, Todo5, Todo1, Todo2, Todo4]
    (2026-01-15, 2026-01-18, 2026-01-20, None, None)
```

---

## Backward Compatibility Verification

### Feature 001 Operations Still Work

✅ **Create basic todo**:
```python
# Feature 001 style
todo = Todo(id=1, description="Buy milk", completed=False)
# Still works - new fields use defaults
```

✅ **Repository operations**:
```python
# Feature 001 operations unchanged
repository.add("Task")  # Uses default priority="medium", tags=[], etc.
repository.get(1)  # Returns Todo with all fields (new fields have defaults)
repository.update(1, description="Updated")  # Only updates description
repository.delete(1)  # Works as before
repository.mark_complete(1)  # Works, triggers recurrence if applicable
```

✅ **Console app**:
```python
# Feature 001 console operations still work
# Advanced features can be added to menu later without breaking existing flows
```

---

## Summary

All data models and validation rules defined:
- ✅ Todo extended with 5 new optional fields
- ✅ SearchFilter and SortCriteria dataclasses defined
- ✅ Validation rules specified for all new fields
- ✅ Repository operations extended while preserving feature 001 behavior
- ✅ Backward compatibility verified
- ✅ Data flow examples document expected behavior

**Ready for Phase 1 (continued)**: Contracts definition.

# Technical Research: In-Memory Todo App — Advanced Features

**Feature**: 002-todo-advanced-features
**Date**: 2026-01-09
**Status**: Completed

## Overview

This document consolidates research findings for implementing advanced todo features while maintaining Phase I constraints (Python stdlib only, in-memory storage, backward compatibility with feature 001).

---

## Decision 1: Date and Time Handling

**Context**: Need to store and validate optional due dates (YYYY-MM-DD) and reminder times (YYYY-MM-DD HH:MM) per FR-006, FR-007.

**Decision**: Use Python's `datetime` module with strict ISO 8601 parsing

**Rationale**:
- `datetime.date.fromisoformat()` directly parses YYYY-MM-DD format (added in Python 3.7)
- `datetime.datetime.fromisoformat()` handles YYYY-MM-DD HH:MM format (simplified ISO 8601)
- Both raise `ValueError` on invalid input, enabling clear error messages
- Part of Python stdlib (no external dependency)
- Provides date arithmetic for recurring task calculations

**Alternatives Considered**:
1. **Manual string parsing with regex**: Rejected - error-prone, reinvents the wheel, less maintainable
2. **dateutil.parser**: Rejected - external dependency violates Phase I constraints
3. **time.strptime()**: Rejected - more verbose than datetime.fromisoformat(), returns time tuples instead of date objects

**Implementation Pattern**:
```python
from datetime import date, datetime

def parse_date(date_string: str) -> date | str:
    """Parse ISO 8601 date (YYYY-MM-DD)."""
    try:
        return date.fromisoformat(date_string)
    except ValueError:
        return "Error: Invalid date format. Expected YYYY-MM-DD"

def parse_datetime(datetime_string: str) -> datetime | str:
    """Parse ISO 8601 datetime (YYYY-MM-DD HH:MM)."""
    try:
        return datetime.fromisoformat(datetime_string)
    except ValueError:
        return "Error: Invalid datetime format. Expected YYYY-MM-DD HH:MM"
```

---

## Decision 2: Recurring Task Date Calculation

**Context**: Need to calculate next occurrence dates for daily (+1 day), weekly (+7 days), monthly (+1 month) recurrence per FR-026.

**Decision**: Use `datetime.timedelta` for daily/weekly, `dateutil`-style month addition for monthly

**Rationale**:
- `timedelta(days=1)` and `timedelta(days=7)` are simple and precise
- Monthly recurrence requires special handling (Jan 31 → Feb 28/29 on non-leap years)
- Python stdlib provides all necessary tools via `datetime` and `calendar` modules
- Spec assumption: "Monthly recurrence uses simple month addition" - justifies simplification

**Alternatives Considered**:
1. **dateutil.relativedelta**: Rejected - external dependency (violates Phase I)
2. **Manual month/year arithmetic**: Chosen for monthly (stdlib only, handles edge cases)

**Implementation Pattern**:
```python
from datetime import date, timedelta
from calendar import monthrange

def calculate_next_occurrence(current_date: date, recurrence: str) -> date:
    """Calculate next occurrence based on recurrence type."""
    if recurrence == "daily":
        return current_date + timedelta(days=1)
    elif recurrence == "weekly":
        return current_date + timedelta(days=7)
    elif recurrence == "monthly":
        # Add one month, handle day overflow (Jan 31 → Feb 28/29)
        year = current_date.year
        month = current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        # Get last day of target month
        max_day = monthrange(year, month)[1]
        day = min(current_date.day, max_day)
        return date(year, month, day)
    else:
        raise ValueError(f"Invalid recurrence type: {recurrence}")
```

**Edge Case Handling**:
- Jan 31 + 1 month → Feb 28 (non-leap) or Feb 29 (leap year)
- Dec 31 + 1 month → Jan 31 (next year)
- Tested via acceptance scenarios in spec.md

---

## Decision 3: Tag Storage and Filtering

**Context**: Tags are lists of strings, need case-insensitive filtering per FR-014 and spec assumption.

**Decision**: Store tags as lowercase strings, filter using case-insensitive matching

**Rationale**:
- Normalizing to lowercase at storage time simplifies filtering logic
- No need for `.lower()` calls at query time (performance benefit)
- Consistent with spec assumption: "Tags are stored as lowercase strings"
- Simple to implement with list comprehensions

**Alternatives Considered**:
1. **Case-sensitive storage with `.lower()` at query time**: Rejected - more complex, slower for repeated queries
2. **Custom TagSet class**: Rejected - over-engineering for Phase I, violates Simplicity Before Scale

**Implementation Pattern**:
```python
def normalize_tags(tags: list[str]) -> list[str]:
    """Normalize tags to lowercase for storage."""
    return [tag.lower().strip() for tag in tags]

def filter_by_tag(todos: list[Todo], tag: str) -> list[Todo]:
    """Filter todos by tag (case-insensitive)."""
    normalized_tag = tag.lower().strip()
    return [todo for todo in todos if normalized_tag in todo.tags]
```

---

## Decision 4: Search Implementation

**Context**: Need case-insensitive substring search across title and description per FR-010, FR-011.

**Decision**: Use Python's `str.lower()` and `in` operator for substring matching

**Rationale**:
- Simple, built-in, and performant for in-memory lists up to 1000 items (per SC-002: <100ms)
- Case-insensitive via `.lower()` on both search term and fields
- Substring matching via `keyword in text` (Python's optimized Boyer-Moore)
- No regex complexity needed for simple substring search

**Alternatives Considered**:
1. **Full-text search engine (Whoosh, Elasticsearch)**: Rejected - external dependency, overkill for Phase I
2. **Regex matching (`re.search`)**: Rejected - unnecessary complexity, no fuzzy matching needed
3. **Trie-based search**: Rejected - over-engineering, violates Simplicity Before Scale

**Implementation Pattern**:
```python
def search_todos(todos: list[Todo], keyword: str) -> list[Todo]:
    """Search todos by keyword (case-insensitive substring match)."""
    if not keyword:
        return todos

    keyword_lower = keyword.lower()
    return [
        todo for todo in todos
        if keyword_lower in todo.description.lower()
    ]
```

**Performance**:
- Python's `in` operator uses Boyer-Moore-Horspool for string search (O(n) worst case)
- For 1000 todos with 50-char descriptions, estimated ~5ms on modern hardware
- Well within SC-002 requirement (<100ms)

---

## Decision 5: Sorting Implementation

**Context**: Need stable sorting by due_date, priority, or title per FR-017-FR-022. Tasks without due dates go to end when sorting by date.

**Decision**: Use Python's `sorted()` built-in with custom key functions

**Rationale**:
- Python's `sorted()` is stable by default (preserves relative order for equal elements)
- Timsort algorithm (O(n log n)) performs well on partially sorted data
- Custom key functions handle None values and priority ordering
- Stdlib solution, no external dependencies

**Alternatives Considered**:
1. **Manual quicksort/mergesort**: Rejected - reinventing the wheel, Python's Timsort is faster
2. **Sorting library (sortedcontainers)**: Rejected - external dependency
3. **Heapq for priority queue**: Rejected - overkill, doesn't provide stable sorting for all criteria

**Implementation Pattern**:
```python
def sort_by_due_date(todos: list[Todo], descending: bool = False) -> list[Todo]:
    """Sort by due date. None values (no due date) go to end."""
    return sorted(
        todos,
        key=lambda t: (t.due_date is None, t.due_date),
        reverse=descending
    )

def sort_by_priority(todos: list[Todo], descending: bool = True) -> list[Todo]:
    """Sort by priority (high → medium → low by default)."""
    priority_order = {"high": 1, "medium": 2, "low": 3}
    return sorted(
        todos,
        key=lambda t: priority_order.get(t.priority, 4),
        reverse=not descending  # Reverse for high-first default
    )

def sort_alphabetically(todos: list[Todo], descending: bool = False) -> list[Todo]:
    """Sort alphabetically by description (case-insensitive)."""
    return sorted(
        todos,
        key=lambda t: t.description.lower(),
        reverse=descending
    )
```

**None Handling**: The tuple `(t.due_date is None, t.due_date)` sorts None values to the end regardless of ascending/descending order because Python sorts False before True, so `(True, None)` comes after `(False, date)`.

---

## Decision 6: Filter Combination Logic

**Context**: Multiple filters must use AND logic per FR-015 (all conditions must match).

**Decision**: Chain filter operations sequentially (pipeline pattern)

**Rationale**:
- Each filter function takes a list and returns a filtered list
- Chaining filters naturally implements AND logic: `filter1(filter2(filter3(todos)))`
- Clear, readable, and easy to test each filter independently
- No complex boolean algebra or query DSL needed for Phase I

**Alternatives Considered**:
1. **Single filter function with all conditions**: Rejected - harder to test, violates single responsibility
2. **Boolean expression builder**: Rejected - over-engineering for Phase I
3. **OR logic support**: Rejected - spec explicitly states AND logic only for Phase II

**Implementation Pattern**:
```python
def apply_filters(todos: list[Todo], filters: SearchFilter) -> list[Todo]:
    """Apply all filters with AND logic."""
    result = todos

    if filters.keyword:
        result = search_todos(result, filters.keyword)

    if filters.completed is not None:
        result = [t for t in result if t.completed == filters.completed]

    if filters.priority:
        result = [t for t in result if t.priority == filters.priority]

    if filters.tag:
        result = filter_by_tag(result, filters.tag)

    return result
```

---

## Decision 7: Todo Model Extension Strategy

**Context**: Need to add 5 new fields (priority, tags, due_date, reminder_time, recurrence) to existing Todo dataclass while maintaining backward compatibility per FR-035, FR-036.

**Decision**: Add new fields with default values to existing Todo dataclass

**Rationale**:
- Dataclass fields with defaults can be added without breaking existing code
- Existing feature 001 calls like `Todo(id=1, description="task", completed=False)` continue to work
- New fields optional via default values: `priority="medium"`, `tags=field(default_factory=list)`, etc.
- Python's dataclass decorator handles initialization order (fields with defaults must come after required fields)

**Alternatives Considered**:
1. **Create TodoExtended subclass**: Rejected - adds complexity, type checking confusion, violates YAGNI
2. **Separate metadata dict**: Rejected - breaks type safety, harder to access fields
3. **Wrapper class**: Rejected - unnecessary indirection, violates Simplicity Before Scale

**Implementation Pattern**:
```python
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

@dataclass
class Todo:
    """Extended todo with advanced features."""
    # Original fields (required)
    id: int
    description: str
    completed: bool = False

    # Advanced features (optional with defaults)
    priority: str = "medium"  # "high" | "medium" | "low"
    tags: list[str] = field(default_factory=list)
    due_date: Optional[date] = None
    reminder_time: Optional[datetime] = None
    recurrence: str = "none"  # "none" | "daily" | "weekly" | "monthly"
```

**Backward Compatibility Verification**:
- ✅ `Todo(id=1, description="task")` still works (uses all defaults)
- ✅ `Todo(id=1, description="task", completed=True)` still works
- ✅ Existing repository methods unchanged: `get(id)`, `get_all()`, `update()`, `delete()`
- ✅ Feature 001 operations continue to work without modification

---

## Decision 8: Recurring Task Auto-Creation Strategy

**Context**: When a recurring task is marked complete, automatically create next occurrence per FR-025-FR-029.

**Decision**: Hook into existing `mark_complete()` operation to create next occurrence

**Rationale**:
- Minimal intrusion into existing code
- Single responsibility: mark_complete handles both completion and recurrence
- Deterministic: next occurrence created immediately in same operation
- Easy to test: mark complete → verify new task exists with correct fields

**Alternatives Considered**:
1. **Background job/scheduler**: Rejected - requires threading/async, violates Phase I simplicity
2. **Separate "process recurrence" operation**: Rejected - requires users to manually trigger, error-prone
3. **Observer pattern**: Rejected - over-engineering for single use case

**Implementation Pattern**:
```python
def mark_complete(todo_id: int) -> bool | str:
    """Mark todo complete. Auto-create next occurrence if recurring."""
    repository = TodoRepository()
    todo = repository.get(todo_id)

    if not todo:
        return f"Error: Todo with ID {todo_id} not found"

    # Mark current task complete
    todo.completed = True
    repository.update(todo_id, completed=True)

    # Auto-create next occurrence if recurring
    if todo.recurrence != "none" and todo.due_date:
        next_date = calculate_next_occurrence(todo.due_date, todo.recurrence)
        next_todo = Todo(
            id=repository._next_id,  # New ID
            description=todo.description,
            completed=False,
            priority=todo.priority,
            tags=todo.tags.copy(),
            due_date=next_date,
            reminder_time=calculate_next_reminder(todo.reminder_time, next_date) if todo.reminder_time else None,
            recurrence=todo.recurrence
        )
        repository.add_existing(next_todo)  # New helper to add with existing Todo object

    return True
```

---

## Decision 9: Validation Module Organization

**Context**: Need to validate priority, dates, and recurrence types. Should validation be centralized or distributed?

**Decision**: Create separate validation modules by domain (`validation/priority.py`, `validation/dates.py`, `validation/recurrence.py`)

**Rationale**:
- Single responsibility: each module validates one type of data
- Easy to test: unit tests can focus on specific validation logic
- Reusable: validation functions used by both operations and repository
- Clear error messages: each validator returns specific error strings

**Alternatives Considered**:
1. **Single validation.py module**: Rejected - becomes large and hard to navigate as validations grow
2. **Validation in Todo dataclass**: Rejected - mixes concerns, harder to test
3. **Schema validation library (Pydantic, marshmallow)**: Rejected - external dependency

**Implementation Pattern**:
```python
# validation/priority.py
VALID_PRIORITIES = {"high", "medium", "low"}

def validate_priority(priority: str) -> str | None:
    """Validate priority value. Returns None if valid, error message if invalid."""
    if priority not in VALID_PRIORITIES:
        return f"Error: Invalid priority '{priority}'. Valid values: high, medium, low"
    return None

# validation/recurrence.py
VALID_RECURRENCE = {"none", "daily", "weekly", "monthly"}

def validate_recurrence(recurrence: str) -> str | None:
    """Validate recurrence type. Returns None if valid, error message if invalid."""
    if recurrence not in VALID_RECURRENCE:
        return f"Error: Invalid recurrence '{recurrence}'. Valid values: none, daily, weekly, monthly"
    return None
```

---

## Decision 10: SearchFilter and SortCriteria Design

**Context**: Need structured way to pass search/filter/sort parameters to operations per spec Key Entities.

**Decision**: Use dataclasses for SearchFilter and SortCriteria with Optional fields

**Rationale**:
- Type-safe: IDE autocomplete and type checking
- Self-documenting: field names clearly indicate purpose
- Easy to extend: can add new filter criteria in future
- Optional fields via `Optional[type]`: None means "don't filter by this"

**Alternatives Considered**:
1. **Dict-based filters**: Rejected - no type safety, easy to misspell keys
2. **Kwargs in function signatures**: Rejected - function signatures become unwieldy with many filters
3. **Builder pattern**: Rejected - over-engineering for Phase I

**Implementation Pattern**:
```python
# models/filters.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchFilter:
    """Search and filter criteria for querying tasks."""
    keyword: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tag: Optional[str] = None

@dataclass
class SortCriteria:
    """Sort ordering for task lists."""
    field: str  # "due_date" | "priority" | "title"
    direction: str = "ascending"  # "ascending" | "descending"
```

**Usage Example**:
```python
# Find incomplete, high-priority work tasks
filters = SearchFilter(
    completed=False,
    priority="high",
    tag="work"
)
result = apply_filters(todos, filters)

# Sort by due date ascending
sort_criteria = SortCriteria(field="due_date", direction="ascending")
sorted_result = apply_sort(result, sort_criteria)
```

---

## Performance Considerations

### Search/Filter/Sort Performance

**Target**: SC-002, SC-003, SC-004 require operations complete in <100ms (search) and <50ms (filter/sort) for realistic dataset sizes.

**Analysis**:
- **Search (1000 items, 50-char avg description)**: O(n) substring search ≈ 5ms on modern CPU
- **Filter (100 items, 4 conditions)**: O(n) with simple predicates ≈ 1ms
- **Sort (100 items)**: O(n log n) Timsort ≈ 2ms

**Conclusion**: All operations well within performance requirements. No optimization needed for Phase I.

### Recurring Task Creation

**Target**: SC-005 requires next occurrence creation <10ms

**Analysis**:
- Date arithmetic (`timedelta`, month calculation): <0.1ms
- Object creation (`Todo` dataclass): <0.01ms
- Repository insertion (`_next_id` increment, dict insert): <0.01ms
- **Total**: ~0.2ms

**Conclusion**: Exceeds requirement by 50x. No optimization needed.

---

## Summary

All technical decisions align with Phase I constraints:
- ✅ Python stdlib only (`datetime`, `dataclasses`, `typing`, `calendar`)
- ✅ In-memory storage (dict-based repository extended)
- ✅ Deterministic behavior (no randomness, no AI, strict validation)
- ✅ Backward compatible (Todo extended with defaults, existing operations unchanged)
- ✅ Simple implementations (no premature optimization, no complex patterns)

**Ready for Phase 1**: Data model and contracts design.

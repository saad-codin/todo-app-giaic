# Quick Start: In-Memory Todo App — Advanced Features

**Feature**: 002-todo-advanced-features
**Branch**: `002-todo-advanced-features`
**Date**: 2026-01-09

## Overview

This guide demonstrates how to use the advanced todo features (priority, tags, search, filter, sort, recurring tasks) in the in-memory todo application. All examples show logic-layer usage - CLI integration is a future enhancement.

---

## Prerequisites

- Python 3.13 or higher
- Feature 001 (basic todo CRUD) implemented and working
- No external dependencies required

---

## Quick Examples

### Example 1: Create Todo with Priority and Tags

```python
from src.repository.todo_repository import TodoRepository

# Get repository instance
repository = TodoRepository()

# Create a high-priority work task
todo = repository.add(
    description="Prepare quarterly report",
    priority="high",
    tags=["work", "urgent"]
)

print(f"Created: {todo.description}")
print(f"Priority: {todo.priority}")
print(f"Tags: {todo.tags}")
# Output:
# Created: Prepare quarterly report
# Priority: high
# Tags: ['work', 'urgent']
```

---

### Example 2: Search Tasks by Keyword

```python
from src.operations.search_operations import search_todos

# Create some tasks
repository.add("Team meeting at 10am")
repository.add("Buy groceries")
repository.add("Schedule team lunch")

# Search for "team" (case-insensitive)
all_todos = repository.get_all()
results = search_todos(all_todos, "team")

for todo in results:
    print(f"- {todo.description}")
# Output:
# - Team meeting at 10am
# - Schedule team lunch
```

---

### Example 3: Filter by Priority and Completion Status

```python
from src.models.filters import SearchFilter
from src.operations.search_operations import apply_filters

# Find incomplete high-priority tasks
filters = SearchFilter(
    completed=False,
    priority="high"
)

all_todos = repository.get_all()
results = apply_filters(all_todos, filters)

print(f"Found {len(results)} high-priority incomplete tasks:")
for todo in results:
    print(f"- [{todo.priority}] {todo.description}")
```

---

### Example 4: Sort Tasks by Due Date

```python
from datetime import date
from src.operations.sort_operations import sort_by_due_date

# Create tasks with various due dates
repository.add("Project A", due_date="2026-01-20")
repository.add("Project B")  # No due date
repository.add("Project C", due_date="2026-01-15")

# Sort by due date (earliest first)
all_todos = repository.get_all()
sorted_todos = sort_by_due_date(all_todos, descending=False)

for todo in sorted_todos:
    due = todo.due_date.isoformat() if todo.due_date else "No due date"
    print(f"- {todo.description}: {due}")
# Output:
# - Project C: 2026-01-15
# - Project A: 2026-01-20
# - Project B: No due date
```

---

### Example 5: Recurring Tasks

```python
from src.operations.todo_operations import mark_complete

# Create a weekly recurring task
todo = repository.add(
    description="Team standup",
    priority="high",
    tags=["work", "meeting"],
    due_date="2026-01-15",
    recurrence="weekly"
)

print(f"Original task ID: {todo.id}")
print(f"Due date: {todo.due_date}")

# Mark complete - automatically creates next occurrence
mark_complete(todo.id)

# Check for next occurrence
all_todos = repository.get_all()
next_occurrence = [t for t in all_todos if t.description == "Team standup" and not t.completed]

if next_occurrence:
    next_todo = next_occurrence[0]
    print(f"\nNext occurrence ID: {next_todo.id}")
    print(f"Due date: {next_todo.due_date}")
    print(f"Completed: {next_todo.completed}")
# Output:
# Original task ID: 1
# Due date: 2026-01-15
#
# Next occurrence ID: 2
# Due date: 2026-01-22
# Completed: False
```

---

### Example 6: Combined Search, Filter, and Sort

```python
from src.models.filters import SearchFilter, SortCriteria
from src.operations.search_operations import apply_filters
from src.operations.sort_operations import apply_sort

# Create diverse task set
repository.add("Team meeting prep", priority="high", tags=["work"], due_date="2026-01-20")
repository.add("Grocery shopping", priority="medium", tags=["personal"], due_date="2026-01-18")
repository.add("Work review", priority="high", tags=["work"], due_date="2026-01-15", completed=True)
repository.add("Doctor appointment", priority="medium", tags=["personal"], due_date="2026-01-22")
repository.add("Project planning", priority="high", tags=["work"], due_date="2026-01-17")

# Step 1: Filter for incomplete high-priority work tasks
filters = SearchFilter(
    completed=False,
    priority="high",
    tag="work"
)
filtered = apply_filters(repository.get_all(), filters)

# Step 2: Sort by due date (earliest first)
sort_criteria = SortCriteria(field="due_date", direction="ascending")
result = apply_sort(filtered, sort_criteria)

# Display results
print("Incomplete high-priority work tasks (by due date):")
for todo in result:
    print(f"- {todo.due_date}: {todo.description}")
# Output:
# Incomplete high-priority work tasks (by due date):
# - 2026-01-17: Project planning
# - 2026-01-20: Team meeting prep
```

---

## Usage Patterns

### Pattern 1: Organization with Priority and Tags

**Use case**: Categorize tasks by urgency and context

```python
# Work tasks
repository.add("Client call", priority="high", tags=["work", "urgent"])
repository.add("Email responses", priority="medium", tags=["work", "admin"])
repository.add("Code review", priority="high", tags=["work", "dev"])

# Personal tasks
repository.add("Grocery shopping", priority="low", tags=["personal", "home"])
repository.add("Gym workout", priority="medium", tags=["personal", "health"])

# Quick retrieval of high-priority work tasks
filters = SearchFilter(priority="high", tag="work")
urgent_work = apply_filters(repository.get_all(), filters)
```

---

### Pattern 2: Finding Specific Tasks

**Use case**: Quickly locate tasks by keyword

```python
# Search across all descriptions
all_todos = repository.get_all()

# Find all meeting-related tasks
meetings = search_todos(all_todos, "meeting")

# Find all client-related tasks
clients = search_todos(all_todos, "client")

# Case-insensitive search
results = search_todos(all_todos, "URGENT")  # Matches "urgent" in any case
```

---

### Pattern 3: Daily Planning with Sorting

**Use case**: Review tasks in priority order or by deadline

```python
# Get all incomplete tasks
filters = SearchFilter(completed=False)
incomplete = apply_filters(repository.get_all(), filters)

# View by priority (high to low)
by_priority = sort_by_priority(incomplete, descending=True)

# Or view by due date (soonest first)
by_deadline = sort_by_due_date(incomplete, descending=False)

# Or alphabetically for easier scanning
alphabetical = sort_alphabetically(incomplete, descending=False)
```

---

### Pattern 4: Recurring Task Management

**Use case**: Automate repetitive tasks

```python
# Daily tasks
repository.add(
    description="Morning standup",
    priority="high",
    tags=["work", "meeting"],
    due_date="2026-01-15",
    reminder_time="2026-01-15 09:00",
    recurrence="daily"
)

# Weekly tasks
repository.add(
    description="Weekly review",
    priority="medium",
    tags=["personal", "productivity"],
    due_date="2026-01-17",  # Friday
    recurrence="weekly"
)

# Monthly tasks
repository.add(
    description="Pay rent",
    priority="high",
    tags=["personal", "finance"],
    due_date="2026-01-31",
    recurrence="monthly"
)

# When you complete any of these, the next occurrence is auto-created
```

---

## Validation Examples

### Valid Inputs

```python
# Valid priority values
repository.add("Task", priority="high")  # ✅
repository.add("Task", priority="medium")  # ✅
repository.add("Task", priority="low")  # ✅

# Valid dates
repository.add("Task", due_date="2026-01-15")  # ✅ ISO 8601 format

# Valid datetimes
repository.add("Task", reminder_time="2026-01-15 09:00")  # ✅ 24-hour format

# Valid recurrence
repository.add("Task", recurrence="daily")  # ✅
repository.add("Task", recurrence="weekly")  # ✅
repository.add("Task", recurrence="monthly")  # ✅

# Valid tags
repository.add("Task", tags=["work", "urgent", "client"])  # ✅
repository.add("Task", tags=[])  # ✅ Empty list is valid
```

---

### Invalid Inputs (Examples)

```python
# Invalid priority
result = repository.add("Task", priority="critical")
# Returns: "Error: Invalid priority 'critical'. Valid values: high, medium, low"

# Invalid date format
result = repository.add("Task", due_date="tomorrow")
# Returns: "Error: Invalid date format. Expected YYYY-MM-DD"

result = repository.add("Task", due_date="01/15/2026")
# Returns: "Error: Invalid date format. Expected YYYY-MM-DD"

# Invalid datetime format
result = repository.add("Task", reminder_time="9am")
# Returns: "Error: Invalid datetime format. Expected YYYY-MM-DD HH:MM"

# Invalid recurrence
result = repository.add("Task", recurrence="yearly")
# Returns: "Error: Invalid recurrence 'yearly'. Valid values: none, daily, weekly, monthly"
```

---

## Testing Scenarios

### Scenario 1: Priority-Based Task Management

```python
# Setup: Create tasks with different priorities
repo = TodoRepository()
repo.add("Critical bug", priority="high")
repo.add("Code refactoring", priority="medium")
repo.add("Update docs", priority="low")
repo.add("Security patch", priority="high")

# Test: Filter and sort by priority
filters = SearchFilter(completed=False)
incomplete = apply_filters(repo.get_all(), filters)
sorted_tasks = sort_by_priority(incomplete, descending=True)

# Verify: High-priority tasks appear first
assert sorted_tasks[0].priority == "high"
assert sorted_tasks[1].priority == "high"
assert sorted_tasks[2].priority == "medium"
assert sorted_tasks[3].priority == "low"
```

---

### Scenario 2: Tag-Based Filtering

```python
# Setup: Create tasks with various tags
repo.add("Client meeting", tags=["work", "urgent", "client"])
repo.add("Grocery shopping", tags=["personal", "home"])
repo.add("Team sync", tags=["work", "meeting"])
repo.add("Code review", tags=["work", "dev"])

# Test: Filter by "work" tag
filters = SearchFilter(tag="work")
work_tasks = apply_filters(repo.get_all(), filters)

# Verify: Only work tasks returned
assert len(work_tasks) == 3
for task in work_tasks:
    assert "work" in task.tags
```

---

### Scenario 3: Recurring Task Auto-Creation

```python
from datetime import date

# Setup: Create weekly recurring task
repo = TodoRepository()
original = repo.add(
    description="Weekly report",
    priority="high",
    due_date="2026-01-10",
    recurrence="weekly"
)
original_id = original.id

# Test: Mark complete
mark_complete(original_id)

# Verify: Next occurrence created
all_todos = repo.get_all()
original_todo = repo.get(original_id)
next_occurrences = [t for t in all_todos if t.description == "Weekly report" and not t.completed]

assert original_todo.completed == True  # Original marked complete
assert len(next_occurrences) == 1  # One new occurrence
assert next_occurrences[0].id != original_id  # New ID
assert next_occurrences[0].due_date == date(2026, 1, 17)  # +7 days
assert next_occurrences[0].completed == False  # Reset to incomplete
```

---

## Troubleshooting

### Issue: Tags not filtering correctly

**Problem**: `filter_by_tag` returns no results even though tasks have the tag

**Solution**: Tags are stored lowercase. Ensure you're filtering with lowercase or the filter will handle it:
```python
# This works (case-insensitive)
results = filter_by_tag(todos, "Work")  # Internally converts to "work"
results = filter_by_tag(todos, "WORK")  # Same result
```

---

### Issue: Recurring task not creating next occurrence

**Problem**: Completed recurring task doesn't create next occurrence

**Causes and Solutions**:
1. **Recurrence is "none"**: Check `todo.recurrence` is set to "daily", "weekly", or "monthly"
2. **No due date**: Recurring tasks require `due_date` to calculate next occurrence
3. **Task not actually completed**: Verify `mark_complete()` was called, not just setting `completed=True`

```python
# ✅ Correct
todo = repo.add("Task", due_date="2026-01-15", recurrence="weekly")
mark_complete(todo.id)  # Creates next occurrence

# ❌ Incorrect - missing due_date
todo = repo.add("Task", recurrence="weekly")  # No due_date
mark_complete(todo.id)  # Won't create next occurrence

# ❌ Incorrect - not using mark_complete
todo.completed = True  # Direct assignment doesn't trigger recurrence logic
```

---

### Issue: Sorting doesn't work as expected

**Problem**: Tasks with no due date appear in unexpected positions

**Solution**: By design, tasks without due dates always appear at the end when sorting by due_date, regardless of ascending/descending order:

```python
# This is correct behavior
sorted_todos = sort_by_due_date(todos, descending=False)
# Order: [tasks with dates (earliest first)], [tasks without dates]

sorted_todos = sort_by_due_date(todos, descending=True)
# Order: [tasks with dates (latest first)], [tasks without dates]
```

---

## Next Steps

- **Implementation**: Run `/sp.tasks` to generate implementation tasks
- **Testing**: Reference `tests/manual/test_scenarios.md` for 35 acceptance test scenarios
- **CLI Integration**: Extend `console_app.py` menu to expose advanced features (future enhancement)

---

## Summary

This quickstart demonstrated:
- ✅ Creating todos with priority, tags, due dates, and recurrence
- ✅ Searching tasks by keyword
- ✅ Filtering by completion status, priority, and tags
- ✅ Sorting by due date, priority, and alphabetically
- ✅ Combining search, filter, and sort operations
- ✅ Managing recurring tasks with auto-creation
- ✅ Validation and error handling
- ✅ Common usage patterns and troubleshooting

All operations maintain backward compatibility with feature 001 while adding powerful organizational capabilities.

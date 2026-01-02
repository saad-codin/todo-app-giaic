# Operation Contracts: In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2026-01-02
**Purpose**: Define internal operation signatures, inputs, outputs, and error conditions

## Overview

This document specifies the contracts for todo operations. Since this is a console application (not a web API), these are internal Python function contracts rather than HTTP endpoints.

## Todo Operations

### 1. Add Todo

**Operation**: `add_todo(description: str) -> Result[Todo, str]`

**Purpose**: Create a new todo with auto-assigned ID (FR-001, FR-002)

**Inputs**:
- `description` (str): Text description of the todo task

**Preconditions**:
- Description must not be empty string
- Description must not be whitespace-only

**Outputs**:
- **Success**: Returns Todo object with auto-assigned ID, provided description, completed=False
- **Failure**: Returns error message string

**Postconditions**:
- Todo is stored in repository
- Next ID counter is incremented
- Todo ID is unique and never reused

**Error Conditions**:
| Condition | Error Message |
|-----------|---------------|
| Empty description | "Error: Description cannot be empty" |
| Whitespace-only description | "Error: Description cannot be whitespace-only" |

**Example**:
```python
# Success case
result = add_todo("Buy groceries")
# Returns: Todo(id=1, description="Buy groceries", completed=False)

# Failure case
result = add_todo("")
# Returns: "Error: Description cannot be empty"
```

---

### 2. Get All Todos

**Operation**: `get_all_todos() -> list[Todo]`

**Purpose**: Retrieve all todos for display (FR-006)

**Inputs**: None

**Preconditions**: None

**Outputs**:
- **Success**: Returns list of all Todo objects, sorted by ID (ascending)
- **Empty**: Returns empty list if no todos exist

**Postconditions**:
- Repository state unchanged (read-only operation)

**Error Conditions**: None (always succeeds, may return empty list)

**Example**:
```python
# With todos
todos = get_all_todos()
# Returns: [Todo(id=1, ...), Todo(id=2, ...), Todo(id=3, ...)]

# No todos
todos = get_all_todos()
# Returns: []
```

---

### 3. Update Todo

**Operation**: `update_todo(id: int, new_description: str) -> Result[Todo, str]`

**Purpose**: Update the description of an existing todo (FR-007)

**Inputs**:
- `id` (int): ID of the todo to update
- `new_description` (str): New text description

**Preconditions**:
- Todo with given ID must exist
- New description must not be empty string
- New description must not be whitespace-only

**Outputs**:
- **Success**: Returns updated Todo object
- **Failure**: Returns error message string

**Postconditions**:
- Todo description is updated in repository
- Todo ID and completed status remain unchanged

**Error Conditions**:
| Condition | Error Message |
|-----------|---------------|
| Todo ID not found | "Error: Todo with ID {id} not found" |
| Empty description | "Error: Description cannot be empty" |
| Whitespace-only description | "Error: Description cannot be whitespace-only" |

**Example**:
```python
# Success case
result = update_todo(1, "Buy organic groceries")
# Returns: Todo(id=1, description="Buy organic groceries", completed=False)

# Failure case
result = update_todo(999, "New description")
# Returns: "Error: Todo with ID 999 not found"
```

---

### 4. Delete Todo

**Operation**: `delete_todo(id: int) -> Result[bool, str]`

**Purpose**: Remove a todo from storage (FR-009)

**Inputs**:
- `id` (int): ID of the todo to delete

**Preconditions**:
- Todo with given ID must exist

**Outputs**:
- **Success**: Returns True
- **Failure**: Returns error message string

**Postconditions**:
- Todo is removed from repository
- ID is never reused (next ID counter continues)

**Error Conditions**:
| Condition | Error Message |
|-----------|---------------|
| Todo ID not found | "Error: Todo with ID {id} not found" |

**Example**:
```python
# Success case
result = delete_todo(1)
# Returns: True

# Failure case
result = delete_todo(999)
# Returns: "Error: Todo with ID 999 not found"
```

---

### 5. Mark Todo Complete

**Operation**: `mark_complete(id: int) -> Result[Todo, str]`

**Purpose**: Set a todo's completed status to True (FR-008)

**Inputs**:
- `id` (int): ID of the todo to mark complete

**Preconditions**:
- Todo with given ID must exist

**Outputs**:
- **Success**: Returns updated Todo object with completed=True
- **Failure**: Returns error message string

**Postconditions**:
- Todo completed status is set to True
- Todo ID and description remain unchanged

**Error Conditions**:
| Condition | Error Message |
|-----------|---------------|
| Todo ID not found | "Error: Todo with ID {id} not found" |

**Example**:
```python
# Success case
result = mark_complete(1)
# Returns: Todo(id=1, description="Buy groceries", completed=True)

# Failure case
result = mark_complete(999)
# Returns: "Error: Todo with ID 999 not found"
```

---

### 6. Mark Todo Incomplete

**Operation**: `mark_incomplete(id: int) -> Result[Todo, str]`

**Purpose**: Set a todo's completed status to False (FR-008)

**Inputs**:
- `id` (int): ID of the todo to mark incomplete

**Preconditions**:
- Todo with given ID must exist

**Outputs**:
- **Success**: Returns updated Todo object with completed=False
- **Failure**: Returns error message string

**Postconditions**:
- Todo completed status is set to False
- Todo ID and description remain unchanged

**Error Conditions**:
| Condition | Error Message |
|-----------|---------------|
| Todo ID not found | "Error: Todo with ID {id} not found" |

**Example**:
```python
# Success case
result = mark_incomplete(1)
# Returns: Todo(id=1, description="Buy groceries", completed=False)

# Failure case
result = mark_incomplete(999)
# Returns: "Error: Todo with ID 999 not found"
```

---

## Result Type

**Pattern**: Use Python's union types for success/failure results

```python
from typing import TypeAlias

# Success returns data, failure returns error message
Result[T, E]: TypeAlias = T | E

# Example usage
def add_todo(description: str) -> Todo | str:
    if not description.strip():
        return "Error: Description cannot be empty"
    # ... create todo
    return todo
```

**Rationale**: Simple error handling without exceptions for expected failures (validation errors, not found)

## Console Interface Contract

**Menu Display** (FR-004):
```
=== Todo Application ===
1. Add Todo
2. View All Todos
3. Update Todo
4. Delete Todo
5. Mark Todo Complete
6. Mark Todo Incomplete
7. Exit

Enter your choice (1-7):
```

**Todo Display Format** (FR-016):
```
[ ] 1: Buy groceries
[✓] 2: Call dentist
[ ] 3: Finish project report
```

- `[ ]` indicates incomplete
- `[✓]` indicates complete
- Format: `[status] id: description`

## Validation Rules Summary

| Validation | Rule | Error Message |
|------------|------|---------------|
| Description not empty | `description.strip() != ""` | "Error: Description cannot be empty" or "Error: Description cannot be whitespace-only" |
| Todo exists | `id in repository._todos` | "Error: Todo with ID {id} not found" |
| Valid menu choice | `choice in [1, 2, 3, 4, 5, 6, 7]` | "Error: Invalid choice. Please enter a number between 1 and 7" |

## Performance Contracts

All operations must complete in under 100ms (SC-002):

| Operation | Expected Time | Complexity |
|-----------|---------------|------------|
| Add Todo | <1ms | O(1) - dict insert |
| Get All Todos | <1ms for <1000 todos | O(n) - list all |
| Update Todo | <1ms | O(1) - dict lookup + update |
| Delete Todo | <1ms | O(1) - dict delete |
| Mark Complete/Incomplete | <1ms | O(1) - dict lookup + update |

## Error Handling Strategy

**Expected Errors** (validation, not found):
- Return error message string
- Display to user via console
- Return to main menu

**Unexpected Errors** (programming bugs):
- Catch with try/except
- Display friendly message: "An unexpected error occurred. Please try again."
- Log error details to console for debugging
- Return to main menu (do not crash)

## Future API Evolution

**Phase II Web API Mapping**:
These internal operations will map to RESTful HTTP endpoints:

| Internal Operation | HTTP Endpoint | Method |
|--------------------|---------------|--------|
| add_todo | POST /todos | Create |
| get_all_todos | GET /todos | Read All |
| update_todo | PUT /todos/{id} | Update |
| delete_todo | DELETE /todos/{id} | Delete |
| mark_complete | PATCH /todos/{id}/complete | Partial Update |
| mark_incomplete | PATCH /todos/{id}/incomplete | Partial Update |

This contract design ensures clean evolution from console to web API in Phase II.

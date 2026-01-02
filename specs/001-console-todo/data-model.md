# Data Model: In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2026-01-02
**Purpose**: Define data structures and validation rules for Phase I implementation

## Entities

### Todo

**Description**: Represents a single todo item with unique ID, description, and completion status.

**Fields**:

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| id | int | Yes | Auto-assigned | Must be positive integer | Unique identifier, auto-incremented from 1 |
| description | str | Yes | None | Must be non-empty, no whitespace-only | User-provided task description |
| completed | bool | Yes | False | Must be True or False | Completion status (True = complete, False = incomplete) |

**Invariants**:
- ID is immutable once assigned (never changes for a todo)
- ID is never reused even after deletion
- Description cannot be empty string or whitespace-only
- Completed status can toggle between True and False

**State Transitions**:
```
[Created] → completed=False
   ↓
[Incomplete] ←→ [Complete]  (toggle via mark complete/incomplete operations)
   ↓
[Deleted] (removed from storage, ID never reused)
```

**Relationships**:
- None (todos are independent entities with no relationships)

**Python Representation**:
```python
from dataclasses import dataclass

@dataclass
class Todo:
    id: int
    description: str
    completed: bool = False
```

## Repository Schema

**TodoRepository**: In-memory storage for todos

**Internal Structure**:
- `_todos: dict[int, Todo]` - Dictionary mapping todo IDs to Todo objects
- `_next_id: int` - Counter for auto-incrementing IDs, starts at 1

**Operations**:
- `add(description: str) -> Todo` - Create new todo with auto-assigned ID
- `get(id: int) -> Todo | None` - Retrieve todo by ID
- `get_all() -> list[Todo]` - Retrieve all todos (ordered by ID)
- `update(id: int, description: str) -> Todo | None` - Update todo description
- `delete(id: int) -> bool` - Remove todo from storage
- `mark_complete(id: int) -> Todo | None` - Set completed=True
- `mark_incomplete(id: int) -> Todo | None` - Set completed=False

**Constraints**:
- All data stored in memory only
- State resets on application restart
- No persistence to disk
- Single repository instance (singleton pattern)

## Validation Rules

### Description Validation (FR-015)

**Rule**: Description must not be empty or whitespace-only

**Implementation**:
```python
def is_valid_description(description: str) -> bool:
    return description and description.strip() != ""
```

**Error Handling**:
- Empty string: "Error: Description cannot be empty"
- Whitespace only: "Error: Description cannot be empty or whitespace-only"

### ID Validation

**Rule**: ID must exist in repository for get/update/delete/mark operations

**Implementation**:
```python
def exists(id: int) -> bool:
    return id in self._todos
```

**Error Handling**:
- Non-existent ID: "Error: Todo with ID {id} not found"

## Data Flow

### Add Todo
```
User input (description)
   → Validate description (not empty/whitespace)
   → Generate new ID (auto-increment)
   → Create Todo(id, description, completed=False)
   → Store in _todos dict
   → Return Todo object
```

### View Todos
```
Request all todos
   → Retrieve all Todo objects from _todos dict
   → Sort by ID (ascending)
   → Return list[Todo]
```

### Update Todo
```
User input (id, new_description)
   → Validate description (not empty/whitespace)
   → Check ID exists
   → Update description field
   → Return updated Todo object
```

### Delete Todo
```
User input (id)
   → Check ID exists
   → Remove from _todos dict
   → Do NOT reuse ID (next_id continues incrementing)
   → Return success boolean
```

### Mark Complete/Incomplete
```
User input (id)
   → Check ID exists
   → Toggle completed field (True/False)
   → Return updated Todo object
```

## Memory Management

**Scope**: Application session only

**Lifecycle**:
1. Application starts → Repository initialized with empty dict, next_id=1
2. Operations modify in-memory dict
3. Application exits → All data lost (expected behavior per FR-014)

**Limits**: No hard limits (Python dict can grow to available memory)

**Cleanup**: Not required (data discarded on exit)

## Future Evolution Notes

**Phase II Compatibility**:
- Todo dataclass can be reused with SQLModel for database persistence
- Repository pattern allows easy swap to database-backed implementation
- Validation rules remain the same
- ID generation will shift to database auto-increment

**Phase III Compatibility**:
- Todo model unchanged
- AI features will operate on same data model
- Validation rules preserved

This data model design ensures Phase I simplicity while supporting clean evolution to future phases.

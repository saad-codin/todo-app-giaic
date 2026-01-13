"""Business logic for todo operations."""

from datetime import date, datetime
from typing import Optional
from src.models.todo import Todo
from src.repository.todo_repository import TodoRepository
from src.validation.dates import validate_date, validate_datetime


def is_valid_description(description: str) -> bool:
    """Validate that description is non-empty and not whitespace-only.

    Args:
        description: Description to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(description and description.strip())


def normalize_tags(tags: list[str]) -> list[str]:
    """Normalize tags to lowercase and trim whitespace.

    Args:
        tags: List of tag strings

    Returns:
        List of normalized tag strings (lowercase, trimmed, no empty strings)
    """
    return [tag.strip().lower() for tag in tags if tag.strip()]


def add_todo(
    description: str,
    priority: str = "medium",
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    recurrence: str = "none",
) -> Todo | str:
    """Add a new todo with validation.

    Args:
        description: Task description
        priority: Priority level ("high", "medium", or "low")
        tags: List of tags for categorization
        due_date: Optional due date in YYYY-MM-DD format
        reminder_time: Optional reminder time in YYYY-MM-DD HH:MM format
        recurrence: Recurrence pattern ("none", "daily", "weekly", or "monthly")

    Returns:
        Todo object on success, error message string on failure
    """
    # Validate description
    if not description:
        return "Error: Description cannot be empty"
    if not description.strip():
        return "Error: Description cannot be whitespace-only"

    # Normalize tags
    normalized_tags = normalize_tags(tags) if tags else []

    # Parse and validate due_date if provided
    parsed_due_date = None
    if due_date:
        result = validate_date(due_date)
        if isinstance(result, str):
            return result  # Return error message
        parsed_due_date = result

    # Parse and validate reminder_time if provided
    parsed_reminder_time = None
    if reminder_time:
        result = validate_datetime(reminder_time)
        if isinstance(result, str):
            return result  # Return error message
        parsed_reminder_time = result

    # Call repository with all parameters
    repository = TodoRepository()
    return repository.add(
        description=description.strip(),
        priority=priority,
        tags=normalized_tags,
        due_date=parsed_due_date,
        reminder_time=parsed_reminder_time,
        recurrence=recurrence,
    )


def get_all_todos() -> list[Todo]:
    """Retrieve all todos.

    Returns:
        List of all Todo objects, sorted by ID
    """
    repository = TodoRepository()
    return repository.get_all()


def update_todo(
    id: int,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    recurrence: Optional[str] = None,
    completed: Optional[bool] = None,
) -> Todo | str:
    """Update a todo's fields with validation.

    Args:
        id: Todo ID to update
        description: New description (optional)
        priority: New priority level (optional)
        tags: New tags list (optional)
        due_date: New due date in YYYY-MM-DD format (optional)
        reminder_time: New reminder time in YYYY-MM-DD HH:MM format (optional)
        recurrence: New recurrence pattern (optional)
        completed: New completion status (optional)

    Returns:
        Updated Todo object on success, error message string on failure
    """
    # Build kwargs for repository update
    kwargs = {}

    # Validate and add description
    if description is not None:
        if not description:
            return "Error: Description cannot be empty"
        if not description.strip():
            return "Error: Description cannot be whitespace-only"
        kwargs["description"] = description.strip()

    # Add priority if provided (validation happens in repository)
    if priority is not None:
        kwargs["priority"] = priority

    # Normalize and add tags
    if tags is not None:
        kwargs["tags"] = normalize_tags(tags)

    # Parse and validate due_date
    if due_date is not None:
        result = validate_date(due_date)
        if isinstance(result, str):
            return result  # Return error message
        kwargs["due_date"] = result

    # Parse and validate reminder_time
    if reminder_time is not None:
        result = validate_datetime(reminder_time)
        if isinstance(result, str):
            return result  # Return error message
        kwargs["reminder_time"] = result

    # Add recurrence if provided (validation happens in repository)
    if recurrence is not None:
        kwargs["recurrence"] = recurrence

    # Add completed status
    if completed is not None:
        kwargs["completed"] = completed

    # Call repository update
    repository = TodoRepository()
    result = repository.update(id, **kwargs)

    if result is None:
        return f"Error: Todo with ID {id} not found"
    if isinstance(result, str):
        return result  # Return validation error from repository

    return result


def delete_todo(id: int) -> bool | str:
    """Delete a todo by ID.

    Args:
        id: Todo ID to delete

    Returns:
        True on success, error message string on failure
    """
    repository = TodoRepository()
    success = repository.delete(id)

    if not success:
        return f"Error: Todo with ID {id} not found"

    return True


def mark_complete(id: int) -> Todo | str:
    """Mark a todo as complete.

    For recurring todos with due dates, automatically creates the next occurrence.

    Args:
        id: Todo ID to mark complete

    Returns:
        Updated Todo object on success, error message string on failure
    """
    repository = TodoRepository()
    todo = repository.mark_complete(id)

    if todo is None:
        return f"Error: Todo with ID {id} not found"

    # Create next occurrence for recurring tasks
    if todo.recurrence != "none" and todo.due_date is not None:
        from src.operations.recurrence import create_next_occurrence

        create_next_occurrence(todo)

    return todo


def mark_incomplete(id: int) -> Todo | str:
    """Mark a todo as incomplete.

    Args:
        id: Todo ID to mark incomplete

    Returns:
        Updated Todo object on success, error message string on failure
    """
    repository = TodoRepository()
    todo = repository.mark_incomplete(id)

    if todo is None:
        return f"Error: Todo with ID {id} not found"

    return todo


def add_tag(id: int, tag: str) -> Todo | str:
    """Add a tag to a todo.

    Args:
        id: Todo ID to add tag to
        tag: Tag to add (will be normalized)

    Returns:
        Updated Todo object on success, error message string on failure
    """
    if not tag or not tag.strip():
        return "Error: Tag cannot be empty"

    repository = TodoRepository()
    todo = repository.get(id)

    if todo is None:
        return f"Error: Todo with ID {id} not found"

    # Normalize tag and add if not already present
    normalized_tag = tag.strip().lower()
    if normalized_tag not in todo.tags:
        todo.tags.append(normalized_tag)

    return todo


def remove_tag(id: int, tag: str) -> Todo | str:
    """Remove a tag from a todo.

    Args:
        id: Todo ID to remove tag from
        tag: Tag to remove (case-insensitive)

    Returns:
        Updated Todo object on success, error message string on failure
    """
    repository = TodoRepository()
    todo = repository.get(id)

    if todo is None:
        return f"Error: Todo with ID {id} not found"

    # Normalize tag for case-insensitive removal
    normalized_tag = tag.strip().lower()
    if normalized_tag in todo.tags:
        todo.tags.remove(normalized_tag)

    return todo


def update_tags(id: int, tags: list[str]) -> Todo | str:
    """Replace all tags for a todo.

    Args:
        id: Todo ID to update tags for
        tags: New list of tags (will be normalized)

    Returns:
        Updated Todo object on success, error message string on failure
    """
    repository = TodoRepository()
    todo = repository.get(id)

    if todo is None:
        return f"Error: Todo with ID {id} not found"

    # Normalize and replace all tags
    todo.tags = normalize_tags(tags)

    return todo

"""Business logic for todo operations."""

from src.models.todo import Todo
from src.repository.todo_repository import TodoRepository


def is_valid_description(description: str) -> bool:
    """Validate that description is non-empty and not whitespace-only.

    Args:
        description: Description to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(description and description.strip())


def add_todo(description: str) -> Todo | str:
    """Add a new todo with validation.

    Args:
        description: Task description

    Returns:
        Todo object on success, error message string on failure
    """
    if not description:
        return "Error: Description cannot be empty"
    if not description.strip():
        return "Error: Description cannot be whitespace-only"

    repository = TodoRepository()
    return repository.add(description.strip())


def get_all_todos() -> list[Todo]:
    """Retrieve all todos.

    Returns:
        List of all Todo objects, sorted by ID
    """
    repository = TodoRepository()
    return repository.get_all()


def update_todo(id: int, new_description: str) -> Todo | str:
    """Update a todo's description with validation.

    Args:
        id: Todo ID to update
        new_description: New description

    Returns:
        Updated Todo object on success, error message string on failure
    """
    if not new_description:
        return "Error: Description cannot be empty"
    if not new_description.strip():
        return "Error: Description cannot be whitespace-only"

    repository = TodoRepository()
    todo = repository.update(id, new_description.strip())

    if todo is None:
        return f"Error: Todo with ID {id} not found"

    return todo


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

    Args:
        id: Todo ID to mark complete

    Returns:
        Updated Todo object on success, error message string on failure
    """
    repository = TodoRepository()
    todo = repository.mark_complete(id)

    if todo is None:
        return f"Error: Todo with ID {id} not found"

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

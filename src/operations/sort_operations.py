"""Sort operations for todos."""

from src.models.todo import Todo
from src.models.filters import SortCriteria


# Priority mapping for stable numeric sorting
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}


def sort_by_due_date(todos: list[Todo], direction: str = "ascending") -> list[Todo]:
    """Sort todos by due date (stable sort, None values at end).

    Args:
        todos: List of todos to sort
        direction: Sort direction ("ascending" or "descending")

    Returns:
        Sorted list of todos
    """
    # Use tuple key: (is_none, date_value) to place None at end
    # is_none=False comes before is_none=True in ascending order
    reverse = direction == "descending"

    def sort_key(todo: Todo):
        if todo.due_date is None:
            # Place None at end regardless of direction
            return (True, None) if not reverse else (False, None)
        return (False, todo.due_date)

    return sorted(todos, key=sort_key, reverse=reverse)


def sort_by_priority(todos: list[Todo], direction: str = "ascending") -> list[Todo]:
    """Sort todos by priority (high=1, medium=2, low=3).

    Args:
        todos: List of todos to sort
        direction: Sort direction ("ascending" or "descending")

    Returns:
        Sorted list of todos
    """
    reverse = direction == "descending"

    def sort_key(todo: Todo):
        return PRIORITY_ORDER.get(todo.priority, 99)  # Unknown priority goes last

    return sorted(todos, key=sort_key, reverse=reverse)


def sort_alphabetically(todos: list[Todo], direction: str = "ascending") -> list[Todo]:
    """Sort todos alphabetically by description (case-insensitive).

    Args:
        todos: List of todos to sort
        direction: Sort direction ("ascending" or "descending")

    Returns:
        Sorted list of todos
    """
    reverse = direction == "descending"
    return sorted(todos, key=lambda todo: todo.description.lower(), reverse=reverse)


def apply_sort(todos: list[Todo], sort_criteria: SortCriteria) -> list[Todo]:
    """Apply sort based on criteria.

    Args:
        todos: List of todos to sort
        sort_criteria: SortCriteria specifying field and direction

    Returns:
        Sorted list of todos
    """
    if sort_criteria.field == "due_date":
        return sort_by_due_date(todos, sort_criteria.direction)
    elif sort_criteria.field == "priority":
        return sort_by_priority(todos, sort_criteria.direction)
    elif sort_criteria.field == "alphabetical":
        return sort_alphabetically(todos, sort_criteria.direction)
    else:
        raise ValueError(f"Unknown sort field: {sort_criteria.field}")

"""Search and filter operations for todos."""

from src.models.todo import Todo
from src.models.filters import SearchFilter


def search_todos(todos: list[Todo], keyword: str) -> list[Todo]:
    """Search todos by keyword (case-insensitive substring match on description).

    Args:
        todos: List of todos to search
        keyword: Search keyword

    Returns:
        List of todos matching the keyword
    """
    if not keyword:
        return todos

    keyword_lower = keyword.lower()
    return [todo for todo in todos if keyword_lower in todo.description.lower()]


def filter_by_completed(todos: list[Todo], completed: bool) -> list[Todo]:
    """Filter todos by completion status.

    Args:
        todos: List of todos to filter
        completed: Completion status to filter by (True/False)

    Returns:
        List of todos matching the completion status
    """
    return [todo for todo in todos if todo.completed == completed]


def filter_by_priority(todos: list[Todo], priority: str) -> list[Todo]:
    """Filter todos by priority level.

    Args:
        todos: List of todos to filter
        priority: Priority level ("high", "medium", or "low")

    Returns:
        List of todos matching the priority
    """
    return [todo for todo in todos if todo.priority == priority]


def filter_by_tag(todos: list[Todo], tag: str) -> list[Todo]:
    """Filter todos by tag (case-insensitive).

    Args:
        todos: List of todos to filter
        tag: Tag to filter by

    Returns:
        List of todos that have the specified tag
    """
    tag_lower = tag.lower()
    return [todo for todo in todos if tag_lower in todo.tags]


def apply_filters(todos: list[Todo], search_filter: SearchFilter) -> list[Todo]:
    """Apply multiple filters with AND logic (sequential pipeline).

    Filters are applied in sequence: keyword → completed → priority → tag.
    All non-None filters must match (AND logic).

    Args:
        todos: List of todos to filter
        search_filter: SearchFilter with criteria to apply

    Returns:
        List of todos matching all specified filter criteria
    """
    result = todos

    # Apply keyword search
    if search_filter.keyword is not None:
        result = search_todos(result, search_filter.keyword)

    # Apply completion status filter
    if search_filter.completed is not None:
        result = filter_by_completed(result, search_filter.completed)

    # Apply priority filter
    if search_filter.priority is not None:
        result = filter_by_priority(result, search_filter.priority)

    # Apply tag filter
    if search_filter.tag is not None:
        result = filter_by_tag(result, search_filter.tag)

    return result

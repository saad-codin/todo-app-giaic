"""Filter and sort criteria models for todo operations."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchFilter:
    """Criteria for filtering todos.

    All fields are optional. When provided, filters are combined with AND logic.

    Attributes:
        keyword: Case-insensitive substring match on description
        completed: Filter by completion status (True/False/None for all)
        priority: Filter by priority level ("high", "medium", or "low")
        tag: Case-insensitive tag match (todo must have this tag)
    """

    keyword: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tag: Optional[str] = None


@dataclass
class SortCriteria:
    """Criteria for sorting todos.

    Attributes:
        field: Field to sort by ("due_date", "priority", or "alphabetical")
        direction: Sort direction ("ascending" or "descending")
    """

    field: str
    direction: str = "ascending"

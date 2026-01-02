"""Todo data model for in-memory todo application."""

from dataclasses import dataclass


@dataclass
class Todo:
    """Represents a single todo item.

    Attributes:
        id: Unique identifier (auto-assigned, immutable)
        description: Task description (user-provided, required)
        completed: Completion status (default: False)
    """
    id: int
    description: str
    completed: bool = False

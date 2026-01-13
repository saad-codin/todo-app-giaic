"""Todo data model for in-memory todo application."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Todo:
    """Represents a single todo item with advanced features.

    Attributes:
        id: Unique identifier (auto-assigned, immutable)
        description: Task description (user-provided, required)
        completed: Completion status (default: False)
        priority: Task priority level - "high", "medium", or "low" (default: "medium")
        tags: Categories/labels for organization (default: empty list)
        due_date: Optional target completion date in YYYY-MM-DD format
        reminder_time: Optional reminder timestamp in YYYY-MM-DD HH:MM format
        recurrence: Recurrence pattern - "none", "daily", "weekly", or "monthly" (default: "none")
    """
    id: int
    description: str
    completed: bool = False
    priority: str = "medium"
    tags: list[str] = field(default_factory=list)
    due_date: Optional[date] = None
    reminder_time: Optional[datetime] = None
    recurrence: str = "none"

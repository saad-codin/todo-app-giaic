"""Event schema dataclasses for Dapr pub/sub messaging."""

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class TaskCreatedEvent:
    """Published when a task is created."""
    event_id: str
    task_id: str
    user_id: str
    description: str
    priority: str
    tags: list[str]
    due_date: Optional[str]
    due_time: Optional[str]
    recurrence: str
    is_completion_based: bool
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskUpdatedEvent:
    """Published when a task is updated."""
    event_id: str
    task_id: str
    user_id: str
    changed_fields: dict
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskCompletedEvent:
    """Published when a task is completed."""
    event_id: str
    task_id: str
    user_id: str
    completed_at: str
    had_recurrence: bool
    is_completion_based: bool
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskDeletedEvent:
    """Published when a task is deleted."""
    event_id: str
    task_id: str
    user_id: str
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskSyncEvent:
    """Published to task-updates topic for real-time sync."""
    event_id: str
    user_id: str
    action: str  # created, updated, completed, deleted
    task: Optional[dict]  # TaskResponse as dict, None for deleted
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)

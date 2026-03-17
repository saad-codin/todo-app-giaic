"""SQLModel database models for Todo App Backend."""

from datetime import datetime
from typing import Optional, Any
from sqlmodel import Field, SQLModel, JSON, Column
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""
    urgent = "urgent"
    high = "high"
    medium = "medium"
    low = "low"


class Recurrence(str, Enum):
    """Task recurrence options."""
    none = "none"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class MessageRole(str, Enum):
    """Chat message role types."""
    user = "user"
    assistant = "assistant"
    tool = "tool"


class ReminderStatus(str, Enum):
    """Reminder delivery status."""
    pending = "pending"
    sent = "sent"
    cancelled = "cancelled"


class ReminderType(str, Enum):
    """Reminder timing type."""
    twenty_four_hours = "24h"
    one_hour = "1h"


class RecurrenceRule(SQLModel, table=True):
    """Recurrence rule for repeating tasks."""
    __tablename__ = "recurrence_rule"

    id: str = Field(primary_key=True)
    task_id: str = Field(foreign_key="task.id", index=True)
    user_id: str = Field(foreign_key="user.id")
    frequency: str  # daily, weekly, monthly
    interval_value: int = Field(default=1)
    day_of_week: Optional[int] = None     # 0=Mon..6=Sun
    day_of_month: Optional[int] = None    # 1-28
    is_completion_based: bool = Field(default=False)
    next_occurrence: str                   # YYYY-MM-DD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskEvent(SQLModel, table=True):
    """Immutable task event log (audit stub)."""
    __tablename__ = "task_event"

    id: str = Field(primary_key=True)
    event_type: str
    task_id: str
    user_id: str
    payload: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Reminder(SQLModel, table=True):
    """Scheduled reminder for a task."""
    id: str = Field(primary_key=True)
    task_id: str = Field(foreign_key="task.id", index=True)
    user_id: str = Field(foreign_key="user.id")
    trigger_time: datetime
    reminder_type: ReminderType
    status: ReminderStatus = Field(default=ReminderStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserBase(SQLModel):
    """Base user model."""
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None


class User(UserBase, table=True):
    """User database model."""
    id: Optional[str] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    """User creation schema."""
    email: str
    password: str
    name: Optional[str] = None


class UserResponse(SQLModel):
    """User response schema (no password)."""
    id: str
    email: str
    name: Optional[str] = None
    createdAt: str


class TaskBase(SQLModel):
    """Base task model."""
    description: str = Field(min_length=1, max_length=500)
    completed: bool = Field(default=False)
    priority: Priority = Field(default=Priority.medium)
    tags: list[str] = Field(default=[], sa_column=Column(JSON))
    due_date: Optional[str] = Field(default=None)  # YYYY-MM-DD
    due_time: Optional[str] = Field(default=None)  # HH:MM
    reminder_time: Optional[str] = Field(default=None)  # ISO datetime
    recurrence: Recurrence = Field(default=Recurrence.none)


class Task(TaskBase, table=True):
    """Task database model."""
    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(SQLModel):
    """Task creation schema."""
    description: str
    priority: Optional[Priority] = Priority.medium
    tags: Optional[list[str]] = []
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    reminderTime: Optional[str] = None
    recurrence: Optional[Recurrence] = Recurrence.none
    recurrenceInterval: Optional[int] = None
    recurrenceDayOfWeek: Optional[int] = None
    recurrenceDayOfMonth: Optional[int] = None
    isCompletionBased: Optional[bool] = False


class TaskUpdate(SQLModel):
    """Task update schema (all fields optional)."""
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    tags: Optional[list[str]] = None
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    reminderTime: Optional[str] = None
    recurrence: Optional[Recurrence] = None
    recurrenceInterval: Optional[int] = None
    recurrenceDayOfWeek: Optional[int] = None
    recurrenceDayOfMonth: Optional[int] = None
    isCompletionBased: Optional[bool] = None


class TaskResponse(SQLModel):
    """Task response schema (camelCase for frontend)."""
    id: str
    userId: str
    description: str
    completed: bool
    priority: Priority
    tags: list[str]
    dueDate: Optional[str]
    dueTime: Optional[str]
    reminderTime: Optional[str]
    recurrence: Recurrence
    isCompletionBased: bool = False
    nextOccurrence: Optional[str] = None
    createdAt: str
    updatedAt: str

    @classmethod
    def from_task(cls, task: Task) -> "TaskResponse":
        """Convert Task model to TaskResponse."""
        return cls(
            id=task.id,
            userId=task.user_id,
            description=task.description,
            completed=task.completed,
            priority=task.priority,
            tags=task.tags or [],
            dueDate=task.due_date,
            dueTime=task.due_time,
            reminderTime=task.reminder_time,
            recurrence=task.recurrence,
            isCompletionBased=False,
            nextOccurrence=None,
            createdAt=task.created_at.isoformat() + "Z",
            updatedAt=task.updated_at.isoformat() + "Z",
        )


# Phase III: Conversation models for AI chatbot

class Conversation(SQLModel, table=True):
    """Conversation database model for chat sessions."""
    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(SQLModel, table=True):
    """Chat message database model."""
    id: Optional[str] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: MessageRole
    content: str
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tool_call_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(SQLModel):
    """Chat request schema."""
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatResponse(SQLModel):
    """Chat response schema."""
    response: str
    conversation_id: str
    tool_results: Optional[list[dict]] = None


class ConversationSummary(SQLModel):
    """Conversation summary for list view."""
    id: str
    title: Optional[str]
    created_at: str
    updated_at: str
    message_count: int


class ConversationListResponse(SQLModel):
    """Response for listing conversations."""
    conversations: list[ConversationSummary]
    total: int


class ChatMessageResponse(SQLModel):
    """Chat message response schema."""
    id: str
    role: MessageRole
    content: str
    tool_calls: Optional[dict] = None
    created_at: str


class ConversationDetailResponse(SQLModel):
    """Response for conversation detail with messages."""
    id: str
    title: Optional[str]
    messages: list[ChatMessageResponse]
    created_at: str
    updated_at: str

"""Recurrence operations for recurring todos."""

import calendar
from datetime import date, datetime, timedelta
from src.models.todo import Todo
from src.repository.todo_repository import TodoRepository


def calculate_next_occurrence(current_date: date, recurrence: str) -> date:
    """Calculate the next occurrence date based on recurrence pattern.

    Args:
        current_date: Current due date
        recurrence: Recurrence pattern ("daily", "weekly", or "monthly")

    Returns:
        Next occurrence date
    """
    if recurrence == "daily":
        return current_date + timedelta(days=1)
    elif recurrence == "weekly":
        return current_date + timedelta(days=7)
    elif recurrence == "monthly":
        # Handle month overflow (e.g., Jan 31 → Feb 28/29)
        year = current_date.year
        month = current_date.month + 1
        day = current_date.day

        # Roll over to next year if needed
        if month > 12:
            month = 1
            year += 1

        # Handle day overflow (e.g., Jan 31 → Feb 28)
        max_day = calendar.monthrange(year, month)[1]
        if day > max_day:
            day = max_day

        return date(year, month, day)
    else:
        raise ValueError(f"Invalid recurrence pattern: {recurrence}")


def calculate_next_reminder(
    current_reminder: datetime, next_due_date: date
) -> datetime:
    """Calculate next reminder time preserving time component.

    Args:
        current_reminder: Current reminder datetime
        next_due_date: Next occurrence due date

    Returns:
        Next reminder datetime with same time on next due date
    """
    return datetime(
        year=next_due_date.year,
        month=next_due_date.month,
        day=next_due_date.day,
        hour=current_reminder.hour,
        minute=current_reminder.minute,
        second=current_reminder.second,
    )


def create_next_occurrence(todo: Todo) -> Todo:
    """Create next occurrence of a recurring todo.

    Args:
        todo: Completed todo with recurrence pattern

    Returns:
        New Todo object for next occurrence (with new ID, incomplete status)
    """
    if todo.recurrence == "none" or todo.due_date is None:
        raise ValueError("Todo must have recurrence pattern and due date")

    # Calculate next due date
    next_due_date = calculate_next_occurrence(todo.due_date, todo.recurrence)

    # Calculate next reminder if current todo has one
    next_reminder = None
    if todo.reminder_time is not None:
        next_reminder = calculate_next_reminder(todo.reminder_time, next_due_date)

    # Create new todo with next occurrence dates and same metadata
    next_todo = Todo(
        id=0,  # Will be assigned by repository
        description=todo.description,
        completed=False,  # New occurrence starts incomplete
        priority=todo.priority,
        tags=todo.tags.copy(),  # Copy list to avoid shared reference
        due_date=next_due_date,
        reminder_time=next_reminder,
        recurrence=todo.recurrence,  # Preserve recurrence pattern
    )

    # Add to repository using add_existing helper
    repository = TodoRepository()
    return repository.add_existing(next_todo)

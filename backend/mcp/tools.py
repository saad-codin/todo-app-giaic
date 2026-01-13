"""MCP Tools for todo task operations.

These tools are used by the AI agent to perform task operations.
Each tool receives user_id from the request context (not from AI) for security.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select

from models import Task, Priority, Recurrence


def parse_natural_date(date_str: str) -> Optional[str]:
    """Parse natural language date to YYYY-MM-DD format."""
    if not date_str:
        return None

    date_str = date_str.lower().strip()
    today = datetime.now().date()

    if date_str == "today":
        return today.isoformat()
    elif date_str == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    elif date_str == "yesterday":
        return (today - timedelta(days=1)).isoformat()

    # Handle weekday names
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if date_str in weekdays:
        target_day = weekdays.index(date_str)
        current_day = today.weekday()
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).isoformat()

    # Try to parse as ISO date
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
        return parsed.isoformat()
    except ValueError:
        pass

    return None


def fuzzy_match_task(query: str, tasks: list[Task]) -> list[Task]:
    """Find tasks that match the query string (fuzzy matching)."""
    query_lower = query.lower().strip()

    # Exact match first
    exact_matches = [t for t in tasks if query_lower == t.description.lower()]
    if exact_matches:
        return exact_matches

    # Contains match
    contains_matches = [t for t in tasks if query_lower in t.description.lower()]
    if contains_matches:
        return contains_matches

    # Word overlap match
    query_words = set(query_lower.split())
    matches = []
    for task in tasks:
        task_words = set(task.description.lower().split())
        if query_words & task_words:  # Any word overlap
            matches.append(task)

    return matches


def create_task(
    session: Session,
    user_id: str,
    description: str,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    due_time: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Create a new task for the user.

    Args:
        session: Database session
        user_id: User ID from JWT (security: injected, not from AI)
        description: Task description (required)
        priority: Priority level (low, medium, high)
        due_date: Due date in YYYY-MM-DD format or natural language
        due_time: Due time in HH:MM format
        tags: List of tags

    Returns:
        dict with success status and task details
    """
    # Parse priority
    task_priority = Priority.medium
    if priority:
        priority_lower = priority.lower()
        if priority_lower in ["high", "h", "urgent", "important"]:
            task_priority = Priority.high
        elif priority_lower in ["low", "l"]:
            task_priority = Priority.low

    # Parse due date
    parsed_date = parse_natural_date(due_date) if due_date else None

    # Create task
    task = Task(
        id=str(uuid.uuid4()),
        user_id=user_id,
        description=description[:500],  # Truncate to max length
        priority=task_priority,
        due_date=parsed_date,
        due_time=due_time,
        tags=tags or [],
        recurrence=Recurrence.none,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return {
        "success": True,
        "task_id": task.id,
        "description": task.description,
        "priority": task.priority.value,
        "due_date": task.due_date,
        "message": f"Created task: {task.description}",
    }


def list_tasks(
    session: Session,
    user_id: str,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
) -> dict:
    """List tasks for the user with optional filters.

    Args:
        session: Database session
        user_id: User ID from JWT
        completed: Filter by completion status
        priority: Filter by priority
        due_date: Filter by due date (natural language supported)

    Returns:
        dict with task list
    """
    query = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority:
        priority_lower = priority.lower()
        if priority_lower in ["high", "h"]:
            query = query.where(Task.priority == Priority.high)
        elif priority_lower in ["medium", "m"]:
            query = query.where(Task.priority == Priority.medium)
        elif priority_lower in ["low", "l"]:
            query = query.where(Task.priority == Priority.low)

    if due_date:
        parsed_date = parse_natural_date(due_date)
        if parsed_date:
            query = query.where(Task.due_date == parsed_date)

    query = query.order_by(Task.created_at.desc())
    tasks = session.exec(query).all()

    # Format tasks for display
    task_list = []
    for task in tasks:
        status = "✓" if task.completed else "○"
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        p_emoji = priority_emoji.get(task.priority.value, "")
        due = f" (due: {task.due_date})" if task.due_date else ""
        task_list.append(f"{status} {p_emoji} {task.description}{due}")

    return {
        "success": True,
        "count": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "description": t.description,
                "completed": t.completed,
                "priority": t.priority.value,
                "due_date": t.due_date,
                "tags": t.tags,
            }
            for t in tasks
        ],
        "formatted": "\n".join(task_list) if task_list else "No tasks found.",
    }


def search_tasks(
    session: Session,
    user_id: str,
    query: str,
) -> dict:
    """Search tasks by description.

    Args:
        session: Database session
        user_id: User ID from JWT
        query: Search query string

    Returns:
        dict with matching tasks
    """
    all_tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    matches = fuzzy_match_task(query, all_tasks)

    return {
        "success": True,
        "count": len(matches),
        "tasks": [
            {
                "id": t.id,
                "description": t.description,
                "completed": t.completed,
                "priority": t.priority.value,
                "due_date": t.due_date,
            }
            for t in matches
        ],
    }


def complete_task(
    session: Session,
    user_id: str,
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
) -> dict:
    """Mark a task as complete.

    Args:
        session: Database session
        user_id: User ID from JWT
        task_id: Direct task ID (if known)
        description_match: Task description to match (fuzzy)

    Returns:
        dict with success status
    """
    task = None

    if task_id:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
    elif description_match:
        all_tasks = session.exec(
            select(Task).where(Task.user_id == user_id, Task.completed == False)
        ).all()
        matches = fuzzy_match_task(description_match, all_tasks)

        if len(matches) == 0:
            return {
                "success": False,
                "error": f"No task found matching '{description_match}'",
                "suggestion": "Would you like to see your current tasks?",
            }
        elif len(matches) > 1:
            return {
                "success": False,
                "error": "Multiple tasks match that description",
                "matches": [{"id": t.id, "description": t.description} for t in matches],
                "suggestion": "Please be more specific or use the task ID.",
            }
        task = matches[0]

    if not task:
        return {
            "success": False,
            "error": "Task not found",
        }

    task.completed = True
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

    return {
        "success": True,
        "task_id": task.id,
        "description": task.description,
        "message": f"Marked '{task.description}' as complete!",
    }


def update_task(
    session: Session,
    user_id: str,
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
    new_description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Update a task's attributes.

    Args:
        session: Database session
        user_id: User ID from JWT
        task_id: Direct task ID (if known)
        description_match: Task description to match (fuzzy)
        new_description: New task description
        priority: New priority level
        due_date: New due date
        tags: New tags list

    Returns:
        dict with success status
    """
    task = None

    if task_id:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
    elif description_match:
        all_tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()
        matches = fuzzy_match_task(description_match, all_tasks)

        if len(matches) == 0:
            return {
                "success": False,
                "error": f"No task found matching '{description_match}'",
            }
        elif len(matches) > 1:
            return {
                "success": False,
                "error": "Multiple tasks match that description",
                "matches": [{"id": t.id, "description": t.description} for t in matches],
            }
        task = matches[0]

    if not task:
        return {
            "success": False,
            "error": "Task not found",
        }

    changes = []

    if new_description:
        task.description = new_description[:500]
        changes.append(f"description to '{new_description}'")

    if priority:
        priority_lower = priority.lower()
        if priority_lower in ["high", "h", "urgent"]:
            task.priority = Priority.high
            changes.append("priority to high")
        elif priority_lower in ["medium", "m"]:
            task.priority = Priority.medium
            changes.append("priority to medium")
        elif priority_lower in ["low", "l"]:
            task.priority = Priority.low
            changes.append("priority to low")

    if due_date:
        parsed_date = parse_natural_date(due_date)
        if parsed_date:
            task.due_date = parsed_date
            changes.append(f"due date to {parsed_date}")

    if tags is not None:
        task.tags = tags
        changes.append(f"tags to {tags}")

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

    return {
        "success": True,
        "task_id": task.id,
        "description": task.description,
        "changes": changes,
        "message": f"Updated '{task.description}': {', '.join(changes)}" if changes else "No changes made",
    }


def delete_task(
    session: Session,
    user_id: str,
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
) -> dict:
    """Delete a task.

    Args:
        session: Database session
        user_id: User ID from JWT
        task_id: Direct task ID (if known)
        description_match: Task description to match (fuzzy)

    Returns:
        dict with success status
    """
    task = None

    if task_id:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
    elif description_match:
        all_tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()
        matches = fuzzy_match_task(description_match, all_tasks)

        if len(matches) == 0:
            return {
                "success": False,
                "error": f"No task found matching '{description_match}'",
                "suggestion": "Would you like to see your current tasks?",
            }
        elif len(matches) > 1:
            return {
                "success": False,
                "error": "Multiple tasks match that description",
                "matches": [{"id": t.id, "description": t.description} for t in matches],
            }
        task = matches[0]

    if not task:
        return {
            "success": False,
            "error": "Task not found",
        }

    description = task.description
    session.delete(task)
    session.commit()

    return {
        "success": True,
        "deleted_description": description,
        "message": f"Deleted task: {description}",
    }

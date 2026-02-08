"""Standalone MCP server for todo task management.

Runs as a subprocess via stdio transport, connected by MCPServerStdio
from the OpenAI Agents SDK in the FastAPI host process.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, SQLModel, create_engine, select

# Ensure backend directory is on the path for model imports
sys.path.insert(0, os.path.dirname(__file__))

from models import Task, Priority, Recurrence

load_dotenv()

# --- Own DB engine (separate subprocess, can't share FastAPI's) ---

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

pool_args = {}
if "neon" in DATABASE_URL or "postgresql" in DATABASE_URL:
    pool_args = {"pool_pre_ping": True}

_engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args, **pool_args)

# --- Helpers ---


def _get_session() -> Session:
    return Session(_engine)


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

    weekdays = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    ]
    if date_str in weekdays:
        target_day = weekdays.index(date_str)
        current_day = today.weekday()
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).isoformat()

    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
        return parsed.isoformat()
    except ValueError:
        pass

    return None


def fuzzy_match_task(query: str, tasks: list[Task]) -> list[Task]:
    """Find tasks that match the query string."""
    query_lower = query.lower().strip()

    exact_matches = [t for t in tasks if query_lower == t.description.lower()]
    if exact_matches:
        return exact_matches

    contains_matches = [t for t in tasks if query_lower in t.description.lower()]
    if contains_matches:
        return contains_matches

    query_words = set(query_lower.split())
    matches = []
    for task in tasks:
        task_words = set(task.description.lower().split())
        if query_words & task_words:
            matches.append(task)

    return matches


def _resolve_priority(priority: Optional[str]) -> Priority:
    """Resolve a priority string to a Priority enum value."""
    if not priority:
        return Priority.medium
    p = priority.lower()
    if p in ("high", "h", "urgent", "important"):
        return Priority.high
    if p in ("low", "l"):
        return Priority.low
    return Priority.medium


# --- MCP Server ---

mcp = FastMCP("TodoMCP")


@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Create a new task for the user.

    Args:
        user_id: The ID of the user who owns the task.
        title: Short title / description of the task.
        description: Longer description (unused currently, title is primary).
        priority: Priority level - high, medium, or low.
        due_date: Due date (today, tomorrow, weekday name, or YYYY-MM-DD).
        tags: List of tags for the task.
    """
    session = _get_session()
    try:
        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            description=title[:500],
            priority=_resolve_priority(priority),
            due_date=parse_natural_date(due_date) if due_date else None,
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
    finally:
        session.close()


@mcp.tool()
def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search_query: Optional[str] = None,
) -> dict:
    """List the user's tasks with optional filters.

    Args:
        user_id: The ID of the user who owns the tasks.
        status: Filter by status - 'completed' or 'pending'.
        priority: Filter by priority - high, medium, or low.
        search_query: Search text to match against task descriptions.
    """
    session = _get_session()
    try:
        query = select(Task).where(Task.user_id == user_id)

        if status == "completed":
            query = query.where(Task.completed == True)
        elif status == "pending":
            query = query.where(Task.completed == False)

        if priority:
            p = _resolve_priority(priority)
            query = query.where(Task.priority == p)

        query = query.order_by(Task.created_at.desc())
        tasks = list(session.exec(query).all())

        if search_query:
            tasks = fuzzy_match_task(search_query, tasks)

        task_list = []
        for task in tasks:
            s = "completed" if task.completed else "pending"
            due = f" (due: {task.due_date})" if task.due_date else ""
            task_list.append(f"[{s}] [{task.priority.value}] {task.description}{due}")

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
    finally:
        session.close()


@mcp.tool()
def complete_task(
    user_id: str,
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
) -> dict:
    """Mark a task as complete.

    Args:
        user_id: The ID of the user who owns the task.
        task_id: The ID of the task to complete.
        description_match: Text to fuzzy-match against task descriptions.
    """
    session = _get_session()
    try:
        task = None

        if task_id:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
        elif description_match:
            all_tasks = list(session.exec(
                select(Task).where(Task.user_id == user_id, Task.completed == False)
            ).all())
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
            return {"success": False, "error": "Task not found"}

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
    finally:
        session.close()


@mcp.tool()
def update_task(
    user_id: str,
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Update a task's details.

    Args:
        user_id: The ID of the user who owns the task.
        task_id: The ID of the task to update.
        description_match: Text to fuzzy-match against task descriptions.
        title: New title/description for the task.
        description: Alternative new description for the task.
        priority: New priority - high, medium, or low.
        due_date: New due date (today, tomorrow, weekday name, or YYYY-MM-DD).
        tags: New list of tags.
    """
    session = _get_session()
    try:
        task = None

        if task_id:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
        elif description_match:
            all_tasks = list(session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all())
            matches = fuzzy_match_task(description_match, all_tasks)

            if len(matches) == 0:
                return {"success": False, "error": f"No task found matching '{description_match}'"}
            elif len(matches) > 1:
                return {
                    "success": False,
                    "error": "Multiple tasks match that description",
                    "matches": [{"id": t.id, "description": t.description} for t in matches],
                }
            task = matches[0]

        if not task:
            return {"success": False, "error": "Task not found"}

        changes = []
        new_desc = title or description
        if new_desc:
            task.description = new_desc[:500]
            changes.append(f"description to '{new_desc}'")

        if priority:
            task.priority = _resolve_priority(priority)
            changes.append(f"priority to {task.priority.value}")

        if due_date:
            parsed = parse_natural_date(due_date)
            if parsed:
                task.due_date = parsed
                changes.append(f"due date to {parsed}")

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
    finally:
        session.close()


@mcp.tool()
def delete_task(
    user_id: str,
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
) -> dict:
    """Delete a task.

    Args:
        user_id: The ID of the user who owns the task.
        task_id: The ID of the task to delete.
        description_match: Text to fuzzy-match against task descriptions.
    """
    session = _get_session()
    try:
        task = None

        if task_id:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
        elif description_match:
            all_tasks = list(session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all())
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
            return {"success": False, "error": "Task not found"}

        desc = task.description
        session.delete(task)
        session.commit()

        return {
            "success": True,
            "deleted_description": desc,
            "message": f"Deleted task: {desc}",
        }
    finally:
        session.close()


if __name__ == "__main__":
    mcp.run()

"""ChatKit Agent with MCP tools for todo task management."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select

from agents import Agent, function_tool

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

    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
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


@dataclass
class TodoContext:
    """Context for todo agent operations."""
    user_id: str
    session: Session


# Global context holder for tools (set per-request)
_current_context: Optional[TodoContext] = None


def set_context(ctx: TodoContext):
    """Set the current context for tool operations."""
    global _current_context
    _current_context = ctx


def get_context() -> TodoContext:
    """Get the current context for tool operations."""
    if _current_context is None:
        raise RuntimeError("No context set for tool operations")
    return _current_context


# Define MCP tools using the agents SDK function_tool decorator

@function_tool
def create_task(
    description: str,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    due_time: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Create a new task for the user. Use when user wants to add, create, or make a new task.

    Args:
        description: The task description
        priority: Priority level (high, medium, low)
        due_date: Due date (today, tomorrow, weekday name, or YYYY-MM-DD)
        due_time: Due time in HH:MM format
        tags: List of tags for the task
    """
    import uuid
    ctx = get_context()

    task_priority = Priority.medium
    if priority:
        priority_lower = priority.lower()
        if priority_lower in ["high", "h", "urgent", "important"]:
            task_priority = Priority.high
        elif priority_lower in ["low", "l"]:
            task_priority = Priority.low

    parsed_date = parse_natural_date(due_date) if due_date else None

    task = Task(
        id=str(uuid.uuid4()),
        user_id=ctx.user_id,
        description=description[:500],
        priority=task_priority,
        due_date=parsed_date,
        due_time=due_time,
        tags=tags or [],
        recurrence=Recurrence.none,
    )

    ctx.session.add(task)
    ctx.session.commit()
    ctx.session.refresh(task)

    return {
        "success": True,
        "task_id": task.id,
        "description": task.description,
        "priority": task.priority.value,
        "due_date": task.due_date,
        "message": f"Created task: {task.description}",
    }


@function_tool
def list_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
) -> dict:
    """List the user's tasks. Use when user wants to see, view, or show their tasks.

    Args:
        completed: Filter by completion status (True/False)
        priority: Filter by priority (high, medium, low)
        due_date: Filter by due date
    """
    ctx = get_context()
    query = select(Task).where(Task.user_id == ctx.user_id)

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
    tasks = ctx.session.exec(query).all()

    task_list = []
    for task in tasks:
        status = "completed" if task.completed else "pending"
        priority_label = task.priority.value
        due = f" (due: {task.due_date})" if task.due_date else ""
        task_list.append(f"[{status}] [{priority_label}] {task.description}{due}")

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


@function_tool
def search_tasks(query: str) -> dict:
    """Search for tasks by description. Use when user is looking for a specific task.

    Args:
        query: Search query to match against task descriptions
    """
    ctx = get_context()
    all_tasks = ctx.session.exec(
        select(Task).where(Task.user_id == ctx.user_id)
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


@function_tool
def complete_task(
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
) -> dict:
    """Mark a task as complete. Use when user wants to mark, complete, finish, or check off a task.

    Args:
        task_id: The ID of the task to complete
        description_match: Text to match against task description
    """
    ctx = get_context()
    task = None

    if task_id:
        task = ctx.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == ctx.user_id)
        ).first()
    elif description_match:
        all_tasks = ctx.session.exec(
            select(Task).where(Task.user_id == ctx.user_id, Task.completed == False)
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
        return {"success": False, "error": "Task not found"}

    task.completed = True
    task.updated_at = datetime.utcnow()
    ctx.session.add(task)
    ctx.session.commit()

    return {
        "success": True,
        "task_id": task.id,
        "description": task.description,
        "message": f"Marked '{task.description}' as complete!",
    }


@function_tool
def update_task(
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
    new_description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Update a task's details. Use when user wants to change, modify, edit, or update a task.

    Args:
        task_id: The ID of the task to update
        description_match: Text to match against task description
        new_description: New description for the task
        priority: New priority (high, medium, low)
        due_date: New due date
        tags: New list of tags
    """
    ctx = get_context()
    task = None

    if task_id:
        task = ctx.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == ctx.user_id)
        ).first()
    elif description_match:
        all_tasks = ctx.session.exec(
            select(Task).where(Task.user_id == ctx.user_id)
        ).all()
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
    ctx.session.add(task)
    ctx.session.commit()

    return {
        "success": True,
        "task_id": task.id,
        "description": task.description,
        "changes": changes,
        "message": f"Updated '{task.description}': {', '.join(changes)}" if changes else "No changes made",
    }


@function_tool
def delete_task(
    task_id: Optional[str] = None,
    description_match: Optional[str] = None,
) -> dict:
    """Delete a task. Use when user wants to remove, delete, or discard a task.

    Args:
        task_id: The ID of the task to delete
        description_match: Text to match against task description
    """
    ctx = get_context()
    task = None

    if task_id:
        task = ctx.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == ctx.user_id)
        ).first()
    elif description_match:
        all_tasks = ctx.session.exec(
            select(Task).where(Task.user_id == ctx.user_id)
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
        return {"success": False, "error": "Task not found"}

    description = task.description
    ctx.session.delete(task)
    ctx.session.commit()

    return {
        "success": True,
        "deleted_description": description,
        "message": f"Deleted task: {description}",
    }


# Create the todo assistant agent with MCP tools
todo_assistant = Agent(
    name="TodoAssistant",
    instructions="""You are a helpful todo task assistant. Your job is to help users manage their tasks through natural conversation.

You can:
- Create new tasks (with optional priority, due date, time, and tags)
- List and view tasks (with optional filters)
- Search for specific tasks
- Mark tasks as complete
- Update task details (description, priority, due date, tags)
- Delete tasks

Guidelines:
1. Be friendly and conversational
2. Confirm actions clearly (e.g., "I've added 'buy groceries' to your list")
3. When listing tasks, format them nicely and ask if the user wants to take action
4. When a task isn't found, offer to show the task list or suggest alternatives
5. For ambiguous references like "it" or "that one", use context from the conversation
6. If the user's message isn't about tasks, politely redirect them

Remember to use natural language dates when possible (today, tomorrow, Friday).""",
    model="gpt-4o-mini",
    tools=[create_task, list_tasks, search_tasks, complete_task, update_task, delete_task],
)

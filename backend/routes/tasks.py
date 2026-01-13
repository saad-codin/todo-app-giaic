"""Task CRUD routes."""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from pydantic import BaseModel

from db import get_session
from models import Task, TaskCreate, TaskUpdate, TaskResponse, Priority, Recurrence
from auth import get_current_user, User

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskListResponse(BaseModel):
    """Task list response."""
    tasks: list[TaskResponse]
    total: int
    hasMore: bool


class SingleTaskResponse(BaseModel):
    """Single task response."""
    task: TaskResponse


class CompleteTaskResponse(BaseModel):
    """Complete task response."""
    task: TaskResponse
    nextOccurrence: Optional[TaskResponse] = None


class SuccessResponse(BaseModel):
    """Success response."""
    success: bool


def calculate_next_due_date(due_date: str, recurrence: Recurrence) -> str:
    """Calculate the next due date based on recurrence."""
    from datetime import datetime

    date = datetime.strptime(due_date, "%Y-%m-%d")

    if recurrence == Recurrence.daily:
        next_date = date + timedelta(days=1)
    elif recurrence == Recurrence.weekly:
        next_date = date + timedelta(weeks=1)
    elif recurrence == Recurrence.monthly:
        # Add one month (handle edge cases)
        month = date.month + 1
        year = date.year
        if month > 12:
            month = 1
            year += 1
        day = min(date.day, 28)  # Safe day for all months
        next_date = date.replace(year=year, month=month, day=day)
    else:
        return due_date

    return next_date.strftime("%Y-%m-%d")


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    search: Optional[str] = Query(None),
    completed: Optional[bool] = Query(None),
    priority: Optional[Priority] = Query(None),
    tag: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    sortBy: Optional[str] = Query(None),
    sortOrder: Optional[str] = Query("asc"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List tasks for authenticated user with filtering and sorting."""
    # Base query
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply filters
    if search:
        query = query.where(Task.description.contains(search))

    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority:
        query = query.where(Task.priority == priority)

    # Tag filtering requires checking JSON array
    # Note: SQLite JSON support varies, this is a simplified approach

    if startDate:
        query = query.where(Task.due_date >= startDate)

    if endDate:
        query = query.where(Task.due_date <= endDate)

    # Apply sorting
    if sortBy == "dueDate":
        if sortOrder == "desc":
            query = query.order_by(Task.due_date.desc())
        else:
            query = query.order_by(Task.due_date.asc())
    elif sortBy == "priority":
        # Custom priority order: high > medium > low
        if sortOrder == "desc":
            query = query.order_by(Task.priority.desc())
        else:
            query = query.order_by(Task.priority.asc())
    elif sortBy == "createdAt":
        if sortOrder == "desc":
            query = query.order_by(Task.created_at.desc())
        else:
            query = query.order_by(Task.created_at.asc())
    else:
        # Default: newest first
        query = query.order_by(Task.created_at.desc())

    # Get total count (without pagination)
    count_query = select(Task).where(Task.user_id == current_user.id)
    if search:
        count_query = count_query.where(Task.description.contains(search))
    if completed is not None:
        count_query = count_query.where(Task.completed == completed)
    if priority:
        count_query = count_query.where(Task.priority == priority)
    if startDate:
        count_query = count_query.where(Task.due_date >= startDate)
    if endDate:
        count_query = count_query.where(Task.due_date <= endDate)

    all_tasks = session.exec(count_query).all()
    total = len(all_tasks)

    # Apply pagination
    query = query.offset(offset).limit(limit)
    tasks = session.exec(query).all()

    # Filter by tag in Python (JSON array handling)
    if tag:
        tasks = [t for t in tasks if tag in (t.tags or [])]
        # Recalculate total with tag filter
        all_tasks_with_tag = [t for t in all_tasks if tag in (t.tags or [])]
        total = len(all_tasks_with_tag)

    has_more = offset + len(tasks) < total

    return TaskListResponse(
        tasks=[TaskResponse.from_task(t) for t in tasks],
        total=total,
        hasMore=has_more,
    )


@router.post("", response_model=SingleTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task."""
    # Validate description
    if not request.description or len(request.description.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Description is required",
                "details": {"field": "description", "constraint": "required"},
            },
        )

    task = Task(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        description=request.description.strip(),
        priority=request.priority or Priority.medium,
        tags=request.tags or [],
        due_date=request.dueDate,
        due_time=request.dueTime,
        reminder_time=request.reminderTime,
        recurrence=request.recurrence or Recurrence.none,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return SingleTaskResponse(task=TaskResponse.from_task(task))


@router.get("/{task_id}", response_model=SingleTaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a single task by ID."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Task not found"},
        )

    return SingleTaskResponse(task=TaskResponse.from_task(task))


@router.patch("/{task_id}", response_model=SingleTaskResponse)
async def update_task(
    task_id: str,
    request: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a task."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Task not found"},
        )

    # Update fields if provided
    if request.description is not None:
        if len(request.description.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Description cannot be empty",
                    "details": {"field": "description", "constraint": "required"},
                },
            )
        task.description = request.description.strip()

    if request.completed is not None:
        task.completed = request.completed

    if request.priority is not None:
        task.priority = request.priority

    if request.tags is not None:
        task.tags = request.tags

    if request.dueDate is not None:
        task.due_date = request.dueDate if request.dueDate else None

    if request.dueTime is not None:
        task.due_time = request.dueTime if request.dueTime else None

    if request.reminderTime is not None:
        task.reminder_time = request.reminderTime if request.reminderTime else None

    if request.recurrence is not None:
        task.recurrence = request.recurrence

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return SingleTaskResponse(task=TaskResponse.from_task(task))


@router.delete("/{task_id}", response_model=SuccessResponse)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a task."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Task not found"},
        )

    session.delete(task)
    session.commit()

    return SuccessResponse(success=True)


@router.post("/{task_id}/complete", response_model=CompleteTaskResponse)
async def complete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Mark task complete and handle recurring tasks."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Task not found"},
        )

    task.completed = True
    task.updated_at = datetime.utcnow()

    next_occurrence = None

    # Create next occurrence for recurring tasks
    if task.recurrence != Recurrence.none and task.due_date:
        next_due_date = calculate_next_due_date(task.due_date, task.recurrence)

        next_task = Task(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            description=task.description,
            completed=False,
            priority=task.priority,
            tags=task.tags,
            due_date=next_due_date,
            due_time=task.due_time,
            reminder_time=task.reminder_time,
            recurrence=task.recurrence,
        )

        session.add(next_task)
        next_occurrence = next_task

    session.add(task)
    session.commit()
    session.refresh(task)

    if next_occurrence:
        session.refresh(next_occurrence)

    return CompleteTaskResponse(
        task=TaskResponse.from_task(task),
        nextOccurrence=TaskResponse.from_task(next_occurrence) if next_occurrence else None,
    )


@router.post("/{task_id}/incomplete", response_model=SingleTaskResponse)
async def incomplete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Mark task incomplete."""
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Task not found"},
        )

    task.completed = False
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return SingleTaskResponse(task=TaskResponse.from_task(task))

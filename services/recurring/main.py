"""
Recurring Task Service - Dapr-enabled microservice for managing recurring tasks.

Responsibilities:
- Process task events from Dapr pubsub
- Manage recurrence rules in database
- Generate recurring task instances
- Handle completion-based and time-based recurrence
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

import requests
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, SQLModel

# Configure logging (JSON format in cloud, human-readable locally)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        import json as _json
        return _json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "recurring-service",
            "logger": record.name,
            "message": record.getMessage(),
        })

_handler = logging.StreamHandler()
if os.getenv("LOG_FORMAT") == "json":
    _handler.setFormatter(JsonFormatter())
else:
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_handler])
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/todos")
# Ensure asyncpg driver prefix for SQLAlchemy async engine
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
# asyncpg doesn't support sslmode as a URL query param; strip it and use connect_args
_connect_args = {}
if "sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")
    _connect_args = {"ssl": True}
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=_connect_args)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_STATE_STORE = os.getenv("DAPR_STATE_STORE", "statestore")

# Background task control
background_task = None
shutdown_event = asyncio.Event()


# Database Models
class RecurrenceRule(SQLModel, table=True):
    """Recurrence rule for recurring tasks."""
    __tablename__ = "recurrence_rule"

    id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    user_id: str
    frequency: str  # daily, weekly, monthly
    interval_value: int = Field(default=1)
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None
    is_completion_based: bool = Field(default=False)
    next_occurrence: str  # YYYY-MM-DD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Pydantic Models
class CloudEvent(BaseModel):
    """CloudEvent schema for Dapr pubsub."""
    specversion: str
    type: str
    source: str
    id: str
    time: str
    datacontenttype: str
    data: dict


class EventResponse(BaseModel):
    """Response for event processing."""
    status: str  # SUCCESS, RETRY, DROP


# Utility Functions
def calculate_next_occurrence(
    frequency: str,
    interval_value: int,
    day_of_week: Optional[int],
    day_of_month: Optional[int],
    from_date: Optional[datetime] = None
) -> str:
    """Calculate next occurrence date based on recurrence rule.

    Args:
        frequency: daily, weekly, or monthly
        interval_value: Number of intervals (e.g., 2 for every 2 days)
        day_of_week: Day of week for weekly (0=Monday, 6=Sunday)
        day_of_month: Day of month for monthly (clamped to 28)
        from_date: Starting date (defaults to today)

    Returns:
        Next occurrence date in YYYY-MM-DD format
    """
    base_date = from_date or datetime.utcnow()

    if frequency == "daily":
        next_date = base_date + timedelta(days=interval_value)

    elif frequency == "weekly":
        # Add interval weeks
        next_date = base_date + timedelta(weeks=interval_value)

        # If day_of_week is specified, anchor to that day
        if day_of_week is not None:
            current_weekday = next_date.weekday()
            days_ahead = (day_of_week - current_weekday) % 7
            if days_ahead == 0 and next_date <= base_date:
                days_ahead = 7
            next_date = next_date + timedelta(days=days_ahead)

    elif frequency == "monthly":
        # Add interval months
        month = base_date.month + interval_value
        year = base_date.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1

        # Clamp day to 28 to avoid month-end issues
        day = min(day_of_month or base_date.day, 28)

        next_date = base_date.replace(year=year, month=month, day=day)

        # If we're still on or before the base date, add another month
        if next_date <= base_date:
            month = month + 1
            year = year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            next_date = next_date.replace(year=year, month=month)

    else:
        # Default to 1 day if unknown frequency
        next_date = base_date + timedelta(days=1)

    return next_date.strftime("%Y-%m-%d")


async def check_dedup(event_id: str) -> bool:
    """Check if event has already been processed using Dapr state store.

    Args:
        event_id: Unique event identifier

    Returns:
        True if event was already processed, False otherwise
    """
    try:
        key = f"dedup:recurring:{event_id}"
        url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}/{key}"

        response = requests.get(url, timeout=5)

        if response.status_code == 200 and response.text:
            logger.info(f"Event {event_id} already processed (dedup)")
            return True

        # Mark as processed
        requests.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}",
            json=[{"key": key, "value": {"processed_at": datetime.utcnow().isoformat()}}],
            timeout=5
        )

        return False

    except Exception as e:
        logger.warning(f"Dedup check failed for {event_id}: {e}")
        # On error, assume not processed to avoid dropping events
        return False


def create_task_via_dapr(
    user_id: str,
    description: str,
    priority: str,
    tags: list,
    due_date: Optional[str],
    due_time: Optional[str],
    recurrence: str
) -> Optional[dict]:
    """Create task via Dapr service invocation to backend.

    Args:
        user_id: User ID for the task
        description: Task description
        priority: Task priority (low, medium, high)
        tags: List of tags
        due_date: Due date in YYYY-MM-DD format
        due_time: Due time in HH:MM format
        recurrence: Recurrence pattern

    Returns:
        Created task data or None on failure
    """
    try:
        url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke/backend/method/api/tasks"

        # Note: This bypasses auth - for service-to-service calls
        # In production, use service-level auth or pass through user token
        response = requests.post(
            url,
            json={
                "description": description,
                "priority": priority,
                "tags": tags,
                "dueDate": due_date,
                "dueTime": due_time,
                "recurrence": recurrence,
            },
            headers={
                "Content-Type": "application/json",
                "X-User-ID": user_id,  # Pass user context
            },
            timeout=10
        )

        if response.ok:
            logger.info(f"Created recurring task instance for user {user_id}")
            return response.json()
        else:
            logger.error(f"Failed to create task: {response.status_code} {response.text}")
            return None

    except Exception as e:
        logger.warning(f"Failed to create task via Dapr: {e}")
        return None


def publish_task_sync_event(task_data: dict):
    """Publish task.sync event to task-updates topic via Dapr.

    Args:
        task_data: Task data to include in event
    """
    try:
        url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/taskpubsub/task-updates"

        event_data = {
            "event_type": "task.sync",
            "event_id": f"sync_{task_data.get('id')}_{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": task_data.get("userId"),
            "task": task_data
        }

        requests.post(url, json=event_data, timeout=5)
        logger.info(f"Published task.sync event for task {task_data.get('id')}")

    except Exception as e:
        logger.warning(f"Failed to publish task.sync event: {e}")


async def process_task_created(data: dict, session: AsyncSession):
    """Process task.created event.

    Creates a RecurrenceRule if task has recurrence != 'none'.

    Args:
        data: Event data (flat structure from backend publisher)
        session: Database session
    """
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    recurrence = data.get("recurrence", "none")

    if recurrence == "none":
        logger.info(f"Task {task_id} has no recurrence, skipping")
        return

    frequency = recurrence  # daily, weekly, monthly
    interval_value = 1
    is_completion_based = data.get("is_completion_based", False)

    # Calculate next occurrence
    due_date_str = data.get("due_date")
    from_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else datetime.utcnow()

    next_occurrence = calculate_next_occurrence(
        frequency=frequency,
        interval_value=interval_value,
        day_of_week=None,
        day_of_month=None,
        from_date=from_date
    )

    import uuid as _uuid
    rule = RecurrenceRule(
        id=str(_uuid.uuid4()),
        task_id=task_id,
        user_id=user_id,
        frequency=frequency,
        interval_value=interval_value,
        day_of_week=None,
        day_of_month=None,
        is_completion_based=is_completion_based,
        next_occurrence=next_occurrence
    )

    session.add(rule)
    await session.commit()

    logger.info(f"Created recurrence rule for task {task_id}: {frequency} every {interval_value}, next: {next_occurrence}")


async def process_task_completed(data: dict, session: AsyncSession):
    """Process task.completed event.

    For completion-based recurrence, creates a new task instance.

    Args:
        data: Event data (flat structure from backend publisher)
        session: Database session
    """
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    completed_at_str = data.get("completed_at")

    # Find recurrence rule
    result = await session.execute(
        select(RecurrenceRule).where(RecurrenceRule.task_id == task_id)
    )
    rule = result.scalar_one_or_none()

    if not rule:
        logger.info(f"No recurrence rule found for task {task_id}")
        return

    if not rule.is_completion_based:
        logger.info(f"Task {task_id} is not completion-based, skipping")
        return

    # Calculate next occurrence from completion time
    completed_at = datetime.fromisoformat(completed_at_str) if completed_at_str else datetime.utcnow()

    next_due_date = calculate_next_occurrence(
        frequency=rule.frequency,
        interval_value=rule.interval_value,
        day_of_week=rule.day_of_week,
        day_of_month=rule.day_of_month,
        from_date=completed_at
    )

    # Create new task instance (we don't have full task details, use minimal data)
    new_task = create_task_via_dapr(
        user_id=user_id,
        description=f"Recurring task",
        priority="medium",
        tags=[],
        due_date=next_due_date,
        due_time=None,
        recurrence=rule.frequency
    )

    if new_task:
        task_data = new_task.get("task", new_task)
        new_task_id = task_data.get("id")
        if new_task_id:
            rule.task_id = new_task_id
        rule.next_occurrence = next_due_date
        rule.updated_at = datetime.utcnow()
        await session.commit()

        publish_task_sync_event(task_data)

        logger.info(f"Created completion-based recurring task for user {user_id}")


async def process_task_deleted(data: dict, session: AsyncSession):
    """Process task.deleted event.

    Removes the RecurrenceRule for the deleted task.

    Args:
        data: Event data
        session: Database session
    """
    task_id = data.get("task_id")

    result = await session.execute(
        select(RecurrenceRule).where(RecurrenceRule.task_id == task_id)
    )
    rule = result.scalar_one_or_none()

    if rule:
        await session.delete(rule)
        await session.commit()
        logger.info(f"Deleted recurrence rule for task {task_id}")


async def poll_time_based_recurrence():
    """Background task to poll for time-based recurring tasks.

    Runs every 60 seconds, checking for RecurrenceRules where:
    - next_occurrence <= today
    - is_completion_based = false

    Creates new task instances and advances next_occurrence.
    """
    logger.info("Starting time-based recurrence polling loop")

    while not shutdown_event.is_set():
        try:
            async with async_session_maker() as session:
                today = datetime.utcnow().strftime("%Y-%m-%d")

                # Find rules ready for next occurrence
                result = await session.execute(
                    select(RecurrenceRule).where(
                        RecurrenceRule.next_occurrence <= today,
                        RecurrenceRule.is_completion_based == False
                    )
                )
                rules = result.scalars().all()

                logger.info(f"Found {len(rules)} time-based recurrence rules ready for processing")

                for rule in rules:
                    try:
                        # Create new task instance
                        # Note: We need to fetch original task details
                        # For now, use minimal data (extend with task template storage)
                        new_task = create_task_via_dapr(
                            user_id=rule.user_id,
                            description=f"Recurring task (rule {rule.id})",
                            priority="medium",
                            tags=[],
                            due_date=rule.next_occurrence,
                            due_time=None,
                            recurrence=f"{rule.frequency}:{rule.interval_value}"
                        )

                        if new_task:
                            # Advance next occurrence
                            next_date = calculate_next_occurrence(
                                frequency=rule.frequency,
                                interval_value=rule.interval_value,
                                day_of_week=rule.day_of_week,
                                day_of_month=rule.day_of_month,
                                from_date=datetime.fromisoformat(rule.next_occurrence)
                            )

                            rule.next_occurrence = next_date
                            rule.updated_at = datetime.utcnow()
                            await session.commit()

                            # Publish sync event
                            publish_task_sync_event(new_task)

                            logger.info(f"Created time-based recurring task for rule {rule.id}, next: {next_date}")

                    except Exception as e:
                        logger.error(f"Failed to process recurrence rule {rule.id}: {e}")
                        await session.rollback()

        except Exception as e:
            logger.error(f"Error in polling loop: {e}")

        # Wait 60 seconds or until shutdown
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=60.0)
            break
        except asyncio.TimeoutError:
            continue

    logger.info("Stopped time-based recurrence polling loop")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for background tasks."""
    global background_task

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Start background polling task
    background_task = asyncio.create_task(poll_time_based_recurrence())

    logger.info("Recurring service started")

    yield

    # Shutdown
    logger.info("Shutting down recurring service")
    shutdown_event.set()

    if background_task:
        await background_task

    await engine.dispose()


# FastAPI Application
app = FastAPI(
    title="Recurring Task Service",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "recurring-service",
        "dapr": True
    }


@app.post("/events/task")
async def handle_task_event(request: Request):
    """Handle task events from Dapr pubsub (CloudEvents envelope).

    Processes:
    - task.created: Create recurrence rule if task has recurrence
    - task.completed: Generate next instance for completion-based recurrence
    - task.deleted: Remove recurrence rule
    """
    try:
        body = await request.json()
        event_type = body.get("type", "")
        data = body.get("data", {})
        event_id = data.get("event_id")

        logger.info(f"Received event: {event_type} (id: {event_id})")

        if not event_id:
            return EventResponse(status="DROP")

        # Check for duplicate
        if await check_dedup(event_id):
            return EventResponse(status="DROP")

        # Process event based on type
        async with async_session_maker() as session:
            if event_type == "task.created":
                await process_task_created(data, session)

            elif event_type == "task.completed":
                await process_task_completed(data, session)

            elif event_type == "task.deleted":
                await process_task_deleted(data, session)

            else:
                logger.info(f"Ignoring event type: {event_type}")

        return EventResponse(status="SUCCESS")

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        return EventResponse(status="RETRY")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)

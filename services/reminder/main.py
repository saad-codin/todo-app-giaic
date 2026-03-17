"""
Reminder Service - FastAPI microservice for handling task reminder events via Dapr.

This service:
1. Receives task events from Dapr pub/sub
2. Schedules reminders (24h and 1h before due date)
3. Polls for pending reminders and publishes reminder.triggered events
4. Implements idempotency using Dapr state store
"""

import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from dapr.clients import DaprClient
from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, SQLModel, select

# Configure logging (JSON format in cloud, human-readable locally)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "reminder-service",
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

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/todo")
# Ensure asyncpg driver prefix for SQLAlchemy async engine
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
# asyncpg doesn't support sslmode as a URL query param; strip it and use connect_args
_connect_args = {}
if "sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")
    _connect_args = {"ssl": True}
engine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=_connect_args)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Background task control
background_task = None
shutdown_event = asyncio.Event()


# Database Models
class ReminderStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    cancelled = "cancelled"


class ReminderType(str, Enum):
    twenty_four_hours = "24h"
    one_hour = "1h"


class Reminder(SQLModel, table=True):
    __tablename__ = "reminder"

    id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    user_id: str
    trigger_time: datetime
    reminder_type: ReminderType
    status: ReminderStatus = Field(default=ReminderStatus.pending)
    task_description: str = ""
    due_date: str = ""
    due_time: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Dapr State Store Functions
def is_processed(event_id: str) -> bool:
    """Check if event has already been processed using Dapr state store."""
    try:
        with DaprClient() as client:
            state = client.get_state("statestore", f"dedup:reminder:{event_id}")
            return state.data is not None and len(state.data) > 0
    except Exception as e:
        logger.warning(f"Error checking dedup state: {e}")
        return False


def mark_processed(event_id: str):
    """Mark event as processed in Dapr state store with 24h TTL."""
    try:
        with DaprClient() as client:
            client.save_state(
                "statestore",
                f"dedup:reminder:{event_id}",
                "1",
                state_metadata={"ttlInSeconds": "86400"}
            )
    except Exception as e:
        logger.warning(f"Error marking event as processed: {e}")


# Dapr Pub/Sub Functions
async def publish_reminder(reminder: Reminder, task_description: str, due_date: str, due_time: Optional[str]):
    """Publish reminder.triggered event to reminders topic."""
    try:
        with DaprClient() as client:
            data = {
                "event_id": str(uuid.uuid4()),
                "reminder_id": reminder.id,
                "task_id": reminder.task_id,
                "user_id": reminder.user_id,
                "reminder_type": reminder.reminder_type.value,
                "task_description": task_description,
                "due_date": due_date,
                "due_time": due_time,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            client.publish_event(
                "taskpubsub",
                "reminders",
                json.dumps(data),
                data_content_type="application/json"
            )
            logger.info(f"Published reminder.triggered event for task {reminder.task_id}")
    except Exception as e:
        logger.error(f"Error publishing reminder event: {e}")


# Reminder Scheduling Logic
def parse_due_datetime(due_date: str, due_time: Optional[str] = None) -> Optional[datetime]:
    """Parse due_date and optional due_time into datetime object."""
    try:
        if due_time:
            dt_str = f"{due_date} {due_time}"
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        else:
            # Default to end of day if no time specified
            return datetime.strptime(due_date, "%Y-%m-%d").replace(hour=23, minute=59)
    except Exception as e:
        logger.error(f"Error parsing due datetime: {e}")
        return None


async def schedule_reminders(
    task_id: str,
    user_id: str,
    task_description: str,
    due_date: str,
    due_time: Optional[str] = None
):
    """Schedule 24h and 1h reminders for a task."""
    due_dt = parse_due_datetime(due_date, due_time)
    if not due_dt:
        logger.warning(f"Could not parse due date for task {task_id}")
        return

    reminders_to_create = []

    # Schedule 24h reminder
    trigger_24h = due_dt - timedelta(hours=24)
    if trigger_24h > datetime.utcnow():
        reminders_to_create.append(Reminder(
            id=str(uuid.uuid4()),
            task_id=task_id,
            user_id=user_id,
            trigger_time=trigger_24h,
            reminder_type=ReminderType.twenty_four_hours,
            status=ReminderStatus.pending,
            task_description=task_description,
            due_date=due_date,
            due_time=due_time,
        ))

    # Schedule 1h reminder
    trigger_1h = due_dt - timedelta(hours=1)
    if trigger_1h > datetime.utcnow():
        reminders_to_create.append(Reminder(
            id=str(uuid.uuid4()),
            task_id=task_id,
            user_id=user_id,
            trigger_time=trigger_1h,
            reminder_type=ReminderType.one_hour,
            status=ReminderStatus.pending,
            task_description=task_description,
            due_date=due_date,
            due_time=due_time,
        ))

    if reminders_to_create:
        async with async_session_maker() as session:
            for reminder in reminders_to_create:
                session.add(reminder)
            await session.commit()
            logger.info(f"Scheduled {len(reminders_to_create)} reminder(s) for task {task_id}")


async def cancel_reminders(task_id: str):
    """Cancel all pending reminders for a task."""
    async with async_session_maker() as session:
        stmt = select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.status == ReminderStatus.pending
        )
        result = await session.execute(stmt)
        reminders = result.scalars().all()

        for reminder in reminders:
            reminder.status = ReminderStatus.cancelled
            reminder.updated_at = datetime.utcnow()

        await session.commit()
        logger.info(f"Cancelled {len(reminders)} reminder(s) for task {task_id}")


# Event Handlers
async def handle_task_created(event_data: dict):
    """Handle task.created event."""
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    due_date = event_data.get("due_date")
    due_time = event_data.get("due_time")
    task_description = event_data.get("description", "")

    if task_id and user_id and due_date:
        await schedule_reminders(task_id, user_id, task_description, due_date, due_time)


async def handle_task_updated(event_data: dict):
    """Handle task.updated event."""
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    due_date = event_data.get("due_date")
    due_time = event_data.get("due_time")
    task_description = event_data.get("description", "")

    if task_id:
        # Cancel existing reminders
        await cancel_reminders(task_id)

        # Schedule new reminders if due_date exists
        if user_id and due_date:
            await schedule_reminders(task_id, user_id, task_description, due_date, due_time)


async def handle_task_completed(event_data: dict):
    """Handle task.completed event."""
    task_id = event_data.get("task_id")
    if task_id:
        await cancel_reminders(task_id)


async def handle_task_deleted(event_data: dict):
    """Handle task.deleted event."""
    task_id = event_data.get("task_id")
    if task_id:
        await cancel_reminders(task_id)


# Background Polling Task
async def poll_pending_reminders():
    """Background task that polls for pending reminders and publishes events."""
    logger.info("Starting reminder polling background task")

    # On startup, fire all overdue reminders immediately
    async with async_session_maker() as session:
        stmt = select(Reminder).where(
            Reminder.status == ReminderStatus.pending,
            Reminder.trigger_time <= datetime.utcnow()
        )
        result = await session.execute(stmt)
        overdue_reminders = result.scalars().all()

        if overdue_reminders:
            logger.info(f"Found {len(overdue_reminders)} overdue reminder(s) on startup")
            for reminder in overdue_reminders:
                # Log simulated delivery
                logger.info(
                    f"[REMINDER] user={reminder.user_id} task={reminder.task_id} "
                    f"type={reminder.reminder_type.value} "
                    f"message=\"Task '{reminder.task_description}' is due in {reminder.reminder_type.value}\""
                )

                # Publish event
                await publish_reminder(
                    reminder,
                    reminder.task_description,
                    reminder.due_date,
                    reminder.due_time
                )

                # Update status
                reminder.status = ReminderStatus.sent
                reminder.updated_at = datetime.utcnow()

            await session.commit()

    # Main polling loop
    while not shutdown_event.is_set():
        try:
            async with async_session_maker() as session:
                stmt = select(Reminder).where(
                    Reminder.status == ReminderStatus.pending,
                    Reminder.trigger_time <= datetime.utcnow()
                )
                result = await session.execute(stmt)
                pending_reminders = result.scalars().all()

                for reminder in pending_reminders:
                    # Log simulated delivery
                    logger.info(
                        f"[REMINDER] user={reminder.user_id} task={reminder.task_id} "
                        f"type={reminder.reminder_type.value} "
                        f"message=\"Task '{reminder.task_description}' is due in {reminder.reminder_type.value}\""
                    )

                    # Publish event
                    await publish_reminder(
                        reminder,
                        reminder.task_description,
                        reminder.due_date,
                        reminder.due_time
                    )

                    # Update status
                    reminder.status = ReminderStatus.sent
                    reminder.updated_at = datetime.utcnow()

                if pending_reminders:
                    await session.commit()
                    logger.info(f"Processed {len(pending_reminders)} pending reminder(s)")

            # Wait 60 seconds before next poll
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error in reminder polling loop: {e}")
            await asyncio.sleep(60)

    logger.info("Reminder polling background task stopped")


# FastAPI Application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global background_task

    # Startup: Create tables and start background task
    logger.info("Starting Reminder Service...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database tables created")

    background_task = asyncio.create_task(poll_pending_reminders())

    yield

    # Shutdown: Stop background task
    logger.info("Shutting down Reminder Service...")
    shutdown_event.set()
    if background_task:
        await background_task
    logger.info("Reminder Service stopped")


app = FastAPI(title="Reminder Service", lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "reminder-service",
        "dapr": True
    }


@app.post("/events/task")
async def handle_task_event(request: Request):
    """
    Handle CloudEvents from Dapr pub/sub for task events.

    Implements idempotency using Dapr state store.
    """
    try:
        body = await request.json()
        logger.info(f"Received event: {body.get('type', 'unknown')}")

        # Extract event data
        event_type = body.get("type")
        event_data = body.get("data", {})
        event_id = event_data.get("event_id")

        if not event_id:
            logger.warning("Event missing event_id, skipping")
            return {"status": "DROP"}

        # Check idempotency
        if is_processed(event_id):
            logger.info(f"Event {event_id} already processed, skipping")
            return {"status": "DROP"}

        # Route to appropriate handler
        if event_type == "task.created":
            await handle_task_created(event_data)
        elif event_type == "task.updated":
            await handle_task_updated(event_data)
        elif event_type == "task.completed":
            await handle_task_completed(event_data)
        elif event_type == "task.deleted":
            await handle_task_deleted(event_data)
        else:
            logger.warning(f"Unknown event type: {event_type}")

        # Mark as processed
        mark_processed(event_id)

        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error handling task event: {e}")
        return {"status": "RETRY"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

"""
Sync Service - WebSocket-based real-time synchronization service.

This service maintains WebSocket connections with authenticated clients and broadcasts
task updates and reminders received from Dapr pub/sub topics.
"""

import asyncio
import json
import logging
import os
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from pydantic import BaseModel, Field

# Configure logging (JSON format in cloud, human-readable locally)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "sync-service",
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

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"

# WebSocket heartbeat interval (seconds)
HEARTBEAT_INTERVAL = 30


# ============================================================================
# Pydantic Models
# ============================================================================

class TaskSyncEvent(BaseModel):
    """Task sync event from task-updates topic."""
    user_id: str
    action: str  # created, updated, completed, deleted
    task: Optional[dict] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ReminderEvent(BaseModel):
    """Reminder event from reminders topic."""
    user_id: str
    task_id: str
    task_description: str
    reminder_type: str  # 24h, 1h
    due_date: str
    due_time: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class WsTaskUpdate(BaseModel):
    """WebSocket message for task updates."""
    type: str = "task_update"
    action: str
    task: Optional[dict] = None
    timestamp: str


class WsReminder(BaseModel):
    """WebSocket message for reminders."""
    type: str = "reminder"
    task_id: str
    task_description: str
    reminder_type: str
    due_date: str
    due_time: Optional[str] = None
    timestamp: str


class WsConnected(BaseModel):
    """WebSocket connection acknowledgment."""
    type: str = "connected"
    message: str = "Connected to sync service"


class WsHeartbeat(BaseModel):
    """WebSocket heartbeat message."""
    type: str = "ping"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# Connection Registry
# ============================================================================

class ConnectionRegistry:
    """Manages WebSocket connections per user."""

    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._user_by_ws: dict[WebSocket, str] = {}
        self._lock = asyncio.Lock()

    async def add(self, user_id: str, ws: WebSocket):
        """Add a WebSocket connection for a user."""
        async with self._lock:
            self._connections[user_id].add(ws)
            self._user_by_ws[ws] = user_id
            logger.info(f"Added connection for user {user_id}. Total: {len(self._connections[user_id])}")

    async def remove(self, ws: WebSocket):
        """Remove a WebSocket connection."""
        async with self._lock:
            user_id = self._user_by_ws.pop(ws, None)
            if user_id:
                self._connections[user_id].discard(ws)
                if not self._connections[user_id]:
                    del self._connections[user_id]
                logger.info(f"Removed connection for user {user_id}")

    async def broadcast(self, user_id: str, message: dict):
        """Broadcast a message to all connections for a user."""
        connections = list(self._connections.get(user_id, set()))
        if not connections:
            logger.debug(f"No connections for user {user_id}, skipping broadcast")
            return

        message_text = json.dumps(message)
        logger.info(f"Broadcasting to {len(connections)} connection(s) for user {user_id}")

        for ws in connections:
            try:
                await ws.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                await self.remove(ws)

    def get_stats(self) -> dict:
        """Get connection statistics."""
        total_users = len(self._connections)
        total_connections = sum(len(conns) for conns in self._connections.values())
        return {
            "total_users": total_users,
            "total_connections": total_connections,
            "users": {user_id: len(conns) for user_id, conns in self._connections.items()}
        }


# Global connection registry
registry = ConnectionRegistry()


# ============================================================================
# JWT Validation
# ============================================================================

def validate_token(token: str) -> Optional[str]:
    """Validate JWT and return user_id."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            logger.warning("Token missing user_id/sub claim")
            return None
        return user_id
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        return None


# ============================================================================
# Background Tasks
# ============================================================================

async def heartbeat_task():
    """Send periodic heartbeat messages to all connected clients."""
    logger.info("Starting heartbeat task")
    while True:
        try:
            await asyncio.sleep(HEARTBEAT_INTERVAL)

            stats = registry.get_stats()
            if stats["total_connections"] > 0:
                logger.debug(f"Sending heartbeat to {stats['total_connections']} connection(s)")

                heartbeat_msg = WsHeartbeat().model_dump()

                # Send to all users
                for user_id in list(stats["users"].keys()):
                    await registry.broadcast(user_id, heartbeat_msg)
        except asyncio.CancelledError:
            logger.info("Heartbeat task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in heartbeat task: {e}")


# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting sync service")
    heartbeat = asyncio.create_task(heartbeat_task())

    yield

    # Shutdown
    logger.info("Shutting down sync service")
    heartbeat.cancel()
    try:
        await heartbeat
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Sync Service",
    description="WebSocket-based real-time synchronization service",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# Health Endpoint
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    stats = registry.get_stats()
    return {
        "status": "healthy",
        "service": "sync-service",
        "dapr": True,
        "connections": stats
    }


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket endpoint for real-time sync."""

    # Validate token
    if not token:
        logger.warning("WebSocket connection attempted without token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return

    user_id = validate_token(token)
    if not user_id:
        logger.warning("WebSocket connection attempted with invalid token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    # Accept connection
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for user {user_id}")

    # Add to registry
    await registry.add(user_id, websocket)

    try:
        # Send connection acknowledgment
        connected_msg = WsConnected().model_dump()
        await websocket.send_text(json.dumps(connected_msg))

        # Keep connection alive and handle client messages
        while True:
            try:
                # Receive messages (we don't process them, just keep connection alive)
                data = await websocket.receive_text()
                logger.debug(f"Received message from user {user_id}: {data}")
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
                break
            except Exception as e:
                logger.error(f"Error receiving WebSocket message: {e}")
                break

    finally:
        # Remove from registry
        await registry.remove(websocket)


# ============================================================================
# Dapr Pub/Sub Endpoints
# ============================================================================

@app.post("/events/sync")
async def handle_task_sync_event(request: Request):
    """
    Handle task sync events from task-updates topic (CloudEvents from Dapr).
    Broadcasts the update to all WebSocket connections for the affected user.
    """
    body = await request.json()
    # Dapr sends CloudEvents - extract data from envelope
    data = body.get("data", body)
    user_id = data.get("user_id", "")
    action = data.get("action", "")
    task = data.get("task")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())

    logger.info(f"Received task sync event: user={user_id}, action={action}")

    ws_message = WsTaskUpdate(
        action=action,
        task=task,
        timestamp=timestamp
    ).model_dump()

    await registry.broadcast(user_id, ws_message)

    return {"status": "SUCCESS"}


@app.post("/events/reminder")
async def handle_reminder_event(request: Request):
    """
    Handle reminder events from reminders topic (CloudEvents from Dapr).
    Broadcasts the reminder to all WebSocket connections for the affected user.
    """
    body = await request.json()
    data = body.get("data", body)
    user_id = data.get("user_id", "")
    task_id = data.get("task_id", "")
    reminder_type = data.get("reminder_type", "")
    task_description = data.get("task_description", "")
    due_date = data.get("due_date", "")
    due_time = data.get("due_time")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())

    logger.info(f"Received reminder event: user={user_id}, task={task_id}, type={reminder_type}")

    ws_message = WsReminder(
        task_id=task_id,
        task_description=task_description,
        reminder_type=reminder_type,
        due_date=due_date,
        due_time=due_time,
        timestamp=timestamp
    ).model_dump()

    await registry.broadcast(user_id, ws_message)

    return {"status": "SUCCESS"}


# ============================================================================
# Debug/Admin Endpoints
# ============================================================================

@app.get("/debug/connections")
async def debug_connections():
    """Get current connection statistics (for debugging)."""
    return registry.get_stats()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8003"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting sync service on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

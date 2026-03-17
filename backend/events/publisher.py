"""Dapr event publisher helper with fire-and-forget error handling."""

import json
import os
import uuid
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "backend",
            "logger": record.name,
            "message": record.getMessage(),
        })


logger = logging.getLogger(__name__)
if os.getenv("LOG_FORMAT") == "json" and not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(JsonFormatter())
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

PUBSUB_NAME = "taskpubsub"


async def publish_event(topic: str, event_type: str, data: dict) -> str:
    """Fire-and-forget event publishing via Dapr sidecar.

    Returns the event_id. Never raises - failures are logged and swallowed
    so that task CRUD operations always succeed (FR-013 degraded mode).
    """
    event_id = str(uuid.uuid4())
    data["event_id"] = event_id
    try:
        from dapr.clients import DaprClient

        with DaprClient() as client:
            client.publish_event(
                pubsub_name=PUBSUB_NAME,
                topic_name=topic,
                data=json.dumps(data),
                data_content_type="application/json",
            )
        logger.info("Published %s event %s to %s", event_type, event_id, topic)
    except Exception as e:
        logger.warning("Failed to publish %s event to %s: %s (degraded mode)", event_type, topic, e)
    return event_id

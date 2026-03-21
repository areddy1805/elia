from loguru import logger
import os
import json

# ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# configure logger
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    serialize=False
)


def log_event(event_type, payload):
    logger.info({
        "event": event_type,
        "data": payload
    })
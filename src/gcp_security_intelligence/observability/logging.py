import json
import logging
import sys
from datetime import datetime, UTC


def get_logger(agent_name: str) -> logging.Logger:
    """Return a logger pre-configured for structured JSON output."""
    logger = logging.getLogger(agent_name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_event(
    logger: logging.Logger,
    trace_id: str,
    agent_name: str,
    event_type: str,
    **kwargs,
) -> None:
    """Emit a structured JSON log entry with required observability fields."""
    entry = {
        "trace_id": trace_id,
        "agent_name": agent_name,
        "event_type": event_type,
        "timestamp": datetime.now(UTC).isoformat(),
        **kwargs,
    }
    logger.info(json.dumps(entry))


class _JsonFormatter(logging.Formatter):
    """Emit log records as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        """Return the log message as-is — already JSON from log_event."""
        return record.getMessage()

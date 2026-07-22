import json
import logging
import sys
from typing import Any


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as JSON strings.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
        }

        # Catch correlation request_id if attached or in tracing context
        from src.api.middlewares.tracing import get_request_id
        req_id = get_request_id()
        if req_id:
            log_data["request_id"] = req_id
        elif hasattr(record, "request_id"):
            log_data["request_id"] = getattr(record, "request_id")

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(environment: str = "development") -> None:
    """
    Sets up logging handlers. Standard stream for local dev and JSON format for production.
    """
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers = []

    if environment == "production":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
    else:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s (%(filename)s:%(lineno)d): %(message)s"
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)

    # Disable excessive log spam from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

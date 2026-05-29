"""
Logging system for the E-Commerce Analytics Engine.
Tracks backend activity, errors, and suspicious transactions.
Provides comprehensive monitoring and debugging capabilities.
"""

import logging
import datetime
import sys
from pathlib import Path
from app.config import LOG_FORMAT, LOG_FILE, LOG_LEVEL

# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger("ecommerce_analytics")
logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

# Prevent duplicate handlers
if logger.hasHandlers():
    logger.handlers.clear()

# File handler
file_handler = logging.FileHandler(f"logs/{LOG_FILE}")
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to root logger
logger.propagate = False


def log_transaction(
    user_id: str,
    amount: float,
    city: str,
    payment_method: str,
    is_suspicious: bool = False
):
    """Log transaction event."""
    status = "SUSPICIOUS" if is_suspicious else "OK"

    logger.info(
        f"Transaction | User: {user_id} | Amount: ${amount:.2f} | "
        f"City: {city} | Method: {payment_method} | Status: {status}"
    )


def log_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float = 0
):
    """Log API request."""
    duration_str = (
        f" | Duration: {duration_ms:.2f}ms"
        if duration_ms > 0
        else ""
    )

    logger.info(
        f"API | {method} {endpoint} | "
        f"Status: {status_code}{duration_str}"
    )


def log_error(
    error: str,
    context: str = "",
    exc_info=False
):
    """Log error safely."""
    context_str = (
        f" | Context: {context}"
        if context
        else ""
    )

    logger.error(
        f"ERROR{context_str} | {error}",
        exc_info=exc_info
    )


def log_analytics_generated(
    report_type: str,
    record_count: int
):
    """Log analytics generation."""
    logger.info(
        f"Analytics | Type: {report_type} | "
        f"Records: {record_count}"
    )


def log_suspicious_transaction(
    transaction_id: int,
    reason: str
):
    """Log suspicious transaction."""
    logger.warning(
        f"Suspicious Transaction | "
        f"ID: {transaction_id} | Reason: {reason}"
    )


def log_database_operation(
    operation: str,
    success: bool,
    detail: str = ""
):
    """Log DB operations."""
    status = "SUCCESS" if success else "FAILED"
    detail_str = f" | {detail}" if detail else ""

    logger.info(
        f"Database | {status} | "
        f"{operation}{detail_str}"
    )


def log_csv_upload(
    filename: str,
    records: int,
    failed: int
):
    """Log CSV upload."""
    logger.info(
        f"CSV Upload | File: {filename} | "
        f"Processed: {records} | Failed: {failed}"
    )


def log_cache_operation(
    operation: str,
    key: str
):
    """Log cache operation."""
    logger.debug(
        f"Cache | {operation} | Key: {key}"
    )


def format_date(
    date: datetime.datetime
) -> str:
    """Format datetime."""
    return date.strftime("%Y-%m-%d %H:%M:%S")


# Attach custom methods to logger object
logger.log_error = log_error
logger.log_api_request = log_api_request
logger.log_transaction = log_transaction
logger.format_date = format_date
logger.datetime = datetime
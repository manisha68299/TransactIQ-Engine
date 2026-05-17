"""
Logging system for the E-Commerce Analytics Engine.
Tracks backend activity, errors, and suspicious transactions.
"""

import logging
from datetime import datetime
from app.config import LOG_FORMAT, LOG_FILE

# Create logger
logger = logging.getLogger("ecommerce_analytics")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_transaction(user_id: str, amount: float, city: str, payment_method: str, is_suspicious: bool = False):
    """Log a transaction event."""
    status = "SUSPICIOUS" if is_suspicious else "OK"
    logger.info(f"Transaction | User: {user_id} | Amount: ${amount} | City: {city} | Method: {payment_method} | Status: {status}")


def log_api_request(method: str, endpoint: str, status_code: int):
    """Log API request."""
    logger.info(f"API Request | Method: {method} | Endpoint: {endpoint} | Status: {status_code}")


def log_error(error: str, context: str = ""):
    """Log error event."""
    logger.error(f"Error | Context: {context} | Message: {error}")


def log_analytics_generated(report_type: str, record_count: int):
    """Log analytics report generation."""
    logger.info(f"Analytics Generated | Type: {report_type} | Records: {record_count}")

"""
Utility helper functions for the analytics engine.
Common functions used across the project.
"""

from datetime import datetime
from typing import List, Dict, Any
import json


def format_date(date: datetime) -> str:
    """Format datetime to readable string."""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:,.2f}"


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage safely."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)


def format_analytics_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format analytics response with proper types."""
    formatted = {}
    for key, value in data.items():
        if isinstance(value, float):
            formatted[key] = round(value, 2)
        else:
            formatted[key] = value
    return formatted


def validate_csv_headers(headers: List[str]) -> bool:
    """Validate if CSV has required headers."""
    required_headers = {"user_id", "amount", "city", "payment_method"}
    return required_headers.issubset(set(headers))


def safe_float_convert(value: str) -> float:
    """Safely convert string to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def get_date_string(date: datetime) -> str:
    """Get date string for grouping."""
    return date.strftime("%Y-%m-%d")

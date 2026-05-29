"""
Utility helper functions for the analytics engine.
Common functions used across the project for formatting and calculations.
"""

from datetime import datetime
from typing import List, Dict, Any
import json
import re


def format_date(date: datetime) -> str:
    """Format datetime to readable string (YYYY-MM-DD HH:MM:SS)."""
    if not date:
        return "N/A"
    return date.strftime("%Y-%m-%d %H:%M:%S")


def format_date_iso(date: datetime) -> str:
    """Format datetime to ISO format."""
    if not date:
        return "N/A"
    return date.isoformat()


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def calculate_percentage(value: float, total: float) -> float:
    """
    Calculate percentage safely.
    Handles division by zero gracefully.
    """
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)


def format_analytics_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format analytics response with proper types and rounding."""
    formatted = {}
    for key, value in data.items():
        if isinstance(value, float):
            formatted[key] = round(value, 2)
        elif isinstance(value, list):
            formatted[key] = [
                format_analytics_response(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            formatted[key] = value
    return formatted


def validate_csv_headers(headers: List[str]) -> bool:
    """
    Validate if CSV has required headers.
    Required: user_id, amount, city, payment_method
    """
    required_headers = {"user_id", "amount", "city", "payment_method"}
    return required_headers.issubset(set([h.lower().strip() for h in headers]))


def safe_float_convert(value: str) -> float:
    """Safely convert string to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def safe_int_convert(value: str) -> int:
    """Safely convert string to integer."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def get_date_string(date: datetime) -> str:
    """Get date string for grouping (YYYY-MM-DD)."""
    if not date:
        return "N/A"
    return date.strftime("%Y-%m-%d")


def sanitize_string(value: str) -> str:
    """Sanitize string input."""
    if not value:
        return ""
    return str(value).strip().lower()


def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)
"""
Robust configuration for the E-Commerce Analytics Engine.

- Loads .env if python-dotenv is available (optional).
- Reads and casts environment variables with safe defaults.
- Fails fast in production if SECRET_KEY is missing.
"""

from __future__ import annotations
import os
import logging
from typing import List

# Try to load .env (optional). If python-dotenv is not installed, continue silently.
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv not installed or .env missing -> continue using os.environ
    pass


def getenv_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def getenv_int(key: str, default: int = 0) -> int:
    val = os.getenv(key)
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def getenv_list(key: str, default: List[str] | None = None, sep: str = ",") -> List[str]:
    raw = os.getenv(key)
    if raw is None:
        return default or []
    return [p.strip() for p in raw.split(sep) if p.strip()]


# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
DATABASE_ECHO = getenv_bool("DATABASE_ECHO", False)

# Transaction Limits
MAX_TRANSACTION_AMOUNT = getenv_int("MAX_TRANSACTION_AMOUNT", 50000)
MIN_TRANSACTION_AMOUNT = getenv_int("MIN_TRANSACTION_AMOUNT", 1)

# Fraud Detection Threshold
SUSPICIOUS_TRANSACTION_THRESHOLD = getenv_int("SUSPICIOUS_TRANSACTION_THRESHOLD", 10000)

# Valid Payment Methods (can be overriden via env e.g. PAYMENT_METHODS=credit_card,debit_card)
VALID_PAYMENT_METHODS = getenv_list(
    "VALID_PAYMENT_METHODS",
    default=[
        "credit_card",
        "debit_card",
        "digital_wallet",
        "bank_transfer",
        "upi",
        "paypal",
        "apple_pay",
        "google_pay",
    ],
)

# Valid Cities for Analytics (kept as default list; can be overridden via env VALID_CITIES="City1,City2")
VALID_CITIES = getenv_list(
    "VALID_CITIES",
    default=[
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
        "London", "Paris", "Berlin", "Madrid", "Amsterdam",
        "Milan", "Rome", "Vienna", "Brussels", "Dublin",
        "Tokyo", "Singapore", "Hong Kong", "Bangkok", "Seoul",
        "Shanghai", "Beijing", "Dubai", "Istanbul", "Jakarta",
    ],
)

# API Configuration
API_TITLE = os.getenv("API_TITLE", "Real-Time E-Commerce Analytics Engine")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_DESCRIPTION = os.getenv(
    "API_DESCRIPTION",
    """Professional backend intelligence system for transaction analytics and business insights.
Features: real-time processing, analytics, fraud detection, CSV bulk import.""",
)

# Security Configuration
ALLOWED_HOSTS = getenv_list("ALLOWED_HOSTS", default=["*"]) or ["*"]
SECRET_KEY = os.getenv("SECRET_KEY")  # do NOT set a meaningful default here
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)

# Logging Configuration
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = os.getenv("LOG_FILE", "app_logs.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Pagination
DEFAULT_SKIP = getenv_int("DEFAULT_SKIP", 0)
DEFAULT_LIMIT = getenv_int("DEFAULT_LIMIT", 100)
MAX_LIMIT = getenv_int("MAX_LIMIT", 1000)

# CSV Upload Configuration
MAX_UPLOAD_FILE_SIZE = getenv_int("MAX_UPLOAD_FILE_SIZE", 50 * 1024 * 1024)  # default 50MB
ALLOWED_UPLOAD_FORMATS = getenv_list("ALLOWED_UPLOAD_FORMATS", default=["csv"])

# Performance Configuration
ANALYTICS_BATCH_SIZE = getenv_int("ANALYTICS_BATCH_SIZE", 1000)
CACHE_TTL_SECONDS = getenv_int("CACHE_TTL_SECONDS", 300)  # 5 minutes

# Environment mode
ENVIRONMENT = os.getenv("ENV", "development").lower()

# Fail fast in production if SECRET_KEY missing
if ENVIRONMENT == "production" and not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in production environment (via env var).")

# Configure basic logging for modules that import config early
try:
    logging.basicConfig(format=LOG_FORMAT)
    logging.getLogger().setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
except Exception:
    # If logging configuration fails for any reason, ignore here
    pass
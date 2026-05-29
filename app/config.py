"""
Configuration file for the E-Commerce Analytics Engine.
Stores all reusable configuration values, constants, and environment variables.
Production-ready with environment-based configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"

# Transaction Limits
MAX_TRANSACTION_AMOUNT = 50000
MIN_TRANSACTION_AMOUNT = 1

# Fraud Detection Threshold
SUSPICIOUS_TRANSACTION_THRESHOLD = 10000

# Valid Payment Methods
VALID_PAYMENT_METHODS = [
    "credit_card",
    "debit_card",
    "digital_wallet",
    "bank_transfer",
    "upi",
    "paypal",
    "apple_pay",
    "google_pay"
]

# Valid Cities for Analytics (Global Coverage)
VALID_CITIES = [
    # USA
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    
    # India
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    
    # Europe
    "London", "Paris", "Berlin", "Madrid", "Amsterdam",
    "Milan", "Rome", "Vienna", "Brussels", "Dublin",
    
    # Asia
    "Tokyo", "Singapore", "Hong Kong", "Bangkok", "Seoul",
    "Shanghai", "Beijing", "Dubai", "Istanbul", "Jakarta"
]

# API Configuration
API_TITLE = "Real-Time E-Commerce Analytics Engine"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
Professional backend intelligence system for transaction analytics and business insights.

This API processes e-commerce transaction data in real-time, validates incoming data,
stores it securely, performs advanced analytics using Pandas and NumPy, and returns
meaningful business intelligence through REST APIs.

Features:
- Real-time transaction processing
- Advanced business analytics
- Fraud detection
- Revenue analysis
- Payment insights
- CSV bulk import
"""

# Security Configuration
ALLOWED_HOSTS = ["*"]  # In production, restrict to specific domains
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "app_logs.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Pagination
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000

# CSV Upload Configuration
MAX_UPLOAD_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_UPLOAD_FORMATS = ["csv"]

# Performance Configuration
ANALYTICS_BATCH_SIZE = 1000
CACHE_TTL_SECONDS = 300  # 5 minutes
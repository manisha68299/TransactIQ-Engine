"""
Configuration file for the E-Commerce Analytics Engine.
Stores all reusable configuration values and constants.
"""

DATABASE_URL = "sqlite:///./ecommerce.db"

# Transaction limits
MAX_TRANSACTION_AMOUNT = 50000
MIN_TRANSACTION_AMOUNT = 1

# Fraud detection threshold (transactions above this are flagged as suspicious)
SUSPICIOUS_TRANSACTION_THRESHOLD = 10000

# Valid payment methods
VALID_PAYMENT_METHODS = ["credit_card", "debit_card", "digital_wallet", "bank_transfer", "upi"]

# Valid cities for analytics
VALID_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "London", "Paris", "Berlin", "Tokyo", "Singapore"
]

# API configuration
API_TITLE = "Real-Time E-Commerce Analytics Engine"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Professional backend intelligence system for transaction analytics and business insights"

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "app_logs.log"

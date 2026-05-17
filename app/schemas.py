"""
Pydantic schemas for request/response validation.
Validates incoming API data before processing.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from app.config import VALID_PAYMENT_METHODS, MIN_TRANSACTION_AMOUNT, MAX_TRANSACTION_AMOUNT


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    user_id: str = Field(..., min_length=1, max_length=50, description="User ID")
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    payment_method: str = Field(..., description="Payment method used")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < MIN_TRANSACTION_AMOUNT or v > MAX_TRANSACTION_AMOUNT:
            raise ValueError(f'Amount must be between ${MIN_TRANSACTION_AMOUNT} and ${MAX_TRANSACTION_AMOUNT}')
        return v

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        if v.lower() not in VALID_PAYMENT_METHODS:
            raise ValueError(f'Payment method must be one of {VALID_PAYMENT_METHODS}')
        return v.lower()

    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        if not v.strip():
            raise ValueError('City cannot be empty')
        return v.strip()


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: int
    user_id: str
    amount: float
    city: str
    payment_method: str
    is_suspicious: bool
    timestamp: datetime

    class Config:
        from_attributes = True


class RevenueAnalyticsResponse(BaseModel):
    """Schema for revenue analytics response."""
    total_revenue: float
    transaction_count: int
    average_transaction_value: float
    min_transaction: float
    max_transaction: float
    standard_deviation: float


class CityAnalyticsResponse(BaseModel):
    """Schema for city-wise analytics response."""
    city: str
    revenue: float
    transaction_count: int
    percentage_of_total: float


class PaymentAnalyticsResponse(BaseModel):
    """Schema for payment method analytics response."""
    payment_method: str
    transaction_count: int
    total_amount: float
    percentage_of_total: float


class SuspiciousTransactionResponse(BaseModel):
    """Schema for suspicious transaction response."""
    id: int
    user_id: str
    amount: float
    city: str
    payment_method: str
    timestamp: datetime
    reason: str


class DailyTrendResponse(BaseModel):
    """Schema for daily transaction trends."""
    date: str
    transaction_count: int
    total_revenue: float
    average_transaction_value: float


class UploadStatusResponse(BaseModel):
    """Schema for CSV upload response."""
    status: str
    message: str
    transactions_processed: int
    transactions_failed: int

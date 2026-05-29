"""
Pydantic schemas for request/response validation.
Validates incoming API data before processing.
Ensures data integrity and type safety across the entire application.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from app.config import (
    VALID_PAYMENT_METHODS,
    MIN_TRANSACTION_AMOUNT,
    MAX_TRANSACTION_AMOUNT,
    VALID_CITIES
)


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique user identifier"
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Transaction amount in USD"
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name"
    )
    payment_method: str = Field(
        ...,
        description="Payment method used"
    )

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate transaction amount is within acceptable range."""
        if v < MIN_TRANSACTION_AMOUNT or v > MAX_TRANSACTION_AMOUNT:
            raise ValueError(
                f'Amount must be between ${MIN_TRANSACTION_AMOUNT} and ${MAX_TRANSACTION_AMOUNT}'
            )
        return round(v, 2)

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        """Validate payment method is from approved list."""
        if v.lower() not in VALID_PAYMENT_METHODS:
            raise ValueError(
                f'Payment method must be one of: {", ".join(VALID_PAYMENT_METHODS)}'
            )
        return v.lower()

    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        """Validate and clean city name."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError('City cannot be empty')
        return cleaned

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        """Validate user ID format."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError('User ID cannot be empty')
        return cleaned


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: int
    user_id: str
    amount: float
    city: str
    payment_method: str
    is_suspicious: bool
    timestamp: datetime
    reference_id: str

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for transaction list response with pagination."""
    total: int
    skip: int
    limit: int
    data: List[TransactionResponse]


class RevenueAnalyticsResponse(BaseModel):
    """Schema for revenue analytics response."""
    total_revenue: float = Field(..., description="Total revenue in USD")
    transaction_count: int = Field(..., description="Total number of transactions")
    average_transaction_value: float = Field(..., description="Average transaction amount")
    min_transaction: float = Field(..., description="Minimum transaction amount")
    max_transaction: float = Field(..., description="Maximum transaction amount")
    standard_deviation: float = Field(..., description="Standard deviation of amounts")


class CityAnalyticsResponse(BaseModel):
    """Schema for city-wise analytics response."""
    city: str
    revenue: float
    transaction_count: int
    percentage_of_total: float


class CityAnalyticsListResponse(BaseModel):
    """Schema for city analytics list response."""
    total_cities: int
    total_revenue: float
    data: List[CityAnalyticsResponse]


class PaymentAnalyticsResponse(BaseModel):
    """Schema for payment method analytics response."""
    payment_method: str
    transaction_count: int
    total_amount: float
    percentage_of_total: float


class PaymentAnalyticsListResponse(BaseModel):
    """Schema for payment analytics list response."""
    payment_methods: int
    total_transactions: int
    data: List[PaymentAnalyticsResponse]


class DailyTrendResponse(BaseModel):
    """Schema for daily transaction trends."""
    date: str
    transaction_count: int
    total_revenue: float
    average_transaction_value: float


class DailyTrendsListResponse(BaseModel):
    """Schema for daily trends list response."""
    total_days: int
    total_revenue: float
    total_transactions: int
    data: List[DailyTrendResponse]


class TopUserResponse(BaseModel):
    """Schema for top user by spending."""
    user_id: str
    total_spending: float
    transaction_count: int
    average_transaction: float


class TopUsersListResponse(BaseModel):
    """Schema for top users list response."""
    total_users: int
    data: List[TopUserResponse]


class StatisticalSummaryResponse(BaseModel):
    """Schema for statistical summary response."""
    total_transactions: int
    total_revenue: float
    average: float
    median: float
    std_dev: float
    percentile_25: float
    percentile_75: float
    percentile_95: float
    min_value: float
    max_value: float


class SuspiciousTransactionResponse(BaseModel):
    """Schema for suspicious transaction."""
    id: int
    user_id: str
    amount: float
    city: str
    payment_method: str
    timestamp: datetime
    reason: str


class SuspiciousTransactionListResponse(BaseModel):
    """Schema for suspicious transactions list."""
    total_suspicious: int
    total_amount_flagged: float
    data: List[SuspiciousTransactionResponse]


class UploadStatusResponse(BaseModel):
    """Schema for CSV upload response."""
    status: str
    message: str
    transactions_processed: int
    transactions_failed: int
    transactions_successful: int
    processing_time_seconds: float


class ExecutiveSummaryResponse(BaseModel):
    """Schema for executive summary dashboard."""
    total_revenue: float
    total_transactions: int
    average_transaction: float
    top_city: str
    top_payment_method: str
    suspicious_transactions: int
    total_users: int
    timestamp: datetime
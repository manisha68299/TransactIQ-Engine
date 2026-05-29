"""
SQLAlchemy ORM models that define database table structure.
Represents how transaction data is stored in SQLite.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index, TIMESTAMP
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Transaction(Base):
    """
    Transaction table model.
    Stores e-commerce transaction records with comprehensive indexing.
    
    Attributes:
        id: Unique transaction identifier
        user_id: Customer identifier
        amount: Transaction amount in USD
        city: Transaction location
        payment_method: Payment method used
        is_suspicious: Flag for suspicious transactions
        timestamp: Transaction timestamp
        reference_id: Unique reference for tracking
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    city = Column(String(100), index=True, nullable=False)
    payment_method = Column(String(50), index=True, nullable=False)
    is_suspicious = Column(Boolean, default=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    reference_id = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_city_timestamp', 'city', 'timestamp'),
        Index('idx_amount_suspicious', 'amount', 'is_suspicious'),
    )

    def __repr__(self):
        return (
            f"<Transaction("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"amount=${self.amount:.2f}, "
            f"city={self.city}, "
            f"suspicious={self.is_suspicious}"
            f")>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "city": self.city,
            "payment_method": self.payment_method,
            "is_suspicious": self.is_suspicious,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "reference_id": self.reference_id
        }


class Analytics(Base):
    """
    Analytics cache table for storing pre-computed analytics results.
    Improves performance for frequently accessed reports.
    """
    __tablename__ = "analytics_cache"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(100), index=True, nullable=False)
    report_data = Column(String, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)

    def __repr__(self):
        return f"<Analytics(id={self.id}, report_type={self.report_type})>"
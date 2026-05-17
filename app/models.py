"""
SQLAlchemy ORM models that define database table structure.
Represents how transaction data is stored in SQLite.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Transaction(Base):
    """
    Transaction table model.
    Stores e-commerce transaction records.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    city = Column(String(100), nullable=False)
    payment_method = Column(String(50), nullable=False)
    is_suspicious = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, city={self.city})>"

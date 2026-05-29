"""
CRUD layer for database operations.
Handles all create, read, update, delete operations separately from API logic.
Provides clean abstraction for database interactions.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models import Transaction
from app.schemas import TransactionCreate
from app.logger import logger
from typing import List, Optional, Tuple
from datetime import datetime, timedelta


def create_transaction(
    db: Session,
    transaction: TransactionCreate,
    is_suspicious: bool = False
) -> Transaction:
    """
    Create and save a new transaction to database.
    
    Args:
        db: Database session
        transaction: Transaction data
        is_suspicious: Flag for suspicious transactions
        
    Returns:
        Transaction: Created transaction object
        
    Raises:
        Exception: If database operation fails
    """
    try:
        db_transaction = Transaction(
            user_id=transaction.user_id,
            amount=transaction.amount,
            city=transaction.city,
            payment_method=transaction.payment_method,
            is_suspicious=is_suspicious
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        logger.info(f" Transaction created: ID={db_transaction.id}, User={transaction.user_id}, Amount=${transaction.amount}")
        return db_transaction
    except Exception as e:
        db.rollback()
        logger.log_error(f" Failed to create transaction: {str(e)}")
        raise


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Fetch a single transaction by ID."""
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_all_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Transaction], int]:
    """
    Fetch all transactions with pagination.
    
    Returns:
        Tuple of (transactions list, total count)
    """
    total = db.query(Transaction).count()
    transactions = (
        db.query(Transaction)
        .order_by(desc(Transaction.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions, total


def get_transactions_by_city(db: Session, city: str) -> List[Transaction]:
    """Fetch all transactions for a specific city."""
    return (
        db.query(Transaction)
        .filter(Transaction.city == city)
        .order_by(desc(Transaction.timestamp))
        .all()
    )


def get_transactions_by_user(db: Session, user_id: str) -> List[Transaction]:
    """Fetch all transactions for a specific user."""
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(desc(Transaction.timestamp))
        .all()
    )


def get_suspicious_transactions(db: Session) -> List[Transaction]:
    """Fetch all flagged suspicious transactions."""
    return (
        db.query(Transaction)
        .filter(Transaction.is_suspicious == True)
        .order_by(desc(Transaction.timestamp))
        .all()
    )


def get_all_transactions_for_analytics(db: Session) -> List[Transaction]:
    """Fetch all transactions for analytics processing."""
    return db.query(Transaction).all()


def get_transactions_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> List[Transaction]:
    """Fetch transactions within a date range."""
    return (
        db.query(Transaction)
        .filter(Transaction.timestamp >= start_date)
        .filter(Transaction.timestamp <= end_date)
        .order_by(desc(Transaction.timestamp))
        .all()
    )


def transaction_count(db: Session) -> int:
    """Get total count of transactions in database."""
    return db.query(Transaction).count()


def suspicious_transaction_count(db: Session) -> int:
    """Get count of suspicious transactions."""
    return db.query(Transaction).filter(Transaction.is_suspicious == True).count()


def get_unique_users_count(db: Session) -> int:
    """Get count of unique users."""
    return db.query(func.count(func.distinct(Transaction.user_id))).scalar()


def get_unique_cities_count(db: Session) -> int:
    """Get count of unique cities."""
    return db.query(func.count(func.distinct(Transaction.city))).scalar()


def bulk_create_transactions(
    db: Session,
    transactions: List[tuple]
) -> Tuple[int, int]:
    """
    Create multiple transactions from a list of tuples.
    
    Args:
        db: Database session
        transactions: List of (user_id, amount, city, payment_method, is_suspicious) tuples
        
    Returns:
        Tuple of (successful_count, failed_count)
    """
    successful = 0
    failed = 0

    for user_id, amount, city, payment_method, is_suspicious in transactions:
        try:
            db_transaction = Transaction(
                user_id=str(user_id).strip(),
                amount=float(amount),
                city=str(city).strip(),
                payment_method=str(payment_method).lower().strip(),
                is_suspicious=bool(is_suspicious)
            )
            db.add(db_transaction)
            successful += 1
        except Exception as e:
            failed += 1
            logger.log_error(f" Bulk create error for user {user_id}: {str(e)}")

    try:
        db.commit()
        logger.info(f" Bulk insert completed: {successful} successful, {failed} failed")
    except Exception as e:
        db.rollback()
        logger.log_error(f" Bulk commit error: {str(e)}")
        return (0, successful + failed)

    return (successful, failed)


def get_revenue_summary(db: Session) -> dict:
    """Get revenue summary statistics."""
    total = db.query(func.sum(Transaction.amount)).scalar() or 0.0
    count = db.query(func.count(Transaction.id)).scalar()
    
    return {
        "total_revenue": float(total),
        "transaction_count": count,
        "average_transaction": float(total / count) if count > 0 else 0.0
    }


def mark_suspicious_transaction(db: Session, transaction_id: int) -> bool:
    """Mark a transaction as suspicious."""
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            transaction.is_suspicious = True
            db.commit()
            logger.info(f" Marked transaction {transaction_id} as suspicious")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.log_error(f" Error marking transaction as suspicious: {str(e)}")
        return False
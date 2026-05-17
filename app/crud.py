"""
CRUD layer for database operations.
Handles all create, read, update, delete operations separately from API logic.
"""

from sqlalchemy.orm import Session
from app.models import Transaction
from app.schemas import TransactionCreate
from app.logger import log_error
from typing import List, Optional


def create_transaction(db: Session, transaction: TransactionCreate, is_suspicious: bool = False) -> Transaction:
    """
    Create and save a new transaction to database.
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
        return db_transaction
    except Exception as e:
        db.rollback()
        log_error(str(e), "create_transaction")
        raise


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Fetch a single transaction by ID."""
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_all_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[Transaction]:
    """Fetch all transactions with pagination."""
    return db.query(Transaction).offset(skip).limit(limit).all()


def get_transactions_by_city(db: Session, city: str) -> List[Transaction]:
    """Fetch all transactions for a specific city."""
    return db.query(Transaction).filter(Transaction.city == city).all()


def get_transactions_by_user(db: Session, user_id: str) -> List[Transaction]:
    """Fetch all transactions for a specific user."""
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()


def get_suspicious_transactions(db: Session) -> List[Transaction]:
    """Fetch all flagged suspicious transactions."""
    return db.query(Transaction).filter(Transaction.is_suspicious == True).all()


def get_all_transactions_for_analytics(db: Session) -> List[Transaction]:
    """Fetch all transactions for analytics processing."""
    return db.query(Transaction).all()


def transaction_count(db: Session) -> int:
    """Get total count of transactions in database."""
    return db.query(Transaction).count()


def bulk_create_transactions(db: Session, transactions: List[tuple]) -> tuple:
    """
    Create multiple transactions from a list of tuples.
    Returns (successful_count, failed_count)
    """
    successful = 0
    failed = 0

    for user_id, amount, city, payment_method, is_suspicious in transactions:
        try:
            db_transaction = Transaction(
                user_id=user_id,
                amount=float(amount),
                city=city,
                payment_method=payment_method.lower(),
                is_suspicious=is_suspicious
            )
            db.add(db_transaction)
            successful += 1
        except Exception as e:
            failed += 1
            log_error(str(e), f"bulk_create_transactions - user: {user_id}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        log_error(str(e), "bulk_create_transactions - commit")
        return (0, successful + failed)

    return (successful, failed)

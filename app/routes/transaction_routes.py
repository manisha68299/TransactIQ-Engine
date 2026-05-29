"""
API routes for transaction operations.
Handles submission, retrieval, and filtering of transaction data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse
)
from app.crud import (
    create_transaction,
    get_all_transactions,
    get_transactions_by_city,
    get_transactions_by_user,
    get_suspicious_transactions,
    transaction_count,
    suspicious_transaction_count,
    get_unique_users_count,
    get_unique_cities_count,
    get_transaction
)
from app.analytics import AnalyticsEngine
from app.logger import logger
from app.config import SUSPICIOUS_TRANSACTION_THRESHOLD
from typing import List

router = APIRouter()


@router.post("/transactions", response_model=TransactionResponse, tags=["Transactions"])
async def submit_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new transaction.
    
    The system will:
    1. Validate the transaction data using Pydantic
    2. Check if amount exceeds suspicious threshold
    3. Save to database
    4. Return transaction details with ID
    """
    try:
        # Check if transaction is suspicious
        is_suspicious = transaction.amount > SUSPICIOUS_TRANSACTION_THRESHOLD
        
        # Create transaction
        db_transaction = create_transaction(db, transaction, is_suspicious)
        
        # Log transaction
        logger.log_transaction(
            transaction.user_id,
            transaction.amount,
            transaction.city,
            transaction.payment_method,
            is_suspicious
        )
        
        if is_suspicious:
            logger.log_suspicious_transaction(
                db_transaction.id,
                f"Amount ${transaction.amount} exceeds threshold ${SUSPICIOUS_TRANSACTION_THRESHOLD}"
            )
        
        return db_transaction
    except Exception as e:
        logger.log_error(str(e), "submit_transaction")
        raise HTTPException(status_code=500, detail="Failed to create transaction")


@router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve all transactions with pagination.
    
    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Number of records to return (default: 100, max: 1000)
    """
    try:
        transactions, total = get_all_transactions(db, skip=skip, limit=limit)
        logger.log_api_request("GET", "/transactions", 200)
        
        return TransactionListResponse(
            total=total,
            skip=skip,
            limit=limit,
            data=transactions
        )
    except Exception as e:
        logger.log_error(str(e), "get_transactions")
        raise HTTPException(status_code=500, detail="Failed to retrieve transactions")


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID."""
    try:
        transaction = get_transaction(db, transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        logger.log_api_request("GET", f"/transactions/{transaction_id}", 200)
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(str(e), "get_transaction_by_id")
        raise HTTPException(status_code=500, detail="Failed to retrieve transaction")


@router.get("/transactions/by-city/{city}", response_model=List[TransactionResponse])
async def get_by_city(
    city: str,
    db: Session = Depends(get_db)
):
    """Get all transactions for a specific city."""
    try:
        transactions = get_transactions_by_city(db, city)
        logger.log_api_request("GET", f"/transactions/by-city/{city}", 200)
        
        return transactions
    except Exception as e:
        logger.log_error(str(e), "get_by_city")
        raise HTTPException(status_code=500, detail="Failed to retrieve city transactions")


@router.get("/transactions/by-user/{user_id}", response_model=List[TransactionResponse])
async def get_by_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all transactions for a specific user."""
    try:
        transactions = get_transactions_by_user(db, user_id)
        logger.log_api_request("GET", f"/transactions/by-user/{user_id}", 200)
        
        return transactions
    except Exception as e:
        logger.log_error(str(e), "get_by_user")
        raise HTTPException(status_code=500, detail="Failed to retrieve user transactions")


@router.get("/transactions/suspicious/all")
async def get_suspicious(db: Session = Depends(get_db)):
    """Get all flagged suspicious transactions."""
    try:
        transactions = get_suspicious_transactions(db)
        logger.log_api_request("GET", "/transactions/suspicious/all", 200)
        
        return {
            "total_suspicious": len(transactions),
            "transactions": transactions
        }
    except Exception as e:
        logger.log_error(str(e), "get_suspicious")
        raise HTTPException(status_code=500, detail="Failed to retrieve suspicious transactions")


@router.get("/transactions/stats/summary")
async def get_transaction_stats(db: Session = Depends(get_db)):
    """Get transaction statistics summary."""
    try:
        total_transactions = transaction_count(db)
        total_suspicious = suspicious_transaction_count(db)
        total_users = get_unique_users_count(db)
        total_cities = get_unique_cities_count(db)
        
        logger.log_api_request("GET", "/transactions/stats/summary", 200)
        
        return {
            "total_transactions": total_transactions,
            "total_suspicious": total_suspicious,
            "total_users": total_users,
            "total_cities": total_cities,
            "suspicious_percentage": round((total_suspicious / total_transactions * 100) if total_transactions > 0 else 0, 2)
        }
    except Exception as e:
        logger.log_error(str(e), "get_transaction_stats")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
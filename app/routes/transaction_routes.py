"""
Transaction API routes.
Handles POST and GET requests for transaction submission and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import TransactionCreate, TransactionResponse
from app.crud import create_transaction, get_all_transactions, get_transactions_by_city, get_suspicious_transactions
from app.analytics import AnalyticsEngine
from app.logger import log_transaction, log_api_request, log_error
from app.config import SUSPICIOUS_TRANSACTION_THRESHOLD

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=201)
def submit_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """
    Submit a new transaction.
    Validates data, detects suspicious transactions, stores in database.
    """
    try:
        is_suspicious = transaction.amount > SUSPICIOUS_TRANSACTION_THRESHOLD

        db_transaction = create_transaction(db, transaction, is_suspicious=is_suspicious)

        log_transaction(
            transaction.user_id,
            transaction.amount,
            transaction.city,
            transaction.payment_method,
            is_suspicious
        )
        log_api_request("POST", "/transactions", 201)

        return db_transaction
    except Exception as e:
        log_error(str(e), "submit_transaction")
        raise HTTPException(status_code=500, detail="Error submitting transaction")


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all transactions with pagination.
    """
    try:
        transactions = get_all_transactions(db, skip=skip, limit=limit)
        log_api_request("GET", "/transactions", 200)
        return transactions
    except Exception as e:
        log_error(str(e), "get_transactions")
        raise HTTPException(status_code=500, detail="Error retrieving transactions")


@router.get("/by-city/{city}", response_model=List[TransactionResponse])
def get_transactions_by_city_route(city: str, db: Session = Depends(get_db)):
    """
    Retrieve all transactions for a specific city.
    """
    try:
        transactions = get_transactions_by_city(db, city)
        log_api_request("GET", f"/transactions/by-city/{city}", 200)
        return transactions
    except Exception as e:
        log_error(str(e), "get_transactions_by_city")
        raise HTTPException(status_code=500, detail="Error retrieving transactions")


@router.get("/suspicious/all", response_model=List[TransactionResponse])
def get_suspicious_transactions_route(db: Session = Depends(get_db)):
    """
    Retrieve all flagged suspicious transactions.
    """
    try:
        transactions = get_suspicious_transactions(db)
        log_api_request("GET", "/transactions/suspicious/all", 200)
        return transactions
    except Exception as e:
        log_error(str(e), "get_suspicious_transactions")
        raise HTTPException(status_code=500, detail="Error retrieving suspicious transactions")

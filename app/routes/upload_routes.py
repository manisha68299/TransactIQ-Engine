"""
API routes for CSV file uploads and bulk transaction processing.
Handles CSV parsing, validation, and bulk data import.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import bulk_create_transactions
from app.logger import logger
from app.utils import validate_csv_headers, safe_float_convert, safe_int_convert
from app.config import ALLOWED_UPLOAD_FORMATS, MAX_UPLOAD_FILE_SIZE
from app.schemas import UploadStatusResponse
import csv
import io
import time

router = APIRouter()


@router.post("/upload/csv", response_model=UploadStatusResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload CSV file for bulk transaction processing.
    
    CSV Format:
    - Required columns: user_id, amount, city, payment_method
    - Optional: is_suspicious (true/false)
    
    Example:
    ```
    user_id,amount,city,payment_method
    user123,1500.00,New York,credit_card
    user456,2500.00,Mumbai,debit_card
    ```
    """
    start_time = time.time()
    
    try:
        # Validate file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Expected CSV, got {file.filename.split('.')[-1]}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_UPLOAD_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_UPLOAD_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Parse CSV
        csv_file = io.StringIO(content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_file)
        
        # Validate headers
        if not csv_reader.fieldnames or not validate_csv_headers(csv_reader.fieldnames):
            raise HTTPException(
                status_code=400,
                detail="CSV must contain: user_id, amount, city, payment_method"
            )
        
        # Parse rows
        transactions = []
        for idx, row in enumerate(csv_reader, 1):
            try:
                user_id = row.get('user_id', '').strip()
                amount = safe_float_convert(row.get('amount', '0'))
                city = row.get('city', '').strip()
                payment_method = row.get('payment_method', '').strip()
                is_suspicious = row.get('is_suspicious', 'false').lower() == 'true'
                
                # Validate required fields
                if not user_id or amount <= 0 or not city or not payment_method:
                    logger.log_error(f"Invalid row {idx}: missing or invalid fields")
                    continue
                
                transactions.append((user_id, amount, city, payment_method, is_suspicious))
            except Exception as e:
                logger.log_error(f"CSV parse error at row {idx}: {str(e)}")
                continue
        
        if not transactions:
            raise HTTPException(
                status_code=400,
                detail="No valid transactions found in CSV"
            )
        
        # Bulk insert
        successful, failed = bulk_create_transactions(db, transactions)
        
        processing_time = time.time() - start_time
        
        logger.log_csv_upload(file.filename, successful, failed)
        logger.log_api_request("POST", "/upload/csv", 200)
        
        return UploadStatusResponse(
            status="success" if failed == 0 else "partial",
            message=f"Processed {successful} transactions. {failed} failed." if failed > 0 else "All transactions processed successfully.",
            transactions_processed=successful + failed,
            transactions_failed=failed,
            transactions_successful=successful,
            processing_time_seconds=processing_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(str(e), "upload_csv")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/upload/templates")
async def get_csv_template():
    """Get CSV template for bulk upload."""
    return {
        "filename": "transactions_template.csv",
        "headers": ["user_id", "amount", "city", "payment_method", "is_suspicious"],
        "example_rows": [
            {
                "user_id": "user_001",
                "amount": "1500.00",
                "city": "New York",
                "payment_method": "credit_card",
                "is_suspicious": "false"
            },
            {
                "user_id": "user_002",
                "amount": "2500.00",
                "city": "Mumbai",
                "payment_method": "debit_card",
                "is_suspicious": "false"
            },
            {
                "user_id": "user_003",
                "amount": "15000.00",
                "city": "London",
                "payment_method": "bank_transfer",
                "is_suspicious": "true"
            }
        ],
        "notes": [
            "user_id: Unique customer identifier (max 50 characters)",
            "amount: Transaction amount in USD (must be numeric)",
            "city: Transaction location",
            "payment_method: One of [credit_card, debit_card, digital_wallet, bank_transfer, upi, paypal, apple_pay, google_pay]",
            "is_suspicious: Optional, defaults to false"
        ]
    }
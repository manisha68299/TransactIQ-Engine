"""
CSV Upload and Bulk Processing routes.
Handles CSV file uploads and processes bulk transaction data.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
from app.database import get_db
from app.schemas import UploadStatusResponse, TransactionCreate
from app.crud import bulk_create_transactions
from app.logger import log_error, log_api_request
from app.utils import validate_csv_headers, safe_float_convert
from app.config import SUSPICIOUS_TRANSACTION_THRESHOLD

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/csv", response_model=UploadStatusResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV file for bulk transaction processing.
    Expected columns: user_id, amount, city, payment_method
    """
    try:
        # Validate file type
        if not file.filename.endswith(".csv"):
            log_api_request("POST", "/upload/csv", 400)
            raise HTTPException(status_code=400, detail="File must be CSV format")

        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # Validate headers
        if not validate_csv_headers(df.columns.tolist()):
            log_api_request("POST", "/upload/csv", 400)
            raise HTTPException(
                status_code=400,
                detail="CSV must contain columns: user_id, amount, city, payment_method"
            )

        # Prepare transactions for bulk insert
        transactions_list = []
        failed_count = 0

        for idx, row in df.iterrows():
            try:
                user_id = str(row["user_id"]).strip()
                amount = safe_float_convert(row["amount"])
                city = str(row["city"]).strip()
                payment_method = str(row["payment_method"]).strip().lower()

                # Validate
                if not user_id or not city or not payment_method:
                    failed_count += 1
                    continue

                if amount <= 0:
                    failed_count += 1
                    continue

                # Detect suspicious
                is_suspicious = amount > SUSPICIOUS_TRANSACTION_THRESHOLD

                transactions_list.append((user_id, amount, city, payment_method, is_suspicious))

            except Exception as e:
                failed_count += 1
                log_error(f"Row {idx}: {str(e)}", "upload_csv_parsing")
                continue

        # Bulk insert
        if transactions_list:
            successful, bulk_failed = bulk_create_transactions(db, transactions_list)
        else:
            successful = 0
            bulk_failed = len(df)

        log_api_request("POST", "/upload/csv", 200)

        return {
            "status": "success",
            "message": f"Processed {len(df)} rows from CSV",
            "transactions_processed": successful,
            "transactions_failed": failed_count + bulk_failed
        }

    except HTTPException:
        raise
    except Exception as e:
        log_error(str(e), "upload_csv")
        raise HTTPException(status_code=500, detail="Error processing CSV file")

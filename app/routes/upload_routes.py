from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Any
from app.auth import get_current_user  # dependency is available now

router = APIRouter(prefix="/api/upload", tags=["upload"])


def process_csv_bytes(file_bytes: bytes) -> dict:
    """
    Placeholder CSV processing for local dev.
    Replace with real parsing / DB inserts as needed.
    """
    # crude row count (works if file ends with newline for rows)
    row_count = file_bytes.count(b"\n")
    return {"status": "ok", "rows": row_count}


@router.post("/csv")
async def upload_csv(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    # accept only csv by filename
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    contents = await file.read()
    result = process_csv_bytes(contents)

    # return immediate result (synchronous). If you need background jobs, add guarded rq usage.
    return {"status": "completed", "result": result}
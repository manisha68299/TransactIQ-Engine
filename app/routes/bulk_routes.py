"""
Background/bulk routes that demonstrate enqueuing CSV import jobs to Redis/RQ.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.auth import get_current_user
from rq import Queue
from redis import Redis
import os
from app.tasks import enqueue_csv_processing

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
q = Queue(connection=redis_conn)


@router.post("/upload/enqueue", tags=["Upload"])
async def upload_enqueue(file: UploadFile = File(...), user=Depends(get_current_user)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    # Save temporarily
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(content)

    # Enqueue background job
    job = q.enqueue("app.tasks.process_csv_file", tmp_path)
    return {"job_id": job.get_id(), "status": "queued"}
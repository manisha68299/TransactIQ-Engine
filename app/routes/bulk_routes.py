# Optional stub to avoid importing rq on Windows.
from fastapi import APIRouter

router = APIRouter(prefix="/api/bulk", tags=["bulk"])

@router.get("/health")
async def bulk_health():
    return {"status": "bulk-stub"}
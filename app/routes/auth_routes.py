from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import authenticate_user, create_access_token
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.main import limiter

router = APIRouter()

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/auth/token", response_model=TokenResponse)
@limiter.limit("10/minute")
async def token(request: TokenRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token}
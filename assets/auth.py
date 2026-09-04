"""
Authentication utilities for TransactIQ Engine.

- Reads SECRET_KEY / ALGORITHM / ACCESS_TOKEN_EXPIRE_MINUTES from app.config
  (falls back to sensible defaults if app.config is not available).
- Provides password hashing/verification (passlib).
- Creates and verifies JWT access tokens (python-jose).
- Exposes FastAPI dependency `get_current_user` (uses OAuth2PasswordBearer).
- Demo-only: includes an in-memory fake_users_db. Replace with real user store for production.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Try to import config values from app.config; fall back to env/defaults
try:
    from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
except Exception:
    SECRET_KEY = os.getenv("SECRET_KEY", None)
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    # minutes; default 24 hours
    try:
        ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))
    except Exception:
        ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Fail fast if no SECRET_KEY configured (recommended for production)
if not SECRET_KEY:
    # We don't raise here to keep development convenient, but log a warning is recommended.
    # For stricter behavior uncomment the next line.
    # raise RuntimeError("SECRET_KEY is not set. Set SECRET_KEY environment variable or app.config.SECRET_KEY")
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# Pydantic model for token payload data
class TokenData(BaseModel):
    username: Optional[str] = None
    exp: Optional[int] = None


# Demo in-memory user store. Replace with DB-backed user model in production.
# Password for 'admin' is 'changeme' (hashed at runtime).
fake_users_db: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("changeme"),
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the stored hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Return bcrypt hash of the password."""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user dict from fake_users_db (replace with DB lookup)."""
    if not username:
        return None
    return fake_users_db.get(username)


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user using the demo store.
    Returns the user dict on success, otherwise None.
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    - `data` should include identifying claims (e.g., {"sub": username}).
    - `expires_delta` overrides ACCESS_TOKEN_EXPIRE_MINUTES when provided.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    FastAPI dependency to retrieve the current user from a JWT token.
    Raises 401 HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub") or payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, exp=payload.get("exp"))
    except JWTError:
        raise credentials_exception

    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    if user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
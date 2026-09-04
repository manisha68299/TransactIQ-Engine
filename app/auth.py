# app/auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

from jose import JWTError, jwt
from passlib.context import CryptContext

# Use pbkdf2_sha256 backend to avoid bcrypt-specific 72-byte limit issues for dev/demo
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Demo in-memory user store. Hashed password generated once.
fake_users_db: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        # create hashed password lazily at import (short demo password)
        "hashed_password": get_password_hash("changeme"),
        "disabled": False,
    }
}

def get_user(username: str) -> Optional[Dict[str, Any]]:
    return fake_users_db.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
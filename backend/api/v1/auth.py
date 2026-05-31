"""
Authentication and authorization endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional
import jwt

from db.database import get_db_session
from config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "email": payload.get("email")}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login")
async def login(email: str, password: str, db: AsyncSession = Depends(get_db_session)):
    """User login endpoint"""
    # Mock implementation - in production, verify against database
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    # For demo - accept any credentials
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires

    payload = {
        "sub": 1,
        "email": email,
        "exp": expire
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """User logout endpoint"""
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(current_user = Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires

    payload = {
        "sub": current_user.get("id"),
        "email": current_user.get("email"),
        "exp": expire
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_MINUTES * 60
    }

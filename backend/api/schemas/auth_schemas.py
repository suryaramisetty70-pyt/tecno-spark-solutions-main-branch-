"""
Authentication schemas for FastAPI
"""
from pydantic import BaseModel
from typing import Optional


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


class CurrentUser(BaseModel):
    user_id: str
    email: Optional[str] = None
    username: Optional[str] = None

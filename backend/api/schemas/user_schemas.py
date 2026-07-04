"""
User management request/response schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GoalStatus(str, Enum):
    """Goal status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class UserProfileRequest(BaseModel):
    """Update user profile request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=256)
    bio: Optional[str] = Field(None, max_length=1000)
    profile_picture_url: Optional[str] = Field(None, max_length=2048)
    phone_number: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=256)
    timezone: Optional[str] = Field(None, max_length=50)


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    profile_picture_url: Optional[str]
    phone_number: Optional[str]
    location: Optional[str]
    timezone: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]


class UserPreferenceRequest(BaseModel):
    """Update user preferences request"""
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    language: Optional[str] = Field(None, max_length=10)
    notifications_email: Optional[bool] = None
    notifications_push: Optional[bool] = None
    notifications_sms: Optional[bool] = None
    email_digest_frequency: Optional[str] = Field(None, pattern="^(daily|weekly|never)$")
    two_factor_enabled: Optional[bool] = None
    show_online_status: Optional[bool] = None
    auto_save_enabled: Optional[bool] = None
    data_export_frequency: Optional[str] = Field(None, pattern="^(never|monthly|quarterly)$")

    @validator('theme', 'language', 'email_digest_frequency', pre=True)
    @classmethod
    def validate_strings(cls, v):
        """Validate string fields"""
        if v is not None and isinstance(v, str):
            v = v.lower().strip()
        return v


class UserPreferenceResponse(BaseModel):
    """User preferences response"""
    user_id: int
    theme: str
    language: str
    notifications_email: bool
    notifications_push: bool
    notifications_sms: bool
    email_digest_frequency: str
    two_factor_enabled: bool
    show_online_status: bool
    auto_save_enabled: bool
    data_export_frequency: str
    updated_at: datetime


class CreateGoalRequest(BaseModel):
    """Create user goal request"""
    goal: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    deadline: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")

    @validator('goal')
    @classmethod
    def validate_goal(cls, v):
        """Validate goal field"""
        if v and not v.strip():
            raise ValueError("Goal cannot be empty")
        return v.strip()


class UpdateGoalRequest(BaseModel):
    """Update user goal request"""
    goal: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    deadline: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[GoalStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


class UserGoalResponse(BaseModel):
    """User goal response"""
    id: int
    user_id: int
    goal: str
    description: Optional[str]
    category: Optional[str]
    deadline: Optional[datetime]
    priority: str
    status: GoalStatus
    progress: int
    created_at: datetime
    updated_at: datetime


class UserSettingsResponse(BaseModel):
    """User settings response (profile + preferences)"""
    profile: UserProfileResponse
    preferences: UserPreferenceResponse
    goals: List[UserGoalResponse]


class AccountDeactivateRequest(BaseModel):
    """Deactivate account request"""
    password: str = Field(..., min_length=1)
    reason: Optional[str] = Field(None, max_length=500)
    send_confirmation_email: bool = True


class AccountDeactivateResponse(BaseModel):
    """Account deactivation response"""
    message: str
    user_id: int
    deactivated_at: datetime
    reactivation_deadline: Optional[datetime]


class DeleteAccountRequest(BaseModel):
    """Delete account request"""
    password: str = Field(..., min_length=1)
    confirm_deletion: bool = Field(..., description="User must confirm deletion")
    export_data: bool = False


class DeleteAccountResponse(BaseModel):
    """Delete account response"""
    message: str
    user_id: int
    deleted_at: datetime


class UserActivityResponse(BaseModel):
    """User activity summary"""
    user_id: int
    total_logins: int
    last_login: Optional[datetime]
    total_goals: int
    completed_goals: int
    active_goals: int
    goals_progress_average: float
    account_created_at: datetime
    account_age_days: int


class ChangeEmailRequest(BaseModel):
    """Change email address request"""
    new_email: EmailStr = Field(...)
    password: str = Field(..., min_length=1)


class ChangeEmailResponse(BaseModel):
    """Change email response"""
    message: str
    old_email: str
    new_email: str
    verification_required: bool


class UserListResponse(BaseModel):
    """User list response (for admin)"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]


class ErrorResponse(BaseModel):
    """Error response"""
    status_code: int
    message: str
    detail: str

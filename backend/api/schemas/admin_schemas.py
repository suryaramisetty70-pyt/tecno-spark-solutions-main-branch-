"""
Admin management request/response schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AdminRole(str, Enum):
    """Admin role levels"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"


class AdminActionType(str, Enum):
    """Admin action types"""
    USER_SUSPEND = "user_suspend"
    USER_BAN = "user_ban"
    USER_DELETE = "user_delete"
    CONTENT_REMOVE = "content_remove"
    WORKFLOW_DISABLE = "workflow_disable"
    AGENT_DISABLE = "agent_disable"
    SYSTEM_CONFIG = "system_config"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class AdminCreateRequest(BaseModel):
    """Create admin request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: AdminRole = Field(default=AdminRole.MODERATOR)
    permissions: List[str] = Field(default_factory=list)


class AdminResponse(BaseModel):
    """Admin response"""
    id: int
    email: str
    username: str
    full_name: str
    role: AdminRole
    is_active: bool
    permissions: List[str]
    created_at: datetime
    updated_at: datetime


class AdminActionRequest(BaseModel):
    """Admin action request"""
    target_user_id: int = Field(...)
    action_type: AdminActionType = Field(...)
    reason: str = Field(..., min_length=10, max_length=1000)
    duration_days: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class AdminActionResponse(BaseModel):
    """Admin action response"""
    id: int
    admin_id: int
    target_user_id: int
    action_type: AdminActionType
    reason: str
    status: str
    executed_at: datetime
    created_at: datetime


class AdminDashboardRequest(BaseModel):
    """Dashboard stats request"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    grouping: str = Field(default="daily")


class AdminDashboardResponse(BaseModel):
    """Dashboard stats response"""
    total_users: int
    active_users: int
    suspended_users: int
    banned_users: int
    new_users_today: int
    total_workflows: int
    total_agents: int
    total_integrations: int
    system_health: float
    api_calls_today: int
    error_rate: float
    generated_at: datetime


class UserManagementRequest(BaseModel):
    """User management request"""
    user_id: int
    status: UserStatus
    reason: Optional[str] = None


class UserManagementResponse(BaseModel):
    """User management response"""
    user_id: int
    previous_status: str
    new_status: str
    changed_at: datetime


class SystemConfigRequest(BaseModel):
    """System configuration request"""
    config_key: str = Field(..., min_length=1, max_length=255)
    config_value: Any
    description: Optional[str] = None


class SystemConfigResponse(BaseModel):
    """System configuration response"""
    id: int
    config_key: str
    config_value: Any
    description: Optional[str]
    updated_at: datetime


class AuditLogResponse(BaseModel):
    """Audit log response"""
    id: int
    admin_id: int
    action: str
    target_id: Optional[int]
    details: Dict[str, Any]
    timestamp: datetime


class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime
    format: str = Field(default="json")


class ReportResponse(BaseModel):
    """Report response"""
    report_id: str
    report_type: str
    status: str
    generated_at: datetime
    file_url: Optional[str]

"""
Notification management request/response schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification type enum"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationStatus(str, Enum):
    """Notification status enum"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    OPENED = "opened"


class ChannelType(str, Enum):
    """Channel type enum"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class NotificationCreateRequest(BaseModel):
    """Create notification request"""
    title: str = Field(..., min_length=1, max_length=256)
    message: str = Field(..., min_length=1, max_length=4000)
    notification_type: NotificationType = Field(...)
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    recipient_id: Optional[int] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    channels: List[ChannelType] = Field(default_factory=list)
    template_id: Optional[int] = None
    template_variables: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    channels: List[str]
    is_read: bool
    read_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    error_message: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class NotificationTemplateCreateRequest(BaseModel):
    """Create notification template request"""
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    notification_type: NotificationType = Field(...)
    subject: Optional[str] = Field(None, max_length=256)
    body: str = Field(..., min_length=1, max_length=4000)
    variables: List[str] = Field(default_factory=list)
    is_active: bool = True


class NotificationTemplateResponse(BaseModel):
    """Notification template response"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    notification_type: NotificationType
    subject: Optional[str]
    body: str
    variables: List[str]
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime


class NotificationPreferenceRequest(BaseModel):
    """Update notification preferences request"""
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    email_digest_frequency: Optional[str] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    do_not_disturb: Optional[bool] = None
    mute_keywords: Optional[List[str]] = None
    notification_channels: Optional[List[ChannelType]] = None


class NotificationPreferenceResponse(BaseModel):
    """Notification preferences response"""
    id: int
    user_id: int
    email_enabled: bool
    push_enabled: bool
    sms_enabled: bool
    in_app_enabled: bool
    email_digest_frequency: str
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    do_not_disturb: bool
    mute_keywords: Optional[List[str]]
    notification_channels: List[str]
    updated_at: datetime


class NotificationScheduleRequest(BaseModel):
    """Schedule notification request"""
    notification_id: int = Field(...)
    scheduled_at: datetime = Field(...)
    timezone: Optional[str] = None


class NotificationScheduleResponse(BaseModel):
    """Notification schedule response"""
    id: int
    notification_id: int
    scheduled_at: datetime
    sent_at: Optional[datetime]
    status: str
    created_at: datetime


class BulkNotificationRequest(BaseModel):
    """Send bulk notification request"""
    title: str = Field(..., min_length=1, max_length=256)
    message: str = Field(..., min_length=1, max_length=4000)
    notification_type: NotificationType = Field(...)
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    recipient_filter: Dict[str, Any] = Field(...)
    channels: List[ChannelType] = Field(default_factory=list)
    scheduled_at: Optional[datetime] = None


class BulkNotificationResponse(BaseModel):
    """Bulk notification response"""
    batch_id: str
    total_recipients: int
    notifications_created: int
    status: str
    created_at: datetime


class NotificationStatsResponse(BaseModel):
    """Notification statistics"""
    user_id: int
    total_notifications: int
    sent_count: int
    failed_count: int
    opened_count: int
    open_rate: float
    unread_count: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]


class NotificationListResponse(BaseModel):
    """Notification list response"""
    total: int
    page: int
    per_page: int
    unread_count: int
    notifications: List[NotificationResponse]


class ErrorResponse(BaseModel):
    """Error response"""
    status_code: int
    message: str
    detail: str

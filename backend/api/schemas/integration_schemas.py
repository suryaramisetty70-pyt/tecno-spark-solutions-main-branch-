"""
Integration management request/response schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntegrationStatus(str, Enum):
    """Integration status enum"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    EXPIRED = "expired"
    PENDING_AUTH = "pending_auth"


class ServiceType(str, Enum):
    """Service type enum"""
    EMAIL = "email"
    MESSAGING = "messaging"
    CALENDAR = "calendar"
    PAYMENT = "payment"
    STORAGE = "storage"
    ANALYTICS = "analytics"
    CRM = "crm"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    COLLABORATION = "collaboration"


class IntegrationConnectRequest(BaseModel):
    """Connect new integration request"""
    service: str = Field(..., min_length=1, max_length=256)
    service_type: ServiceType = Field(...)
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    config: Dict[str, Any] = Field(default_factory=dict)
    api_key: Optional[str] = Field(None, max_length=2048)
    oauth_code: Optional[str] = Field(None, max_length=2048)
    webhook_url: Optional[str] = Field(None, max_length=2048)


class IntegrationResponse(BaseModel):
    """Integration response"""
    id: int
    user_id: int
    service: str
    service_type: ServiceType
    name: str
    description: Optional[str]
    status: IntegrationStatus
    is_active: bool
    auth_method: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]
    synced_at: Optional[datetime]
    expires_at: Optional[datetime]
    error_message: Optional[str]
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class IntegrationUpdateRequest(BaseModel):
    """Update integration request"""
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = Field(None, max_length=2048)


class ServiceCredentialRequest(BaseModel):
    """Store service credential request"""
    credential_type: str = Field(..., min_length=1, max_length=100)
    credential_value: str = Field(..., min_length=1, max_length=4096)
    expires_in_days: Optional[int] = None


class ServiceCredentialResponse(BaseModel):
    """Service credential response"""
    id: int
    integration_id: int
    credential_type: str
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class IntegrationTestRequest(BaseModel):
    """Test integration connection request"""
    config: Optional[Dict[str, Any]] = None


class IntegrationTestResponse(BaseModel):
    """Integration test response"""
    success: bool
    message: str
    error: Optional[str]
    latency_ms: float


class IntegrationSyncRequest(BaseModel):
    """Sync integration data request"""
    sync_type: str = Field(..., min_length=1, max_length=100)
    full_sync: bool = False
    filter_config: Optional[Dict[str, Any]] = None


class IntegrationSyncResponse(BaseModel):
    """Integration sync response"""
    sync_id: str
    integration_id: int
    sync_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    items_synced: int
    items_failed: int
    error_message: Optional[str]


class IntegrationListResponse(BaseModel):
    """Integration list response"""
    total: int
    page: int
    per_page: int
    integrations: List[IntegrationResponse]


class ServiceCatalogResponse(BaseModel):
    """Available service response"""
    id: int
    service_name: str
    service_type: ServiceType
    description: str
    logo_url: Optional[str]
    auth_methods: List[str]
    documentation_url: Optional[str]
    is_oauth2: bool
    oauth_scopes: Optional[List[str]]
    required_fields: List[str]
    optional_fields: List[str]
    rate_limit: Optional[str]
    pricing: Optional[str]
    status: str


class WebhookEventRequest(BaseModel):
    """Webhook event request"""
    event_type: str = Field(..., min_length=1, max_length=256)
    event_data: Dict[str, Any] = Field(...)
    timestamp: Optional[datetime] = None


class WebhookLogResponse(BaseModel):
    """Webhook log response"""
    id: int
    integration_id: int
    event_type: str
    status: str
    status_code: Optional[int]
    request_payload: Dict[str, Any]
    response_payload: Optional[Dict[str, Any]]
    error_message: Optional[str]
    latency_ms: float
    created_at: datetime


class IntegrationMetricsResponse(BaseModel):
    """Integration metrics"""
    integration_id: int
    service_name: str
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    last_sync: Optional[datetime]
    items_synced_total: int
    webhook_calls_total: int
    webhook_calls_failed: int
    average_sync_time_seconds: float
    average_webhook_latency_ms: float


class ErrorResponse(BaseModel):
    """Error response"""
    status_code: int
    message: str
    detail: str

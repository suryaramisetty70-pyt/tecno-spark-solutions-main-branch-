"""
Agent management request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    ERROR = "error"


class AgentCapability(str, Enum):
    """Agent capabilities"""
    EMAIL = "email"
    MESSAGING = "messaging"
    SCHEDULING = "scheduling"
    RESEARCH = "research"
    AUTOMATION = "automation"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    PERSONALIZATION = "personalization"
    LEARNING = "learning"
    CONTENT = "content"


class AgentRequest(BaseModel):
    """Register/create new agent request"""
    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(..., min_length=1, max_length=2000)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    capabilities: List[AgentCapability] = Field(..., min_items=1)
    config: Optional[Dict[str, Any]] = Field(None)
    enabled_by_default: bool = True
    requires_authentication: bool = True
    author: Optional[str] = Field(None, max_length=256)
    documentation_url: Optional[str] = Field(None, max_length=2048)


class AgentResponse(BaseModel):
    """Agent response"""
    id: int
    name: str
    description: str
    version: str
    capabilities: List[str]
    status: AgentStatus
    enabled_by_default: bool
    requires_authentication: bool
    author: Optional[str]
    documentation_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    downloads: int
    rating: float
    total_reviews: int


class AgentConfigRequest(BaseModel):
    """Update agent configuration request"""
    config: Dict[str, Any] = Field(...)


class AgentEnableRequest(BaseModel):
    """Enable/disable agent for user request"""
    enabled: bool = Field(...)
    permissions: Optional[List[str]] = Field(None)


class AgentInstanceResponse(BaseModel):
    """Agent instance for user"""
    id: int
    user_id: int
    agent_id: int
    agent_name: str
    status: AgentStatus
    enabled: bool
    config: Optional[Dict[str, Any]]
    permissions: List[str]
    last_used: Optional[datetime]
    usage_count: int
    created_at: datetime
    updated_at: datetime


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    agent_id: int
    agent_name: str
    status: AgentStatus
    uptime_percentage: float
    last_health_check: datetime
    error_count_24h: int
    execution_count_24h: int
    average_execution_time_ms: float


class AgentMetricsResponse(BaseModel):
    """Agent metrics"""
    agent_id: int
    agent_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time_ms: float
    success_rate: float
    most_common_error: Optional[str]
    last_executed: Optional[datetime]
    daily_executions: List[Dict[str, Any]]


class AgentListResponse(BaseModel):
    """List of agents"""
    total: int
    page: int
    per_page: int
    agents: List[AgentResponse]


class UserAgentListResponse(BaseModel):
    """List of user's enabled agents"""
    total: int
    enabled_count: int
    disabled_count: int
    agents: List[AgentInstanceResponse]


class AgentExecutionRequest(BaseModel):
    """Execute agent request"""
    agent_id: int = Field(...)
    input_data: Dict[str, Any] = Field(...)
    async_execution: bool = False


class AgentExecutionResponse(BaseModel):
    """Agent execution response"""
    execution_id: str
    agent_id: int
    agent_name: str
    status: str
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time_ms: float
    timestamp: datetime


class AgentToolRequest(BaseModel):
    """Register tool for agent"""
    tool_name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(..., min_length=1, max_length=2000)
    input_schema: Dict[str, Any] = Field(...)
    output_schema: Dict[str, Any] = Field(...)
    requires_auth: bool = False


class AgentToolResponse(BaseModel):
    """Tool response"""
    id: int
    agent_id: int
    tool_name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    requires_auth: bool
    created_at: datetime


class AgentPermissionRequest(BaseModel):
    """Agent permission request"""
    permission: str = Field(..., min_length=1, max_length=256)


class ErrorResponse(BaseModel):
    """Error response"""
    status_code: int
    message: str
    detail: str

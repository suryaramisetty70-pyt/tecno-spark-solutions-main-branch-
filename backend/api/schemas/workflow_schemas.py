"""
Workflow management request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Workflow status enum"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    ERROR = "error"


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class TriggerType(str, Enum):
    """Trigger type enum"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    CONDITIONAL = "conditional"


class StepType(str, Enum):
    """Step type enum"""
    AGENT = "agent"
    CONDITION = "condition"
    DELAY = "delay"
    WEBHOOK = "webhook"
    PARALLEL = "parallel"
    LOOP = "loop"


class WorkflowCreateRequest(BaseModel):
    """Create workflow request"""
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    enabled: bool = True


class WorkflowResponse(BaseModel):
    """Workflow response"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    status: WorkflowStatus
    enabled: bool
    step_count: int
    execution_count: int
    success_count: int
    failure_count: int
    last_executed: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class WorkflowStepCreateRequest(BaseModel):
    """Create workflow step request"""
    workflow_id: int = Field(...)
    step_order: int = Field(..., ge=1)
    step_type: StepType = Field(...)
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    config: Dict[str, Any] = Field(default_factory=dict)
    agent_id: Optional[int] = None
    condition: Optional[str] = None
    input_mapping: Optional[Dict[str, str]] = None
    output_mapping: Optional[Dict[str, str]] = None
    on_success_next_step: Optional[int] = None
    on_failure_next_step: Optional[int] = None
    retry_count: int = Field(0, ge=0)
    retry_delay_seconds: int = Field(0, ge=0)
    timeout_seconds: Optional[int] = None


class WorkflowStepResponse(BaseModel):
    """Workflow step response"""
    id: int
    workflow_id: int
    step_order: int
    step_type: StepType
    name: str
    description: Optional[str]
    config: Dict[str, Any]
    agent_id: Optional[int]
    condition: Optional[str]
    input_mapping: Optional[Dict[str, str]]
    output_mapping: Optional[Dict[str, str]]
    on_success_next_step: Optional[int]
    on_failure_next_step: Optional[int]
    retry_count: int
    retry_delay_seconds: int
    timeout_seconds: Optional[int]
    created_at: datetime
    updated_at: datetime


class TriggerCreateRequest(BaseModel):
    """Create workflow trigger request"""
    workflow_id: int = Field(...)
    trigger_type: TriggerType = Field(...)
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    condition: Optional[str] = None
    schedule_cron: Optional[str] = None
    event_type: Optional[str] = None
    webhook_path: Optional[str] = None
    enabled: bool = True
    input_data: Optional[Dict[str, Any]] = None


class TriggerResponse(BaseModel):
    """Trigger response"""
    id: int
    workflow_id: int
    trigger_type: TriggerType
    name: str
    description: Optional[str]
    condition: Optional[str]
    schedule_cron: Optional[str]
    event_type: Optional[str]
    webhook_path: Optional[str]
    enabled: bool
    last_triggered: Optional[datetime]
    trigger_count: int
    created_at: datetime
    updated_at: datetime


class WorkflowExecutionCreateRequest(BaseModel):
    """Execute workflow request"""
    workflow_id: int = Field(...)
    trigger_id: Optional[int] = None
    input_data: Optional[Dict[str, Any]] = None
    run_as_async: bool = False


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response"""
    id: int
    workflow_id: int
    workflow_name: str
    user_id: int
    trigger_id: Optional[int]
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    step_executions_count: int
    current_step: Optional[int]
    progress_percentage: float


class StepExecutionResponse(BaseModel):
    """Step execution response"""
    id: int
    execution_id: int
    step_id: int
    step_order: int
    step_name: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_attempt: int


class WorkflowUpdateRequest(BaseModel):
    """Update workflow request"""
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    enabled: Optional[bool] = None
    status: Optional[WorkflowStatus] = None


class WorkflowListResponse(BaseModel):
    """Workflow list response"""
    total: int
    page: int
    per_page: int
    workflows: List[WorkflowResponse]


class WorkflowExecutionListResponse(BaseModel):
    """Workflow execution list response"""
    total: int
    page: int
    per_page: int
    executions: List[WorkflowExecutionResponse]


class WorkflowStatsResponse(BaseModel):
    """Workflow statistics response"""
    workflow_id: int
    workflow_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration_seconds: float
    success_rate: float
    last_execution: Optional[datetime]
    most_common_error: Optional[str]


class ErrorResponse(BaseModel):
    """Error response"""
    status_code: int
    message: str
    detail: str

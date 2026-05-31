"""
Analytics and reporting schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TimeRange(str, Enum):
    """Time range for analytics"""
    LAST_24H = "24h"
    LAST_7D = "7d"
    LAST_30D = "30d"
    LAST_90D = "90d"


class MetricType(str, Enum):
    """Metric types"""
    USER_ACTIVITY = "user_activity"
    WORKFLOW_EXECUTION = "workflow_execution"
    AGENT_USAGE = "agent_usage"
    INTEGRATION_USAGE = "integration_usage"
    API_PERFORMANCE = "api_performance"


class ChartType(str, Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class AnalyticsDataPoint(BaseModel):
    """Analytics data point"""
    timestamp: datetime
    value: float
    label: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricResponse(BaseModel):
    """Metric response"""
    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    unit: str
    change_percentage: Optional[float] = None
    trend: str
    timestamp: datetime


class ChartDataResponse(BaseModel):
    """Chart data response"""
    chart_id: str
    chart_type: ChartType
    title: str
    description: Optional[str]
    data_points: List[AnalyticsDataPoint]
    generated_at: datetime


class DashboardResponse(BaseModel):
    """Dashboard response"""
    dashboard_id: str
    user_id: int
    title: str
    metrics: List[MetricResponse]
    charts: List[ChartDataResponse]
    generated_at: datetime


class UserAnalyticsResponse(BaseModel):
    """User analytics response"""
    user_id: int
    total_logins: int
    active_days: int
    last_login: datetime
    average_session_duration: float
    total_workflows_created: int
    total_workflows_executed: int
    workflows_success_rate: float
    total_agents_used: int
    integrations_connected: int


class WorkflowAnalyticsResponse(BaseModel):
    """Workflow analytics response"""
    workflow_id: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    average_execution_time: float
    total_processing_time: float
    error_count: int
    last_executed: datetime


class AgentAnalyticsResponse(BaseModel):
    """Agent analytics response"""
    agent_id: int
    total_invocations: int
    successful_invocations: int
    failed_invocations: int
    success_rate: float
    average_response_time: float
    total_users: int
    last_used: datetime


class IntegrationAnalyticsResponse(BaseModel):
    """Integration analytics response"""
    integration_id: int
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    sync_success_rate: float
    average_sync_time: float
    total_data_transferred: int
    last_sync: datetime


class APIAnalyticsResponse(BaseModel):
    """API analytics response"""
    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    average_response_time: float
    p95_response_time: float
    p99_response_time: float


class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: str = Field(..., min_length=1, max_length=100)
    time_range: TimeRange = Field(default=TimeRange.LAST_30D)
    metrics: List[str] = Field(default_factory=list)
    format: str = Field(default="json")


class ReportResponse(BaseModel):
    """Report response"""
    report_id: str
    report_type: str
    time_range: str
    status: str
    generated_at: datetime
    download_url: Optional[str] = None


class HealthMetricsResponse(BaseModel):
    """System health metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    database_health: str
    api_health: str
    cache_health: str
    overall_health: float
    last_updated: datetime

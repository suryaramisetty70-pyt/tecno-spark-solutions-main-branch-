"""
Analytics and reporting API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_session
from api.schemas.analytics_schemas import (
    UserAnalyticsResponse, WorkflowAnalyticsResponse, AgentAnalyticsResponse,
    IntegrationAnalyticsResponse, APIAnalyticsResponse, DashboardResponse,
    ReportRequest, ReportResponse, HealthMetricsResponse
)
from services.analytics_service import AnalyticsService
from api.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/user", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    time_range: str = Query("30d"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user analytics"""
    try:
        analytics = await AnalyticsService.get_user_analytics(db, current_user.id, time_range)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=WorkflowAnalyticsResponse)
async def get_workflow_analytics(
    workflow_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get workflow analytics"""
    try:
        analytics = await AnalyticsService.get_workflow_analytics(db, workflow_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}", response_model=AgentAnalyticsResponse)
async def get_agent_analytics(
    agent_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get agent analytics"""
    try:
        analytics = await AnalyticsService.get_agent_analytics(db, agent_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/integrations/{integration_id}", response_model=IntegrationAnalyticsResponse)
async def get_integration_analytics(
    integration_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get integration analytics"""
    try:
        analytics = await AnalyticsService.get_integration_analytics(db, integration_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api", response_model=list)
async def get_api_analytics(
    endpoint: str = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get API analytics"""
    try:
        analytics = await AnalyticsService.get_api_analytics(db, endpoint)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    time_range: str = Query("30d"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get analytics dashboard"""
    try:
        dashboard = await AnalyticsService.get_dashboard(db, current_user.id, time_range)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports", response_model=ReportResponse)
async def generate_report(
    report_request: ReportRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate analytics report"""
    try:
        report = await AnalyticsService.generate_report(
            db, report_request.report_type, report_request.time_range.value,
            report_request.metrics
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthMetricsResponse)
async def get_health_metrics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get system health metrics"""
    try:
        health = await AnalyticsService.get_health_metrics(db)
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeseries")
async def get_timeseries(
    metric_type: str = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    granularity: str = Query(default="daily"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get time series data"""
    try:
        data = await AnalyticsService.get_time_series_data(
            db, metric_type, start_date, end_date, granularity
        )
        return {
            "metric_type": metric_type,
            "granularity": granularity,
            "start_date": start_date,
            "end_date": end_date,
            "data_points": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

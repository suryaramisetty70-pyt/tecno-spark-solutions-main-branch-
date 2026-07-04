"""
Admin management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db.database import get_db_session
from api.schemas.admin_schemas import (
    AdminCreateRequest, AdminResponse, AdminActionRequest, AdminActionResponse,
    AdminDashboardResponse, UserManagementRequest, SystemConfigRequest, AuditLogResponse
)
from services.admin_service import AdminService
from api.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/admins", response_model=AdminResponse, status_code=201)
async def create_admin(
    admin_data: AdminCreateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create new admin user"""
    try:
        admin = await AdminService.create_admin(db, admin_data)
        return admin
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admins", response_model=list)
async def list_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List all admins"""
    try:
        admins = await AdminService.list_admins(db, skip, limit)
        return admins
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/suspend", response_model=AdminActionResponse)
async def suspend_user(
    request: UserManagementRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Suspend user account"""
    try:
        result = await AdminService.suspend_user(
            db, current_user.id, request.user_id, request.reason or "No reason provided"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/ban", response_model=AdminActionResponse)
async def ban_user(
    request: UserManagementRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Ban user permanently"""
    try:
        result = await AdminService.ban_user(
            db, current_user.id, request.user_id, request.reason or "No reason provided"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/status")
async def get_user_status(
    user_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user account status"""
    try:
        status = await AdminService.get_user_status(db, user_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_dashboard(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get admin dashboard statistics"""
    try:
        dashboard = await AdminService.get_admin_dashboard(db, start_date, end_date)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actions", response_model=AdminActionResponse)
async def record_action(
    action_data: AdminActionRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Record admin action"""
    try:
        result = await AdminService.record_admin_action(db, current_user.id, action_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-logs", response_model=list)
async def get_audit_logs(
    admin_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get audit logs"""
    try:
        logs = await AdminService.get_audit_logs(db, admin_id, skip, limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def set_config(
    config_data: SystemConfigRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Set system configuration"""
    try:
        result = await AdminService.set_system_config(
            db, config_data.config_key, config_data.config_value, config_data.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{config_key}")
async def get_config(
    config_key: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get system configuration"""
    try:
        config = await AdminService.get_system_config(db, config_key)
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports")
async def generate_report(
    report_type: str = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate system report"""
    try:
        report = await AdminService.generate_report(db, report_type, start_date, end_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

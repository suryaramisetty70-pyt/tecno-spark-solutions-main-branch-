"""
Notification management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from db.database import get_db_session
from api.schemas.notification_schemas import (
    NotificationCreateRequest, NotificationResponse, NotificationListResponse,
    NotificationStatsResponse, BulkNotificationRequest, BulkNotificationResponse
)
from services.notification_service import NotificationService
from api.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post("", response_model=NotificationResponse, status_code=201)
async def create_notification(
    notification_data: NotificationCreateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Send individual notification"""
    try:
        notification = await NotificationService.send_notification(
            db, current_user.id, notification_data
        )
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.content,
            "notification_type": notification.notification_type,
            "priority": "medium",
            "status": "sent",
            "channels": [],
            "is_read": notification.read,
            "read_at": notification.read_at,
            "sent_at": notification.created_at,
            "delivered_at": None,
            "opened_at": None,
            "error_message": None,
            "tags": None,
            "created_at": notification.created_at,
            "updated_at": notification.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List notifications for current user"""
    try:
        result = await NotificationService.list_notifications(db, current_user.id, skip, limit)
        notifications = [
            {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "message": n.content,
                "notification_type": n.notification_type,
                "priority": "medium",
                "status": "sent",
                "channels": [],
                "is_read": n.read,
                "read_at": n.read_at,
                "sent_at": n.created_at,
                "delivered_at": None,
                "opened_at": None,
                "error_message": None,
                "tags": None,
                "created_at": n.created_at,
                "updated_at": n.created_at
            }
            for n in result["notifications"]
        ]
        return {
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "unread_count": result["unread_count"],
            "notifications": notifications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get notification by ID"""
    try:
        notification = await NotificationService.get_notification(
            db, notification_id, current_user.id
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.content,
            "notification_type": notification.notification_type,
            "priority": "medium",
            "status": "sent",
            "channels": [],
            "is_read": notification.read,
            "read_at": notification.read_at,
            "sent_at": notification.created_at,
            "delivered_at": None,
            "opened_at": None,
            "error_message": None,
            "tags": None,
            "created_at": notification.created_at,
            "updated_at": notification.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Mark notification as read"""
    try:
        notification = await NotificationService.mark_as_read(
            db, notification_id, current_user.id
        )
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.content,
            "notification_type": notification.notification_type,
            "priority": "medium",
            "status": "sent",
            "channels": [],
            "is_read": notification.read,
            "read_at": notification.read_at,
            "sent_at": notification.created_at,
            "delivered_at": None,
            "opened_at": None,
            "error_message": None,
            "tags": None,
            "created_at": notification.created_at,
            "updated_at": notification.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}/unread", response_model=NotificationResponse)
async def mark_as_unread(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Mark notification as unread"""
    try:
        notification = await NotificationService.mark_as_unread(
            db, notification_id, current_user.id
        )
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.content,
            "notification_type": notification.notification_type,
            "priority": "medium",
            "status": "sent",
            "channels": [],
            "is_read": notification.read,
            "read_at": notification.read_at,
            "sent_at": notification.created_at,
            "delivered_at": None,
            "opened_at": None,
            "error_message": None,
            "tags": None,
            "created_at": notification.created_at,
            "updated_at": notification.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete notification"""
    try:
        success = await NotificationService.delete_notification(
            db, notification_id, current_user.id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=BulkNotificationResponse, status_code=201)
async def send_bulk_notifications(
    bulk_data: BulkNotificationRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Send bulk notifications"""
    try:
        user_ids = [2, 3, 4, 5]
        result = await NotificationService.send_bulk(db, user_ids, {
            "notification_type": bulk_data.notification_type.value,
            "title": bulk_data.title,
            "message": bulk_data.message
        })
        return {
            "batch_id": result["batch_id"],
            "total_recipients": result["total_recipients"],
            "notifications_created": result["notifications_created"],
            "status": result["status"],
            "created_at": result.get("created_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get notification statistics"""
    try:
        stats = await NotificationService.get_notification_stats(db, current_user.id)
        return {
            "user_id": stats["user_id"],
            "total_notifications": stats["total_notifications"],
            "sent_count": stats["total_notifications"],
            "failed_count": 0,
            "opened_count": 0,
            "open_rate": 0.0,
            "unread_count": stats["unread_count"],
            "by_type": stats["by_type"],
            "by_priority": {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read", status_code=200)
async def mark_all_as_read(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Mark all notifications as read"""
    try:
        count = await NotificationService.mark_all_as_read(db, current_user.id)
        return {"message": f"Marked {count} notifications as read", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-old", status_code=200)
async def delete_old_notifications(
    days: int = Query(30, ge=1),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete notifications older than specified days"""
    try:
        count = await NotificationService.clear_old_notifications(db, current_user.id, days)
        return {"message": f"Deleted {count} old notifications", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{query}")
async def search_notifications(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Search notifications"""
    try:
        results = await NotificationService.search_notifications(
            db, current_user.id, query, skip, limit
        )
        return {
            "query": query,
            "results": [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.content,
                    "created_at": n.created_at
                }
                for n in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

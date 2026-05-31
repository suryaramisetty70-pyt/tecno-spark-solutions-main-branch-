"""
Notification management service - business logic for notifications
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
import uuid

from db.models import Notification, User
from api.schemas.notification_schemas import (
    NotificationCreateRequest, NotificationPreferenceRequest,
    NotificationStatus, NotificationType, NotificationPriority
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Notification management service"""

    @staticmethod
    async def send_notification(
        db: AsyncSession, user_id: int, notification_data: NotificationCreateRequest
    ) -> Notification:
        """Send individual notification"""
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_data.notification_type.value,
                title=notification_data.title,
                content=notification_data.message,
                read=False,
                created_at=datetime.utcnow()
            )
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            return notification
        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending notification: {e}")
            raise

    @staticmethod
    async def get_notification(db: AsyncSession, notification_id: int, user_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        try:
            result = await db.execute(
                select(Notification).where(
                    Notification.id == notification_id
                ).where(Notification.user_id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching notification: {e}")
            raise

    @staticmethod
    async def list_notifications(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> Dict[str, Any]:
        """List notifications for user with pagination"""
        try:
            total_result = await db.execute(
                select(Notification).where(Notification.user_id == user_id)
            )
            total = len(total_result.scalars().all())

            result = await db.execute(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            notifications = result.scalars().all()

            unread_result = await db.execute(
                select(Notification).where(
                    Notification.user_id == user_id
                ).where(Notification.read == False)
            )
            unread_count = len(unread_result.scalars().all())

            return {
                "total": total,
                "page": skip // limit + 1,
                "per_page": limit,
                "unread_count": unread_count,
                "notifications": notifications
            }
        except Exception as e:
            logger.error(f"Error listing notifications: {e}")
            raise

    @staticmethod
    async def mark_as_read(db: AsyncSession, notification_id: int, user_id: int) -> Notification:
        """Mark notification as read"""
        try:
            notification = await NotificationService.get_notification(db, notification_id, user_id)
            if not notification:
                raise ValueError("Notification not found")

            notification.read = True
            notification.read_at = datetime.utcnow()
            await db.commit()
            await db.refresh(notification)
            return notification
        except Exception as e:
            await db.rollback()
            logger.error(f"Error marking notification as read: {e}")
            raise

    @staticmethod
    async def mark_as_unread(db: AsyncSession, notification_id: int, user_id: int) -> Notification:
        """Mark notification as unread"""
        try:
            notification = await NotificationService.get_notification(db, notification_id, user_id)
            if not notification:
                raise ValueError("Notification not found")

            notification.read = False
            notification.read_at = None
            await db.commit()
            await db.refresh(notification)
            return notification
        except Exception as e:
            await db.rollback()
            logger.error(f"Error marking notification as unread: {e}")
            raise

    @staticmethod
    async def delete_notification(db: AsyncSession, notification_id: int, user_id: int) -> bool:
        """Delete notification"""
        try:
            notification = await NotificationService.get_notification(db, notification_id, user_id)
            if not notification:
                raise ValueError("Notification not found")

            await db.delete(notification)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting notification: {e}")
            raise

    @staticmethod
    async def delete_all_read_notifications(db: AsyncSession, user_id: int) -> int:
        """Delete all read notifications for user"""
        try:
            result = await db.execute(
                select(Notification).where(
                    Notification.user_id == user_id
                ).where(Notification.read == True)
            )
            notifications = result.scalars().all()
            count = len(notifications)

            for notification in notifications:
                await db.delete(notification)

            await db.commit()
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting read notifications: {e}")
            raise

    @staticmethod
    async def send_bulk(
        db: AsyncSession, user_ids: List[int], notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send bulk notifications"""
        try:
            batch_id = str(uuid.uuid4())
            created_count = 0

            for user_id in user_ids:
                notification = Notification(
                    user_id=user_id,
                    notification_type=notification_data.get("notification_type", "info"),
                    title=notification_data.get("title", ""),
                    content=notification_data.get("message", ""),
                    read=False,
                    created_at=datetime.utcnow()
                )
                db.add(notification)
                created_count += 1

            await db.commit()
            return {
                "batch_id": batch_id,
                "total_recipients": len(user_ids),
                "notifications_created": created_count,
                "status": "completed"
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending bulk notifications: {e}")
            raise

    @staticmethod
    async def get_notification_stats(db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get notification statistics for user"""
        try:
            all_result = await db.execute(
                select(Notification).where(Notification.user_id == user_id)
            )
            all_notifications = all_result.scalars().all()

            total = len(all_notifications)
            unread = len([n for n in all_notifications if not n.read])
            by_type = {}

            for notification in all_notifications:
                notif_type = notification.notification_type
                by_type[notif_type] = by_type.get(notif_type, 0) + 1

            return {
                "user_id": user_id,
                "total_notifications": total,
                "unread_count": unread,
                "by_type": by_type,
                "stats_generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching notification stats: {e}")
            raise

    @staticmethod
    async def clear_old_notifications(db: AsyncSession, user_id: int, days: int = 30) -> int:
        """Clear notifications older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await db.execute(
                select(Notification).where(
                    Notification.user_id == user_id
                ).where(Notification.created_at < cutoff_date)
            )
            old_notifications = result.scalars().all()
            count = len(old_notifications)

            for notification in old_notifications:
                await db.delete(notification)

            await db.commit()
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"Error clearing old notifications: {e}")
            raise

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: int) -> int:
        """Mark all notifications as read"""
        try:
            result = await db.execute(
                select(Notification).where(
                    Notification.user_id == user_id
                ).where(Notification.read == False)
            )
            unread_notifications = result.scalars().all()
            count = len(unread_notifications)

            for notification in unread_notifications:
                notification.read = True
                notification.read_at = datetime.utcnow()

            await db.commit()
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"Error marking all as read: {e}")
            raise

    @staticmethod
    async def search_notifications(
        db: AsyncSession, user_id: int, query: str, skip: int = 0, limit: int = 20
    ) -> List[Notification]:
        """Search notifications by title or content"""
        try:
            result = await db.execute(
                select(Notification).where(
                    Notification.user_id == user_id
                ).where(
                    (Notification.title.ilike(f"%{query}%")) |
                    (Notification.content.ilike(f"%{query}%"))
                ).order_by(Notification.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching notifications: {e}")
            raise

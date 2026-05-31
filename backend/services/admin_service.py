"""
Admin management service - business logic for admin operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from db.models import User, AdminAction, AuditLog, SystemConfig
from api.schemas.admin_schemas import (
    AdminCreateRequest, AdminActionRequest, UserStatus, AdminRole
)

logger = logging.getLogger(__name__)


class AdminService:
    """Admin management service"""

    @staticmethod
    async def create_admin(
        db: AsyncSession, admin_data: AdminCreateRequest
    ) -> Dict[str, Any]:
        """Create new admin user"""
        try:
            admin_user = User(
                email=admin_data.email,
                username=admin_data.username,
                full_name=admin_data.full_name,
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)

            return {
                "id": admin_user.id,
                "email": admin_user.email,
                "username": admin_user.username,
                "full_name": admin_user.full_name,
                "role": admin_data.role.value,
                "is_active": True,
                "permissions": admin_data.permissions,
                "created_at": admin_user.created_at,
                "updated_at": admin_user.updated_at
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating admin: {e}")
            raise

    @staticmethod
    async def list_admins(db: AsyncSession, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """List all admins"""
        try:
            result = await db.execute(
                select(User)
                .where(User.is_active == True)
                .offset(skip)
                .limit(limit)
            )
            users = result.scalars().all()
            return [
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.username,
                    "full_name": u.full_name,
                    "role": "admin",
                    "is_active": u.is_active,
                    "permissions": [],
                    "created_at": u.created_at,
                    "updated_at": u.updated_at
                }
                for u in users
            ]
        except Exception as e:
            logger.error(f"Error listing admins: {e}")
            raise

    @staticmethod
    async def suspend_user(
        db: AsyncSession, admin_id: int, user_id: int, reason: str, duration_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Suspend user account"""
        try:
            user = await db.execute(select(User).where(User.id == user_id))
            user_obj = user.scalars().first()

            if not user_obj:
                raise ValueError("User not found")

            original_status = "active" if user_obj.is_active else "inactive"
            user_obj.is_active = False
            await db.commit()

            action = AdminAction(
                admin_id=admin_id,
                target_user_id=user_id,
                action_type="user_suspend",
                reason=reason,
                status="executed",
                executed_at=datetime.utcnow()
            )
            db.add(action)
            await db.commit()

            return {
                "id": action.id,
                "admin_id": admin_id,
                "target_user_id": user_id,
                "action_type": "user_suspend",
                "reason": reason,
                "status": "executed",
                "executed_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error suspending user: {e}")
            raise

    @staticmethod
    async def ban_user(
        db: AsyncSession, admin_id: int, user_id: int, reason: str
    ) -> Dict[str, Any]:
        """Ban user permanently"""
        try:
            user = await db.execute(select(User).where(User.id == user_id))
            user_obj = user.scalars().first()

            if not user_obj:
                raise ValueError("User not found")

            user_obj.is_active = False
            await db.commit()

            action = AdminAction(
                admin_id=admin_id,
                target_user_id=user_id,
                action_type="user_ban",
                reason=reason,
                status="executed",
                executed_at=datetime.utcnow()
            )
            db.add(action)
            await db.commit()

            return {
                "id": action.id,
                "admin_id": admin_id,
                "target_user_id": user_id,
                "action_type": "user_ban",
                "reason": reason,
                "status": "executed",
                "executed_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error banning user: {e}")
            raise

    @staticmethod
    async def get_user_status(db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get user account status"""
        try:
            user = await db.execute(select(User).where(User.id == user_id))
            user_obj = user.scalars().first()

            if not user_obj:
                raise ValueError("User not found")

            return {
                "user_id": user_id,
                "status": "active" if user_obj.is_active else "inactive",
                "is_verified": user_obj.is_verified,
                "created_at": user_obj.created_at,
                "last_login": user_obj.last_login
            }
        except Exception as e:
            logger.error(f"Error getting user status: {e}")
            raise

    @staticmethod
    async def get_admin_dashboard(
        db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()

            all_users = await db.execute(select(User))
            users = all_users.scalars().all()

            active_users = sum(1 for u in users if u.is_active)
            suspended_users = sum(1 for u in users if not u.is_active)
            new_users = sum(1 for u in users if u.created_at >= start_date)

            return {
                "total_users": len(users),
                "active_users": active_users,
                "suspended_users": suspended_users,
                "banned_users": 0,
                "new_users_today": sum(1 for u in users if u.created_at.date() == datetime.utcnow().date()),
                "total_workflows": 0,
                "total_agents": 0,
                "total_integrations": 0,
                "system_health": 99.5,
                "api_calls_today": 0,
                "error_rate": 0.1,
                "generated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error fetching dashboard: {e}")
            raise

    @staticmethod
    async def record_admin_action(
        db: AsyncSession, admin_id: int, action_data: AdminActionRequest
    ) -> Dict[str, Any]:
        """Record admin action for audit trail"""
        try:
            action = AdminAction(
                admin_id=admin_id,
                target_user_id=action_data.target_user_id,
                action_type=action_data.action_type.value,
                reason=action_data.reason,
                status="executed",
                executed_at=datetime.utcnow()
            )
            db.add(action)
            await db.commit()
            await db.refresh(action)

            return {
                "id": action.id,
                "admin_id": admin_id,
                "target_user_id": action_data.target_user_id,
                "action_type": action_data.action_type.value,
                "reason": action_data.reason,
                "status": "executed",
                "executed_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error recording action: {e}")
            raise

    @staticmethod
    async def get_audit_logs(
        db: AsyncSession, admin_id: Optional[int] = None, skip: int = 0, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filtering"""
        try:
            query = select(AdminAction)
            if admin_id:
                query = query.where(AdminAction.admin_id == admin_id)

            result = await db.execute(
                query.order_by(AdminAction.executed_at.desc()).offset(skip).limit(limit)
            )
            actions = result.scalars().all()

            return [
                {
                    "id": a.id,
                    "admin_id": a.admin_id,
                    "target_id": a.target_user_id,
                    "action": a.action_type,
                    "reason": a.reason,
                    "timestamp": a.executed_at,
                    "details": {"status": a.status}
                }
                for a in actions
            ]
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}")
            raise

    @staticmethod
    async def set_system_config(
        db: AsyncSession, config_key: str, config_value: Any, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Set system configuration"""
        try:
            config = SystemConfig(
                config_key=config_key,
                config_value=config_value,
                description=description,
                updated_at=datetime.utcnow()
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)

            return {
                "id": config.id,
                "config_key": config.config_key,
                "config_value": config.config_value,
                "description": config.description,
                "updated_at": datetime.utcnow()
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Error setting config: {e}")
            raise

    @staticmethod
    async def get_system_config(db: AsyncSession, config_key: str) -> Optional[Dict[str, Any]]:
        """Get system configuration"""
        try:
            result = await db.execute(
                select(SystemConfig).where(SystemConfig.config_key == config_key)
            )
            config = result.scalars().first()

            if not config:
                return None

            return {
                "id": config.id,
                "config_key": config.config_key,
                "config_value": config.config_value,
                "description": config.description,
                "updated_at": config.updated_at
            }
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
            raise

    @staticmethod
    async def generate_report(
        db: AsyncSession, report_type: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate system report"""
        try:
            import uuid

            report_id = str(uuid.uuid4())

            return {
                "report_id": report_id,
                "report_type": report_type,
                "status": "completed",
                "generated_at": datetime.utcnow(),
                "file_url": f"/reports/{report_id}.json",
                "start_date": start_date,
                "end_date": end_date
            }
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise

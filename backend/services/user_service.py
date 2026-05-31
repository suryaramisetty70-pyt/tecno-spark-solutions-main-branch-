"""
User management service - business logic for user operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from db.models import User, UserProfile, UserPreference, UserGoal
from api.schemas.user_schemas import (
    UserProfileRequest, UserPreferenceRequest, CreateGoalRequest,
    UpdateGoalRequest, GoalStatus, AccountDeactivateRequest, DeleteAccountRequest
)
from utils.password_utils import verify_password, hash_password

logger = logging.getLogger(__name__)


class UserService:
    """User management service"""

    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user profile by ID"""
        try:
            result = await db.execute(
                select(User).where(User.id == user_id).where(User.is_active == True)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            raise

    @staticmethod
    async def update_user_profile(
        db: AsyncSession, user_id: int, profile_data: UserProfileRequest
    ) -> User:
        """Update user profile"""
        try:
            user = await UserService.get_user_profile(db, user_id)
            if not user:
                raise ValueError("User not found")

            user_profile = await db.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = user_profile.scalars().first()

            if not profile:
                profile = UserProfile(user_id=user_id)
                db.add(profile)

            # Update user fields
            if profile_data.full_name:
                user.full_name = profile_data.full_name

            # Update profile fields
            if profile_data.bio is not None:
                profile.bio = profile_data.bio
            if profile_data.profile_picture_url is not None:
                profile.profile_picture_url = profile_data.profile_picture_url
            if profile_data.phone_number is not None:
                profile.phone_number = profile_data.phone_number
            if profile_data.location is not None:
                profile.location = profile_data.location
            if profile_data.timezone is not None:
                profile.timezone = profile_data.timezone

            user.updated_at = datetime.utcnow()
            profile.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(user)
            logger.info(f"User profile updated for user_id={user_id}")
            return user

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating user profile: {e}")
            raise

    @staticmethod
    async def get_user_preferences(db: AsyncSession, user_id: int) -> Optional[UserPreference]:
        """Get user preferences"""
        try:
            result = await db.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            prefs = result.scalars().first()

            if not prefs:
                prefs = UserPreference(user_id=user_id)
                db.add(prefs)
                await db.commit()
                await db.refresh(prefs)

            return prefs
        except Exception as e:
            logger.error(f"Error fetching user preferences: {e}")
            raise

    @staticmethod
    async def update_user_preferences(
        db: AsyncSession, user_id: int, pref_data: UserPreferenceRequest
    ) -> UserPreference:
        """Update user preferences"""
        try:
            prefs = await UserService.get_user_preferences(db, user_id)
            if not prefs:
                raise ValueError("Preferences not found")

            # Update only provided fields
            if pref_data.theme is not None:
                prefs.theme = pref_data.theme
            if pref_data.language is not None:
                prefs.language = pref_data.language
            if pref_data.notifications_email is not None:
                prefs.notifications_email = pref_data.notifications_email
            if pref_data.notifications_push is not None:
                prefs.notifications_push = pref_data.notifications_push
            if pref_data.notifications_sms is not None:
                prefs.notifications_sms = pref_data.notifications_sms
            if pref_data.email_digest_frequency is not None:
                prefs.email_digest_frequency = pref_data.email_digest_frequency
            if pref_data.two_factor_enabled is not None:
                prefs.two_factor_enabled = pref_data.two_factor_enabled
            if pref_data.show_online_status is not None:
                prefs.show_online_status = pref_data.show_online_status
            if pref_data.auto_save_enabled is not None:
                prefs.auto_save_enabled = pref_data.auto_save_enabled
            if pref_data.data_export_frequency is not None:
                prefs.data_export_frequency = pref_data.data_export_frequency

            prefs.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(prefs)
            logger.info(f"User preferences updated for user_id={user_id}")
            return prefs

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating user preferences: {e}")
            raise

    @staticmethod
    async def create_goal(
        db: AsyncSession, user_id: int, goal_data: CreateGoalRequest
    ) -> UserGoal:
        """Create user goal"""
        try:
            goal = UserGoal(
                user_id=user_id,
                goal=goal_data.goal,
                description=goal_data.description,
                category=goal_data.category,
                deadline=goal_data.deadline,
                priority=goal_data.priority or "medium",
                status=GoalStatus.ACTIVE,
                progress=0
            )
            db.add(goal)
            await db.commit()
            await db.refresh(goal)
            logger.info(f"Goal created: id={goal.id}, user_id={user_id}")
            return goal

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error creating goal: {e}")
            raise ValueError("Invalid goal data")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating goal: {e}")
            raise

    @staticmethod
    async def get_goal(db: AsyncSession, goal_id: int, user_id: int) -> Optional[UserGoal]:
        """Get single goal by ID"""
        try:
            result = await db.execute(
                select(UserGoal).where(
                    UserGoal.id == goal_id
                ).where(UserGoal.user_id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching goal: {e}")
            raise

    @staticmethod
    async def get_user_goals(
        db: AsyncSession, user_id: int, status: Optional[GoalStatus] = None
    ) -> List[UserGoal]:
        """Get all goals for user"""
        try:
            query = select(UserGoal).where(UserGoal.user_id == user_id)

            if status:
                query = query.where(UserGoal.status == status)

            query = query.order_by(UserGoal.created_at.desc())
            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error fetching user goals: {e}")
            raise

    @staticmethod
    async def update_goal(
        db: AsyncSession, goal_id: int, user_id: int, goal_data: UpdateGoalRequest
    ) -> UserGoal:
        """Update user goal"""
        try:
            goal = await UserService.get_goal(db, goal_id, user_id)
            if not goal:
                raise ValueError("Goal not found")

            if goal_data.goal is not None:
                goal.goal = goal_data.goal
            if goal_data.description is not None:
                goal.description = goal_data.description
            if goal_data.category is not None:
                goal.category = goal_data.category
            if goal_data.deadline is not None:
                goal.deadline = goal_data.deadline
            if goal_data.priority is not None:
                goal.priority = goal_data.priority
            if goal_data.status is not None:
                goal.status = goal_data.status
            if goal_data.progress is not None:
                goal.progress = min(100, max(0, goal_data.progress))
                if goal.progress == 100 and goal.status == GoalStatus.ACTIVE:
                    goal.status = GoalStatus.COMPLETED

            goal.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(goal)
            logger.info(f"Goal updated: id={goal_id}, user_id={user_id}")
            return goal

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating goal: {e}")
            raise

    @staticmethod
    async def delete_goal(db: AsyncSession, goal_id: int, user_id: int) -> bool:
        """Delete user goal"""
        try:
            goal = await UserService.get_goal(db, goal_id, user_id)
            if not goal:
                raise ValueError("Goal not found")

            await db.delete(goal)
            await db.commit()
            logger.info(f"Goal deleted: id={goal_id}, user_id={user_id}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting goal: {e}")
            raise

    @staticmethod
    async def deactivate_account(
        db: AsyncSession, user_id: int, deactivate_data: AccountDeactivateRequest
    ) -> dict:
        """Deactivate user account"""
        try:
            user = await UserService.get_user_profile(db, user_id)
            if not user:
                raise ValueError("User not found")

            # Verify password
            if not verify_password(deactivate_data.password, user.password_hash):
                logger.warning(f"Invalid password for account deactivation: user_id={user_id}")
                raise ValueError("Invalid password")

            # Deactivate account
            user.is_active = False
            user.updated_at = datetime.utcnow()

            await db.commit()
            logger.info(f"Account deactivated: user_id={user_id}")

            return {
                "user_id": user.id,
                "deactivated_at": user.updated_at,
                "reactivation_deadline": user.updated_at + timedelta(days=30)
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deactivating account: {e}")
            raise

    @staticmethod
    async def reactivate_account(db: AsyncSession, user_id: int) -> User:
        """Reactivate user account"""
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalars().first()

            if not user:
                raise ValueError("User not found")

            user.is_active = True
            user.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(user)
            logger.info(f"Account reactivated: user_id={user_id}")
            return user

        except Exception as e:
            await db.rollback()
            logger.error(f"Error reactivating account: {e}")
            raise

    @staticmethod
    async def delete_account(
        db: AsyncSession, user_id: int, delete_data: DeleteAccountRequest
    ) -> dict:
        """Permanently delete user account"""
        try:
            user = await UserService.get_user_profile(db, user_id)
            if not user:
                raise ValueError("User not found")

            # Verify password
            if not verify_password(delete_data.password, user.password_hash):
                logger.warning(f"Invalid password for account deletion: user_id={user_id}")
                raise ValueError("Invalid password")

            # Delete related data
            if delete_data.export_data:
                logger.info(f"User data export requested: user_id={user_id}")

            # Delete goals
            goals = await UserService.get_user_goals(db, user_id)
            for goal in goals:
                await db.delete(goal)

            # Delete preferences
            prefs = await UserService.get_user_preferences(db, user_id)
            if prefs:
                await db.delete(prefs)

            # Delete profile
            profile = await db.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile_obj = profile.scalars().first()
            if profile_obj:
                await db.delete(profile_obj)

            # Delete user
            await db.delete(user)
            await db.commit()

            logger.info(f"Account permanently deleted: user_id={user_id}")
            return {
                "user_id": user_id,
                "deleted_at": datetime.utcnow()
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting account: {e}")
            raise

    @staticmethod
    async def get_user_activity(db: AsyncSession, user_id: int) -> dict:
        """Get user activity summary"""
        try:
            user = await UserService.get_user_profile(db, user_id)
            if not user:
                raise ValueError("User not found")

            goals = await UserService.get_user_goals(db, user_id)
            completed_goals = [g for g in goals if g.status == GoalStatus.COMPLETED]
            active_goals = [g for g in goals if g.status == GoalStatus.ACTIVE]

            progress_avg = 0
            if goals:
                progress_avg = sum(g.progress for g in goals) / len(goals)

            account_age = (datetime.utcnow() - user.created_at).days

            return {
                "user_id": user.id,
                "total_logins": getattr(user, 'login_count', 0),
                "last_login": user.last_login,
                "total_goals": len(goals),
                "completed_goals": len(completed_goals),
                "active_goals": len(active_goals),
                "goals_progress_average": round(progress_avg, 2),
                "account_created_at": user.created_at,
                "account_age_days": account_age
            }

        except Exception as e:
            logger.error(f"Error fetching user activity: {e}")
            raise

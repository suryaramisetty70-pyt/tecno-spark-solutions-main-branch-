"""
User management API endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.dependencies.auth_dependencies import get_db_session, get_current_user
from api.schemas.auth_schemas import CurrentUser
from api.schemas.user_schemas import (
    UserProfileRequest, UserProfileResponse, UserPreferenceRequest, UserPreferenceResponse,
    CreateGoalRequest, UpdateGoalRequest, UserGoalResponse, UserPreferenceRequest,
    AccountDeactivateRequest, AccountDeactivateResponse, DeleteAccountRequest,
    DeleteAccountResponse, UserActivityResponse, ErrorResponse, ChangeEmailRequest
)
from services.user_service import UserService
from db.models import User, UserProfile, UserPreference, UserGoal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def get_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user profile"""
    try:
        user = await UserService.get_user_profile(db, current_user.id)
        if not user:
            return {
                "status_code": 404,
                "message": "Not Found",
                "detail": "User profile not found"
            }

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            bio=None,
            profile_picture_url=None,
            phone_number=None,
            location=None,
            timezone=None
        )

    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error retrieving profile"
        }


@router.put("/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    profile_data: UserProfileRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update current user profile"""
    try:
        user = await UserService.update_user_profile(db, current_user.id, profile_data)

        profile = await db.execute(
            db.select(UserProfile).where(UserProfile.user_id == current_user.id)
        )
        user_profile = profile.scalars().first()

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            bio=user_profile.bio if user_profile else None,
            profile_picture_url=user_profile.profile_picture_url if user_profile else None,
            phone_number=user_profile.phone_number if user_profile else None,
            location=user_profile.location if user_profile else None,
            timezone=user_profile.timezone if user_profile else None
        )

    except ValueError as e:
        logger.warning(f"Validation error updating profile: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error updating profile"
        }


@router.get("/preferences", response_model=UserPreferenceResponse, status_code=status.HTTP_200_OK)
async def get_preferences(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user preferences"""
    try:
        prefs = await UserService.get_user_preferences(db, current_user.id)
        if not prefs:
            return {
                "status_code": 404,
                "message": "Not Found",
                "detail": "User preferences not found"
            }

        return UserPreferenceResponse(
            user_id=prefs.user_id,
            theme=prefs.theme,
            language=prefs.language,
            notifications_email=prefs.notifications_email,
            notifications_push=prefs.notifications_push,
            notifications_sms=prefs.notifications_sms,
            email_digest_frequency=prefs.email_digest_frequency,
            two_factor_enabled=prefs.two_factor_enabled,
            show_online_status=prefs.show_online_status,
            auto_save_enabled=prefs.auto_save_enabled,
            data_export_frequency=prefs.data_export_frequency,
            updated_at=prefs.updated_at
        )

    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error retrieving preferences"
        }


@router.put("/preferences", response_model=UserPreferenceResponse, status_code=status.HTTP_200_OK)
async def update_preferences(
    pref_data: UserPreferenceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update current user preferences"""
    try:
        prefs = await UserService.update_user_preferences(db, current_user.id, pref_data)

        return UserPreferenceResponse(
            user_id=prefs.user_id,
            theme=prefs.theme,
            language=prefs.language,
            notifications_email=prefs.notifications_email,
            notifications_push=prefs.notifications_push,
            notifications_sms=prefs.notifications_sms,
            email_digest_frequency=prefs.email_digest_frequency,
            two_factor_enabled=prefs.two_factor_enabled,
            show_online_status=prefs.show_online_status,
            auto_save_enabled=prefs.auto_save_enabled,
            data_export_frequency=prefs.data_export_frequency,
            updated_at=prefs.updated_at
        )

    except ValueError as e:
        logger.warning(f"Validation error updating preferences: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error updating preferences"
        }


@router.get("/goals", response_model=list[UserGoalResponse], status_code=status.HTTP_200_OK)
async def get_goals(
    status_filter: str = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all user goals"""
    try:
        goals = await UserService.get_user_goals(db, current_user.id)

        return [
            UserGoalResponse(
                id=g.id,
                user_id=g.user_id,
                goal=g.goal,
                description=g.description,
                category=g.category,
                deadline=g.deadline,
                priority=g.priority,
                status=g.status,
                progress=g.progress,
                created_at=g.created_at,
                updated_at=g.updated_at
            )
            for g in goals
        ]

    except Exception as e:
        logger.error(f"Error getting user goals: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error retrieving goals"
        }


@router.post("/goals", response_model=UserGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: CreateGoalRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create new user goal"""
    try:
        goal = await UserService.create_goal(db, current_user.id, goal_data)

        return UserGoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            goal=goal.goal,
            description=goal.description,
            category=goal.category,
            deadline=goal.deadline,
            priority=goal.priority,
            status=goal.status,
            progress=goal.progress,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )

    except ValueError as e:
        logger.warning(f"Validation error creating goal: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error creating goal"
        }


@router.put("/goals/{goal_id}", response_model=UserGoalResponse, status_code=status.HTTP_200_OK)
async def update_goal(
    goal_id: int,
    goal_data: UpdateGoalRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update user goal"""
    try:
        goal = await UserService.update_goal(db, goal_id, current_user.id, goal_data)

        return UserGoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            goal=goal.goal,
            description=goal.description,
            category=goal.category,
            deadline=goal.deadline,
            priority=goal.priority,
            status=goal.status,
            progress=goal.progress,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )

    except ValueError as e:
        logger.warning(f"Goal not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error updating goal: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error updating goal"
        }


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete user goal"""
    try:
        await UserService.delete_goal(db, goal_id, current_user.id)
        return None

    except ValueError as e:
        logger.warning(f"Goal not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error deleting goal: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error deleting goal"
        }


@router.get("/activity", response_model=UserActivityResponse, status_code=status.HTTP_200_OK)
async def get_activity(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user activity summary"""
    try:
        activity = await UserService.get_user_activity(db, current_user.id)

        return UserActivityResponse(
            user_id=activity["user_id"],
            total_logins=activity["total_logins"],
            last_login=activity["last_login"],
            total_goals=activity["total_goals"],
            completed_goals=activity["completed_goals"],
            active_goals=activity["active_goals"],
            goals_progress_average=activity["goals_progress_average"],
            account_created_at=activity["account_created_at"],
            account_age_days=activity["account_age_days"]
        )

    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error retrieving activity"
        }


@router.post("/deactivate", response_model=AccountDeactivateResponse, status_code=status.HTTP_200_OK)
async def deactivate_account(
    deactivate_data: AccountDeactivateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Deactivate user account"""
    try:
        result = await UserService.deactivate_account(db, current_user.id, deactivate_data)

        return AccountDeactivateResponse(
            message="Account deactivated successfully. You can reactivate within 30 days.",
            user_id=result["user_id"],
            deactivated_at=result["deactivated_at"],
            reactivation_deadline=result["reactivation_deadline"]
        )

    except ValueError as e:
        logger.warning(f"Error deactivating account: {e}")
        return {
            "status_code": 401,
            "message": "Unauthorized",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error deactivating account: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error deactivating account"
        }


@router.post("/reactivate", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def reactivate_account(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Reactivate deactivated user account"""
    try:
        user = await UserService.reactivate_account(db, current_user.id)

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            bio=None,
            profile_picture_url=None,
            phone_number=None,
            location=None,
            timezone=None
        )

    except ValueError as e:
        logger.warning(f"Account not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error reactivating account: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error reactivating account"
        }


@router.delete("/delete", response_model=DeleteAccountResponse, status_code=status.HTTP_200_OK)
async def delete_account(
    delete_data: DeleteAccountRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Permanently delete user account"""
    try:
        result = await UserService.delete_account(db, current_user.id, delete_data)

        return DeleteAccountResponse(
            message="Account permanently deleted. All associated data has been removed.",
            user_id=result["user_id"],
            deleted_at=result["deleted_at"]
        )

    except ValueError as e:
        logger.warning(f"Error deleting account: {e}")
        return {
            "status_code": 401,
            "message": "Unauthorized",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error deleting account"
        }

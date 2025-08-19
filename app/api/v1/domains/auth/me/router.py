"""
Me Router for Authentication Domain.

Эндпоинты для работы с информацией о текущем пользователе.
"""

from fastapi import APIRouter, HTTPException, status
from app.api.dependencies.core.auth import CurrentUserDep
from app.api.dependencies.core.database import SessionDep
from app.api.v1.common.responses import create_response, success_response, error_response, not_found_response
from app.api.v1.domains.auth.schemas import UserBasicResponse, UserDetailedResponse, UserWithRelationsResponse
from app.crud import user as crud_user



router = APIRouter()


@router.get("/", summary="Get Current User Information")
async def get_me(
    current_user: CurrentUserDep,
):
    """
    Получить информацию о текущем пользователе.

    Возвращает детальную информацию о пользователе, включая профиль,
    настройки и другие связанные данные.
    """
    try:
        user_data = UserDetailedResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            username=current_user.username,
            is_active=current_user.is_active,
            is_email_verified=current_user.is_email_verified,
            last_login_at=current_user.last_login_at,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            company_id=current_user.company_id,
            status=getattr(current_user, 'status', None),
        )
        
        return create_response(
            data=user_data.model_dump(),
            message="User information retrieved successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve user information: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/profile", summary="Get User Profile")
async def get_profile(
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Получить профиль пользователя.

    Возвращает расширенную информацию о профиле пользователя
    включая личные данные, настройки приватности и т.д.
    """
    try:
        # Получаем свежие данные пользователя с отношениями
        fresh_user = await crud_user.get_by_email_with_all_relations(
            db, email=current_user.email
        )
        
        if not fresh_user:
            return not_found_response(message="User not found")
        
        # Базовая информация пользователя
        user_data = UserDetailedResponse(
            id=fresh_user.id,
            email=fresh_user.email,
            name=fresh_user.name,
            username=fresh_user.username,
            is_active=fresh_user.is_active,
            is_email_verified=fresh_user.is_email_verified,
            last_login_at=fresh_user.last_login_at,
            created_at=fresh_user.created_at,
            updated_at=fresh_user.updated_at,
            company_id=fresh_user.company_id,
            status=getattr(fresh_user, 'status', None),
        )
        
        # Дополнительная информация профиля
        profile_data = {
            "user": user_data.model_dump(),
            "profile": {
                "bio": getattr(fresh_user, 'bio', None),
                "avatar_url": getattr(fresh_user, 'avatar_url', None),
                "location": getattr(fresh_user, 'location', None),
                "website": getattr(fresh_user, 'website', None),
                "social_links": getattr(fresh_user, 'social_links', {}),
            },
            "preferences": {
                "language": getattr(fresh_user, 'language', 'en'),
                "timezone": getattr(fresh_user, 'timezone', 'UTC'),
                "notifications": getattr(fresh_user, 'notifications_enabled', True),
            },
            "roles": fresh_user.roles if hasattr(fresh_user, 'roles') else [],
            "company": fresh_user.company_id,
        }
        
        return create_response(
            data=profile_data,
            message="User profile retrieved successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve user profile: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/status", summary="Get Account Status")
async def get_account_status(
    current_user: CurrentUserDep,
):
    """
    Получить статус аккаунта пользователя.

    Возвращает информацию о состоянии аккаунта: активность,
    верификация email, блокировки и т.д.
    """
    try:
        status_data = {
            "is_active": current_user.is_active,
            "email_verified": current_user.is_email_verified,
            "two_factor_enabled": getattr(current_user, "two_factor_enabled", False),
            "last_login": current_user.last_login_at,
            "account_locked": not current_user.is_active,
            "lock_reason": None if current_user.is_active else "Account deactivated",
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
        }
        
        return create_response(
            data=status_data,
            message="Account status retrieved successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve account status: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

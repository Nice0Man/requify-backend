from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.common.responses import (
    create_response,
    error_response,
    success_response,
    not_found_response,
    forbidden_response,
    unauthorized_response,
)
from app.api.dependencies.core.auth import CurrentUserDep, get_current_user
from app.api.dependencies.core.database import SessionDep, get_db
from app.api.v1.domains.auth.schemas import (
    UserWithRelationsResponse,
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    LogoutRequest,
    LoginResponse,
    RegisterResponse,
    LogoutResponse,
    TokenRefreshResponse,
    UserBasicResponse,
)
from app.services.auth_service import authentication_service
from app.services.user_registration_service import user_registration_service
from app.crud.user import crud_user
from app.models.user import User
from app.utils.logger import logger

"""
Root Authentication Router.

Роутер для основных операций аутентификации: login, register, logout, refresh token.
"""


router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="Authenticate User")
async def login(
    db: SessionDep,
    request_obj: Request,
    login_data: LoginRequest,
):
    """
    Authenticate user and return JWT tokens.

    - **email**: User email
    - **password**: User password
    - **remember_me**: Whether to extend token lifetime
    """
    try:
        # Authenticate user
        user = await authentication_service.authenticate_user(
            db=db,
            credentials={
                "username_or_email": login_data.email or login_data.username,
                "password": login_data.password,
            },
        )

        # Generate tokens
        tokens = await authentication_service.create_user_tokens(
            db=db,
            user=user,
            request=request_obj,
        )

        # Get user data for response
        user_data = UserBasicResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            username=user.username,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            company_id=user.company_id,
        )

        return create_response(
            data={
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": "bearer",
                "expires_in": tokens["expires_in"],
                "refresh_expires_in": tokens.get("refresh_expires_in"),
                "user": user_data.model_dump(),
            },
            message="Authentication successful",
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        return unauthorized_response(
            message=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", summary="Get Current User")
async def get_current_user_info(
    current_user: CurrentUserDep,
):
    """
    Get current authenticated user information.

    Returns basic user profile information for the authenticated user.
    """
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "name": current_user.name,
            "status": current_user.status,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
        }
    }


@router.post("/register", response_model=RegisterResponse, summary="Register User")
async def register(
    register_data: RegisterRequest,
    db: SessionDep,
):
    """
    Register a new user.

    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Strong password
    - **confirm_password**: Password confirmation
    - **company_name**: Optional company name
    """
    try:
        # Check if user exists
        existing_user = await crud_user.get_by_email(db, register_data.email)
        if existing_user:
            return error_response(
                message="User with this email already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Create user data
        user_data = {
            "email": register_data.email,
            "password": register_data.password,
            "name": register_data.name,
            "username": register_data.username,
            "company_name": register_data.company_name,
        }

        # Register user
        user = await user_registration_service.register_user(db, user_data)

        return create_response(
            data={
                "success": True,
                "message": "User registered successfully. Please verify your email.",
                "user_id": user.id,
                "email_verification_required": True,
            },
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        return error_response(
            message=f"Registration failed: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/logout", response_model=LogoutResponse, summary="Logout User")
async def logout(
    logout_data: LogoutRequest,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Logout user and revoke tokens.

    - **refresh_token**: Optional refresh token to revoke
    - **logout_all_devices**: Whether to logout from all devices
    """
    try:
        # Logout user
        await authentication_service.logout_user(
            db=db,
            user_id=current_user.id,
            refresh_token=logout_data.refresh_token,
            logout_all_devices=logout_data.logout_all_devices,
        )

        return create_response(
            data={
                "success": True,
                "message": "Successfully logged out",
            },
            message="Logout successful",
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        return error_response(
            message=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post("/logout/simple", summary="Simple Logout")
async def logout_simple(
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Simple logout - revoke current user's tokens without body parameters.
    """
    try:
        await authentication_service.logout_user(
            db=db,
            user_id=current_user.id,
            refresh_token=None,
            logout_all_devices=False,
        )

        return create_response(
            data={
                "success": True,
                "message": "Successfully logged out",
            },
            message="Logout successful",
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        return error_response(
            message=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post("/refresh", response_model=TokenRefreshResponse, summary="Refresh Token")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request_obj: Request,
    db: SessionDep,
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token
    """
    try:
        tokens = await authentication_service.refresh_access_token(
            db=db,
            refresh_token=refresh_data.refresh_token,
            request=request_obj,
        )

        return create_response(
            data={
                "access_token": tokens["access_token"],
                "token_type": "bearer",
                "expires_in": tokens["expires_in"],
            },
            message="Token refreshed successfully",
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        return unauthorized_response(
            message=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/validate-token", summary="Validate Token")
async def validate_token(
    current_user: CurrentUserDep,
):
    """
    Validate current JWT token from Authorization header.

    Returns information about the current valid token.
    """
    try:
        user_data = UserBasicResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            username=current_user.username,
            is_active=current_user.is_active,
            is_email_verified=current_user.is_email_verified,
            last_login_at=current_user.last_login_at,
            created_at=current_user.created_at,
            company_id=current_user.company_id,
        )

        return create_response(
            data={
                "valid": True,
                "user": user_data.model_dump(),
            },
            message="Token is valid",
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        return unauthorized_response(
            message="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

"""
OAuth2 Authentication Router.

Роутер для OAuth2 интеграции (Auth0, Google, GitHub и др.).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.common.responses import (
    create_response,
    error_response,
    success_response,
    not_found_response,
    forbidden_response,
    unauthorized_response,
)
from app.api.dependencies.core.auth import get_current_user
from app.api.dependencies.core.database import get_db
from app.models.user import User
from app.services.auth0_service import Auth0Service

from .schemas import (
    OAuth2AuthorizeRequest,
    OAuth2AuthorizeResponse,
    OAuth2CallbackRequest,
    OAuth2CallbackResponse,
    OAuth2LinkRequest,
    OAuth2LinkResponse,
    OAuth2UnlinkRequest,
    OAuth2UnlinkResponse,
)

router = APIRouter()


class OAuth2ProviderService:
    """Фабрика OAuth2 провайдеров."""
    
    @staticmethod
    async def get_authorization_url(provider: str, redirect_uri: str = None, state: str = None):
        """Получить URL авторизации для провайдера."""
        if provider == "auth0":
            return await Auth0Service().get_authorization_url(
                redirect_uri=redirect_uri,
                state=state,
            )
        elif provider == "google":
            # Реализация Google OAuth2
            from app.services.google_oauth_service import GoogleOAuthService
            return await GoogleOAuthService().get_authorization_url(
                redirect_uri=redirect_uri,
                state=state,
            )
        elif provider == "github":
            # Реализация GitHub OAuth2
            from app.services.github_oauth_service import GitHubOAuthService
            return await GitHubOAuthService().get_authorization_url(
                redirect_uri=redirect_uri,
                state=state,
            )
        elif provider == "microsoft":
            # Реализация Microsoft OAuth2
            from app.services.microsoft_oauth_service import MicrosoftOAuthService
            return await MicrosoftOAuthService().get_authorization_url(
                redirect_uri=redirect_uri,
                state=state,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Provider {provider} not implemented yet",
            )

    @staticmethod
    async def handle_callback(provider: str, db: AsyncSession, code: str, state: str = None):
        """Обработать callback от провайдера."""
        if provider == "auth0":
            return await Auth0Service().handle_callback(
                db=db,
                code=code,
                state=state,
            )
        elif provider == "google":
            from app.services.google_oauth_service import GoogleOAuthService
            return await GoogleOAuthService().handle_callback(
                db=db,
                code=code,
                state=state,
            )
        elif provider == "github":
            from app.services.github_oauth_service import GitHubOAuthService
            return await GitHubOAuthService().handle_callback(
                db=db,
                code=code,
                state=state,
            )
        elif provider == "microsoft":
            from app.services.microsoft_oauth_service import MicrosoftOAuthService
            return await MicrosoftOAuthService().handle_callback(
                db=db,
                code=code,
                state=state,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Provider {provider} not implemented yet",
            )

    @staticmethod
    async def link_account(provider: str, db: AsyncSession, user: User, access_token: str):
        """Привязать OAuth2 аккаунт к пользователю."""
        if provider == "auth0":
            return await Auth0Service().link_account(
                db=db,
                user=user,
                access_token=access_token,
            )
        elif provider == "google":
            from app.services.google_oauth_service import GoogleOAuthService
            return await GoogleOAuthService().link_account(
                db=db,
                user=user,
                access_token=access_token,
            )
        elif provider == "github":
            from app.services.github_oauth_service import GitHubOAuthService
            return await GitHubOAuthService().link_account(
                db=db,
                user=user,
                access_token=access_token,
            )
        elif provider == "microsoft":
            from app.services.microsoft_oauth_service import MicrosoftOAuthService
            return await MicrosoftOAuthService().link_account(
                db=db,
                user=user,
                access_token=access_token,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Provider {provider} not implemented yet",
            )

    @staticmethod
    async def unlink_account(provider: str, db: AsyncSession, user: User):
        """Отвязать OAuth2 аккаунт от пользователя."""
        if provider == "auth0":
            return await Auth0Service().unlink_account(
                db=db,
                user=user,
            )
        elif provider == "google":
            from app.services.google_oauth_service import GoogleOAuthService
            return await GoogleOAuthService().unlink_account(
                db=db,
                user=user,
            )
        elif provider == "github":
            from app.services.github_oauth_service import GitHubOAuthService
            return await GitHubOAuthService().unlink_account(
                db=db,
                user=user,
            )
        elif provider == "microsoft":
            from app.services.microsoft_oauth_service import MicrosoftOAuthService
            return await MicrosoftOAuthService().unlink_account(
                db=db,
                user=user,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Provider {provider} not implemented yet",
            )


@router.post(
    "/authorize", response_model=OAuth2AuthorizeResponse, summary="OAuth2 Authorize"
)
async def oauth2_authorize(
    request: OAuth2AuthorizeRequest,
):
    """
    Initialize OAuth2 authorization flow.

    - **provider**: OAuth2 provider (auth0, google, github, microsoft)
    - **redirect_uri**: Optional redirect URI
    - **state**: Optional state parameter for CSRF protection
    """
    try:
        authorization_data = await OAuth2ProviderService.get_authorization_url(
            provider=request.provider,
            redirect_uri=request.redirect_uri,
            state=request.state,
        )

        return OAuth2AuthorizeResponse(
            authorization_url=authorization_data["authorization_url"],
            state=authorization_data["state"],
        )

    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post(
    "/callback/{provider}",
    response_model=OAuth2CallbackResponse,
    summary="OAuth2 Callback",
)
async def oauth2_callback(
    provider: str,
    request: OAuth2CallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth2 callback from provider.

    - **provider**: OAuth2 provider
    - **code**: Authorization code from provider
    - **state**: State parameter for CSRF protection
    """
    try:
        if request.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth2 error: {request.error} - {request.error_description}",
            )

        auth_result = await OAuth2ProviderService.handle_callback(
            provider=provider,
            db=db,
            code=request.code,
            state=request.state,
        )

        # Get detailed user info
        from app.api.v1.domains.auth.schemas import UserWithRelationsResponse

        user_detailed = UserWithRelationsResponse.model_validate(auth_result["user"])

        return OAuth2CallbackResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            expires_in=auth_result["expires_in"],
            refresh_expires_in=auth_result.get("refresh_expires_in"),
            user=user_detailed,
            is_new_user=auth_result.get("is_new_user", False),
        )

    except HTTPException:
        raise
    except Exception as e:
        if "invalid" in str(e).lower() or "expired" in str(e).lower():
            return error_response(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )
        return error_response(
            message="OAuth2 authentication failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/link", response_model=OAuth2LinkResponse, summary="Link OAuth2 Account")
async def link_oauth2_account(
    request: OAuth2LinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Link OAuth2 account to current user.

    - **provider**: OAuth2 provider
    - **access_token**: Access token from provider
    """
    try:
        await OAuth2ProviderService.link_account(
            provider=request.provider,
            db=db,
            user=current_user,
            access_token=request.access_token,
        )

        return OAuth2LinkResponse(
            message="OAuth2 account linked successfully",
            linked=True,
            provider=request.provider,
        )

    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post(
    "/unlink", response_model=OAuth2UnlinkResponse, summary="Unlink OAuth2 Account"
)
async def unlink_oauth2_account(
    request: OAuth2UnlinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unlink OAuth2 account from current user.

    - **provider**: OAuth2 provider to unlink
    """
    try:
        await OAuth2ProviderService.unlink_account(
            provider=request.provider,
            db=db,
            user=current_user,
        )

        return OAuth2UnlinkResponse(
            message="OAuth2 account unlinked successfully",
            unlinked=True,
            provider=request.provider,
        )

    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
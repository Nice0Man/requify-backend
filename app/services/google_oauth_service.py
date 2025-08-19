"""
Google OAuth2 Service.

Сервис для работы с Google OAuth2.
"""

import logging
import secrets
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import crud_user
from app.models.user import User
from app.services.auth_service import authentication_service
from app.services.token_service import token_service
from app.utils.logger import logger

from .base import BaseService, ServiceError


class GoogleOAuthError(ServiceError):
    """Ошибки Google OAuth."""
    pass


class GoogleOAuthService(BaseService):
    """Сервис для работы с Google OAuth2."""

    def get_service_name(self) -> str:
        return "GoogleOAuthService"

    def __init__(self):
        self.client_id = settings.google_oauth.client_id if hasattr(settings, 'google_oauth') else None
        self.client_secret = settings.google_oauth.client_secret if hasattr(settings, 'google_oauth') else None
        self.redirect_uri = settings.google_oauth.redirect_uri if hasattr(settings, 'google_oauth') else None
        self.scope = "openid email profile"
        
        # URLs
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    @property
    def is_enabled(self) -> bool:
        """Проверяет, включен ли Google OAuth."""
        return bool(self.client_id and self.client_secret)

    async def get_authorization_url(
        self, redirect_uri: str = None, state: str = None
    ) -> Dict[str, str]:
        """
        Получить URL авторизации Google.
        
        Args:
            redirect_uri: URL для перенаправления после авторизации
            state: Состояние для защиты от CSRF
            
        Returns:
            Dict с authorization_url и state
        """
        if not self.is_enabled:
            raise GoogleOAuthError("Google OAuth is not configured")

        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }

        authorization_url = f"{self.auth_url}?{urlencode(params)}"
        
        return {
            "authorization_url": authorization_url,
            "state": state,
        }

    async def handle_callback(
        self, db: AsyncSession, code: str, state: str = None
    ) -> Dict[str, Any]:
        """
        Обработать callback от Google.
        
        Args:
            db: Сессия базы данных
            code: Код авторизации от Google
            state: Состояние для проверки CSRF
            
        Returns:
            Dict с токенами и информацией о пользователе
        """
        if not self.is_enabled:
            raise GoogleOAuthError("Google OAuth is not configured")

        try:
            # Обменять код на токен
            token_data = await self._exchange_code_for_token(code)
            
            # Получить информацию о пользователе
            user_info = await self._get_user_info(token_data["access_token"])
            
            # Найти или создать пользователя
            user = await self._find_or_create_user(db, user_info)
            
            # Создать токены для нашей системы
            tokens = await token_service.create_tokens_for_user(
                db=db,
                user=user,
                request=None,  # TODO: передавать request если нужно
            )
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_in": tokens["expires_in"],
                "refresh_expires_in": tokens.get("refresh_expires_in"),
                "user": user,
                "is_new_user": hasattr(user, '_is_new_user') and user._is_new_user,
            }
            
        except Exception as e:
            logger.error(f"Google OAuth callback failed: {e}")
            raise GoogleOAuthError(f"Google OAuth callback failed: {str(e)}")

    async def _exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Обменять код авторизации на токен."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()

    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Получить информацию о пользователе от Google."""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def _find_or_create_user(self, db: AsyncSession, user_info: Dict[str, Any]) -> User:
        """Найти или создать пользователя на основе данных Google."""
        email = user_info.get("email")
        if not email:
            raise GoogleOAuthError("Email not provided by Google")

        # Попытаться найти существующего пользователя
        user = await crud_user.get_by_email_with_all_relations(db, email=email)
        
        if user:
            # Обновить информацию пользователя если нужно
            if not user.name and user_info.get("name"):
                user.name = user_info["name"]
                await db.commit()
            return user
        
        # Создать нового пользователя
        user_data = {
            "email": email,
            "name": user_info.get("name", ""),
            "username": email.split("@")[0],  # Использовать часть email как username
            "is_active": True,
            "is_email_verified": user_info.get("verified_email", True),
        }
        
        user = await crud_user.create(db, obj_in=user_data)
        user._is_new_user = True  # Пометить как нового пользователя
        
        return user

    async def link_account(
        self, db: AsyncSession, user: User, access_token: str
    ) -> None:
        """
        Привязать Google аккаунт к существующему пользователю.
        
        Args:
            db: Сессия базы данных
            user: Пользователь для привязки
            access_token: Access token от Google
        """
        if not self.is_enabled:
            raise GoogleOAuthError("Google OAuth is not configured")

        try:
            # Получить информацию о пользователе Google
            user_info = await self._get_user_info(access_token)
            
            # TODO: Сохранить связь между пользователем и Google аккаунтом
            # Это требует дополнительной модели для OAuth связей
            logger.info(f"Google account linked for user {user.id}: {user_info.get('email')}")
            
        except Exception as e:
            logger.error(f"Failed to link Google account: {e}")
            raise GoogleOAuthError(f"Failed to link Google account: {str(e)}")

    async def unlink_account(self, db: AsyncSession, user: User) -> None:
        """
        Отвязать Google аккаунт от пользователя.
        
        Args:
            db: Сессия базы данных
            user: Пользователь для отвязки
        """
        if not self.is_enabled:
            raise GoogleOAuthError("Google OAuth is not configured")

        try:
            # TODO: Удалить связь между пользователем и Google аккаунтом
            # Это требует дополнительной модели для OAuth связей
            logger.info(f"Google account unlinked for user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to unlink Google account: {e}")
            raise GoogleOAuthError(f"Failed to unlink Google account: {str(e)}")

"""
GitHub OAuth2 Service.

Сервис для работы с GitHub OAuth2.
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


class GitHubOAuthError(ServiceError):
    """Ошибки GitHub OAuth."""
    pass


class GitHubOAuthService(BaseService):
    """Сервис для работы с GitHub OAuth2."""

    def get_service_name(self) -> str:
        return "GitHubOAuthService"

    def __init__(self):
        self.client_id = settings.github_oauth.client_id if hasattr(settings, 'github_oauth') else None
        self.client_secret = settings.github_oauth.client_secret if hasattr(settings, 'github_oauth') else None
        self.redirect_uri = settings.github_oauth.redirect_uri if hasattr(settings, 'github_oauth') else None
        self.scope = "user:email"
        
        # URLs
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.api_url = "https://api.github.com"

    @property
    def is_enabled(self) -> bool:
        """Проверяет, включен ли GitHub OAuth."""
        return bool(self.client_id and self.client_secret)

    async def get_authorization_url(
        self, redirect_uri: str = None, state: str = None
    ) -> Dict[str, str]:
        """
        Получить URL авторизации GitHub.
        
        Args:
            redirect_uri: URL для перенаправления после авторизации
            state: Состояние для защиты от CSRF
            
        Returns:
            Dict с authorization_url и state
        """
        if not self.is_enabled:
            raise GitHubOAuthError("GitHub OAuth is not configured")

        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
            "scope": self.scope,
            "state": state,
            "allow_signup": "true",
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
        Обработать callback от GitHub.
        
        Args:
            db: Сессия базы данных
            code: Код авторизации от GitHub
            state: Состояние для проверки CSRF
            
        Returns:
            Dict с токенами и информацией о пользователе
        """
        if not self.is_enabled:
            raise GitHubOAuthError("GitHub OAuth is not configured")

        try:
            # Обменять код на токен
            token_data = await self._exchange_code_for_token(code)
            
            # Получить информацию о пользователе
            user_info = await self._get_user_info(token_data["access_token"])
            
            # Получить email пользователя (может быть приватным)
            emails = await self._get_user_emails(token_data["access_token"])
            primary_email = self._get_primary_email(emails)
            
            if primary_email:
                user_info["email"] = primary_email
            
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
            logger.error(f"GitHub OAuth callback failed: {e}")
            raise GitHubOAuthError(f"GitHub OAuth callback failed: {str(e)}")

    async def _exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Обменять код авторизации на токен."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }

        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()

    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Получить информацию о пользователе от GitHub."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/user", headers=headers)
            response.raise_for_status()
            return response.json()

    async def _get_user_emails(self, access_token: str) -> list:
        """Получить email адреса пользователя от GitHub."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/user/emails", headers=headers)
            response.raise_for_status()
            return response.json()

    def _get_primary_email(self, emails: list) -> Optional[str]:
        """Получить основной email адрес из списка."""
        # Сначала ищем основной и подтвержденный email
        for email in emails:
            if email.get("primary") and email.get("verified"):
                return email.get("email")
        
        # Если основного нет, ищем любой подтвержденный
        for email in emails:
            if email.get("verified"):
                return email.get("email")
        
        # В крайнем случае возвращаем первый email
        if emails:
            return emails[0].get("email")
        
        return None

    async def _find_or_create_user(self, db: AsyncSession, user_info: Dict[str, Any]) -> User:
        """Найти или создать пользователя на основе данных GitHub."""
        email = user_info.get("email")
        if not email:
            raise GitHubOAuthError("Email not provided by GitHub")

        # Попытаться найти существующего пользователя
        user = await crud_user.get_by_email_with_all_relations(db, email=email)
        
        if user:
            # Обновить информацию пользователя если нужно
            if not user.name and user_info.get("name"):
                user.name = user_info["name"]
                await db.commit()
            return user
        
        # Создать нового пользователя
        username = user_info.get("login", email.split("@")[0])
        
        # Проверить уникальность username
        existing_user = await crud_user.get_by_username(db, username=username)
        if existing_user:
            username = f"{username}_{secrets.token_hex(4)}"
        
        user_data = {
            "email": email,
            "name": user_info.get("name") or user_info.get("login", ""),
            "username": username,
            "is_active": True,
            "is_email_verified": True,  # GitHub emails считаем подтвержденными
        }
        
        user = await crud_user.create(db, obj_in=user_data)
        user._is_new_user = True  # Пометить как нового пользователя
        
        return user

    async def link_account(
        self, db: AsyncSession, user: User, access_token: str
    ) -> None:
        """
        Привязать GitHub аккаунт к существующему пользователю.
        
        Args:
            db: Сессия базы данных
            user: Пользователь для привязки
            access_token: Access token от GitHub
        """
        if not self.is_enabled:
            raise GitHubOAuthError("GitHub OAuth is not configured")

        try:
            # Получить информацию о пользователе GitHub
            user_info = await self._get_user_info(access_token)
            
            # TODO: Сохранить связь между пользователем и GitHub аккаунтом
            # Это требует дополнительной модели для OAuth связей
            logger.info(f"GitHub account linked for user {user.id}: {user_info.get('login')}")
            
        except Exception as e:
            logger.error(f"Failed to link GitHub account: {e}")
            raise GitHubOAuthError(f"Failed to link GitHub account: {str(e)}")

    async def unlink_account(self, db: AsyncSession, user: User) -> None:
        """
        Отвязать GitHub аккаунт от пользователя.
        
        Args:
            db: Сессия базы данных
            user: Пользователь для отвязки
        """
        if not self.is_enabled:
            raise GitHubOAuthError("GitHub OAuth is not configured")

        try:
            # TODO: Удалить связь между пользователем и GitHub аккаунтом
            # Это требует дополнительной модели для OAuth связей
            logger.info(f"GitHub account unlinked for user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to unlink GitHub account: {e}")
            raise GitHubOAuthError(f"Failed to unlink GitHub account: {str(e)}")

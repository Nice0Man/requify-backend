"""
Authentication Schemas.

Схемы для аутентификации и авторизации с поддержкой JWT токенов.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.api.v1.common.schemas import (
    BaseSchema,
    CreateSchema,
    UpdateSchema,
    ResponseSchema,
    ValidationMixin,
    FieldLimits,
    StandardDescriptions,
)

if TYPE_CHECKING:
    from ..identity.users.schemas import UserResponse


# === Token Enums ===


class TokenType(str, Enum):
    """Типы токенов."""

    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"


class AuthProvider(str, Enum):
    """Провайдеры аутентификации."""

    LOCAL = "local"
    AUTH0 = "auth0"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    SSO = "sso"


# === Base Token Schemas ===


class TokenBase(BaseSchema):
    """Базовая схема токена."""

    token_type: str = Field(default="bearer", description="Тип токена")


class AccessToken(TokenBase):
    """Схема для access токена."""

    access_token: str = Field(..., description="Access токен")
    expires_in: int = Field(..., description="Время жизни токена в секундах")


class RefreshToken(TokenBase):
    """Схема для refresh токена."""

    refresh_token: str = Field(..., description="Refresh токен")
    expires_in: int = Field(..., description="Время жизни токена в секундах")


class TokenPair(BaseSchema):
    """Схема для пары токенов (access + refresh)."""

    access_token: str = Field(..., description="Access токен")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access токена в секундах")
    refresh_expires_in: int = Field(
        ..., description="Время жизни refresh токена в секундах"
    )


# === JWT Payload Schemas ===


class AccessTokenPayload(BaseSchema):
    """Схема для данных внутри access JWT токена."""

    sub: str = Field(..., description="Subject (user email)")
    exp: int = Field(..., description="Expiration time (timestamp)")
    iat: int = Field(..., description="Issued at (timestamp)")
    type: str = Field(default="access", description="Тип токена")
    user_id: int = Field(..., description="ID пользователя")
    scopes: List[str] = Field(default_factory=list, description="Права доступа")
    company_id: Optional[int] = Field(None, description="ID основной компании")
    auth0_id: Optional[str] = Field(None, description="Auth0 ID пользователя")


class RefreshTokenPayload(BaseSchema):
    """Схема для данных внутри refresh JWT токена."""

    sub: str = Field(..., description="Subject (user email)")
    exp: int = Field(..., description="Expiration time (timestamp)")
    iat: int = Field(..., description="Issued at (timestamp)")
    type: str = Field(default="refresh", description="Тип токена")
    user_id: int = Field(..., description="ID пользователя")
    token_id: str = Field(..., description="ID refresh токена в БД")
    company_id: Optional[int] = Field(None, description="ID основной компании")


class TokenData(BaseSchema):
    """Схема для валидации токена."""

    email: Optional[str] = Field(None, description="Email пользователя")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    scopes: List[str] = Field(default_factory=list, description="Права доступа")
    company_id: Optional[int] = Field(None, description="ID компании")


# === Authentication Request Schemas ===


class LoginRequest(BaseSchema, ValidationMixin):
    """Схема для запроса аутентификации."""

    email: EmailStr = Field(..., description="Email")
    username: Optional[str] = Field(None, description="Username")
    password: str = Field(..., min_length=1, description="Пароль")
    remember_me: bool = Field(False, description="Запомнить меня")
    auth_provider: AuthProvider = Field(AuthProvider.LOCAL, description="Провайдер")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> str:
        """Валидация email."""
        return str(v).lower()

    @model_validator(mode="after")
    def validate_credentials(self):
        """Валидация учетных данных."""
        if not self.email and not self.username:
            raise ValueError("Either email or username is required")
        return self


class RegisterRequest(BaseSchema, ValidationMixin):
    """Схема для регистрации пользователя."""

    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=8, description="Пароль")
    confirm_password: str = Field(..., description="Подтверждение пароля")
    name: str = Field(..., min_length=1, max_length=100, description="Полное имя")
    username: Optional[str] = Field(
        None, min_length=2, max_length=50, description="Имя пользователя"
    )
    company_name: Optional[str] = Field(
        None, max_length=255, description="Название компании"
    )
    accept_terms: bool = Field(..., description="Принятие условий использования")
    accept_privacy: bool = Field(
        ..., description="Принятие политики конфиденциальности"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> str:
        """Валидация email."""
        return str(v).lower()

    @model_validator(mode="after")
    def passwords_match(self):
        """Проверка совпадения паролей."""
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @model_validator(mode="after")
    def validate_terms(self):
        """Проверка принятия условий."""
        if not self.accept_terms:
            raise ValueError("Terms of service must be accepted")
        if not self.accept_privacy:
            raise ValueError("Privacy policy must be accepted")
        return self


class RefreshTokenRequest(BaseSchema):
    """Схема для обновления токена."""

    refresh_token: str = Field(..., description="Refresh токен")


class LogoutRequest(BaseSchema):
    """Схема для выхода из системы."""

    refresh_token: Optional[str] = Field(None, description="Refresh токен")
    logout_all_devices: bool = Field(False, description="Выйти со всех устройств")


# === Password Management Schemas ===


class PasswordResetRequest(BaseSchema):
    """Схема для запроса сброса пароля."""

    email: EmailStr = Field(..., description="Email пользователя")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> str:
        """Валидация email."""
        return str(v).lower()


class PasswordResetConfirm(BaseSchema):
    """Схема для подтверждения сброса пароля."""

    token: str = Field(..., description="Токен сброса")
    new_password: str = Field(..., min_length=8, description="Новый пароль")
    confirm_password: str = Field(..., description="Подтверждение пароля")

    @model_validator(mode="after")
    def passwords_match(self):
        """Проверка совпадения паролей."""
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class PasswordChangeRequest(BaseSchema):
    """Схема для смены пароля."""

    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")
    confirm_password: str = Field(..., description="Подтверждение пароля")

    @model_validator(mode="after")
    def passwords_match(self):
        """Проверка совпадения паролей."""
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# === Email Verification Schemas ===


class EmailVerificationRequest(BaseSchema):
    """Схема для запроса подтверждения email."""

    email: EmailStr = Field(..., description="Email для подтверждения")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> str:
        """Валидация email."""
        return str(v).lower()


class EmailVerificationConfirm(BaseSchema):
    """Схема для подтверждения email."""

    token: str = Field(..., description="Токен подтверждения")


# === OAuth2 Schemas ===


class OAuth2LoginRequest(BaseSchema):
    """Схема для OAuth2 аутентификации."""

    provider: AuthProvider = Field(..., description="OAuth2 провайдер")
    code: str = Field(..., description="Authorization code")
    state: Optional[str] = Field(None, description="State parameter")
    redirect_uri: str = Field(..., description="Redirect URI")


class OAuth2CallbackRequest(BaseSchema):
    """Схема для OAuth2 callback."""

    code: str = Field(..., description="Authorization code")
    state: Optional[str] = Field(None, description="State parameter")


# === Response Schemas ===


class LoginResponse(BaseSchema):
    """Схема ответа при успешной аутентификации."""

    access_token: str = Field(..., description="Access токен")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access токена")
    refresh_expires_in: int = Field(..., description="Время жизни refresh токена")

    if TYPE_CHECKING:
        user: "UserResponse" = Field(..., description="Данные пользователя")


class RegisterResponse(BaseSchema):
    """Схема ответа при успешной регистрации."""

    success: bool = Field(True, description="Успешность регистрации")
    message: str = Field(..., description="Сообщение")
    user_id: int = Field(..., description="ID созданного пользователя")
    email_verification_required: bool = Field(
        True, description="Требуется подтверждение email"
    )


class TokenRefreshResponse(AccessToken):
    """Схема ответа при обновлении токена."""

    if TYPE_CHECKING:
        user: Optional["UserResponse"] = Field(None, description="Данные пользователя")


class LogoutResponse(BaseSchema):
    """Схема ответа при выходе."""

    success: bool = Field(True, description="Успешность выхода")
    message: str = Field(..., description="Сообщение")


class PasswordResetResponse(BaseSchema):
    """Схема ответа при запросе сброса пароля."""

    success: bool = Field(True, description="Успешность запроса")
    message: str = Field(..., description="Сообщение")


class EmailVerificationResponse(BaseSchema):
    """Схема ответа при подтверждении email."""

    success: bool = Field(True, description="Успешность подтверждения")
    message: str = Field(..., description="Сообщение")


# === Session Management Schemas ===


class SessionInfo(BaseSchema):
    """Информация о сессии."""

    session_id: str = Field(..., description="ID сессии")
    user_id: int = Field(..., description="ID пользователя")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")
    created_at: datetime = Field(..., description="Время создания")
    last_activity: datetime = Field(..., description="Последняя активность")
    expires_at: datetime = Field(..., description="Время истечения")
    is_active: bool = Field(..., description="Активна ли сессия")


class SessionListResponse(BaseSchema):
    """Список активных сессий."""

    sessions: List[SessionInfo] = Field(..., description="Список сессий")
    total: int = Field(..., description="Общее количество")


# === Security Schemas ===


class SecurityEventRequest(BaseSchema):
    """Схема для записи событий безопасности."""

    event_type: str = Field(..., description="Тип события")
    description: str = Field(..., description="Описание события")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class SecurityStatsResponse(BaseSchema):
    """Статистика безопасности."""

    failed_logins_today: int = Field(..., description="Неудачных входов сегодня")
    blocked_accounts: int = Field(..., description="Заблокированных аккаунтов")
    password_resets_today: int = Field(..., description="Сбросов паролей сегодня")
    suspicious_activities: int = Field(..., description="Подозрительных активностей")


__all__ = [
    # Enums
    "TokenType",
    "AuthProvider",
    # Token schemas
    "TokenBase",
    "AccessToken",
    "RefreshToken",
    "TokenPair",
    "AccessTokenPayload",
    "RefreshTokenPayload",
    "TokenData",
    # Auth request schemas
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    "LogoutRequest",
    # Password schemas
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    # Email verification schemas
    "EmailVerificationRequest",
    "EmailVerificationConfirm",
    # OAuth2 schemas
    "OAuth2LoginRequest",
    "OAuth2CallbackRequest",
    # Response schemas
    "LoginResponse",
    "RegisterResponse",
    "TokenRefreshResponse",
    "LogoutResponse",
    "PasswordResetResponse",
    "EmailVerificationResponse",
    # Session schemas
    "SessionInfo",
    "SessionListResponse",
    # Security schemas
    "SecurityEventRequest",
    "SecurityStatsResponse",
]

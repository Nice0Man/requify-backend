"""
User Management Schemas.

Схемы для управления пользователями с поддержкой Enhanced Role System.
"""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.api.v1.common.schemas import (
    BaseSchema,
    CreateSchema,
    UpdateSchema,
    ResponseSchema,
    ListResponseSchema,
    ValidationMixin,
    FieldLimits,
    StandardDescriptions,
    SearchRequest,
    DateRangeFilter,
)
from app.api.v1.common.schemas.base import StatisticsSchema

# Условные импорты для избежания циклических зависимостей
if TYPE_CHECKING:
    from ..profiles.schemas import UserProfileResponse
    from ...organizations.companies.schemas import CompanyResponse
    from ..roles.schemas import UserRoleAssignmentResponse, EnhancedRoleResponse
    from ...analytics.dashboard.schemas import UserDashboardPreferences
    from ...organizations.teams.schemas import TeamResponse, TeamMemberResponse
    from ...configuration.settings.schemas import UserSettingsResponse


# === User Enums ===


class UserStatus(str, Enum):
    """Статусы пользователя."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class AuthProvider(str, Enum):
    """Провайдеры аутентификации."""

    LOCAL = "local"
    AUTH0 = "auth0"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    SSO = "sso"


# === Base Schemas ===


class UserBase(BaseSchema, ValidationMixin):
    """Базовая схема пользователя."""

    username: Optional[str] = Field(
        None,
        min_length=2,
        max_length=FieldLimits.SHORT_STRING_MAX,
        description="Имя пользователя (уникальное)",
    )
    email: EmailStr = Field(..., description="Email пользователя (уникальный)")
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Полное имя пользователя",
    )
    status: UserStatus = Field(UserStatus.ACTIVE, description="Статус пользователя")
    auth_provider: AuthProvider = Field(
        AuthProvider.LOCAL, description="Провайдер аутентификации"
    )
    auth_provider_id: Optional[str] = Field(
        None,
        max_length=FieldLimits.MEDIUM_STRING_MAX,
        description="ID пользователя у внешнего провайдера",
    )
    company_id: Optional[int] = Field(
        None, gt=0, description="ID основной компании пользователя"
    )
    is_email_verified: bool = Field(False, description="Подтвержден ли email")
    email_verified_at: Optional[datetime] = Field(
        None, description="Дата подтверждения email"
    )
    last_login_at: Optional[datetime] = Field(None, description="Дата последнего входа")
    login_attempts: int = Field(
        0, ge=0, description="Количество неудачных попыток входа"
    )
    locked_until: Optional[datetime] = Field(
        None, description="Заблокирован до (после множественных неудачных попыток)"
    )
    password_changed_at: Optional[datetime] = Field(
        None, description="Дата последней смены пароля"
    )
    terms_accepted_at: Optional[datetime] = Field(
        None, description="Дата принятия условий использования"
    )
    privacy_policy_accepted_at: Optional[datetime] = Field(
        None, description="Дата принятия политики конфиденциальности"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Пользовательские настройки"
    )
    user_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Дополнительные метаданные"
    )
    is_active: bool = Field(True, description=StandardDescriptions.IS_ACTIVE)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Валидация имени пользователя."""
        if v is None:
            return None

        v = cls.validate_non_empty_string(v, "username")
        v = v.strip().lower()

        # Имя пользователя может содержать только буквы, цифры, точки, дефисы и подчеркивания
        if not re.match(r"^[a-zA-Z0-9._-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, dots, hyphens and underscores"
            )

        # Не должно начинаться или заканчиваться специальными символами
        if v.startswith((".", "-", "_")) or v.endswith((".", "-", "_")):
            raise ValueError(
                "Username cannot start or end with dot, hyphen or underscore"
            )

        # Не должно содержать последовательные специальные символы
        if any(combo in v for combo in ["..", "--", "__", ".-", "-_", "_."]):
            raise ValueError("Username cannot contain consecutive special characters")

        # Проверка зарезервированных имен
        reserved_usernames = [
            "root",
            "administrator",
            "superuser",
            "api",
            "www",
            "mail",
            "support",
            "help",
            "service",
            "system",
            "null",
            "undefined",
        ]
        if v in reserved_usernames:
            raise ValueError(f"Username '{v}' is reserved")

        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> str:
        """Дополнительная валидация email."""
        email_str = str(v).lower()

        # Проверяем на запрещенные домены
        forbidden_domains = [
            "temp-mail.org",
            "10minutemail.com",
            "guerrillamail.com",
            "mailinator.com",
            "tempmail.email",
            "throwaway.email",
        ]
        domain = email_str.split("@")[1] if "@" in email_str else ""

        if domain in forbidden_domains:
            raise ValueError(f"Email domain {domain} is not allowed")

        # Проверяем длину локальной части
        local_part = email_str.split("@")[0] if "@" in email_str else ""
        if len(local_part) > 64:
            raise ValueError("Email local part cannot exceed 64 characters")

        return email_str


# === Request Schemas ===


class UserCreateRequest(UserBase, CreateSchema):
    """Схема создания пользователя."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="Пароль (будет захеширован)",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля."""
        v = cls.validate_non_empty_string(v, "password")

        # Минимальная длина
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Максимальная длина
        if len(v) > 255:
            raise ValueError("Password cannot exceed 255 characters")

        # Проверка на сложность (как минимум 3 из 4 типов символов)
        has_upper = bool(re.search(r"[A-Z]", v))
        has_lower = bool(re.search(r"[a-z]", v))
        has_digit = bool(re.search(r"\d", v))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", v))

        complexity_score = sum([has_upper, has_lower, has_digit, has_special])

        if complexity_score < 3:
            raise ValueError(
                "Password must contain at least 3 of: uppercase letter, "
                "lowercase letter, digit, special character"
            )

        # Проверка на общие слабые пароли
        weak_passwords = [
            "password",
            "123456",
            "qwerty",
            "admin",
            "letmein",
            "welcome",
            "monkey",
        ]
        if v.lower() in weak_passwords:
            raise ValueError("This password is too common")

        return v


class UserUpdateRequest(UpdateSchema):
    """Схема обновления пользователя."""

    username: Optional[str] = Field(
        None,
        min_length=2,
        max_length=FieldLimits.SHORT_STRING_MAX,
        description="Имя пользователя",
    )
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Полное имя"
    )
    email: Optional[EmailStr] = Field(None, description="Email")
    status: Optional[UserStatus] = Field(None, description="Статус")
    company_id: Optional[int] = Field(None, gt=0, description="ID компании")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Настройки")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")
    is_active: Optional[bool] = Field(None, description="Активен ли пользователь")


class UserProfileUpdateRequest(BaseSchema):
    """Схема обновления профиля пользователя."""

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Имя"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Фамилия"
    )
    bio: Optional[str] = Field(None, max_length=500, description="Биография")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    timezone: Optional[str] = Field(None, description="Часовой пояс")
    language: Optional[str] = Field(None, description="Предпочитаемый язык")


class UserRoleAssignmentRequest(BaseSchema):
    """Схема назначения роли пользователю."""

    role_id: int = Field(..., description="ID роли")
    context_type: Optional[str] = Field(
        None, description="Тип контекста (company, project, team)"
    )
    context_id: Optional[int] = Field(None, description="ID контекста")


# === Response Schemas ===


class UserResponse(UserBase, ResponseSchema):
    """Базовая информация о пользователе."""

    id: int = Field(..., description="ID пользователя")


class UserDetailResponse(UserResponse):
    """Детальная информация о пользователе."""

    # Статистика
    projects_count: int = Field(0, description="Количество проектов")
    teams_count: int = Field(0, description="Количество команд")
    active_roles_count: int = Field(0, description="Количество активных ролей")

    # Активность
    last_activity_at: Optional[datetime] = Field(
        None, description="Последняя активность"
    )
    total_logins: int = Field(0, description="Общее количество входов")

    # Метаданные
    created_by: Optional[int] = Field(None, description="ID создателя")
    updated_by: Optional[int] = Field(None, description="ID обновившего")


class UserWithRelationsResponse(UserDetailResponse):
    """Пользователь с загруженными связями."""

    if TYPE_CHECKING:
        profile: Optional["UserProfileResponse"] = Field(None, description="Профиль")
        company: Optional["CompanyResponse"] = Field(None, description="Компания")
        roles: List["UserRoleAssignmentResponse"] = Field(
            default_factory=list, description="Роли"
        )
        teams: List["TeamMemberResponse"] = Field(
            default_factory=list, description="Команды"
        )
        settings: Optional["UserSettingsResponse"] = Field(
            None, description="Настройки"
        )


class UserListResponse(ListResponseSchema[UserResponse]):
    """Список пользователей с пагинацией."""

    pass


class UserStatisticsResponse(StatisticsSchema):
    """Статистика пользователей."""

    total_users: int = Field(..., description="Всего пользователей")
    active_users: int = Field(..., description="Активных пользователей")
    new_users_this_month: int = Field(..., description="Новых пользователей за месяц")
    verified_users: int = Field(..., description="Подтвержденных пользователей")
    by_status: Dict[str, int] = Field(..., description="По статусам")
    by_auth_provider: Dict[str, int] = Field(..., description="По провайдерам")
    by_company: Dict[str, int] = Field(..., description="По компаниям")


# === Filter and Search Schemas ===


class UserFilterRequest(BaseSchema):
    """Фильтр пользователей."""

    status: Optional[List[UserStatus]] = Field(None, description="Статусы")
    auth_provider: Optional[List[AuthProvider]] = Field(None, description="Провайдеры")
    company_id: Optional[int] = Field(None, description="ID компании")
    is_email_verified: Optional[bool] = Field(None, description="Email подтвержден")
    created_from: Optional[datetime] = Field(None, description="Создан от")
    created_to: Optional[datetime] = Field(None, description="Создан до")
    last_login_from: Optional[datetime] = Field(None, description="Последний вход от")
    last_login_to: Optional[datetime] = Field(None, description="Последний вход до")


class UserSearchRequest(SearchRequest):
    """Поиск пользователей."""

    filters: Optional[UserFilterRequest] = Field(None, description="Фильтры")


# === Operation Schemas ===


class UserPasswordChangeRequest(BaseSchema):
    """Смена пароля пользователя."""

    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")
    confirm_password: str = Field(..., description="Подтверждение нового пароля")

    @model_validator(mode="after")
    def passwords_match(self):
        """Проверка совпадения паролей."""
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserPasswordResetRequest(BaseSchema):
    """Сброс пароля пользователя."""

    email: EmailStr = Field(..., description="Email пользователя")


class UserEmailVerificationRequest(BaseSchema):
    """Подтверждение email пользователя."""

    token: str = Field(..., description="Токен подтверждения")


class UserOperationResponse(BaseSchema):
    """Ответ операции с пользователем."""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение")
    user_id: Optional[int] = Field(None, description="ID пользователя")


# === Role Assignment Schemas ===


class UserRoleResponse(BaseSchema):
    """Ответ роли пользователя."""

    id: int = Field(..., description="ID назначения роли")
    role_id: int = Field(..., description="ID роли")
    role_name: str = Field(..., description="Название роли")
    context_type: str = Field(..., description="Тип контекста")
    context_id: Optional[int] = Field(None, description="ID контекста")
    assigned_at: datetime = Field(..., description="Дата назначения")
    assigned_by: Optional[int] = Field(None, description="Кто назначил")


__all__ = [
    "UserStatus",
    "AuthProvider",
    "UserBase",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserProfileUpdateRequest",
    "UserRoleAssignmentRequest",
    "UserResponse",
    "UserDetailResponse",
    "UserWithRelationsResponse",
    "UserListResponse",
    "UserStatisticsResponse",
    "UserFilterRequest",
    "UserSearchRequest",
    "UserPasswordChangeRequest",
    "UserPasswordResetRequest",
    "UserEmailVerificationRequest",
    "UserOperationResponse",
    "UserRoleResponse",
]

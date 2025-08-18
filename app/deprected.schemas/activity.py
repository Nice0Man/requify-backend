"""
Activity Tracking Schemas.

Схемы для отслеживания активности пользователей.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import Field

from app.api.v1.common.schemas import (
    BaseSchema,
    CreateSchema,
    UpdateSchema,
    ResponseSchema,
    ListResponseSchema,
    FieldLimits,
    StandardDescriptions,
)


# === Activity Enums ===


class ActivityType(str, Enum):
    """Типы активности."""

    # User activities
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_PROFILE_UPDATE = "user_profile_update"
    USER_PASSWORD_CHANGE = "user_password_change"

    # Project activities
    PROJECT_CREATE = "project_create"
    PROJECT_UPDATE = "project_update"
    PROJECT_DELETE = "project_delete"
    PROJECT_ARCHIVE = "project_archive"

    # Requirement activities
    REQUIREMENT_CREATE = "requirement_create"
    REQUIREMENT_UPDATE = "requirement_update"
    REQUIREMENT_DELETE = "requirement_delete"
    REQUIREMENT_STATUS_CHANGE = "requirement_status_change"

    # Team activities
    TEAM_CREATE = "team_create"
    TEAM_UPDATE = "team_update"
    TEAM_MEMBER_ADD = "team_member_add"
    TEAM_MEMBER_REMOVE = "team_member_remove"

    # Comment activities
    COMMENT_CREATE = "comment_create"
    COMMENT_UPDATE = "comment_update"
    COMMENT_DELETE = "comment_delete"

    # File activities
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"

    # System activities
    SYSTEM_BACKUP = "system_backup"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_UPDATE = "system_update"


class TargetType(str, Enum):
    """Типы объектов активности."""

    USER = "user"
    PROJECT = "project"
    REQUIREMENT = "requirement"
    TEAM = "team"
    COMPANY = "company"
    COMMENT = "comment"
    FILE = "file"
    SYSTEM = "system"


# === Base Schemas ===


class ActivityBase(BaseSchema):
    """Базовая схема активности."""

    activity_type: ActivityType = Field(..., description="Тип активности")
    target_type: TargetType = Field(..., description="Тип объекта")
    target_id: str = Field(..., description="ID объекта")
    description: Optional[str] = Field(
        None, max_length=FieldLimits.LONG_STRING_MAX, description="Описание активности"
    )
    activity_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Дополнительные данные активности"
    )
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")
    project_id: Optional[int] = Field(None, description="ID проекта")
    company_id: Optional[int] = Field(None, description="ID компании")


# === Request Schemas ===


class ActivityCreateRequest(ActivityBase, CreateSchema):
    """Схема создания записи активности."""

    user_id: int = Field(..., description="ID пользователя")


class ActivityUpdateRequest(UpdateSchema):
    """Схема обновления активности."""

    description: Optional[str] = Field(None, description="Описание")
    activity_metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")


# === Response Schemas ===


class ActivityResponse(ActivityBase, ResponseSchema):
    """Схема ответа с данными активности."""

    id: int = Field(..., description="ID активности")
    user_id: int = Field(..., description="ID пользователя")
    created_at: datetime = Field(..., description="Время активности")


class ActivityDetailResponse(ActivityResponse):
    """Детальная информация об активности."""

    # Дополнительные поля для детального просмотра
    duration_seconds: Optional[int] = Field(None, description="Длительность в секундах")
    related_activities: List["ActivityResponse"] = Field(
        default_factory=list, description="Связанные активности"
    )

    # Информация о пользователе (может быть загружена отдельно)
    user_name: Optional[str] = Field(None, description="Имя пользователя")
    user_email: Optional[str] = Field(None, description="Email пользователя")


class ActivityListResponse(ListResponseSchema[ActivityResponse]):
    """Список активностей с пагинацией."""

    pass


class ActivityFeedResponse(BaseSchema):
    """Лента активности."""

    activities: List[ActivityResponse] = Field(
        default_factory=list, description="Список активностей"
    )
    total_count: int = Field(0, description="Общее количество")
    has_more: bool = Field(False, description="Есть ли еще активности")


class ActivityStatisticsResponse(BaseSchema):
    """Статистика активности."""

    total_activities: int = Field(..., description="Всего активностей")
    activities_today: int = Field(..., description="Активностей сегодня")
    activities_this_week: int = Field(..., description="Активностей на этой неделе")
    activities_this_month: int = Field(..., description="Активностей в этом месяце")

    # По типам
    by_type: Dict[str, int] = Field(..., description="По типам активности")
    by_target_type: Dict[str, int] = Field(..., description="По типам объектов")
    by_user: Dict[str, int] = Field(..., description="По пользователям")

    # Самые активные
    most_active_users: List[Dict[str, Any]] = Field(
        default_factory=list, description="Самые активные пользователи"
    )
    most_common_activities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Самые частые активности"
    )


# === Filter and Search Schemas ===


class ActivityFilterRequest(BaseSchema):
    """Фильтр активностей."""

    activity_types: Optional[List[ActivityType]] = Field(
        None, description="Типы активности"
    )
    target_types: Optional[List[TargetType]] = Field(None, description="Типы объектов")
    user_ids: Optional[List[int]] = Field(None, description="ID пользователей")
    project_ids: Optional[List[int]] = Field(None, description="ID проектов")
    company_ids: Optional[List[int]] = Field(None, description="ID компаний")
    date_from: Optional[datetime] = Field(None, description="Дата от")
    date_to: Optional[datetime] = Field(None, description="Дата до")
    target_id: Optional[str] = Field(None, description="ID конкретного объекта")


class ActivitySearchRequest(BaseSchema):
    """Поиск активностей."""

    query: Optional[str] = Field(None, min_length=1, description="Поисковый запрос")
    filters: Optional[ActivityFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")
    sort_by: str = Field("created_at", description="Поле сортировки")
    sort_order: str = Field("desc", description="Порядок сортировки")


# === Batch Operations ===


class ActivityBatchCreateRequest(BaseSchema):
    """Пакетное создание активностей."""

    activities: List[ActivityCreateRequest] = Field(
        ..., min_items=1, max_items=100, description="Список активностей для создания"
    )


class ActivityBatchResponse(BaseSchema):
    """Результат пакетной операции."""

    success: bool = Field(..., description="Успешность операции")
    created_count: int = Field(..., description="Количество созданных записей")
    failed_count: int = Field(..., description="Количество неудачных записей")
    errors: List[str] = Field(default_factory=list, description="Ошибки")


__all__ = [
    "ActivityType",
    "TargetType",
    "ActivityBase",
    "ActivityCreateRequest",
    "ActivityUpdateRequest",
    "ActivityResponse",
    "ActivityDetailResponse",
    "ActivityListResponse",
    "ActivityStatisticsResponse",
    "ActivityFilterRequest",
    "ActivitySearchRequest",
    "ActivityBatchCreateRequest",
    "ActivityBatchResponse",
]

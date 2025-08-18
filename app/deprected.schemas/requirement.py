"""
Requirements Schemas.

Схемы для операций с требованиями.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import Field

from app.api.v1.common.schemas import (
    BaseSchema,
    CreateSchema,
    UpdateSchema,
    ResponseSchema,
    ListResponseSchema,
)


# === Requirement Enums ===


class RequirementType(str, Enum):
    """Типы требований."""

    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER_STORY = "user_story"
    EPIC = "epic"
    FEATURE = "feature"


class RequirementStatus(str, Enum):
    """Статусы требований."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class RequirementPriority(str, Enum):
    """Приоритеты требований."""

    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"
    CRITICAL = "critical"


class RequirementComplexity(str, Enum):
    """Сложность требования."""

    TRIVIAL = "trivial"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
    BLOCKER = "blocker"


# === Base Schemas ===


class RequirementBase(BaseSchema):
    """Базовая схема требования."""

    title: str = Field(..., min_length=1, max_length=255, description="Заголовок")
    description: Optional[str] = Field(None, description="Описание")
    type: RequirementType = Field(..., description="Тип требования")
    priority: RequirementPriority = Field(..., description="Приоритет")
    status: RequirementStatus = Field(RequirementStatus.DRAFT, description="Статус")
    complexity: Optional[RequirementComplexity] = Field(None, description="Сложность")


# === Request Schemas ===


class RequirementCreateRequest(RequirementBase):
    """Схема создания требования."""

    project_id: int = Field(..., gt=0, description="ID проекта")
    parent_id: Optional[int] = Field(None, description="ID родительского требования")
    acceptance_criteria: Optional[str] = Field(None, description="Критерии приемки")
    business_value: Optional[int] = Field(
        None, ge=1, le=10, description="Бизнес-ценность"
    )
    estimated_hours: Optional[float] = Field(None, ge=0, description="Оценка в часах")


class RequirementUpdateRequest(BaseSchema):
    """Схема обновления требования."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Заголовок"
    )
    description: Optional[str] = Field(None, description="Описание")
    type: Optional[RequirementType] = Field(None, description="Тип")
    priority: Optional[RequirementPriority] = Field(None, description="Приоритет")
    status: Optional[RequirementStatus] = Field(None, description="Статус")
    complexity: Optional[RequirementComplexity] = Field(None, description="Сложность")
    acceptance_criteria: Optional[str] = Field(None, description="Критерии приемки")
    business_value: Optional[int] = Field(
        None, ge=1, le=10, description="Бизнес-ценность"
    )
    estimated_hours: Optional[float] = Field(None, ge=0, description="Оценка в часах")


# === Response Schemas ===


class RequirementResponse(RequirementBase):
    """Схема ответа с данными требования."""

    id: int = Field(..., description="ID требования")
    project_id: int = Field(..., description="ID проекта")
    parent_id: Optional[int] = Field(None, description="ID родительского требования")
    acceptance_criteria: Optional[str] = Field(None, description="Критерии приемки")
    business_value: Optional[int] = Field(None, description="Бизнес-ценность")
    estimated_hours: Optional[float] = Field(None, description="Оценка в часах")
    actual_hours: Optional[float] = Field(
        None, description="Фактически потрачено часов"
    )
    created_by: int = Field(..., description="ID автора")
    assigned_to: Optional[int] = Field(None, description="ID ответственного")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class RequirementDetailResponse(RequirementResponse):
    """Детальная информация о требовании."""

    # Дочерние требования
    children_count: int = Field(0, description="Количество дочерних требований")

    # Связи
    relationships_count: int = Field(0, description="Количество связей")

    # Тестирование
    test_cases_count: int = Field(0, description="Количество тест-кейсов")
    passed_tests: int = Field(0, description="Пройденные тесты")

    # Комментарии и активность
    comments_count: int = Field(0, description="Количество комментариев")
    last_activity_at: Optional[datetime] = Field(
        None, description="Последняя активность"
    )

    # Метаданные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class RequirementListResponse(BaseSchema):
    """Список требований с пагинацией."""

    requirements: List[RequirementResponse] = Field(
        ..., description="Список требований"
    )
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Filter and Search Schemas ===


class RequirementFilterRequest(BaseSchema):
    """Фильтр требований."""

    project_id: Optional[int] = Field(None, description="ID проекта")
    type: Optional[List[RequirementType]] = Field(None, description="Типы")
    status: Optional[List[RequirementStatus]] = Field(None, description="Статусы")
    priority: Optional[List[RequirementPriority]] = Field(
        None, description="Приоритеты"
    )
    complexity: Optional[List[RequirementComplexity]] = Field(
        None, description="Сложность"
    )
    assigned_to: Optional[int] = Field(None, description="ID ответственного")
    created_by: Optional[int] = Field(None, description="ID автора")
    parent_id: Optional[int] = Field(None, description="ID родителя")
    has_children: Optional[bool] = Field(None, description="Есть ли дочерние")
    created_from: Optional[datetime] = Field(None, description="Создано с")
    created_to: Optional[datetime] = Field(None, description="Создано до")
    updated_from: Optional[datetime] = Field(None, description="Обновлено с")
    updated_to: Optional[datetime] = Field(None, description="Обновлено до")


class RequirementSearchRequest(BaseSchema):
    """Поиск требований."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    filters: Optional[RequirementFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


# === Configuration Schemas ===


class RequirementTypeConfig(BaseSchema):
    """Конфигурация типа требования."""

    id: int = Field(..., description="ID типа")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    color: Optional[str] = Field(None, description="Цвет")
    icon: Optional[str] = Field(None, description="Иконка")
    is_active: bool = Field(True, description="Активен ли тип")
    sort_order: int = Field(0, description="Порядок сортировки")


class RequirementStatusConfig(BaseSchema):
    """Конфигурация статуса требования."""

    id: int = Field(..., description="ID статуса")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    color: Optional[str] = Field(None, description="Цвет")
    is_final: bool = Field(False, description="Финальный статус")
    is_active: bool = Field(True, description="Активен ли статус")
    sort_order: int = Field(0, description="Порядок сортировки")


class RequirementPriorityConfig(BaseSchema):
    """Конфигурация приоритета требования."""

    id: int = Field(..., description="ID приоритета")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    color: Optional[str] = Field(None, description="Цвет")
    level: int = Field(..., description="Уровень приоритета")
    is_active: bool = Field(True, description="Активен ли приоритет")
    sort_order: int = Field(0, description="Порядок сортировки")


# === Statistics Schemas ===


class RequirementStatisticsResponse(BaseSchema):
    """Статистика по требованиям."""

    total_requirements: int = Field(..., description="Всего требований")
    by_status: Dict[str, int] = Field(..., description="По статусам")
    by_type: Dict[str, int] = Field(..., description="По типам")
    by_priority: Dict[str, int] = Field(..., description="По приоритетам")
    completion_rate: float = Field(..., description="Процент выполнения")
    average_business_value: Optional[float] = Field(
        None, description="Средняя бизнес-ценность"
    )
    total_estimated_hours: Optional[float] = Field(
        None, description="Общая оценка в часах"
    )
    total_actual_hours: Optional[float] = Field(
        None, description="Фактически потрачено часов"
    )


# === Export Schemas ===


class RequirementExportRequest(BaseSchema):
    """Запрос на экспорт требований."""

    requirement_ids: Optional[List[int]] = Field(None, description="ID требований")
    format: str = Field("xlsx", description="Формат экспорта")
    filters: Optional[RequirementFilterRequest] = Field(None, description="Фильтры")
    include_relationships: bool = Field(False, description="Включить связи")
    include_comments: bool = Field(False, description="Включить комментарии")
    include_test_cases: bool = Field(False, description="Включить тест-кейсы")


class RequirementExportResponse(BaseSchema):
    """Ответ экспорта требований."""

    success: bool = Field(..., description="Успешность операции")
    export_id: str = Field(..., description="ID экспорта")
    download_url: str = Field(..., description="URL скачивания")
    file_size_bytes: int = Field(..., description="Размер файла")
    expires_at: datetime = Field(..., description="Время истечения ссылки")


__all__ = [
    "RequirementType",
    "RequirementStatus",
    "RequirementPriority",
    "RequirementComplexity",
    "RequirementBase",
    "RequirementCreateRequest",
    "RequirementUpdateRequest",
    "RequirementResponse",
    "RequirementDetailResponse",
    "RequirementListResponse",
    "RequirementFilterRequest",
    "RequirementSearchRequest",
    "RequirementTypeConfig",
    "RequirementStatusConfig",
    "RequirementPriorityConfig",
    "RequirementStatisticsResponse",
    "RequirementExportRequest",
    "RequirementExportResponse",
]

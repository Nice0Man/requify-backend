"""
Project Core Schemas.

Схемы для основных операций с проектами в соответствии с моделью Project.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import Field

from app.api.v1.common.schemas import (
    BaseSchema,
    CreateSchema,
    UpdateSchema,
    ResponseSchema,
    ListResponseSchema,
)
from app.models.constants import ProjectStatus, Priority


# === Request Schemas ===


class ProjectCreateRequest(CreateSchema):
    """Схема создания проекта в соответствии с моделью Project."""

    code: str = Field(
        ..., min_length=1, max_length=50, description="Уникальный код проекта"
    )
    name: str = Field(..., min_length=1, max_length=255, description="Название проекта")
    description: Optional[str] = Field(None, description="Описание проекта")
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="Статус проекта")
    priority: Priority = Field(Priority.MEDIUM, description="Приоритет проекта")

    # Даты проекта
    start_date: Optional[datetime] = Field(None, description="Дата начала проекта")
    end_date: Optional[datetime] = Field(None, description="Дата окончания проекта")

    # Связи с организационной структурой
    company_id: int = Field(..., gt=0, description="ID компании")
    department_id: Optional[int] = Field(None, gt=0, description="ID департамента")
    team_id: Optional[int] = Field(None, gt=0, description="ID команды")

    # Дополнительные данные
    project_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Метаданные проекта"
    )


class ProjectUpdateRequest(UpdateSchema):
    """Схема обновления проекта в соответствии с моделью Project."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название проекта"
    )
    description: Optional[str] = Field(None, description="Описание проекта")
    status: Optional[ProjectStatus] = Field(None, description="Статус проекта")
    priority: Optional[Priority] = Field(None, description="Приоритет проекта")

    # Даты проекта
    start_date: Optional[datetime] = Field(None, description="Дата начала проекта")
    end_date: Optional[datetime] = Field(None, description="Дата окончания проекта")

    # Организационные связи
    department_id: Optional[int] = Field(None, gt=0, description="ID департамента")
    team_id: Optional[int] = Field(None, gt=0, description="ID команды")

    # Дополнительные данные
    project_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Метаданные проекта"
    )


# === Response Schemas ===


class ProjectResponse(ResponseSchema):
    """Схема ответа с данными проекта в соответствии с моделью Project."""

    id: int = Field(..., description="ID проекта")
    code: str = Field(..., description="Уникальный код проекта")
    name: str = Field(..., description="Название проекта")
    description: Optional[str] = Field(None, description="Описание проекта")
    status: ProjectStatus = Field(..., description="Статус проекта")
    priority: Priority = Field(..., description="Приоритет проекта")

    # Даты проекта
    start_date: Optional[datetime] = Field(None, description="Дата начала проекта")
    end_date: Optional[datetime] = Field(None, description="Дата окончания проекта")

    # Связи с организационной структурой
    company_id: int = Field(..., description="ID компании")
    department_id: Optional[int] = Field(None, description="ID департамента")
    team_id: Optional[int] = Field(None, description="ID команды")

    # Дополнительные данные
    project_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Метаданные проекта"
    )

    # Временные метки
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class ProjectDetailResponse(ProjectResponse):
    """Детальная информация о проекте."""

    # Статистика
    requirements_count: int = Field(0, description="Количество требований")
    completed_requirements: int = Field(0, description="Выполненные требования")
    releases_count: int = Field(0, description="Количество релизов")
    team_members_count: int = Field(0, description="Количество участников")

    # Прогресс
    progress_percentage: float = Field(
        0.0, ge=0, le=100, description="Процент выполнения"
    )

    # Дополнительные данные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class ProjectListResponse(BaseSchema):
    """Список проектов с пагинацией."""

    projects: List[ProjectResponse] = Field(..., description="Список проектов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


class ProjectStatisticsResponse(BaseSchema):
    """Статистика по проектам."""

    total_projects: int = Field(..., description="Всего проектов")
    active_projects: int = Field(..., description="Активных проектов")
    completed_projects: int = Field(..., description="Завершенных проектов")
    overdue_projects: int = Field(..., description="Просроченных проектов")
    average_completion_rate: float = Field(
        ..., description="Средний процент выполнения"
    )


# === Filter and Search Schemas ===


class ProjectFilterRequest(BaseSchema):
    """Фильтр проектов."""

    status: Optional[List[str]] = Field(None, description="Статусы")
    priority: Optional[List[str]] = Field(None, description="Приоритеты")
    company_id: Optional[int] = Field(None, description="ID компании")
    start_date_from: Optional[datetime] = Field(None, description="Дата начала от")
    start_date_to: Optional[datetime] = Field(None, description="Дата начала до")
    end_date_from: Optional[datetime] = Field(None, description="Дата окончания от")
    end_date_to: Optional[datetime] = Field(None, description="Дата окончания до")


class ProjectSearchRequest(BaseSchema):
    """Поиск проектов."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    filters: Optional[ProjectFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


# === Export Schemas ===


class ProjectExportRequest(BaseSchema):
    """Запрос на экспорт проектов."""

    project_ids: Optional[List[int]] = Field(None, description="ID проектов")
    format: str = Field("xlsx", description="Формат экспорта")
    include_requirements: bool = Field(False, description="Включить требования")
    include_releases: bool = Field(False, description="Включить релизы")
    filters: Optional[ProjectFilterRequest] = Field(None, description="Фильтры")


class ProjectExportResponse(BaseSchema):
    """Ответ экспорта проектов."""

    success: bool = Field(..., description="Успешность операции")
    export_id: str = Field(..., description="ID экспорта")
    download_url: str = Field(..., description="URL скачивания")
    file_size_bytes: int = Field(..., description="Размер файла")
    expires_at: datetime = Field(..., description="Время истечения ссылки")


__all__ = [
    "ProjectStatus",
    "ProjectPriority",
    "ProjectPhase",
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    "ProjectResponse",
    "ProjectDetailResponse",
    "ProjectListResponse",
    "ProjectStatisticsResponse",
    "ProjectFilterRequest",
    "ProjectSearchRequest",
    "ProjectExportRequest",
    "ProjectExportResponse",
]

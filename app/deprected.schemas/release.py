"""
Release Schemas.

Схемы для операций с релизами.
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


# === Release Enums ===


class ReleaseStatus(str, Enum):
    """Статусы релизов."""

    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    READY = "ready"
    RELEASED = "released"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ReleaseType(str, Enum):
    """Типы релизов."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    HOTFIX = "hotfix"
    BETA = "beta"
    ALPHA = "alpha"


class ReleaseEnvironment(str, Enum):
    """Среды релиза."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


# === Request Schemas ===


class ReleaseCreateRequest(BaseSchema):
    """Схема создания релиза."""

    name: str = Field(..., min_length=1, max_length=255, description="Название релиза")
    version: str = Field(..., min_length=1, max_length=50, description="Версия")
    description: Optional[str] = Field(None, description="Описание релиза")
    release_type: ReleaseType = Field(..., description="Тип релиза")
    status: ReleaseStatus = Field(ReleaseStatus.PLANNING, description="Статус")
    project_id: int = Field(..., gt=0, description="ID проекта")
    planned_date: Optional[datetime] = Field(None, description="Запланированная дата")
    target_environment: ReleaseEnvironment = Field(..., description="Целевая среда")


class ReleaseUpdateRequest(BaseSchema):
    """Схема обновления релиза."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название"
    )
    version: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Версия"
    )
    description: Optional[str] = Field(None, description="Описание")
    release_type: Optional[ReleaseType] = Field(None, description="Тип релиза")
    status: Optional[ReleaseStatus] = Field(None, description="Статус")
    planned_date: Optional[datetime] = Field(None, description="Запланированная дата")
    actual_date: Optional[datetime] = Field(None, description="Фактическая дата")
    target_environment: Optional[ReleaseEnvironment] = Field(
        None, description="Целевая среда"
    )


# === Response Schemas ===


class ReleaseResponse(BaseSchema):
    """Схема ответа с данными релиза."""

    id: int = Field(..., description="ID релиза")
    name: str = Field(..., description="Название")
    version: str = Field(..., description="Версия")
    description: Optional[str] = Field(None, description="Описание")
    release_type: ReleaseType = Field(..., description="Тип релиза")
    status: ReleaseStatus = Field(..., description="Статус")
    project_id: int = Field(..., description="ID проекта")
    planned_date: Optional[datetime] = Field(None, description="Запланированная дата")
    actual_date: Optional[datetime] = Field(None, description="Фактическая дата")
    target_environment: ReleaseEnvironment = Field(..., description="Целевая среда")
    created_by: int = Field(..., description="ID создателя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class ReleaseDetailResponse(ReleaseResponse):
    """Детальная информация о релизе."""

    # Требования в релизе
    requirements_count: int = Field(0, description="Количество требований")
    completed_requirements: int = Field(0, description="Выполненные требования")

    # Прогресс
    progress_percentage: float = Field(
        0.0, ge=0, le=100, description="Процент готовности"
    )

    # Тестирование
    test_cases_count: int = Field(0, description="Количество тест-кейсов")
    passed_tests: int = Field(0, description="Пройденные тесты")
    failed_tests: int = Field(0, description="Провалившиеся тесты")

    # Дефекты
    defects_count: int = Field(0, description="Количество дефектов")
    open_defects: int = Field(0, description="Открытые дефекты")

    # Изменения
    changelog: Optional[str] = Field(None, description="Список изменений")

    # Метаданные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class ReleaseListResponse(BaseSchema):
    """Список релизов с пагинацией."""

    releases: List[ReleaseResponse] = Field(..., description="Список релизов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Requirements in Release ===


class ReleaseRequirementRequest(BaseSchema):
    """Запрос на добавление требования в релиз."""

    requirement_id: int = Field(..., gt=0, description="ID требования")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Приоритет в релизе")


class ReleaseRequirementResponse(BaseSchema):
    """Требование в релизе."""

    id: int = Field(..., description="ID связи")
    release_id: int = Field(..., description="ID релиза")
    requirement_id: int = Field(..., description="ID требования")
    priority: Optional[int] = Field(None, description="Приоритет в релизе")
    added_at: datetime = Field(..., description="Дата добавления")
    added_by: int = Field(..., description="ID добавившего")


# === Release Deployment ===


class ReleaseDeploymentRequest(BaseSchema):
    """Запрос на развертывание релиза."""

    environment: ReleaseEnvironment = Field(..., description="Среда развертывания")
    notes: Optional[str] = Field(None, description="Примечания к развертыванию")
    rollback_plan: Optional[str] = Field(None, description="План отката")


class ReleaseDeploymentResponse(BaseSchema):
    """Информация о развертывании."""

    id: int = Field(..., description="ID развертывания")
    release_id: int = Field(..., description="ID релиза")
    environment: ReleaseEnvironment = Field(..., description="Среда")
    status: str = Field(..., description="Статус развертывания")
    started_at: datetime = Field(..., description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    deployed_by: int = Field(..., description="ID развернувшего")
    notes: Optional[str] = Field(None, description="Примечания")
    rollback_plan: Optional[str] = Field(None, description="План отката")


# === Release Comparison ===


class ReleaseComparisonRequest(BaseSchema):
    """Запрос на сравнение релизов."""

    source_release_id: int = Field(..., gt=0, description="Исходный релиз")
    target_release_id: int = Field(..., gt=0, description="Целевой релиз")
    include_requirements: bool = Field(True, description="Включить требования")
    include_test_results: bool = Field(True, description="Включить результаты тестов")


class ReleaseComparisonResponse(BaseSchema):
    """Результат сравнения релизов."""

    source_release_id: int = Field(..., description="Исходный релиз")
    target_release_id: int = Field(..., description="Целевой релиз")

    # Различия в требованиях
    added_requirements: List[int] = Field(..., description="Добавленные требования")
    removed_requirements: List[int] = Field(..., description="Удаленные требования")

    # Изменения статуса
    status_changes: Dict[str, Any] = Field(..., description="Изменения статусов")

    # Результаты тестирования
    test_changes: Dict[str, Any] = Field(..., description="Изменения в тестах")


# === Filter and Search Schemas ===


class ReleaseFilterRequest(BaseSchema):
    """Фильтр релизов."""

    project_id: Optional[int] = Field(None, description="ID проекта")
    status: Optional[List[ReleaseStatus]] = Field(None, description="Статусы")
    release_type: Optional[List[ReleaseType]] = Field(None, description="Типы релизов")
    environment: Optional[List[ReleaseEnvironment]] = Field(None, description="Среды")
    planned_from: Optional[datetime] = Field(None, description="Запланировано с")
    planned_to: Optional[datetime] = Field(None, description="Запланировано до")
    actual_from: Optional[datetime] = Field(None, description="Выпущено с")
    actual_to: Optional[datetime] = Field(None, description="Выпущено до")
    created_by: Optional[int] = Field(None, description="ID создателя")


class ReleaseSearchRequest(BaseSchema):
    """Поиск релизов."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    filters: Optional[ReleaseFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


# === Statistics ===


class ReleaseStatisticsResponse(BaseSchema):
    """Статистика по релизам."""

    total_releases: int = Field(..., description="Всего релизов")
    by_status: Dict[str, int] = Field(..., description="По статусам")
    by_type: Dict[str, int] = Field(..., description="По типам")
    by_environment: Dict[str, int] = Field(..., description="По средам")
    average_completion_time_days: Optional[float] = Field(
        None, description="Среднее время завершения"
    )
    on_time_releases: int = Field(..., description="Релизы в срок")
    delayed_releases: int = Field(..., description="Задержанные релизы")


# === Export Schemas ===


class ReleaseExportRequest(BaseSchema):
    """Запрос на экспорт релизов."""

    release_ids: Optional[List[int]] = Field(None, description="ID релизов")
    format: str = Field("xlsx", description="Формат экспорта")
    filters: Optional[ReleaseFilterRequest] = Field(None, description="Фильтры")
    include_requirements: bool = Field(False, description="Включить требования")
    include_changelog: bool = Field(True, description="Включить changelog")
    include_deployment_info: bool = Field(
        False, description="Включить информацию о развертывании"
    )


class ReleaseExportResponse(BaseSchema):
    """Ответ экспорта релизов."""

    success: bool = Field(..., description="Успешность операции")
    export_id: str = Field(..., description="ID экспорта")
    download_url: str = Field(..., description="URL скачивания")
    file_size_bytes: int = Field(..., description="Размер файла")
    expires_at: datetime = Field(..., description="Время истечения ссылки")


__all__ = [
    "ReleaseStatus",
    "ReleaseType",
    "ReleaseEnvironment",
    "ReleaseCreateRequest",
    "ReleaseUpdateRequest",
    "ReleaseResponse",
    "ReleaseDetailResponse",
    "ReleaseListResponse",
    "ReleaseRequirementRequest",
    "ReleaseRequirementResponse",
    "ReleaseDeploymentRequest",
    "ReleaseDeploymentResponse",
    "ReleaseComparisonRequest",
    "ReleaseComparisonResponse",
    "ReleaseFilterRequest",
    "ReleaseSearchRequest",
    "ReleaseStatisticsResponse",
    "ReleaseExportRequest",
    "ReleaseExportResponse",
]

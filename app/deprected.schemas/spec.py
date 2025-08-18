"""
Specification Schemas.

Схемы для операций со спецификациями.
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


# === Specification Enums ===


class SpecificationStatus(str, Enum):
    """Статусы спецификаций."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class SpecificationType(str, Enum):
    """Типы спецификаций."""

    FUNCTIONAL = "functional"
    TECHNICAL = "technical"
    API = "api"
    DATABASE = "database"
    ARCHITECTURE = "architecture"
    INTERFACE = "interface"
    BUSINESS = "business"
    INTEGRATION = "integration"


class DocumentFormat(str, Enum):
    """Форматы документов."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    CONFLUENCE = "confluence"


# === Request Schemas ===


class SpecificationCreateRequest(BaseSchema):
    """Схема создания спецификации."""

    title: str = Field(
        ..., min_length=1, max_length=255, description="Заголовок спецификации"
    )
    description: Optional[str] = Field(None, description="Описание")
    content: str = Field(..., description="Содержимое спецификации")
    specification_type: SpecificationType = Field(..., description="Тип спецификации")
    status: SpecificationStatus = Field(SpecificationStatus.DRAFT, description="Статус")
    project_id: int = Field(..., gt=0, description="ID проекта")
    parent_id: Optional[int] = Field(None, description="ID родительской спецификации")
    version: str = Field("1.0", description="Версия спецификации")
    format: DocumentFormat = Field(
        DocumentFormat.MARKDOWN, description="Формат документа"
    )


class SpecificationUpdateRequest(BaseSchema):
    """Схема обновления спецификации."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Заголовок"
    )
    description: Optional[str] = Field(None, description="Описание")
    content: Optional[str] = Field(None, description="Содержимое")
    specification_type: Optional[SpecificationType] = Field(None, description="Тип")
    status: Optional[SpecificationStatus] = Field(None, description="Статус")
    parent_id: Optional[int] = Field(None, description="ID родительской спецификации")
    version: Optional[str] = Field(None, description="Версия")
    format: Optional[DocumentFormat] = Field(None, description="Формат документа")


# === Response Schemas ===


class SpecificationResponse(BaseSchema):
    """Схема ответа с данными спецификации."""

    id: int = Field(..., description="ID спецификации")
    title: str = Field(..., description="Заголовок")
    description: Optional[str] = Field(None, description="Описание")
    content: str = Field(..., description="Содержимое")
    specification_type: SpecificationType = Field(..., description="Тип")
    status: SpecificationStatus = Field(..., description="Статус")
    project_id: int = Field(..., description="ID проекта")
    parent_id: Optional[int] = Field(None, description="ID родительской спецификации")
    version: str = Field(..., description="Версия")
    format: DocumentFormat = Field(..., description="Формат документа")
    created_by: int = Field(..., description="ID создателя")
    updated_by: Optional[int] = Field(None, description="ID обновившего")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class SpecificationDetailResponse(SpecificationResponse):
    """Детальная информация о спецификации."""

    # Иерархия
    children_count: int = Field(0, description="Количество дочерних спецификаций")
    depth_level: int = Field(0, description="Уровень вложенности")

    # Связи с требованиями
    requirements_count: int = Field(0, description="Количество связанных требований")

    # История изменений
    versions_count: int = Field(0, description="Количество версий")
    last_review_date: Optional[datetime] = Field(
        None, description="Дата последнего обзора"
    )

    # Метрики
    content_length: int = Field(0, description="Длина содержимого")
    reading_time_minutes: int = Field(0, description="Время чтения в минутах")

    # Метаданные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class SpecificationListResponse(BaseSchema):
    """Список спецификаций с пагинацией."""

    specifications: List[SpecificationResponse] = Field(
        ..., description="Список спецификаций"
    )
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Version Management ===


class SpecificationVersionCreateRequest(BaseSchema):
    """Создание новой версии спецификации."""

    version: str = Field(..., description="Номер версии")
    change_description: str = Field(..., description="Описание изменений")
    content: str = Field(..., description="Содержимое новой версии")


class SpecificationVersionResponse(BaseSchema):
    """Информация о версии спецификации."""

    id: int = Field(..., description="ID версии")
    specification_id: int = Field(..., description="ID спецификации")
    version: str = Field(..., description="Номер версии")
    change_description: str = Field(..., description="Описание изменений")
    content: str = Field(..., description="Содержимое версии")
    created_by: int = Field(..., description="ID создателя версии")
    created_at: datetime = Field(..., description="Дата создания версии")
    is_current: bool = Field(False, description="Текущая версия")


class SpecificationVersionCompareRequest(BaseSchema):
    """Запрос на сравнение версий."""

    source_version_id: int = Field(..., description="ID исходной версии")
    target_version_id: int = Field(..., description="ID целевой версии")
    include_content_diff: bool = Field(True, description="Включить различия в контенте")


class SpecificationVersionCompareResponse(BaseSchema):
    """Результат сравнения версий."""

    source_version: str = Field(..., description="Исходная версия")
    target_version: str = Field(..., description="Целевая версия")
    content_diff: Optional[str] = Field(None, description="Различия в контенте")
    changes_summary: Dict[str, Any] = Field(..., description="Сводка изменений")
    generated_at: datetime = Field(..., description="Время генерации сравнения")


# === Review Process ===


class SpecificationReviewRequest(BaseSchema):
    """Запрос на обзор спецификации."""

    reviewer_id: int = Field(..., gt=0, description="ID рецензента")
    deadline: Optional[datetime] = Field(None, description="Срок обзора")
    notes: Optional[str] = Field(None, description="Примечания для рецензента")


class SpecificationReviewResponse(BaseSchema):
    """Результат обзора спецификации."""

    id: int = Field(..., description="ID обзора")
    specification_id: int = Field(..., description="ID спецификации")
    reviewer_id: int = Field(..., description="ID рецензента")
    status: str = Field(..., description="Статус обзора")
    decision: Optional[str] = Field(None, description="Решение рецензента")
    comments: Optional[str] = Field(None, description="Комментарии")
    deadline: Optional[datetime] = Field(None, description="Срок обзора")
    completed_at: Optional[datetime] = Field(None, description="Дата завершения")
    created_at: datetime = Field(..., description="Дата создания")


# === Template Management ===


class SpecificationTemplateCreateRequest(BaseSchema):
    """Создание шаблона спецификации."""

    name: str = Field(..., min_length=1, max_length=255, description="Название шаблона")
    description: Optional[str] = Field(None, description="Описание шаблона")
    content_template: str = Field(..., description="Шаблон содержимого")
    specification_type: SpecificationType = Field(..., description="Тип спецификации")
    is_public: bool = Field(False, description="Публичный шаблон")


class SpecificationTemplateResponse(BaseSchema):
    """Информация о шаблоне спецификации."""

    id: int = Field(..., description="ID шаблона")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    content_template: str = Field(..., description="Шаблон содержимого")
    specification_type: SpecificationType = Field(..., description="Тип")
    is_public: bool = Field(..., description="Публичный шаблон")
    usage_count: int = Field(0, description="Количество использований")
    created_by: int = Field(..., description="ID создателя")
    created_at: datetime = Field(..., description="Дата создания")


# === Filter and Search Schemas ===


class SpecificationFilterRequest(BaseSchema):
    """Фильтр спецификаций."""

    project_id: Optional[int] = Field(None, description="ID проекта")
    specification_type: Optional[List[SpecificationType]] = Field(
        None, description="Типы"
    )
    status: Optional[List[SpecificationStatus]] = Field(None, description="Статусы")
    created_by: Optional[int] = Field(None, description="ID создателя")
    parent_id: Optional[int] = Field(None, description="ID родительской спецификации")
    has_children: Optional[bool] = Field(None, description="Есть ли дочерние")
    created_from: Optional[datetime] = Field(None, description="Создано с")
    created_to: Optional[datetime] = Field(None, description="Создано до")
    updated_from: Optional[datetime] = Field(None, description="Обновлено с")
    updated_to: Optional[datetime] = Field(None, description="Обновлено до")


class SpecificationSearchRequest(BaseSchema):
    """Поиск спецификаций."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    search_in_content: bool = Field(True, description="Искать в содержимом")
    filters: Optional[SpecificationFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


# === Statistics ===


class SpecificationStatisticsResponse(BaseSchema):
    """Статистика по спецификациям."""

    total_specifications: int = Field(..., description="Всего спецификаций")
    by_status: Dict[str, int] = Field(..., description="По статусам")
    by_type: Dict[str, int] = Field(..., description="По типам")
    by_format: Dict[str, int] = Field(..., description="По форматам")
    total_versions: int = Field(..., description="Всего версий")
    average_content_length: float = Field(..., description="Средняя длина контента")
    review_completion_rate: float = Field(
        ..., description="Процент завершенных обзоров"
    )


# === Export Schemas ===


class SpecificationExportRequest(BaseSchema):
    """Запрос на экспорт спецификаций."""

    specification_ids: Optional[List[int]] = Field(None, description="ID спецификаций")
    format: str = Field("docx", description="Формат экспорта")
    filters: Optional[SpecificationFilterRequest] = Field(None, description="Фильтры")
    include_versions: bool = Field(False, description="Включить версии")
    include_reviews: bool = Field(False, description="Включить обзоры")
    merge_into_single_document: bool = Field(
        False, description="Объединить в один документ"
    )


class SpecificationExportResponse(BaseSchema):
    """Ответ экспорта спецификаций."""

    success: bool = Field(..., description="Успешность операции")
    export_id: str = Field(..., description="ID экспорта")
    download_url: str = Field(..., description="URL скачивания")
    file_size_bytes: int = Field(..., description="Размер файла")
    expires_at: datetime = Field(..., description="Время истечения ссылки")


__all__ = [
    "SpecificationStatus",
    "SpecificationType",
    "DocumentFormat",
    "SpecificationCreateRequest",
    "SpecificationUpdateRequest",
    "SpecificationResponse",
    "SpecificationDetailResponse",
    "SpecificationListResponse",
    "SpecificationVersionCreateRequest",
    "SpecificationVersionResponse",
    "SpecificationVersionCompareRequest",
    "SpecificationVersionCompareResponse",
    "SpecificationReviewRequest",
    "SpecificationReviewResponse",
    "SpecificationTemplateCreateRequest",
    "SpecificationTemplateResponse",
    "SpecificationFilterRequest",
    "SpecificationSearchRequest",
    "SpecificationStatisticsResponse",
    "SpecificationExportRequest",
    "SpecificationExportResponse",
]

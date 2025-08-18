"""
Comment Schemas.

Схемы для работы с комментариями в соответствии с моделью Comment.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

from app.api.v1.common.schemas import (
    BaseSchema,
    CreateSchema,
    UpdateSchema,
    ResponseSchema,
    ListResponseSchema,
)


# === Request Schemas ===


class CommentAuthor(BaseSchema):
    """Схема автора комментария."""

    id: int = Field(..., description="ID автора")
    email: str = Field(..., description="Email автора")
    full_name: str = Field(..., description="Полное имя автора")


class CommentRequirement(BaseSchema):
    """Схема требования для комментария."""

    id: int = Field(..., description="ID требования")
    title: str = Field(..., description="Заголовок требования")
    description: Optional[str] = Field(None, description="Описание требования")


class CommentCreateRequest(BaseSchema):
    """Схема запроса на создание комментария."""

    content: str = Field(..., min_length=1, description="Содержание комментария")
    requirement_id: int = Field(..., gt=0, description="ID требования")
    parent_comment_id: Optional[int] = Field(
        None, gt=0, description="ID родительского комментария"
    )


class CommentUpdateRequest(BaseSchema):
    """Схема запроса на обновление комментария."""

    content: str = Field(..., min_length=1, description="Новое содержание комментария")


class CommentCreate(CreateSchema):
    """Схема создания комментария в соответствии с моделью Comment."""

    content: str = Field(..., min_length=1, description="Содержание комментария")
    requirement_id: int = Field(..., gt=0, description="ID требования")
    author_id: int = Field(..., gt=0, description="ID автора")
    parent_comment_id: Optional[int] = Field(
        None, gt=0, description="ID родительского комментария"
    )


class CommentUpdate(UpdateSchema):
    """Схема обновления комментария в соответствии с моделью Comment."""

    content: Optional[str] = Field(
        None, min_length=1, description="Содержание комментария"
    )


# === Response Schemas ===


class CommentResponse(ResponseSchema):
    """Схема ответа с данными комментария в соответствии с моделью Comment."""

    id: int = Field(..., description="ID комментария")
    content: str = Field(..., description="Содержание комментария")

    # Связи
    requirement_id: Optional[int] = Field(None, description="ID требования")
    specification_id: Optional[int] = Field(None, description="ID спецификации")
    author_id: int = Field(..., description="ID автора")

    # Временные метки
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class CommentListResponse(BaseSchema):
    """Схема ответа со списком комментариев."""

    comments: List[CommentResponse] = Field(..., description="Список комментариев")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Общее количество страниц")
    size: int = Field(..., description="Размер страницы")


class CommentSearchRequest(BaseSchema):
    """Схема запроса для поиска комментариев."""

    query: str = Field(..., description="Поисковый запрос")
    requirement_id: Optional[int] = Field(None, description="Фильтр по требованию")
    author_id: Optional[int] = Field(None, description="Фильтр по автору")


class CommentStatisticsResponse(BaseSchema):
    """Схема ответа со статистикой комментариев."""

    total_comments: int = Field(..., description="Общее количество комментариев")
    user_comments: int = Field(..., description="Комментарии пользователя")
    requirement_id: Optional[int] = Field(
        None, description="ID требования для фильтрации"
    )


__all__ = [
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentListResponse",
    "CommentSearchRequest",
    "CommentStatisticsResponse",
]

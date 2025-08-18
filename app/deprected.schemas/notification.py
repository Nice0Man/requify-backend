"""
Notification Schemas for Collaboration Domain.

Схемы для работы с уведомлениями в collaboration домене.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field

from app.api.v1.common.schemas import (
    BaseSchema,
    CreateSchema,
    UpdateSchema,
    ResponseSchema,
    ListResponseSchema,
)


# === Notification Enums ===


class NotificationType(str, Enum):
    """Типы уведомлений."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    SYSTEM = "system"
    USER_ACTION = "user_action"


class NotificationPriority(str, Enum):
    """Приоритеты уведомлений."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# === Request Schemas ===


class NotificationCreate(CreateSchema):
    """Схема создания уведомления."""

    user_id: int = Field(..., gt=0, description="ID получателя")
    notification_type: NotificationType = Field(..., description="Тип уведомления")
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок")
    message: str = Field(..., min_length=1, description="Текст уведомления")
    priority: NotificationPriority = Field(
        NotificationPriority.MEDIUM, description="Приоритет"
    )
    action_url: Optional[str] = Field(None, description="URL для действия")
    action_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Данные для действия"
    )
    expires_at: Optional[datetime] = Field(None, description="Время истечения")


class NotificationUpdate(UpdateSchema):
    """Схема обновления уведомления."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Заголовок"
    )
    message: Optional[str] = Field(None, min_length=1, description="Текст")
    priority: Optional[NotificationPriority] = Field(None, description="Приоритет")
    is_read: Optional[bool] = Field(None, description="Прочитано ли")
    action_url: Optional[str] = Field(None, description="URL действия")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Данные действия")


# === Response Schemas ===


class NotificationResponse(BaseModel):
    """Схема ответа с данными уведомления."""

    id: int = Field(..., description="ID уведомления")
    type: str = Field(..., description="Тип уведомления")
    title: str = Field(..., description="Заголовок уведомления")
    message: str = Field(..., description="Текст уведомления")
    read: bool = Field(..., description="Прочитано ли уведомление")
    created_at: datetime = Field(..., description="Время создания")
    data: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные данные"
    )

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Схема ответа со списком уведомлений."""

    notifications: List[NotificationResponse] = Field(
        ..., description="Список уведомлений"
    )
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Общее количество страниц")
    size: int = Field(..., description="Размер страницы")


class MarkNotificationReadRequest(BaseModel):
    """Схема запроса для изменения статуса прочтения."""

    read: bool = Field(..., description="Новый статус прочтения")


class NotificationUnreadCountResponse(BaseModel):
    """Схема ответа с количеством непрочитанных уведомлений."""

    unread_count: int = Field(..., description="Количество непрочитанных уведомлений")
    user_id: int = Field(..., description="ID пользователя")

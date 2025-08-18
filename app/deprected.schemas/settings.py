"""
Configuration Settings Schemas.

Схемы для работы с настройками системы.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from pydantic import Field

from app.api.v1.common.schemas import BaseSchema


# === Settings Enums ===


class SettingScope(str, Enum):
    """Области действия настроек."""

    GLOBAL = "global"
    COMPANY = "company"
    PROJECT = "project"
    USER = "user"
    TEAM = "team"


class SettingType(str, Enum):
    """Типы настроек."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    ENUM = "enum"
    LIST = "list"
    SECRET = "secret"


class SettingCategory(str, Enum):
    """Категории настроек."""

    GENERAL = "general"
    SECURITY = "security"
    NOTIFICATIONS = "notifications"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    APPEARANCE = "appearance"
    WORKFLOW = "workflow"
    BACKUP = "backup"
    AUDIT = "audit"


class SettingAccess(str, Enum):
    """Уровни доступа к настройкам."""

    PUBLIC = "public"
    INTERNAL = "internal"
    ADMIN_ONLY = "admin_only"
    SYSTEM_ONLY = "system_only"


# === Base Setting Schema ===


class SettingMetadata(BaseSchema):
    """Метаданные настройки."""

    label: str = Field(..., description="Человекочитаемое название")
    description: Optional[str] = Field(None, description="Описание настройки")
    help_text: Optional[str] = Field(None, description="Текст помощи")
    validation_rules: Dict[str, Any] = Field(
        default_factory=dict, description="Правила валидации"
    )
    ui_hints: Dict[str, Any] = Field(
        default_factory=dict, description="Подсказки для UI"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="Зависимые настройки"
    )
    tags: List[str] = Field(default_factory=list, description="Теги")


# === Request Schemas ===


class SettingCreateRequest(BaseSchema):
    """Создание настройки."""

    key: str = Field(..., min_length=1, max_length=255, description="Ключ настройки")
    value: Union[str, int, float, bool, Dict[str, Any], List[Any]] = Field(
        ..., description="Значение настройки"
    )
    setting_type: SettingType = Field(..., description="Тип настройки")
    scope: SettingScope = Field(..., description="Область действия")
    category: SettingCategory = Field(..., description="Категория")
    access_level: SettingAccess = Field(
        SettingAccess.INTERNAL, description="Уровень доступа"
    )
    scope_id: Optional[int] = Field(
        None, description="ID области (компания, проект и т.д.)"
    )
    metadata: Optional[SettingMetadata] = Field(None, description="Метаданные")
    is_encrypted: bool = Field(False, description="Зашифровано ли значение")
    is_required: bool = Field(False, description="Обязательная настройка")


class SettingUpdateRequest(BaseSchema):
    """Обновление настройки."""

    value: Optional[Union[str, int, float, bool, Dict[str, Any], List[Any]]] = Field(
        None, description="Новое значение"
    )
    metadata: Optional[SettingMetadata] = Field(None, description="Метаданные")
    is_active: Optional[bool] = Field(None, description="Активна ли настройка")


class SettingsBulkUpdateRequest(BaseSchema):
    """Массовое обновление настроек."""

    settings: Dict[str, Union[str, int, float, bool, Dict[str, Any], List[Any]]] = (
        Field(..., description="Настройки для обновления")
    )
    scope: SettingScope = Field(..., description="Область действия")
    scope_id: Optional[int] = Field(None, description="ID области")
    validate_all: bool = Field(True, description="Валидировать все настройки")


# === Response Schemas ===


class SettingResponse(BaseSchema):
    """Основная информация о настройке."""

    id: int = Field(..., description="ID настройки")
    key: str = Field(..., description="Ключ")
    value: Union[str, int, float, bool, Dict[str, Any], List[Any]] = Field(
        ..., description="Значение"
    )
    setting_type: SettingType = Field(..., description="Тип")
    scope: SettingScope = Field(..., description="Область действия")
    category: SettingCategory = Field(..., description="Категория")
    access_level: SettingAccess = Field(..., description="Уровень доступа")
    scope_id: Optional[int] = Field(None, description="ID области")
    is_encrypted: bool = Field(..., description="Зашифровано")
    is_required: bool = Field(..., description="Обязательная")
    is_active: bool = Field(..., description="Активная")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class SettingDetailResponse(SettingResponse):
    """Детальная информация о настройке."""

    metadata: Optional[SettingMetadata] = Field(None, description="Метаданные")

    # История изменений
    last_changed_by: Optional[int] = Field(
        None, description="ID последнего изменившего"
    )
    last_changed_at: Optional[datetime] = Field(
        None, description="Дата последнего изменения"
    )

    # Валидация
    validation_errors: List[str] = Field(
        default_factory=list, description="Ошибки валидации"
    )

    # Использование
    is_overridden: bool = Field(False, description="Переопределена ли настройка")
    overridden_by: Optional[Dict[str, Any]] = Field(
        None, description="Кем переопределена"
    )

    # Значение по умолчанию
    default_value: Optional[Union[str, int, float, bool, Dict[str, Any], List[Any]]] = (
        Field(None, description="Значение по умолчанию")
    )


class SettingListResponse(BaseSchema):
    """Список настроек с пагинацией."""

    settings: List[SettingResponse] = Field(..., description="Список настроек")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Settings Groups ===


class SettingGroupResponse(BaseSchema):
    """Группа настроек."""

    category: SettingCategory = Field(..., description="Категория")
    scope: SettingScope = Field(..., description="Область действия")
    scope_id: Optional[int] = Field(None, description="ID области")
    settings: List[SettingResponse] = Field(..., description="Настройки в группе")
    total_settings: int = Field(..., description="Общее количество настроек")
    required_settings: int = Field(..., description="Обязательных настроек")
    configured_settings: int = Field(..., description="Настроенных настроек")
    completion_percentage: float = Field(..., description="Процент завершенности")


class SettingsHierarchyResponse(BaseSchema):
    """Иерархия настроек по областям."""

    scope: SettingScope = Field(..., description="Область действия")
    scope_id: Optional[int] = Field(None, description="ID области")
    settings: List[SettingResponse] = Field(..., description="Настройки области")
    inherited_settings: List[SettingResponse] = Field(
        ..., description="Унаследованные настройки"
    )
    overridden_settings: List[str] = Field(..., description="Переопределенные ключи")
    effective_settings: Dict[str, Any] = Field(..., description="Эффективные настройки")


# === Settings Schema ===


class SettingSchemaDefinition(BaseSchema):
    """Определение схемы настройки."""

    key: str = Field(..., description="Ключ настройки")
    setting_type: SettingType = Field(..., description="Тип")
    category: SettingCategory = Field(..., description="Категория")
    scope: SettingScope = Field(..., description="Область действия")
    access_level: SettingAccess = Field(..., description="Уровень доступа")
    default_value: Optional[Union[str, int, float, bool, Dict[str, Any], List[Any]]] = (
        Field(None, description="Значение по умолчанию")
    )
    metadata: SettingMetadata = Field(..., description="Метаданные")
    is_required: bool = Field(False, description="Обязательная")
    is_encrypted: bool = Field(False, description="Зашифрованная")
    enum_values: Optional[List[str]] = Field(
        None, description="Возможные значения для enum"
    )


class SettingsSchemaResponse(BaseSchema):
    """Схема всех настроек."""

    schema_version: str = Field(..., description="Версия схемы")
    categories: List[SettingCategory] = Field(..., description="Доступные категории")
    scopes: List[SettingScope] = Field(..., description="Доступные области")
    definitions: List[SettingSchemaDefinition] = Field(
        ..., description="Определения настроек"
    )
    total_definitions: int = Field(..., description="Общее количество определений")


# === Validation ===


class SettingValidationRequest(BaseSchema):
    """Запрос валидации настройки."""

    key: str = Field(..., description="Ключ настройки")
    value: Union[str, int, float, bool, Dict[str, Any], List[Any]] = Field(
        ..., description="Значение для валидации"
    )
    scope: SettingScope = Field(..., description="Область действия")
    scope_id: Optional[int] = Field(None, description="ID области")


class SettingValidationResponse(BaseSchema):
    """Результат валидации настройки."""

    is_valid: bool = Field(..., description="Валидно ли значение")
    errors: List[str] = Field(..., description="Ошибки валидации")
    warnings: List[str] = Field(..., description="Предупреждения")
    normalized_value: Optional[
        Union[str, int, float, bool, Dict[str, Any], List[Any]]
    ] = Field(None, description="Нормализованное значение")


# === Search and Filter ===


class SettingFilterRequest(BaseSchema):
    """Фильтр настроек."""

    scope: Optional[List[SettingScope]] = Field(None, description="Области действия")
    category: Optional[List[SettingCategory]] = Field(None, description="Категории")
    access_level: Optional[List[SettingAccess]] = Field(
        None, description="Уровни доступа"
    )
    setting_type: Optional[List[SettingType]] = Field(None, description="Типы настроек")
    scope_id: Optional[int] = Field(None, description="ID области")
    is_required: Optional[bool] = Field(None, description="Обязательные")
    is_encrypted: Optional[bool] = Field(None, description="Зашифрованные")
    is_active: Optional[bool] = Field(None, description="Активные")
    has_default: Optional[bool] = Field(None, description="Есть значение по умолчанию")
    is_overridden: Optional[bool] = Field(None, description="Переопределенные")


class SettingSearchRequest(BaseSchema):
    """Поиск настроек."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    search_in_values: bool = Field(False, description="Искать в значениях")
    search_in_metadata: bool = Field(True, description="Искать в метаданных")
    filters: Optional[SettingFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


# === Import/Export ===


class SettingsExportRequest(BaseSchema):
    """Запрос экспорта настроек."""

    scope: Optional[SettingScope] = Field(None, description="Область действия")
    scope_id: Optional[int] = Field(None, description="ID области")
    categories: Optional[List[SettingCategory]] = Field(None, description="Категории")
    include_encrypted: bool = Field(False, description="Включить зашифрованные")
    include_defaults: bool = Field(False, description="Включить значения по умолчанию")
    format: str = Field("json", description="Формат экспорта")


class SettingsImportRequest(BaseSchema):
    """Запрос импорта настроек."""

    settings_data: Dict[str, Any] = Field(..., description="Данные настроек")
    scope: SettingScope = Field(..., description="Область действия")
    scope_id: Optional[int] = Field(None, description="ID области")
    overwrite_existing: bool = Field(False, description="Перезаписать существующие")
    validate_before_import: bool = Field(
        True, description="Валидировать перед импортом"
    )


class SettingsImportResponse(BaseSchema):
    """Результат импорта настроек."""

    success: bool = Field(..., description="Успешность импорта")
    imported_count: int = Field(..., description="Количество импортированных")
    skipped_count: int = Field(..., description="Количество пропущенных")
    error_count: int = Field(..., description="Количество ошибок")
    errors: List[str] = Field(..., description="Список ошибок")
    imported_keys: List[str] = Field(..., description="Импортированные ключи")
    skipped_keys: List[str] = Field(..., description="Пропущенные ключи")


# === Statistics ===


class SettingsStatisticsResponse(BaseSchema):
    """Статистика настроек."""

    total_settings: int = Field(..., description="Всего настроек")
    by_scope: Dict[str, int] = Field(..., description="По областям")
    by_category: Dict[str, int] = Field(..., description="По категориям")
    by_type: Dict[str, int] = Field(..., description="По типам")
    by_access_level: Dict[str, int] = Field(..., description="По уровням доступа")

    # Состояние
    active_settings: int = Field(..., description="Активные настройки")
    required_settings: int = Field(..., description="Обязательные настройки")
    encrypted_settings: int = Field(..., description="Зашифрованные настройки")
    overridden_settings: int = Field(..., description="Переопределенные настройки")

    # Конфигурация
    completion_by_scope: Dict[str, float] = Field(
        ..., description="Завершенность по областям"
    )
    missing_required: List[str] = Field(..., description="Отсутствующие обязательные")


# === Operation Response ===


class SettingOperationResponse(BaseSchema):
    """Ответ операции с настройкой."""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение")
    setting_key: str = Field(..., description="Ключ настройки")
    operation_type: str = Field(..., description="Тип операции")
    previous_value: Optional[
        Union[str, int, float, bool, Dict[str, Any], List[Any]]
    ] = Field(None, description="Предыдущее значение")
    new_value: Optional[Union[str, int, float, bool, Dict[str, Any], List[Any]]] = (
        Field(None, description="Новое значение")
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Время операции"
    )


# === User Settings Schemas ===


class NotificationSettings(BaseSchema):
    """Настройки уведомлений."""

    email_enabled: bool = Field(True, description="Email уведомления включены")
    browser_enabled: bool = Field(True, description="Браузерные уведомления включены")
    frequency: str = Field("immediate", description="Частота уведомлений")
    types: List[str] = Field(default_factory=list, description="Типы уведомлений")


class InterfaceSettings(BaseSchema):
    """Настройки интерфейса."""

    theme: str = Field("light", description="Тема интерфейса")
    language: str = Field("ru", description="Язык интерфейса")
    timezone: str = Field("UTC", description="Часовой пояс")
    date_format: str = Field("DD.MM.YYYY", description="Формат даты")
    time_format: str = Field("24h", description="Формат времени")


class SecuritySettings(BaseSchema):
    """Настройки безопасности."""

    two_factor_enabled: bool = Field(False, description="Двухфакторная аутентификация")
    session_timeout: int = Field(30, description="Таймаут сессии (минуты)")
    password_expiry_days: Optional[int] = Field(
        None, description="Срок действия пароля"
    )


class PrivacySettings(BaseSchema):
    """Настройки приватности."""

    profile_visibility: str = Field("company", description="Видимость профиля")
    activity_tracking: bool = Field(True, description="Отслеживание активности")
    data_retention_days: Optional[int] = Field(None, description="Хранение данных")


class UserProfileSettings(BaseSchema):
    """Настройки профиля пользователя."""

    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    bio: Optional[str] = Field(None, description="Биография")
    avatar_url: Optional[str] = Field(None, description="URL аватара")


class UserSettings(BaseSchema):
    """Основная схема настроек пользователя."""

    user_id: int = Field(..., description="ID пользователя")
    profile: Optional[UserProfileSettings] = Field(
        None, description="Настройки профиля"
    )
    notifications: Optional[NotificationSettings] = Field(
        None, description="Уведомления"
    )
    interface: Optional[InterfaceSettings] = Field(None, description="Интерфейс")
    security: Optional[SecuritySettings] = Field(None, description="Безопасность")
    privacy: Optional[PrivacySettings] = Field(None, description="Приватность")
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Дополнительные настройки"
    )


class UserSettingsUpdate(BaseSchema):
    """Схема обновления настроек пользователя."""

    profile: Optional[UserProfileSettings] = Field(
        None, description="Настройки профиля"
    )
    notifications: Optional[NotificationSettings] = Field(
        None, description="Уведомления"
    )
    interface: Optional[InterfaceSettings] = Field(None, description="Интерфейс")
    security: Optional[SecuritySettings] = Field(None, description="Безопасность")
    privacy: Optional[PrivacySettings] = Field(None, description="Приватность")
    preferences: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительные настройки"
    )


class SettingsResponse(BaseSchema):
    """Ответ с настройками пользователя."""

    user_id: int = Field(..., description="ID пользователя")
    settings: UserSettings = Field(..., description="Настройки")
    last_updated: datetime = Field(..., description="Последнее обновление")


class UserSession(BaseSchema):
    """Информация о сессии пользователя."""

    id: str = Field(..., description="ID сессии")
    user_id: int = Field(..., description="ID пользователя")
    created_at: datetime = Field(..., description="Время создания")
    last_activity: datetime = Field(..., description="Последняя активность")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")
    is_active: bool = Field(True, description="Активна ли сессия")


__all__ = [
    "SettingScope",
    "SettingType",
    "SettingCategory",
    "SettingAccess",
    "SettingMetadata",
    "SettingCreateRequest",
    "SettingUpdateRequest",
    "SettingsBulkUpdateRequest",
    "SettingResponse",
    "SettingDetailResponse",
    "SettingListResponse",
    "SettingGroupResponse",
    "SettingsHierarchyResponse",
    "SettingSchemaDefinition",
    "SettingsSchemaResponse",
    "SettingValidationRequest",
    "SettingValidationResponse",
    "SettingFilterRequest",
    "SettingSearchRequest",
    "SettingsExportRequest",
    "SettingsImportRequest",
    "SettingsImportResponse",
    "SettingsStatisticsResponse",
    "SettingOperationResponse",
    # User Settings
    "NotificationSettings",
    "InterfaceSettings",
    "SecuritySettings",
    "PrivacySettings",
    "UserProfileSettings",
    "UserSettings",
    "UserSettingsUpdate",
    "SettingsResponse",
    "UserSession",
]

"""
Companies Management Schemas.

Pydantic models для операций с компаниями.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import Field, EmailStr, ConfigDict

from app.api.v1.common.schemas import BaseSchema


# === Company Enums ===


class CompanyStatus(str, Enum):
    """Статусы компании."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    INACTIVE = "inactive"


class SubscriptionPlan(str, Enum):
    """Планы подписки."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class CompanySize(str, Enum):
    """Размеры компании."""

    STARTUP = "startup"  # 1-10
    SMALL = "small"  # 11-50
    MEDIUM = "medium"  # 51-200
    LARGE = "large"  # 201-1000
    ENTERPRISE = "enterprise"  # 1000+


class SSOMProvider(str, Enum):
    """SSO провайдеры."""

    GOOGLE = "google"
    MICROSOFT = "microsoft"
    OKTA = "okta"
    AUTH0 = "auth0"


class ThemePreset(str, Enum):
    """Предустановленные темы."""

    LIGHT = "light"
    DARK = "dark"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    MINIMAL = "minimal"


# === Company Request Schemas ===


class CompanyCreateRequest(BaseSchema):
    """Schema for creating a new company."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Название компании"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Описание компании"
    )
    website: Optional[str] = Field(
        None, max_length=255, description="Веб-сайт компании"
    )
    industry: Optional[str] = Field(None, max_length=100, description="Отрасль")
    size: CompanySize = Field(CompanySize.STARTUP, description="Размер компании")

    # Дополнительные поля для создания
    initial_admin_email: EmailStr = Field(
        ..., description="Email первого администратора"
    )
    subscription_plan: SubscriptionPlan = Field(
        SubscriptionPlan.FREE, description="План подписки"
    )


class CompanyUpdateRequest(BaseSchema):
    """Schema for updating company information."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название компании"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Описание компании"
    )
    website: Optional[str] = Field(
        None, max_length=255, description="Веб-сайт компании"
    )
    industry: Optional[str] = Field(None, max_length=100, description="Отрасль")
    size: Optional[CompanySize] = Field(None, description="Размер компании")


# === Company Response Schemas ===


class CompanyResponse(BaseSchema):
    """Basic company information."""

    id: int = Field(..., description="ID компании")
    name: str = Field(..., description="Название компании")
    description: Optional[str] = Field(None, description="Описание компании")
    website: Optional[str] = Field(None, description="Веб-сайт компании")
    industry: Optional[str] = Field(None, description="Отрасль")
    size: CompanySize = Field(..., description="Размер компании")
    status: CompanyStatus = Field(..., description="Статус компании")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")


class CompanyDetailResponse(CompanyResponse):
    """Detailed company information."""

    # Статистика
    employees_count: int = Field(0, description="Количество сотрудников")
    projects_count: int = Field(0, description="Количество проектов")
    departments_count: int = Field(0, description="Количество департаментов")
    teams_count: int = Field(0, description="Количество команд")

    # Подписка
    subscription_plan: SubscriptionPlan = Field(..., description="План подписки")
    subscription_expires_at: Optional[datetime] = Field(
        None, description="Дата окончания подписки"
    )


class CompanyListResponse(BaseSchema):
    """Response for company list with pagination."""

    companies: List[CompanyResponse] = Field(..., description="Список компаний")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Общее количество страниц")


class CompanyOperationResponse(BaseSchema):
    """Response for company operations."""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение операции")
    company_id: int = Field(..., description="ID компании")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Время операции"
    )


# === Company Settings Schemas ===


class CompanySettingsRequest(BaseSchema):
    """Schema for company settings."""

    timezone: Optional[str] = Field(None, description="Часовой пояс")
    language: Optional[str] = Field(None, description="Язык по умолчанию")
    date_format: Optional[str] = Field(None, description="Формат даты")
    currency: Optional[str] = Field(None, description="Валюта")

    # Security settings
    password_policy_enabled: Optional[bool] = Field(
        None, description="Включена ли политика паролей"
    )
    two_factor_required: Optional[bool] = Field(
        None, description="Обязательная двухфакторная аутентификация"
    )
    session_timeout_minutes: Optional[int] = Field(
        None, ge=5, le=1440, description="Таймаут сессии в минутах"
    )

    # Feature flags
    projects_enabled: Optional[bool] = Field(None, description="Включены ли проекты")
    requirements_enabled: Optional[bool] = Field(
        None, description="Включены ли требования"
    )
    testing_enabled: Optional[bool] = Field(
        None, description="Включено ли тестирование"
    )
    analytics_enabled: Optional[bool] = Field(None, description="Включена ли аналитика")

    # Security settings extended
    enable_sso: Optional[bool] = Field(False, description="Включить SSO")
    sso_provider: Optional[SSOMProvider] = Field(None, description="Провайдер SSO")
    sso_config: Optional[Dict[str, Any]] = Field(None, description="Конфигурация SSO")
    enforce_2fa: Optional[bool] = Field(False, description="Принудительная 2FA")
    require_email_verification: Optional[bool] = Field(
        True, description="Требовать верификацию email"
    )
    max_file_size_mb: Optional[int] = Field(
        10, description="Максимальный размер файла в МБ"
    )

    # Password policy
    password_policy: Optional[Dict[str, Any]] = Field(
        None, description="Политика паролей"
    )

    # Notification settings
    notifications: Optional[Dict[str, Any]] = Field(
        None, description="Настройки уведомлений"
    )

    # Integration settings
    integrations: Optional[Dict[str, Any]] = Field(
        None, description="Настройки интеграций"
    )


class CompanySettingsResponse(BaseSchema):
    """Company settings response."""

    id: int = Field(..., description="ID настроек")
    company_id: int = Field(..., description="ID компании")
    timezone: str = Field(..., description="Часовой пояс")
    language: str = Field(..., description="Язык по умолчанию")
    date_format: str = Field(..., description="Формат даты")
    currency: str = Field(..., description="Валюта")

    # Security settings
    password_policy_enabled: bool = Field(..., description="Политика паролей")
    two_factor_required: bool = Field(..., description="Двухфакторная аутентификация")
    session_timeout_minutes: int = Field(..., description="Таймаут сессии")

    # Feature flags
    projects_enabled: bool = Field(..., description="Проекты")
    requirements_enabled: bool = Field(..., description="Требования")
    testing_enabled: bool = Field(..., description="Тестирование")
    analytics_enabled: bool = Field(..., description="Аналитика")

    # Security settings extended
    enable_sso: bool = Field(False, description="SSO включен")
    sso_provider: Optional[SSOMProvider] = Field(None, description="Провайдер SSO")
    sso_config: Optional[Dict[str, Any]] = Field(None, description="Конфигурация SSO")
    enforce_2fa: bool = Field(False, description="Принудительная 2FA")
    require_email_verification: bool = Field(
        True, description="Требовать верификацию email"
    )
    max_file_size_mb: int = Field(10, description="Максимальный размер файла в МБ")

    # Additional settings
    password_policy: Optional[Dict[str, Any]] = Field(
        None, description="Политика паролей"
    )
    notifications: Optional[Dict[str, Any]] = Field(
        None, description="Настройки уведомлений"
    )
    integrations: Optional[Dict[str, Any]] = Field(
        None, description="Настройки интеграций"
    )

    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")


# === Company Contact Schemas ===


class CompanyContactRequest(BaseSchema):
    """Schema for company contact information."""

    email: Optional[EmailStr] = Field(None, description="Контактный email")
    phone: Optional[str] = Field(None, max_length=20, description="Контактный телефон")
    address: Optional[str] = Field(None, max_length=500, description="Адрес")
    city: Optional[str] = Field(None, max_length=100, description="Город")
    country: Optional[str] = Field(None, max_length=100, description="Страна")
    postal_code: Optional[str] = Field(
        None, max_length=20, description="Почтовый индекс"
    )

    # Extended contact fields
    primary_phone: Optional[str] = Field(
        None, max_length=20, description="Основной телефон"
    )
    secondary_phone: Optional[str] = Field(
        None, max_length=20, description="Дополнительный телефон"
    )
    mobile_phone: Optional[str] = Field(
        None, max_length=20, description="Мобильный телефон"
    )
    fax: Optional[str] = Field(None, max_length=20, description="Факс")
    support_email: Optional[EmailStr] = Field(None, description="Email поддержки")
    sales_email: Optional[EmailStr] = Field(None, description="Email продаж")


class CompanyContactResponse(BaseSchema):
    """Company contact information response."""

    id: int = Field(..., description="ID контактной информации")
    company_id: int = Field(..., description="ID компании")
    email: Optional[str] = Field(None, description="Контактный email")
    phone: Optional[str] = Field(None, description="Контактный телефон")
    address: Optional[str] = Field(None, description="Адрес")
    city: Optional[str] = Field(None, description="Город")
    country: Optional[str] = Field(None, description="Страна")
    postal_code: Optional[str] = Field(None, description="Почтовый индекс")

    # Extended contact fields
    primary_phone: Optional[str] = Field(None, description="Основной телефон")
    secondary_phone: Optional[str] = Field(None, description="Дополнительный телефон")
    mobile_phone: Optional[str] = Field(None, description="Мобильный телефон")
    fax: Optional[str] = Field(None, description="Факс")
    support_email: Optional[str] = Field(None, description="Email поддержки")
    sales_email: Optional[str] = Field(None, description="Email продаж")

    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")


# === Company Branding Schemas ===


class ColorPalette(BaseSchema):
    """Цветовая палитра."""

    primary: str = Field(..., description="Основной цвет")
    secondary: str = Field(..., description="Вторичный цвет")
    accent: str = Field(..., description="Акцентный цвет")
    success: str = Field("#28a745", description="Цвет успеха")
    warning: str = Field("#ffc107", description="Цвет предупреждения")
    error: str = Field("#dc3545", description="Цвет ошибки")
    info: str = Field("#17a2b8", description="Информационный цвет")
    background: str = Field("#ffffff", description="Цвет фона")
    surface: str = Field("#f8f9fa", description="Цвет поверхности")
    text_primary: str = Field("#212529", description="Основной цвет текста")
    text_secondary: str = Field("#6c757d", description="Вторичный цвет текста")


class TypographyConfig(BaseSchema):
    """Конфигурация типографики."""

    font_family_primary: str = Field("Inter", description="Основное семейство шрифтов")
    font_family_secondary: str = Field(
        "Roboto", description="Вторичное семейство шрифтов"
    )
    font_family_monospace: str = Field(
        "'Courier New'", description="Моноширинное семейство шрифтов"
    )
    font_size_base: int = Field(14, description="Базовый размер шрифта")
    font_size_small: int = Field(12, description="Малый размер шрифта")
    font_size_large: int = Field(16, description="Большой размер шрифта")
    line_height_base: float = Field(1.5, description="Базовая высота строки")
    letter_spacing: float = Field(0.0, description="Межбуквенное расстояние")


class ComponentStyles(BaseSchema):
    """Стили компонентов."""

    button_radius: int = Field(4, description="Радиус кнопок")
    input_radius: int = Field(4, description="Радиус полей ввода")
    card_radius: int = Field(8, description="Радиус карточек")
    modal_radius: int = Field(12, description="Радиус модальных окон")
    shadow_elevation: int = Field(2, description="Уровень тени")
    border_width: int = Field(1, description="Ширина границы")
    animation_duration: int = Field(300, description="Длительность анимации в мс")


class LayoutConfig(BaseSchema):
    """Конфигурация макета."""

    container_max_width: int = Field(1200, description="Максимальная ширина контейнера")
    sidebar_width: int = Field(280, description="Ширина боковой панели")
    header_height: int = Field(64, description="Высота заголовка")
    footer_height: int = Field(48, description="Высота подвала")
    spacing_unit: int = Field(8, description="Базовая единица отступов")
    grid_columns: int = Field(12, description="Количество колонок в сетке")


class SocialLinks(BaseSchema):
    """Социальные ссылки."""

    facebook: Optional[str] = Field(None, description="Ссылка на Facebook")
    twitter: Optional[str] = Field(None, description="Ссылка на Twitter")
    linkedin: Optional[str] = Field(None, description="Ссылка на LinkedIn")
    instagram: Optional[str] = Field(None, description="Ссылка на Instagram")
    youtube: Optional[str] = Field(None, description="Ссылка на YouTube")
    github: Optional[str] = Field(None, description="Ссылка на GitHub")


class CompanyBrandingCreate(BaseSchema):
    """Schema для создания брендинга компании."""

    logo_url: Optional[str] = Field(None, description="URL логотипа")
    logo_dark_url: Optional[str] = Field(None, description="URL темного логотипа")
    favicon_url: Optional[str] = Field(None, description="URL favicon")

    # Цветовая схема
    colors: ColorPalette = Field(..., description="Цветовая палитра")

    # Типографика
    typography: TypographyConfig = Field(..., description="Конфигурация типографики")

    # Стили компонентов
    components: ComponentStyles = Field(..., description="Стили компонентов")

    # Макет
    layout: LayoutConfig = Field(..., description="Конфигурация макета")

    # Социальные ссылки
    social_links: Optional[SocialLinks] = Field(None, description="Социальные ссылки")

    # Дополнительные настройки
    theme_preset: ThemePreset = Field(
        ThemePreset.LIGHT, description="Предустановленная тема"
    )
    custom_css: Optional[str] = Field(None, description="Пользовательский CSS")
    brand_guidelines_url: Optional[str] = Field(
        None, description="URL руководства по бренду"
    )


class CompanyBrandingUpdate(BaseSchema):
    """Schema для обновления брендинга компании."""

    logo_url: Optional[str] = Field(None, description="URL логотипа")
    logo_dark_url: Optional[str] = Field(None, description="URL темного логотипа")
    favicon_url: Optional[str] = Field(None, description="URL favicon")

    # Цветовая схема
    colors: Optional[ColorPalette] = Field(None, description="Цветовая палитра")

    # Типографика
    typography: Optional[TypographyConfig] = Field(
        None, description="Конфигурация типографики"
    )

    # Стили компонентов
    components: Optional[ComponentStyles] = Field(None, description="Стили компонентов")

    # Макет
    layout: Optional[LayoutConfig] = Field(None, description="Конфигурация макета")

    # Социальные ссылки
    social_links: Optional[SocialLinks] = Field(None, description="Социальные ссылки")

    # Дополнительные настройки
    theme_preset: Optional[ThemePreset] = Field(
        None, description="Предустановленная тема"
    )
    custom_css: Optional[str] = Field(None, description="Пользовательский CSS")
    brand_guidelines_url: Optional[str] = Field(
        None, description="URL руководства по бренду"
    )


class CompanyBrandingRequest(BaseSchema):
    """Schema for company branding information."""

    logo_url: Optional[str] = Field(None, description="URL логотипа")
    primary_color: Optional[str] = Field(None, description="Основной цвет")
    secondary_color: Optional[str] = Field(None, description="Вторичный цвет")
    accent_color: Optional[str] = Field(None, description="Акцентный цвет")
    font_family: Optional[str] = Field(None, description="Семейство шрифтов")


class CompanyBrandingResponse(BaseSchema):
    """Company branding information response."""

    id: int = Field(..., description="ID брендинга")
    company_id: int = Field(..., description="ID компании")
    logo_url: Optional[str] = Field(None, description="URL логотипа")
    logo_dark_url: Optional[str] = Field(None, description="URL темного логотипа")
    favicon_url: Optional[str] = Field(None, description="URL favicon")

    # Цветовая схема
    colors: ColorPalette = Field(..., description="Цветовая палитра")

    # Типографика
    typography: TypographyConfig = Field(..., description="Конфигурация типографики")

    # Стили компонентов
    components: ComponentStyles = Field(..., description="Стили компонентов")

    # Макет
    layout: LayoutConfig = Field(..., description="Конфигурация макета")

    # Социальные ссылки
    social_links: Optional[SocialLinks] = Field(None, description="Социальные ссылки")

    # Дополнительные настройки
    theme_preset: ThemePreset = Field(..., description="Предустановленная тема")
    custom_css: Optional[str] = Field(None, description="Пользовательский CSS")
    brand_guidelines_url: Optional[str] = Field(
        None, description="URL руководства по бренду"
    )

    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")


class BrandingValidation(BaseSchema):
    """Валидация брендинга."""

    is_valid: bool = Field(..., description="Валидно ли")
    errors: List[str] = Field(default_factory=list, description="Ошибки")
    warnings: List[str] = Field(default_factory=list, description="Предупреждения")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации")


class AssetUpload(BaseSchema):
    """Загрузка ресурса."""

    file_name: str = Field(..., description="Имя файла")
    file_type: str = Field(..., description="Тип файла")
    file_size: int = Field(..., description="Размер файла")
    file_url: str = Field(..., description="URL файла")


class BrandingExport(BaseSchema):
    """Экспорт брендинга."""

    format: str = Field("json", description="Формат экспорта")
    include_assets: bool = Field(True, description="Включать ресурсы")


class BrandingImport(BaseSchema):
    """Импорт брендинга."""

    branding_data: Dict[str, Any] = Field(..., description="Данные брендинга")
    overwrite_existing: bool = Field(False, description="Перезаписать существующие")


# === Company Settings Schemas ===


class CompanySettingsCreate(BaseSchema):
    """Schema for creating company settings."""

    company_id: int = Field(..., description="ID компании")
    setting_key: str = Field(..., max_length=100, description="Ключ настройки")
    setting_value: Optional[str] = Field(None, description="Значение настройки")
    setting_type: str = Field("string", description="Тип настройки")
    is_encrypted: bool = Field(False, description="Зашифровано ли значение")

    # Extended settings
    timezone: str = Field("UTC", description="Часовой пояс")
    language: str = Field("en", description="Язык по умолчанию")
    date_format: str = Field("YYYY-MM-DD", description="Формат даты")
    currency: str = Field("USD", description="Валюта")

    # Security settings
    enable_sso: bool = Field(False, description="Включить SSO")
    sso_provider: Optional[SSOMProvider] = Field(None, description="Провайдер SSO")
    sso_config: Optional[Dict[str, Any]] = Field(None, description="Конфигурация SSO")
    enforce_2fa: bool = Field(False, description="Принудительная 2FA")
    require_email_verification: bool = Field(
        True, description="Требовать верификацию email"
    )
    max_file_size_mb: int = Field(10, description="Максимальный размер файла в МБ")


class CompanySettingsUpdate(BaseSchema):
    """Schema for updating company settings."""

    setting_value: Optional[str] = Field(None, description="Значение настройки")
    setting_type: Optional[str] = Field(None, description="Тип настройки")
    is_encrypted: Optional[bool] = Field(None, description="Зашифровано ли значение")

    # Extended settings
    timezone: Optional[str] = Field(None, description="Часовой пояс")
    language: Optional[str] = Field(None, description="Язык по умолчанию")
    date_format: Optional[str] = Field(None, description="Формат даты")
    currency: Optional[str] = Field(None, description="Валюта")

    # Security settings
    enable_sso: Optional[bool] = Field(None, description="Включить SSO")
    sso_provider: Optional[SSOMProvider] = Field(None, description="Провайдер SSO")
    sso_config: Optional[Dict[str, Any]] = Field(None, description="Конфигурация SSO")
    enforce_2fa: Optional[bool] = Field(None, description="Принудительная 2FA")
    require_email_verification: Optional[bool] = Field(
        None, description="Требовать верификацию email"
    )
    max_file_size_mb: Optional[int] = Field(
        None, description="Максимальный размер файла в МБ"
    )


class PasswordPolicySettings(BaseSchema):
    """Password policy settings."""

    min_length: int = Field(8, description="Минимальная длина пароля")
    max_length: int = Field(128, description="Максимальная длина пароля")
    require_uppercase: bool = Field(
        True, description="Требовать хотя бы одну заглавную букву"
    )
    require_lowercase: bool = Field(
        True, description="Требовать хотя бы одну строчную букву"
    )
    require_numbers: bool = Field(True, description="Требовать хотя бы одну цифру")
    require_special: bool = Field(
        True, description="Требовать хотя бы один специальный символ"
    )
    require_dictionary_words: bool = Field(
        True, description="Требовать слова из словаря"
    )
    require_recent_passwords: bool = Field(
        True, description="Требовать не использовать предыдущие пароли"
    )


class NotificationSettings(BaseSchema):
    """Notification settings."""

    requirement_created: bool = Field(
        True, description="Уведомлять о создании требования"
    )
    requirement_updated: bool = Field(
        True, description="Уведомлять о обновлении требования"
    )
    requirement_approved: bool = Field(
        True, description="Уведомлять о одобрении требования"
    )
    project_invitation: bool = Field(
        True, description="Уведомлять о приглашении в проект"
    )
    team_invitation: bool = Field(
        True, description="Уведомлять о приглашении в команду"
    )
    release_published: bool = Field(True, description="Уведомлять о публикации релиза")
    test_failed: bool = Field(True, description="Уведомлять о провале теста")


class IntegrationSettings(BaseSchema):
    """Integration settings."""

    slack_enabled: bool = Field(True, description="Включен ли Slack")
    jira_enabled: bool = Field(True, description="Включен ли Jira")
    github_enabled: bool = Field(True, description="Включен ли GitHub")
    gitlab_enabled: bool = Field(True, description="Включен ли GitLab")
    figma_enabled: bool = Field(True, description="Включен ли Figma")


class CompanySettingsValidation(BaseSchema):
    """Company settings validation."""

    is_valid: bool = Field(..., description="Валидны ли настройки")
    errors: List[str] = Field(default_factory=list, description="Ошибки валидации")
    warnings: List[str] = Field(default_factory=list, description="Предупреждения")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации")


# Export all schemas
__all__ = [
    "CompanyCreateRequest",
    "CompanyUpdateRequest",
    "CompanyResponse",
    "CompanyDetailResponse",
    "CompanyListResponse",
    "CompanyOperationResponse",
    "CompanySettingsCreate",
    "CompanySettingsUpdate",
    "CompanySettingsRequest",
    "CompanySettingsResponse",
    "CompanyContactRequest",
    "CompanyContactResponse",
    "CompanyBrandingCreate",
    "CompanyBrandingUpdate",
    "CompanyBrandingRequest",
    "CompanyBrandingResponse",
    "PasswordPolicySettings",
    "NotificationSettings",
    "IntegrationSettings",
    "CompanySettingsValidation",
    "ColorPalette",
    "TypographyConfig",
    "ComponentStyles",
    "LayoutConfig",
    "SocialLinks",
    "ThemePreset",
    "BrandingValidation",
    "AssetUpload",
    "BrandingExport",
    "BrandingImport",
    "SSOMProvider",
    "CompanyStatus",
    "SubscriptionPlan",
    "CompanySize",
]

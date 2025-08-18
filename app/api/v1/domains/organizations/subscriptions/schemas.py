"""
Subscription Schemas.

Схемы для работы с подписками организаций.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal

from pydantic import Field

from app.api.v1.common.schemas import BaseSchema


# === Subscription Enums ===


class SubscriptionStatus(str, Enum):
    """Статусы подписки."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PENDING = "pending"


class SubscriptionPlan(str, Enum):
    """Планы подписки."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingPeriod(str, Enum):
    """Периоды биллинга."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class PaymentStatus(str, Enum):
    """Статусы платежей."""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


# === Request Schemas ===


class SubscriptionCreateRequest(BaseSchema):
    """Создание подписки."""

    company_id: int = Field(..., gt=0, description="ID компании")
    plan: SubscriptionPlan = Field(..., description="План подписки")
    billing_period: BillingPeriod = Field(..., description="Период биллинга")
    start_date: datetime = Field(..., description="Дата начала")
    custom_features: Optional[Dict[str, Any]] = Field(
        None, description="Кастомные возможности"
    )
    discount_code: Optional[str] = Field(None, description="Код скидки")


class SubscriptionUpdateRequest(BaseSchema):
    """Обновление подписки."""

    plan: Optional[SubscriptionPlan] = Field(None, description="План подписки")
    billing_period: Optional[BillingPeriod] = Field(None, description="Период биллинга")
    auto_renewal: Optional[bool] = Field(None, description="Автопродление")
    custom_features: Optional[Dict[str, Any]] = Field(
        None, description="Кастомные возможности"
    )


class SubscriptionUpgradeRequest(BaseSchema):
    """Запрос на апгрейд подписки."""

    new_plan: SubscriptionPlan = Field(..., description="Новый план")
    new_billing_period: Optional[BillingPeriod] = Field(
        None, description="Новый период"
    )
    upgrade_immediately: bool = Field(True, description="Апгрейд немедленно")
    prorate_payment: bool = Field(True, description="Пропорциональная оплата")


class SubscriptionCancellationRequest(BaseSchema):
    """Запрос на отмену подписки."""

    reason: str = Field(..., description="Причина отмены")
    cancel_immediately: bool = Field(False, description="Отменить немедленно")
    feedback: Optional[str] = Field(None, description="Обратная связь")


# === Response Schemas ===


class SubscriptionPlanDetailsResponse(BaseSchema):
    """Детали плана подписки."""

    plan: SubscriptionPlan = Field(..., description="План")
    name: str = Field(..., description="Название плана")
    description: str = Field(..., description="Описание")
    price_monthly: Decimal = Field(..., description="Цена в месяц")
    price_annually: Decimal = Field(..., description="Цена в год")
    max_users: Optional[int] = Field(None, description="Максимум пользователей")
    max_projects: Optional[int] = Field(None, description="Максимум проектов")
    max_storage_gb: Optional[int] = Field(None, description="Максимум хранилища ГБ")
    features: List[str] = Field(..., description="Возможности")
    is_available: bool = Field(True, description="Доступен ли план")


class SubscriptionResponse(BaseSchema):
    """Основная информация о подписке."""

    id: int = Field(..., description="ID подписки")
    company_id: int = Field(..., description="ID компании")
    plan: SubscriptionPlan = Field(..., description="План подписки")
    status: SubscriptionStatus = Field(..., description="Статус")
    billing_period: BillingPeriod = Field(..., description="Период биллинга")
    start_date: datetime = Field(..., description="Дата начала")
    end_date: Optional[datetime] = Field(None, description="Дата окончания")
    next_billing_date: Optional[datetime] = Field(
        None, description="Следующая дата биллинга"
    )
    auto_renewal: bool = Field(True, description="Автопродление")
    current_period_start: datetime = Field(..., description="Начало текущего периода")
    current_period_end: datetime = Field(..., description="Конец текущего периода")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class SubscriptionDetailResponse(SubscriptionResponse):
    """Детальная информация о подписке."""

    plan_details: SubscriptionPlanDetailsResponse = Field(
        ..., description="Детали плана"
    )

    # Использование ресурсов
    usage_stats: Dict[str, Any] = Field(..., description="Статистика использования")

    # Кастомные возможности
    custom_features: Dict[str, Any] = Field(
        default_factory=dict, description="Кастомные возможности"
    )

    # Биллинг
    total_amount: Decimal = Field(..., description="Общая сумма")
    currency: str = Field("USD", description="Валюта")

    # История изменений
    last_plan_change_date: Optional[datetime] = Field(
        None, description="Последнее изменение плана"
    )

    # Метаданные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class SubscriptionListResponse(BaseSchema):
    """Список подписок с пагинацией."""

    subscriptions: List[SubscriptionResponse] = Field(
        ..., description="Список подписок"
    )
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Usage and Limits ===


class SubscriptionUsageResponse(BaseSchema):
    """Использование ресурсов подписки."""

    subscription_id: int = Field(..., description="ID подписки")
    current_period_start: datetime = Field(..., description="Начало периода")
    current_period_end: datetime = Field(..., description="Конец периода")

    # Использование ресурсов
    users_count: int = Field(..., description="Количество пользователей")
    users_limit: Optional[int] = Field(None, description="Лимит пользователей")
    projects_count: int = Field(..., description="Количество проектов")
    projects_limit: Optional[int] = Field(None, description="Лимит проектов")
    storage_used_gb: float = Field(..., description="Использовано хранилища ГБ")
    storage_limit_gb: Optional[float] = Field(None, description="Лимит хранилища ГБ")

    # API использование
    api_calls_count: int = Field(0, description="Количество API вызовов")
    api_calls_limit: Optional[int] = Field(None, description="Лимит API вызовов")

    # Процентное использование
    usage_percentages: Dict[str, float] = Field(
        ..., description="Процент использования"
    )

    # Предупреждения
    warnings: List[str] = Field(..., description="Предупреждения об использовании")


class SubscriptionLimitsResponse(BaseSchema):
    """Лимиты подписки."""

    subscription_id: int = Field(..., description="ID подписки")
    plan: SubscriptionPlan = Field(..., description="План")

    # Лимиты
    limits: Dict[str, Any] = Field(..., description="Все лимиты")

    # Мягкие и жесткие лимиты
    soft_limits: Dict[str, Any] = Field(..., description="Мягкие лимиты")
    hard_limits: Dict[str, Any] = Field(..., description="Жесткие лимиты")

    # Возможности
    enabled_features: List[str] = Field(..., description="Включенные возможности")
    disabled_features: List[str] = Field(..., description="Отключенные возможности")


# === Billing and Payments ===


class SubscriptionBillingResponse(BaseSchema):
    """Информация о биллинге подписки."""

    subscription_id: int = Field(..., description="ID подписки")
    billing_period: BillingPeriod = Field(..., description="Период биллинга")
    amount: Decimal = Field(..., description="Сумма")
    currency: str = Field(..., description="Валюта")
    next_billing_date: datetime = Field(..., description="Следующая дата биллинга")

    # Детали биллинга
    base_amount: Decimal = Field(..., description="Базовая сумма")
    discount_amount: Decimal = Field(Decimal("0"), description="Сумма скидки")
    tax_amount: Decimal = Field(Decimal("0"), description="Сумма налога")
    total_amount: Decimal = Field(..., description="Итоговая сумма")

    # Способ оплаты
    payment_method_id: Optional[str] = Field(None, description="ID способа оплаты")
    auto_payment: bool = Field(True, description="Автоплатеж")


class PaymentHistoryResponse(BaseSchema):
    """История платежей."""

    subscription_id: int = Field(..., description="ID подписки")
    payments: List[Dict[str, Any]] = Field(..., description="История платежей")
    total_paid: Decimal = Field(..., description="Общая сумма оплачено")
    pending_amount: Decimal = Field(Decimal("0"), description="Сумма в ожидании")
    failed_payments_count: int = Field(0, description="Количество неудачных платежей")


# === Operations ===


class SubscriptionOperationResponse(BaseSchema):
    """Ответ операции с подпиской."""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение")
    subscription_id: int = Field(..., description="ID подписки")
    operation_type: str = Field(..., description="Тип операции")
    effective_date: Optional[datetime] = Field(
        None, description="Дата вступления в силу"
    )

    # Дополнительная информация
    previous_plan: Optional[SubscriptionPlan] = Field(
        None, description="Предыдущий план"
    )
    new_plan: Optional[SubscriptionPlan] = Field(None, description="Новый план")
    proration_amount: Optional[Decimal] = Field(None, description="Сумма пропорции")


# === Filter and Search ===


class SubscriptionFilterRequest(BaseSchema):
    """Фильтр подписок."""

    company_id: Optional[int] = Field(None, description="ID компании")
    plan: Optional[List[SubscriptionPlan]] = Field(None, description="Планы")
    status: Optional[List[SubscriptionStatus]] = Field(None, description="Статусы")
    billing_period: Optional[List[BillingPeriod]] = Field(
        None, description="Периоды биллинга"
    )
    expires_before: Optional[datetime] = Field(None, description="Истекает до")
    expires_after: Optional[datetime] = Field(None, description="Истекает после")
    auto_renewal: Optional[bool] = Field(None, description="Автопродление")


class SubscriptionSearchRequest(BaseSchema):
    """Поиск подписок."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    filters: Optional[SubscriptionFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


# === Statistics ===


class SubscriptionStatisticsResponse(BaseSchema):
    """Статистика подписок."""

    total_subscriptions: int = Field(..., description="Всего подписок")
    active_subscriptions: int = Field(..., description="Активные подписки")
    trial_subscriptions: int = Field(..., description="Пробные подписки")
    cancelled_subscriptions: int = Field(..., description="Отмененные подписки")

    # По планам
    by_plan: Dict[str, int] = Field(..., description="По планам")

    # По статусам
    by_status: Dict[str, int] = Field(..., description="По статусам")

    # Финансовые метрики
    monthly_recurring_revenue: Decimal = Field(
        ..., description="Месячная регулярная выручка"
    )
    annual_recurring_revenue: Decimal = Field(
        ..., description="Годовая регулярная выручка"
    )
    average_revenue_per_user: Decimal = Field(
        ..., description="Средняя выручка с пользователя"
    )

    # Метрики отказов
    churn_rate: float = Field(..., description="Процент оттока")
    retention_rate: float = Field(..., description="Процент удержания")


__all__ = [
    "SubscriptionStatus",
    "SubscriptionPlan",
    "BillingPeriod",
    "PaymentStatus",
    "SubscriptionCreateRequest",
    "SubscriptionUpdateRequest",
    "SubscriptionUpgradeRequest",
    "SubscriptionCancellationRequest",
    "SubscriptionPlanDetailsResponse",
    "SubscriptionResponse",
    "SubscriptionDetailResponse",
    "SubscriptionListResponse",
    "SubscriptionUsageResponse",
    "SubscriptionLimitsResponse",
    "SubscriptionBillingResponse",
    "PaymentHistoryResponse",
    "SubscriptionOperationResponse",
    "SubscriptionFilterRequest",
    "SubscriptionSearchRequest",
    "SubscriptionStatisticsResponse",
]

"""
Testing Schemas.

Схемы для операций с тестированием.
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


# === Testing Enums ===


class TestCaseStatus(str, Enum):
    """Статусы тест-кейсов."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TestCasePriority(str, Enum):
    """Приоритеты тест-кейсов."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestResultStatus(str, Enum):
    """Статусы результатов тестов."""

    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    NOT_EXECUTED = "not_executed"


class TestType(str, Enum):
    """Типы тестов."""

    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    UNIT = "unit"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    REGRESSION = "regression"
    SMOKE = "smoke"


class TestPlanStatus(str, Enum):
    """Статусы тест-планов."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


# === Test Case Schemas ===


class TestCaseCreateRequest(BaseSchema):
    """Схема создания тест-кейса."""

    title: str = Field(
        ..., min_length=1, max_length=255, description="Название тест-кейса"
    )
    description: Optional[str] = Field(None, description="Описание")
    preconditions: Optional[str] = Field(None, description="Предусловия")
    steps: str = Field(..., description="Шаги выполнения")
    expected_result: str = Field(..., description="Ожидаемый результат")
    test_type: TestType = Field(..., description="Тип теста")
    priority: TestCasePriority = Field(..., description="Приоритет")
    status: TestCaseStatus = Field(TestCaseStatus.DRAFT, description="Статус")
    requirement_id: Optional[int] = Field(None, description="ID связанного требования")
    project_id: int = Field(..., gt=0, description="ID проекта")
    estimated_time_minutes: Optional[int] = Field(
        None, ge=0, description="Оценка времени в минутах"
    )


class TestCaseUpdateRequest(BaseSchema):
    """Схема обновления тест-кейса."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название"
    )
    description: Optional[str] = Field(None, description="Описание")
    preconditions: Optional[str] = Field(None, description="Предусловия")
    steps: Optional[str] = Field(None, description="Шаги выполнения")
    expected_result: Optional[str] = Field(None, description="Ожидаемый результат")
    test_type: Optional[TestType] = Field(None, description="Тип теста")
    priority: Optional[TestCasePriority] = Field(None, description="Приоритет")
    status: Optional[TestCaseStatus] = Field(None, description="Статус")
    requirement_id: Optional[int] = Field(None, description="ID связанного требования")
    estimated_time_minutes: Optional[int] = Field(
        None, ge=0, description="Оценка времени"
    )


class TestCaseResponse(BaseSchema):
    """Схема ответа с данными тест-кейса."""

    id: int = Field(..., description="ID тест-кейса")
    title: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    preconditions: Optional[str] = Field(None, description="Предусловия")
    steps: str = Field(..., description="Шаги выполнения")
    expected_result: str = Field(..., description="Ожидаемый результат")
    test_type: TestType = Field(..., description="Тип теста")
    priority: TestCasePriority = Field(..., description="Приоритет")
    status: TestCaseStatus = Field(..., description="Статус")
    requirement_id: Optional[int] = Field(None, description="ID связанного требования")
    project_id: int = Field(..., description="ID проекта")
    estimated_time_minutes: Optional[int] = Field(None, description="Оценка времени")
    created_by: int = Field(..., description="ID создателя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class TestCaseDetailResponse(TestCaseResponse):
    """Детальная информация о тест-кейсе."""

    # Статистика выполнения
    executions_count: int = Field(0, description="Количество выполнений")
    last_execution_date: Optional[datetime] = Field(
        None, description="Последнее выполнение"
    )
    last_result: Optional[TestResultStatus] = Field(
        None, description="Последний результат"
    )

    # Связанные данные
    defects_count: int = Field(0, description="Количество найденных дефектов")

    # Метаданные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class TestCaseListResponse(BaseSchema):
    """Список тест-кейсов с пагинацией."""

    test_cases: List[TestCaseResponse] = Field(..., description="Список тест-кейсов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Test Result Schemas ===


class TestResultCreateRequest(BaseSchema):
    """Схема создания результата теста."""

    test_case_id: int = Field(..., gt=0, description="ID тест-кейса")
    test_plan_id: Optional[int] = Field(None, description="ID тест-плана")
    status: TestResultStatus = Field(..., description="Статус результата")
    actual_result: Optional[str] = Field(None, description="Фактический результат")
    notes: Optional[str] = Field(None, description="Примечания")
    execution_time_minutes: Optional[int] = Field(
        None, ge=0, description="Время выполнения"
    )
    executed_by: int = Field(..., gt=0, description="ID исполнителя")
    environment: Optional[str] = Field(None, description="Тестовая среда")
    build_version: Optional[str] = Field(None, description="Версия сборки")


class TestResultUpdateRequest(BaseSchema):
    """Схема обновления результата теста."""

    status: Optional[TestResultStatus] = Field(None, description="Статус результата")
    actual_result: Optional[str] = Field(None, description="Фактический результат")
    notes: Optional[str] = Field(None, description="Примечания")
    execution_time_minutes: Optional[int] = Field(
        None, ge=0, description="Время выполнения"
    )
    environment: Optional[str] = Field(None, description="Тестовая среда")
    build_version: Optional[str] = Field(None, description="Версия сборки")


class TestResultResponse(BaseSchema):
    """Схема ответа с результатом теста."""

    id: int = Field(..., description="ID результата")
    test_case_id: int = Field(..., description="ID тест-кейса")
    test_plan_id: Optional[int] = Field(None, description="ID тест-плана")
    status: TestResultStatus = Field(..., description="Статус результата")
    actual_result: Optional[str] = Field(None, description="Фактический результат")
    notes: Optional[str] = Field(None, description="Примечания")
    execution_time_minutes: Optional[int] = Field(None, description="Время выполнения")
    executed_by: int = Field(..., description="ID исполнителя")
    environment: Optional[str] = Field(None, description="Тестовая среда")
    build_version: Optional[str] = Field(None, description="Версия сборки")
    executed_at: datetime = Field(..., description="Дата выполнения")


class TestResultListResponse(BaseSchema):
    """Список результатов тестов с пагинацией."""

    test_results: List[TestResultResponse] = Field(
        ..., description="Список результатов"
    )
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Test Plan Schemas ===


class TestPlanCreateRequest(BaseSchema):
    """Схема создания тест-плана."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Название тест-плана"
    )
    description: Optional[str] = Field(None, description="Описание")
    project_id: int = Field(..., gt=0, description="ID проекта")
    release_id: Optional[int] = Field(None, description="ID релиза")
    start_date: Optional[datetime] = Field(None, description="Дата начала")
    end_date: Optional[datetime] = Field(None, description="Дата окончания")
    status: TestPlanStatus = Field(TestPlanStatus.DRAFT, description="Статус")


class TestPlanUpdateRequest(BaseSchema):
    """Схема обновления тест-плана."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название"
    )
    description: Optional[str] = Field(None, description="Описание")
    release_id: Optional[int] = Field(None, description="ID релиза")
    start_date: Optional[datetime] = Field(None, description="Дата начала")
    end_date: Optional[datetime] = Field(None, description="Дата окончания")
    status: Optional[TestPlanStatus] = Field(None, description="Статус")


class TestPlanResponse(BaseSchema):
    """Схема ответа с данными тест-плана."""

    id: int = Field(..., description="ID тест-плана")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    project_id: int = Field(..., description="ID проекта")
    release_id: Optional[int] = Field(None, description="ID релиза")
    start_date: Optional[datetime] = Field(None, description="Дата начала")
    end_date: Optional[datetime] = Field(None, description="Дата окончания")
    status: TestPlanStatus = Field(..., description="Статус")
    created_by: int = Field(..., description="ID создателя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class TestPlanDetailResponse(TestPlanResponse):
    """Детальная информация о тест-плане."""

    # Статистика
    test_cases_count: int = Field(0, description="Количество тест-кейсов")
    executed_tests: int = Field(0, description="Выполненные тесты")
    passed_tests: int = Field(0, description="Пройденные тесты")
    failed_tests: int = Field(0, description="Проваленные тесты")
    blocked_tests: int = Field(0, description="Заблокированные тесты")

    # Прогресс
    completion_percentage: float = Field(
        0.0, ge=0, le=100, description="Процент выполнения"
    )
    pass_rate: float = Field(0.0, ge=0, le=100, description="Процент прохождения")

    # Время
    estimated_time_hours: Optional[float] = Field(
        None, description="Оценка времени в часах"
    )
    actual_time_hours: Optional[float] = Field(None, description="Фактическое время")


class TestPlanListResponse(BaseSchema):
    """Список тест-планов с пагинацией."""

    test_plans: List[TestPlanResponse] = Field(..., description="Список тест-планов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Filter and Search Schemas ===


class TestCaseFilterRequest(BaseSchema):
    """Фильтр тест-кейсов."""

    project_id: Optional[int] = Field(None, description="ID проекта")
    requirement_id: Optional[int] = Field(None, description="ID требования")
    test_type: Optional[List[TestType]] = Field(None, description="Типы тестов")
    priority: Optional[List[TestCasePriority]] = Field(None, description="Приоритеты")
    status: Optional[List[TestCaseStatus]] = Field(None, description="Статусы")
    created_by: Optional[int] = Field(None, description="ID создателя")
    created_from: Optional[datetime] = Field(None, description="Создано с")
    created_to: Optional[datetime] = Field(None, description="Создано до")


class TestResultFilterRequest(BaseSchema):
    """Фильтр результатов тестов."""

    test_case_id: Optional[int] = Field(None, description="ID тест-кейса")
    test_plan_id: Optional[int] = Field(None, description="ID тест-плана")
    status: Optional[List[TestResultStatus]] = Field(None, description="Статусы")
    executed_by: Optional[int] = Field(None, description="ID исполнителя")
    environment: Optional[str] = Field(None, description="Тестовая среда")
    executed_from: Optional[datetime] = Field(None, description="Выполнено с")
    executed_to: Optional[datetime] = Field(None, description="Выполнено до")


# === Statistics Schemas ===


class TestingStatisticsResponse(BaseSchema):
    """Статистика по тестированию."""

    total_test_cases: int = Field(..., description="Всего тест-кейсов")
    total_executions: int = Field(..., description="Всего выполнений")
    by_status: Dict[str, int] = Field(..., description="По статусам")
    by_type: Dict[str, int] = Field(..., description="По типам")
    by_priority: Dict[str, int] = Field(..., description="По приоритетам")
    pass_rate: float = Field(..., description="Процент прохождения")
    average_execution_time: Optional[float] = Field(
        None, description="Среднее время выполнения"
    )
    defect_detection_rate: float = Field(
        ..., description="Процент обнаружения дефектов"
    )


# === Export Schemas ===


class TestingExportRequest(BaseSchema):
    """Запрос на экспорт данных тестирования."""

    test_case_ids: Optional[List[int]] = Field(None, description="ID тест-кейсов")
    test_plan_id: Optional[int] = Field(None, description="ID тест-плана")
    format: str = Field("xlsx", description="Формат экспорта")
    include_results: bool = Field(True, description="Включить результаты")
    include_defects: bool = Field(False, description="Включить дефекты")
    filters: Optional[TestCaseFilterRequest] = Field(None, description="Фильтры")


class TestingExportResponse(BaseSchema):
    """Ответ экспорта данных тестирования."""

    success: bool = Field(..., description="Успешность операции")
    export_id: str = Field(..., description="ID экспорта")
    download_url: str = Field(..., description="URL скачивания")
    file_size_bytes: int = Field(..., description="Размер файла")
    expires_at: datetime = Field(..., description="Время истечения ссылки")


__all__ = [
    "TestCaseStatus",
    "TestCasePriority",
    "TestResultStatus",
    "TestType",
    "TestPlanStatus",
    "TestCaseCreateRequest",
    "TestCaseUpdateRequest",
    "TestCaseResponse",
    "TestCaseDetailResponse",
    "TestCaseListResponse",
    "TestResultCreateRequest",
    "TestResultUpdateRequest",
    "TestResultResponse",
    "TestResultListResponse",
    "TestPlanCreateRequest",
    "TestPlanUpdateRequest",
    "TestPlanResponse",
    "TestPlanDetailResponse",
    "TestPlanListResponse",
    "TestCaseFilterRequest",
    "TestResultFilterRequest",
    "TestingStatisticsResponse",
    "TestingExportRequest",
    "TestingExportResponse",
]

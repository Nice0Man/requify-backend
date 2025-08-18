"""
Quality Reports Schemas.

Схемы для отчетов по качеству.
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


# === Report Enums ===


class ReportType(str, Enum):
    """Типы отчетов."""

    TEST_EXECUTION = "test_execution"
    REQUIREMENTS_COVERAGE = "requirements_coverage"
    DEFECT_SUMMARY = "defect_summary"
    QUALITY_METRICS = "quality_metrics"
    TRACEABILITY_MATRIX = "traceability_matrix"
    PROGRESS_REPORT = "progress_report"
    RELEASE_READINESS = "release_readiness"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Форматы отчетов."""

    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"
    JSON = "json"
    CSV = "csv"


class ReportStatus(str, Enum):
    """Статусы отчетов."""

    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# === Report Request Schemas ===


class ReportGenerateRequest(BaseSchema):
    """Запрос на генерацию отчета."""

    name: str = Field(..., min_length=1, max_length=255, description="Название отчета")
    report_type: ReportType = Field(..., description="Тип отчета")
    format: ReportFormat = Field(..., description="Формат отчета")
    project_id: Optional[int] = Field(None, description="ID проекта")
    release_id: Optional[int] = Field(None, description="ID релиза")
    test_plan_id: Optional[int] = Field(None, description="ID тест-плана")
    date_from: Optional[datetime] = Field(None, description="Дата начала периода")
    date_to: Optional[datetime] = Field(None, description="Дата окончания периода")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Параметры отчета"
    )
    filters: Dict[str, Any] = Field(default_factory=dict, description="Фильтры")
    schedule: Optional[str] = Field(None, description="Расписание автогенерации")


class ReportUpdateRequest(BaseSchema):
    """Обновление настроек отчета."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название"
    )
    parameters: Optional[Dict[str, Any]] = Field(None, description="Параметры")
    filters: Optional[Dict[str, Any]] = Field(None, description="Фильтры")
    schedule: Optional[str] = Field(None, description="Расписание")
    is_active: Optional[bool] = Field(None, description="Активен ли отчет")


# === Report Response Schemas ===


class ReportResponse(BaseSchema):
    """Базовая информация об отчете."""

    id: int = Field(..., description="ID отчета")
    name: str = Field(..., description="Название")
    report_type: ReportType = Field(..., description="Тип отчета")
    format: ReportFormat = Field(..., description="Формат")
    status: ReportStatus = Field(..., description="Статус")
    project_id: Optional[int] = Field(None, description="ID проекта")
    release_id: Optional[int] = Field(None, description="ID релиза")
    test_plan_id: Optional[int] = Field(None, description="ID тест-плана")
    file_url: Optional[str] = Field(None, description="URL файла отчета")
    file_size_bytes: Optional[int] = Field(None, description="Размер файла")
    created_by: int = Field(..., description="ID создателя")
    generated_at: Optional[datetime] = Field(None, description="Время генерации")
    expires_at: Optional[datetime] = Field(None, description="Время истечения")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class ReportDetailResponse(ReportResponse):
    """Детальная информация об отчете."""

    parameters: Dict[str, Any] = Field(..., description="Параметры отчета")
    filters: Dict[str, Any] = Field(..., description="Фильтры")
    schedule: Optional[str] = Field(None, description="Расписание автогенерации")
    is_active: bool = Field(True, description="Активен ли отчет")

    # Статистика генерации
    generation_time_seconds: Optional[float] = Field(
        None, description="Время генерации в секундах"
    )
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")

    # История
    executions_count: int = Field(0, description="Количество выполнений")
    last_execution_at: Optional[datetime] = Field(
        None, description="Последнее выполнение"
    )

    # Метаданные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class ReportListResponse(BaseSchema):
    """Список отчетов с пагинацией."""

    reports: List[ReportResponse] = Field(..., description="Список отчетов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    pages: int = Field(..., description="Всего страниц")
    size: int = Field(..., description="Размер страницы")


# === Specific Report Schemas ===


class TestExecutionReportData(BaseSchema):
    """Данные отчета по выполнению тестов."""

    total_test_cases: int = Field(..., description="Всего тест-кейсов")
    executed_tests: int = Field(..., description="Выполненные тесты")
    passed_tests: int = Field(..., description="Пройденные тесты")
    failed_tests: int = Field(..., description="Проваленные тесты")
    blocked_tests: int = Field(..., description="Заблокированные тесты")
    skipped_tests: int = Field(..., description="Пропущенные тесты")
    pass_rate: float = Field(..., description="Процент прохождения")
    execution_rate: float = Field(..., description="Процент выполнения")

    # Детализация по приоритетам
    by_priority: Dict[str, Dict[str, int]] = Field(..., description="По приоритетам")

    # Детализация по типам
    by_type: Dict[str, Dict[str, int]] = Field(..., description="По типам тестов")

    # Тренды
    daily_progress: List[Dict[str, Any]] = Field(..., description="Ежедневный прогресс")


class RequirementsCoverageReportData(BaseSchema):
    """Данные отчета по покрытию требований."""

    total_requirements: int = Field(..., description="Всего требований")
    covered_requirements: int = Field(..., description="Покрытые требования")
    uncovered_requirements: int = Field(..., description="Непокрытые требования")
    coverage_percentage: float = Field(..., description="Процент покрытия")

    # Детализация по типам
    by_type: Dict[str, Dict[str, int]] = Field(..., description="По типам требований")

    # Детализация по статусам
    by_status: Dict[str, Dict[str, int]] = Field(..., description="По статусам")

    # Непокрытые требования
    uncovered_list: List[Dict[str, Any]] = Field(..., description="Список непокрытых")


class DefectSummaryReportData(BaseSchema):
    """Данные отчета по дефектам."""

    total_defects: int = Field(..., description="Всего дефектов")
    open_defects: int = Field(..., description="Открытые дефекты")
    resolved_defects: int = Field(..., description="Решенные дефекты")
    closed_defects: int = Field(..., description="Закрытые дефекты")

    # По серьезности
    by_severity: Dict[str, int] = Field(..., description="По серьезности")

    # По приоритету
    by_priority: Dict[str, int] = Field(..., description="По приоритету")

    # По статусу
    by_status: Dict[str, int] = Field(..., description="По статусу")

    # Метрики качества
    defect_density: float = Field(..., description="Плотность дефектов")
    defect_removal_efficiency: float = Field(
        ..., description="Эффективность удаления дефектов"
    )

    # Тренды
    discovery_trend: List[Dict[str, Any]] = Field(..., description="Тренд обнаружения")
    resolution_trend: List[Dict[str, Any]] = Field(..., description="Тренд решения")


class TraceabilityMatrixReportData(BaseSchema):
    """Данные матрицы трассируемости."""

    total_requirements: int = Field(..., description="Всего требований")
    total_test_cases: int = Field(..., description="Всего тест-кейсов")

    # Связи
    requirements_with_tests: int = Field(..., description="Требования с тестами")
    tests_with_requirements: int = Field(..., description="Тесты с требованиями")
    orphaned_tests: int = Field(..., description="Несвязанные тесты")
    untested_requirements: int = Field(..., description="Нетестируемые требования")

    # Матрица
    traceability_matrix: List[Dict[str, Any]] = Field(
        ..., description="Матрица трассируемости"
    )

    # Проблемы
    coverage_gaps: List[Dict[str, Any]] = Field(..., description="Пробелы в покрытии")
    redundant_tests: List[Dict[str, Any]] = Field(..., description="Избыточные тесты")


# === Report Template Schemas ===


class ReportTemplateCreateRequest(BaseSchema):
    """Создание шаблона отчета."""

    name: str = Field(..., min_length=1, max_length=255, description="Название шаблона")
    description: Optional[str] = Field(None, description="Описание")
    report_type: ReportType = Field(..., description="Тип отчета")
    template_config: Dict[str, Any] = Field(..., description="Конфигурация шаблона")
    default_parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Параметры по умолчанию"
    )
    is_public: bool = Field(False, description="Публичный шаблон")


class ReportTemplateResponse(BaseSchema):
    """Информация о шаблоне отчета."""

    id: int = Field(..., description="ID шаблона")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    report_type: ReportType = Field(..., description="Тип отчета")
    template_config: Dict[str, Any] = Field(..., description="Конфигурация")
    default_parameters: Dict[str, Any] = Field(
        ..., description="Параметры по умолчанию"
    )
    is_public: bool = Field(..., description="Публичный шаблон")
    usage_count: int = Field(0, description="Количество использований")
    created_by: int = Field(..., description="ID создателя")
    created_at: datetime = Field(..., description="Дата создания")


# === Filter and Search Schemas ===


class ReportFilterRequest(BaseSchema):
    """Фильтр отчетов."""

    report_type: Optional[List[ReportType]] = Field(None, description="Типы отчетов")
    status: Optional[List[ReportStatus]] = Field(None, description="Статусы")
    format: Optional[List[ReportFormat]] = Field(None, description="Форматы")
    project_id: Optional[int] = Field(None, description="ID проекта")
    created_by: Optional[int] = Field(None, description="ID создателя")
    created_from: Optional[datetime] = Field(None, description="Создано с")
    created_to: Optional[datetime] = Field(None, description="Создано до")
    generated_from: Optional[datetime] = Field(None, description="Сгенерировано с")
    generated_to: Optional[datetime] = Field(None, description="Сгенерировано до")


class ReportSearchRequest(BaseSchema):
    """Поиск отчетов."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    filters: Optional[ReportFilterRequest] = Field(None, description="Фильтры")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


# === Statistics ===


class ReportStatisticsResponse(BaseSchema):
    """Статистика по отчетам."""

    total_reports: int = Field(..., description="Всего отчетов")
    by_type: Dict[str, int] = Field(..., description="По типам")
    by_status: Dict[str, int] = Field(..., description="По статусам")
    by_format: Dict[str, int] = Field(..., description="По форматам")
    successful_generations: int = Field(..., description="Успешные генерации")
    failed_generations: int = Field(..., description="Неудачные генерации")
    average_generation_time: float = Field(..., description="Среднее время генерации")
    total_downloads: int = Field(..., description="Всего загрузок")


# === Operation Response ===


class ReportOperationResponse(BaseSchema):
    """Ответ операции с отчетом."""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение")
    report_id: Optional[int] = Field(None, description="ID отчета")
    job_id: Optional[str] = Field(None, description="ID задачи генерации")
    estimated_completion_time: Optional[datetime] = Field(
        None, description="Ожидаемое время завершения"
    )


__all__ = [
    "ReportType",
    "ReportFormat",
    "ReportStatus",
    "ReportGenerateRequest",
    "ReportUpdateRequest",
    "ReportResponse",
    "ReportDetailResponse",
    "ReportListResponse",
    "TestExecutionReportData",
    "RequirementsCoverageReportData",
    "DefectSummaryReportData",
    "TraceabilityMatrixReportData",
    "ReportTemplateCreateRequest",
    "ReportTemplateResponse",
    "ReportFilterRequest",
    "ReportSearchRequest",
    "ReportStatisticsResponse",
    "ReportOperationResponse",
]

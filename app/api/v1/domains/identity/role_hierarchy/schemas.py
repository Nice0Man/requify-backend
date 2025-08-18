"""
Role Hierarchy Schemas.

Схемы для работы с иерархией ролей.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import Field

from app.api.v1.common.schemas import BaseSchema


# === Role Hierarchy Enums ===


class RoleHierarchyOperationType(str, Enum):
    """Типы операций с иерархией ролей."""

    ADD_PARENT = "add_parent"
    REMOVE_PARENT = "remove_parent"
    ADD_CHILD = "add_child"
    REMOVE_CHILD = "remove_child"
    MOVE_SUBTREE = "move_subtree"
    REORDER = "reorder"


class InheritanceType(str, Enum):
    """Типы наследования прав."""

    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
    CUSTOM = "custom"


# === Request Schemas ===


class RoleHierarchyCreateRequest(BaseSchema):
    """Создание связи в иерархии ролей."""

    parent_role_id: int = Field(..., gt=0, description="ID родительской роли")
    child_role_id: int = Field(..., gt=0, description="ID дочерней роли")
    inheritance_type: InheritanceType = Field(
        InheritanceType.FULL, description="Тип наследования"
    )
    inherit_permissions: bool = Field(True, description="Наследовать права")
    inherit_restrictions: bool = Field(False, description="Наследовать ограничения")
    priority: int = Field(0, description="Приоритет в иерархии")


class RoleHierarchyUpdateRequest(BaseSchema):
    """Обновление связи в иерархии ролей."""

    inheritance_type: Optional[InheritanceType] = Field(
        None, description="Тип наследования"
    )
    inherit_permissions: Optional[bool] = Field(None, description="Наследовать права")
    inherit_restrictions: Optional[bool] = Field(
        None, description="Наследовать ограничения"
    )
    priority: Optional[int] = Field(None, description="Приоритет")


class RoleHierarchyBulkOperationRequest(BaseSchema):
    """Массовые операции с иерархией ролей."""

    operation: RoleHierarchyOperationType = Field(..., description="Тип операции")
    source_role_id: int = Field(..., gt=0, description="ID исходной роли")
    target_role_id: Optional[int] = Field(None, description="ID целевой роли")
    role_ids: Optional[List[int]] = Field(None, description="Список ID ролей")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Параметры операции"
    )


# === Response Schemas ===


class RoleHierarchyRelationResponse(BaseSchema):
    """Связь в иерархии ролей."""

    id: int = Field(..., description="ID связи")
    parent_role_id: int = Field(..., description="ID родительской роли")
    child_role_id: int = Field(..., description="ID дочерней роли")
    inheritance_type: InheritanceType = Field(..., description="Тип наследования")
    inherit_permissions: bool = Field(..., description="Наследует права")
    inherit_restrictions: bool = Field(..., description="Наследует ограничения")
    priority: int = Field(..., description="Приоритет")
    depth_level: int = Field(..., description="Уровень глубины")
    path: str = Field(..., description="Путь в иерархии")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class RoleHierarchyNodeResponse(BaseSchema):
    """Узел иерархии ролей."""

    role_id: int = Field(..., description="ID роли")
    role_name: str = Field(..., description="Название роли")
    role_code: str = Field(..., description="Код роли")
    depth_level: int = Field(..., description="Уровень глубины")
    path: str = Field(..., description="Путь в иерархии")
    is_leaf: bool = Field(..., description="Листовой узел")
    children_count: int = Field(0, description="Количество дочерних ролей")
    permissions_count: int = Field(0, description="Количество прав")
    inherited_permissions_count: int = Field(
        0, description="Количество унаследованных прав"
    )

    # Метаданные
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные")


class RoleHierarchyTreeResponse(BaseSchema):
    """Дерево иерархии ролей."""

    root_nodes: List[RoleHierarchyNodeResponse] = Field(
        ..., description="Корневые узлы"
    )
    total_nodes: int = Field(..., description="Общее количество узлов")
    max_depth: int = Field(..., description="Максимальная глубина")
    relations_count: int = Field(..., description="Количество связей")


class RoleHierarchyPathResponse(BaseSchema):
    """Путь в иерархии ролей."""

    role_id: int = Field(..., description="ID роли")
    ancestors: List[RoleHierarchyNodeResponse] = Field(..., description="Предки")
    descendants: List[RoleHierarchyNodeResponse] = Field(..., description="Потомки")
    siblings: List[RoleHierarchyNodeResponse] = Field(..., description="Соседи")
    depth_level: int = Field(..., description="Уровень глубины")
    full_path: str = Field(..., description="Полный путь")


# === Permissions and Inheritance ===


class RolePermissionInheritanceResponse(BaseSchema):
    """Наследование прав роли."""

    role_id: int = Field(..., description="ID роли")
    permission_id: int = Field(..., description="ID права")
    permission_code: str = Field(..., description="Код права")
    is_direct: bool = Field(..., description="Прямое право")
    is_inherited: bool = Field(..., description="Унаследованное право")
    inherited_from_role_id: Optional[int] = Field(
        None, description="Унаследовано от роли"
    )
    inheritance_path: Optional[str] = Field(None, description="Путь наследования")
    can_be_overridden: bool = Field(True, description="Может быть переопределено")


class RoleEffectivePermissionsResponse(BaseSchema):
    """Эффективные права роли."""

    role_id: int = Field(..., description="ID роли")
    direct_permissions: List[str] = Field(..., description="Прямые права")
    inherited_permissions: List[str] = Field(..., description="Унаследованные права")
    effective_permissions: List[str] = Field(..., description="Эффективные права")
    denied_permissions: List[str] = Field(..., description="Запрещенные права")
    inheritance_details: List[RolePermissionInheritanceResponse] = Field(
        ..., description="Детали наследования"
    )


# === Validation and Analysis ===


class RoleHierarchyValidationRequest(BaseSchema):
    """Запрос на валидацию иерархии."""

    check_cycles: bool = Field(True, description="Проверить циклы")
    check_conflicts: bool = Field(True, description="Проверить конфликты")
    check_orphans: bool = Field(True, description="Проверить сироты")
    check_permissions: bool = Field(True, description="Проверить права")


class RoleHierarchyValidationResponse(BaseSchema):
    """Результат валидации иерархии."""

    is_valid: bool = Field(..., description="Валидна ли иерархия")
    validation_errors: List[str] = Field(..., description="Ошибки валидации")
    validation_warnings: List[str] = Field(..., description="Предупреждения")

    # Детальные проблемы
    cycles_detected: List[Dict[str, Any]] = Field(..., description="Обнаруженные циклы")
    permission_conflicts: List[Dict[str, Any]] = Field(
        ..., description="Конфликты прав"
    )
    orphaned_roles: List[int] = Field(..., description="Роли-сироты")
    inconsistent_inheritance: List[Dict[str, Any]] = Field(
        ..., description="Несогласованное наследование"
    )


class RoleHierarchyAnalysisResponse(BaseSchema):
    """Анализ иерархии ролей."""

    total_roles: int = Field(..., description="Всего ролей")
    hierarchy_depth: int = Field(..., description="Глубина иерархии")
    branch_factor: float = Field(..., description="Фактор ветвления")

    # Статистика по уровням
    level_distribution: Dict[int, int] = Field(
        ..., description="Распределение по уровням"
    )

    # Проблемные области
    potential_issues: List[str] = Field(..., description="Потенциальные проблемы")
    optimization_suggestions: List[str] = Field(
        ..., description="Предложения по оптимизации"
    )

    # Метрики производительности
    performance_metrics: Dict[str, float] = Field(
        ..., description="Метрики производительности"
    )


# === Search and Filter ===


class RoleHierarchySearchRequest(BaseSchema):
    """Поиск в иерархии ролей."""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    search_in_permissions: bool = Field(False, description="Искать в правах")
    max_depth: Optional[int] = Field(None, description="Максимальная глубина")
    role_types: Optional[List[str]] = Field(None, description="Типы ролей")


class RoleHierarchyFilterRequest(BaseSchema):
    """Фильтр иерархии ролей."""

    root_role_id: Optional[int] = Field(None, description="ID корневой роли")
    min_depth: Optional[int] = Field(None, description="Минимальная глубина")
    max_depth: Optional[int] = Field(None, description="Максимальная глубина")
    has_children: Optional[bool] = Field(None, description="Есть ли дочерние")
    inheritance_type: Optional[InheritanceType] = Field(
        None, description="Тип наследования"
    )
    role_types: Optional[List[str]] = Field(None, description="Типы ролей")


# === Statistics ===


class RoleHierarchyStatisticsResponse(BaseSchema):
    """Статистика иерархии ролей."""

    total_roles: int = Field(..., description="Всего ролей")
    total_relations: int = Field(..., description="Всего связей")
    root_roles: int = Field(..., description="Корневые роли")
    leaf_roles: int = Field(..., description="Листовые роли")
    max_depth: int = Field(..., description="Максимальная глубина")
    average_depth: float = Field(..., description="Средняя глубина")
    average_children: float = Field(..., description="Среднее количество детей")

    # Распределения
    depth_distribution: Dict[int, int] = Field(
        ..., description="Распределение по глубине"
    )
    children_distribution: Dict[int, int] = Field(
        ..., description="Распределение по детям"
    )
    inheritance_distribution: Dict[str, int] = Field(
        ..., description="Распределение по типам наследования"
    )


# === Operation Response ===


class RoleHierarchyOperationResponse(BaseSchema):
    """Ответ операции с иерархией ролей."""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение")
    affected_roles: List[int] = Field(..., description="Затронутые роли")
    validation_errors: List[str] = Field(
        default_factory=list, description="Ошибки валидации"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Время операции"
    )


# === Cache Schemas ===


class RoleHierarchyCacheCreate(BaseSchema):
    """Schema for creating role hierarchy cache entry."""

    ancestor_role_id: int = Field(..., description="Ancestor role ID")
    descendant_role_id: int = Field(..., description="Descendant role ID")
    depth: int = Field(..., description="Depth in hierarchy")
    path: Optional[str] = Field(None, description="Path in hierarchy")


class RoleHierarchyCacheUpdate(BaseSchema):
    """Schema for updating role hierarchy cache entry."""

    depth: Optional[int] = Field(None, description="Depth in hierarchy")
    path: Optional[str] = Field(None, description="Path in hierarchy")


__all__ = [
    "RoleHierarchyOperationType",
    "InheritanceType",
    "RoleHierarchyCreateRequest",
    "RoleHierarchyUpdateRequest",
    "RoleHierarchyBulkOperationRequest",
    "RoleHierarchyRelationResponse",
    "RoleHierarchyNodeResponse",
    "RoleHierarchyTreeResponse",
    "RoleHierarchyPathResponse",
    "RolePermissionInheritanceResponse",
    "RoleEffectivePermissionsResponse",
    "RoleHierarchyValidationRequest",
    "RoleHierarchyValidationResponse",
    "RoleHierarchyAnalysisResponse",
    "RoleHierarchySearchRequest",
    "RoleHierarchyFilterRequest",
    "RoleHierarchyStatisticsResponse",
    "RoleHierarchyOperationResponse",
    "RoleHierarchyCacheCreate",
    "RoleHierarchyCacheUpdate",
]

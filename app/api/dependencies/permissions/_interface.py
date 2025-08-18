"""
Стандартизированный интерфейс для permission dependencies.

Определяет единый контракт для всех permission классов в системе.
"""

from typing import Protocol, Callable, Dict, Any, Optional
from app.core.constants import Permission


class PermissionInterface(Protocol):
    """
    Protocol для всех permission классов.

    Определяет минимальный набор методов, которые должны быть
    реализованы в каждом permission классе.
    """

    @staticmethod
    def read() -> Callable:
        """Dependency для чтения данных."""
        ...

    @staticmethod
    def write() -> Callable:
        """Dependency для записи данных."""
        ...


class ExtendedPermissionInterface(PermissionInterface, Protocol):
    """
    Расширенный интерфейс для permission классов.

    Включает дополнительные стандартные методы для полнофункциональных
    permission классов.
    """

    @staticmethod
    def create() -> Callable:
        """Dependency для создания сущностей."""
        ...

    @staticmethod
    def update() -> Callable:
        """Dependency для обновления сущностей."""
        ...

    @staticmethod
    def delete() -> Callable:
        """Dependency для удаления сущностей."""
        ...

    @staticmethod
    def admin() -> Callable:
        """Dependency для административных операций."""
        ...


class PermissionConfig:
    """
    Конфигурация для permission класса.

    Стандартизирует настройки и метаданные для каждого домена.
    """

    def __init__(
        self,
        domain_name: str,
        base_permission: Permission,
        scopes_prefix: str,
        description: str = "",
        special_permissions: Optional[Dict[str, Permission]] = None,
    ):
        self.domain_name = domain_name
        self.base_permission = base_permission
        self.scopes_prefix = scopes_prefix
        self.description = description
        self.special_permissions = special_permissions or {}

    def get_scope(self, operation: str) -> str:
        """Получить OAuth2 scope для операции."""
        return f"{self.scopes_prefix}:{operation}"

    def get_permission(self, operation: str) -> Permission:
        """Получить Permission enum для операции."""
        if operation in self.special_permissions:
            return self.special_permissions[operation]

        # Используем базовое permission для всех операций
        return self.base_permission


# Стандартные конфигурации доменов
DOMAIN_CONFIGS = {
    "User": PermissionConfig(
        domain_name="User",
        base_permission=Permission.VIEW_USERS,
        scopes_prefix="user",
        description="User management operations",
        special_permissions={
            "read": Permission.VIEW_USERS,
            "write": Permission.MANAGE_USERS,
            "create": Permission.MANAGE_USERS,
            "update": Permission.MANAGE_USERS,
            "delete": Permission.REMOVE_USERS,
            "invite": Permission.INVITE_USERS,
        },
    ),
    "Project": PermissionConfig(
        domain_name="Project",
        base_permission=Permission.VIEW_PROJECT,
        scopes_prefix="project",
        description="Project management operations",
        special_permissions={
            "read": Permission.VIEW_PROJECT,
            "write": Permission.MANAGE_PROJECT,
            "create": Permission.CREATE_PROJECT,
            "delete": Permission.DELETE_PROJECT,
            "archive": Permission.ARCHIVE_PROJECT,
            "settings": Permission.MANAGE_PROJECT_SETTINGS,
            "members": Permission.MANAGE_PROJECT_MEMBERS,
            "budget": Permission.MANAGE_PROJECT_BUDGET,
            "analytics": Permission.VIEW_PROJECT_ANALYTICS,
        },
    ),
    "Requirement": PermissionConfig(
        domain_name="Requirement",
        base_permission=Permission.VIEW_REQUIREMENT,
        scopes_prefix="requirement",
        description="Requirements management operations",
        special_permissions={
            "read": Permission.VIEW_REQUIREMENT,
            "write": Permission.EDIT_REQUIREMENT,
            "create": Permission.CREATE_REQUIREMENT,
            "delete": Permission.DELETE_REQUIREMENT,
            "approve": Permission.APPROVE_REQUIREMENT,
            "reject": Permission.REJECT_REQUIREMENT,
            "link": Permission.LINK_REQUIREMENTS,
            "unlink": Permission.UNLINK_REQUIREMENTS,
            "versions": Permission.MANAGE_REQUIREMENT_VERSIONS,
            "export": Permission.EXPORT_REQUIREMENTS,
            "import": Permission.IMPORT_REQUIREMENTS,
            "status": Permission.CHANGE_REQUIREMENT_STATUS,
            "search": Permission.SEARCH_REQUIREMENTS,
        },
    ),
    "Release": PermissionConfig(
        domain_name="Release",
        base_permission=Permission.VIEW_RELEASE,
        scopes_prefix="release",
        description="Release management operations",
        special_permissions={
            "read": Permission.VIEW_RELEASE,
            "write": Permission.MANAGE_RELEASE,
            "create": Permission.CREATE_RELEASE,
            "delete": Permission.DELETE_RELEASE,
            "publish": Permission.PUBLISH_RELEASE,
            "deploy": Permission.DEPLOY_RELEASE,
            "rollback": Permission.ROLLBACK_RELEASE,
            "approve": Permission.APPROVE_RELEASE,
            "specification": Permission.GENERATE_RELEASE_SPECIFICATION,
            "sync": Permission.SYNC_RELEASE_REQUIREMENTS,
            "changelog": Permission.VIEW_RELEASE_CHANGELOG,
        },
    ),
    "Testing": PermissionConfig(
        domain_name="Testing",
        base_permission=Permission.VIEW_TEST_RESULTS,
        scopes_prefix="test",
        description="Testing operations",
        special_permissions={
            "read": Permission.VIEW_TEST_RESULTS,
            "write": Permission.CREATE_TEST,
            "create": Permission.CREATE_TEST,
            "execute": Permission.EXECUTE_TEST,
            "manage_plans": Permission.MANAGE_TEST_PLANS,
            "manage": Permission.MANAGE_TESTS,
            "delete": Permission.DELETE_TEST,
            "integration": Permission.EXECUTE_INTEGRATION_TESTS,
            "approve": Permission.APPROVE_TEST_RESULTS,
            "automation": Permission.CREATE_TEST_AUTOMATION,
            "environments": Permission.MANAGE_TEST_ENVIRONMENTS,
            "case_create": Permission.CREATE_TEST_CASE,
            "case_edit": Permission.EDIT_TEST_CASE,
            "case_delete": Permission.DELETE_TEST_CASE,
            "case_view": Permission.VIEW_TEST_CASES,
            "case_execute": Permission.EXECUTE_TEST_CASE,
            "execution_create": Permission.CREATE_TEST_EXECUTION,
            "execution_view": Permission.VIEW_TEST_EXECUTIONS,
            "summary": Permission.VIEW_TESTING_SUMMARY,
            "requirement_status": Permission.REQUEST_REQUIREMENT_TESTING_STATUS,
            "release_status": Permission.REQUEST_RELEASE_TESTING_STATUS,
            "integration_run": Permission.RUN_INTEGRATION_TESTS,
            "integration_status": Permission.GET_INTEGRATION_TEST_STATUS,
        },
    ),
    "Specification": PermissionConfig(
        domain_name="Specification",
        base_permission=Permission.VIEW_SPECIFICATION,
        scopes_prefix="spec",
        description="Specification operations",
        special_permissions={
            "read": Permission.VIEW_SPECIFICATION,
            "write": Permission.EDIT_SPECIFICATION,
            "create": Permission.CREATE_SPECIFICATION,
            "delete": Permission.DELETE_SPECIFICATION,
            "manage": Permission.MANAGE_SPECIFICATION,
            "approve": Permission.APPROVE_SPECIFICATION,
            "generate_doc": Permission.GENERATE_DOCUMENTATION,
            "generate_spec": Permission.GENERATE_SPECIFICATION_DOCUMENT,
            "view_requirements": Permission.VIEW_SPECIFICATION_REQUIREMENTS,
        },
    ),
    "Comment": PermissionConfig(
        domain_name="Comment",
        base_permission=Permission.VIEW_COMMENT,
        scopes_prefix="comment",
        description="Comment operations",
        special_permissions={
            "read": Permission.VIEW_COMMENT,
            "write": Permission.CREATE_COMMENT,
            "create": Permission.CREATE_COMMENT,
            "edit": Permission.EDIT_COMMENT,
            "delete": Permission.DELETE_COMMENT,
            "moderate": Permission.MODERATE_COMMENTS,
            "view_requirement": Permission.VIEW_REQUIREMENT_COMMENTS,
            "create_requirement": Permission.CREATE_REQUIREMENT_COMMENT,
            "view_recent": Permission.VIEW_RECENT_COMMENTS,
            "view_stats": Permission.VIEW_COMMENTS_STATISTICS,
        },
    ),
    "Relationship": PermissionConfig(
        domain_name="Relationship",
        base_permission=Permission.VIEW_RELATIONSHIP,
        scopes_prefix="relationship",
        description="Relationship operations",
        special_permissions={
            "read": Permission.VIEW_RELATIONSHIP,
            "write": Permission.CREATE_RELATIONSHIP,
            "create": Permission.CREATE_RELATIONSHIP,
            "edit": Permission.EDIT_RELATIONSHIP,
            "delete": Permission.DELETE_RELATIONSHIP,
            "view_requirement": Permission.VIEW_REQUIREMENT_RELATIONSHIPS,
            "create_requirement": Permission.CREATE_REQUIREMENT_RELATIONSHIP,
            "view_dependencies": Permission.VIEW_REQUIREMENT_DEPENDENCIES,
            "view_dependents": Permission.VIEW_REQUIREMENT_DEPENDENTS,
            "view_trace": Permission.VIEW_REQUIREMENT_TRACE_MATRIX,
        },
    ),
    "RequirementType": PermissionConfig(
        domain_name="RequirementType",
        base_permission=Permission.VIEW_REQUIREMENT_TYPES,
        scopes_prefix="requirement_type",
        description="Requirement type operations",
        special_permissions={
            "read": Permission.VIEW_REQUIREMENT_TYPES,
            "create": Permission.CREATE_REQUIREMENT_TYPE,
            "edit": Permission.EDIT_REQUIREMENT_TYPE,
            "delete": Permission.DELETE_REQUIREMENT_TYPE,
        },
    ),
    "RequirementPriority": PermissionConfig(
        domain_name="RequirementPriority",
        base_permission=Permission.VIEW_REQUIREMENT_PRIORITIES,
        scopes_prefix="requirement_priority",
        description="Requirement priority operations",
        special_permissions={
            "read": Permission.VIEW_REQUIREMENT_PRIORITIES,
            "create": Permission.CREATE_REQUIREMENT_PRIORITY,
            "edit": Permission.EDIT_REQUIREMENT_PRIORITY,
            "delete": Permission.DELETE_REQUIREMENT_PRIORITY,
        },
    ),
    "RequirementStatus": PermissionConfig(
        domain_name="RequirementStatus",
        base_permission=Permission.VIEW_REQUIREMENT_STATUSES,
        scopes_prefix="requirement_status",
        description="Requirement status operations",
        special_permissions={
            "read": Permission.VIEW_REQUIREMENT_STATUSES,
            "create": Permission.CREATE_REQUIREMENT_STATUS,
            "edit": Permission.EDIT_REQUIREMENT_STATUS,
            "delete": Permission.DELETE_REQUIREMENT_STATUS,
        },
    ),
    "RelationshipType": PermissionConfig(
        domain_name="RelationshipType",
        base_permission=Permission.VIEW_RELATIONSHIP_TYPES,
        scopes_prefix="relationship_type",
        description="Relationship type operations",
        special_permissions={
            "read": Permission.VIEW_RELATIONSHIP_TYPES,
            "create": Permission.CREATE_RELATIONSHIP_TYPE,
            "edit": Permission.EDIT_RELATIONSHIP_TYPE,
            "delete": Permission.DELETE_RELATIONSHIP_TYPE,
        },
    ),
    "Admin": PermissionConfig(
        domain_name="Admin",
        base_permission=Permission.VIEW_SYSTEM_INFO,
        scopes_prefix="admin",
        description="Administrative operations",
        special_permissions={
            "read": Permission.VIEW_SYSTEM_INFO,
            "system": Permission.MANAGE_SYSTEM_SETTINGS,
            "users": Permission.VIEW_USERS,
            "health": Permission.VIEW_HEALTH_CHECK,
            "metrics": Permission.VIEW_METRICS,
            "users_stats": Permission.VIEW_USERS_STATISTICS,
            "projects_stats": Permission.VIEW_PROJECTS_STATISTICS,
            "backup": Permission.CREATE_BACKUP,
            "view_backups": Permission.VIEW_BACKUPS,
            "settings": Permission.UPDATE_SYSTEM_SETTINGS,
            "audit": Permission.VIEW_AUDIT_LOG,
            "sessions": Permission.REVOKE_SESSIONS,
            "revoke": Permission.REVOKE_SESSIONS,
        },
    ),
    "Company": PermissionConfig(
        domain_name="Company",
        base_permission=Permission.VIEW_COMPANY_SETTINGS,
        scopes_prefix="company",
        description="Company management operations",
        special_permissions={
            "read": Permission.VIEW_COMPANY_SETTINGS,
            "write": Permission.MANAGE_COMPANY_SETTINGS,
            "manage": Permission.MANAGE_COMPANY_SETTINGS,
            "users": Permission.MANAGE_COMPANY_USERS,
            "billing": Permission.MANAGE_COMPANY_BILLING,
            "subscription": Permission.MANAGE_COMPANY_SUBSCRIPTION,
            "search": Permission.SEARCH_COMPANY,
            "analytics": Permission.VIEW_COMPANY_ANALYTICS,
            "export": Permission.EXPORT_COMPANY_DATA,
        },
    ),
    "Department": PermissionConfig(
        domain_name="Department",
        base_permission=Permission.VIEW_DEPARTMENT,
        scopes_prefix="department",
        description="Department management operations",
        special_permissions={
            "read": Permission.VIEW_DEPARTMENT,
            "write": Permission.MANAGE_DEPARTMENT,
            "delete": Permission.DELETE_DEPARTMENT,
            "users": Permission.MANAGE_DEPARTMENT_USERS,
            "budget": Permission.MANAGE_DEPARTMENT_BUDGET,
            "analytics": Permission.VIEW_DEPARTMENT_ANALYTICS,
        },
    ),
    "Team": PermissionConfig(
        domain_name="Team",
        base_permission=Permission.VIEW_TEAM,
        scopes_prefix="team",
        description="Team management operations",
        special_permissions={
            "read": Permission.VIEW_TEAM,
            "write": Permission.MANAGE_TEAM,
            "delete": Permission.DELETE_TEAM,
            "members": Permission.MANAGE_TEAM_MEMBERS,
            "roles": Permission.ASSIGN_TEAM_ROLES,
            "performance": Permission.VIEW_TEAM_PERFORMANCE,
        },
    ),
    "Dashboard": PermissionConfig(
        domain_name="Dashboard",
        base_permission=Permission.VIEW_DASHBOARD_OVERVIEW,
        scopes_prefix="dashboard",
        description="Dashboard operations",
        special_permissions={
            "read": Permission.VIEW_DASHBOARD_OVERVIEW,
            "stats": Permission.VIEW_DASHBOARD_STATS,
            "overview": Permission.VIEW_DASHBOARD_OVERVIEW,
            "projects": Permission.VIEW_MY_PROJECTS,
            "requirements": Permission.VIEW_MY_REQUIREMENTS,
            "activity": Permission.VIEW_MY_ACTIVITY,
            "notifications": Permission.VIEW_MY_NOTIFICATIONS,
            "recent_activity": Permission.VIEW_RECENT_DASHBOARD_ACTIVITY,
            "projects_stats": Permission.VIEW_DASHBOARD_PROJECTS_STATS,
            "recent_projects": Permission.VIEW_RECENT_PROJECTS_DASHBOARD,
            "requirements_stats": Permission.VIEW_DASHBOARD_REQUIREMENTS_STATS,
            "recent_requirements": Permission.VIEW_RECENT_REQUIREMENTS_DASHBOARD,
            "health": Permission.VIEW_DASHBOARD_HEALTH,
            "metrics": Permission.VIEW_DASHBOARD_METRICS,
            "search": Permission.SEARCH_DASHBOARD,
            "filter": Permission.FILTER_DASHBOARD,
            "export_stats": Permission.EXPORT_DASHBOARD_STATS,
            "export_activity": Permission.EXPORT_DASHBOARD_ACTIVITY,
            "create_activity": Permission.CREATE_ACTIVITY_RECORD,
            "update_preferences": Permission.UPDATE_USER_PREFERENCES,
            "create_notification": Permission.CREATE_NOTIFICATION,
            "mark_read": Permission.MARK_NOTIFICATION_READ,
        },
    ),
    "Reports": PermissionConfig(
        domain_name="Reports",
        base_permission=Permission.VIEW_REPORTS,
        scopes_prefix="reports",
        description="Reports operations",
        special_permissions={
            "read": Permission.VIEW_REPORTS,
            "create": Permission.CREATE_REPORTS,
            "export": Permission.EXPORT_REPORTS,
            "analytics": Permission.VIEW_ANALYTICS,
            "generate": Permission.GENERATE_REPORTS,
            "quality": Permission.VIEW_QUALITY_METRICS,
            "advanced": Permission.VIEW_ADVANCED_ANALYTICS,
        },
    ),
    "Integration": PermissionConfig(
        domain_name="Integration",
        base_permission=Permission.USE_API,
        scopes_prefix="integration",
        description="Integration operations",
        special_permissions={
            "api": Permission.USE_API,
            "manage": Permission.MANAGE_INTEGRATIONS,
            "logs": Permission.VIEW_API_LOGS,
            "keys": Permission.CREATE_API_KEYS,
        },
    ),
    "Role": PermissionConfig(
        domain_name="Role",
        base_permission=Permission.VIEW_ROLES,
        scopes_prefix="role",
        description="Role management operations",
        special_permissions={
            "read": Permission.VIEW_ROLES,
            "create": Permission.CREATE_ROLE,
            "edit": Permission.EDIT_ROLE,
            "delete": Permission.DELETE_ROLE,
            "assign": Permission.ASSIGN_ROLE,
        },
    ),
}


def get_domain_config(domain_name: str) -> PermissionConfig:
    """Получить конфигурацию домена."""
    return DOMAIN_CONFIGS.get(
        domain_name,
        PermissionConfig(
            domain_name=domain_name,
            base_permission=Permission.USE_API,
            scopes_prefix=domain_name.lower(),
            description=f"{domain_name} operations",
        ),
    )

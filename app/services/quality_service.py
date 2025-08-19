"""
Quality Service - базовый сервис для всех операций качества.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.test_case import TestCase, TestPlan, TestExecution
from app.models.test_result import TestResult, TestStatus
from app.models.specification import Specification, SpecificationStatus
from app.models.requirement import Requirement
from app.utils.logger import logger
from .base import BaseService


class QualityService(BaseService):
    """
    Базовый сервис для операций качества.
    """

    def get_service_name(self) -> str:
        return "QualityService"

    async def get_quality_dashboard(
        self,
        db: AsyncSession,
        current_user: User,
        project_id: Optional[int] = None,
        time_period: int = 30,
    ) -> Dict[str, Any]:
        """Получить данные дашборда качества."""
        try:
            self._log_operation(
                "get_quality_dashboard",
                {"user_id": current_user.id, "project_id": project_id},
            )

            # Получаем статистику по спецификациям
            specs_query = select(
                func.count(Specification.id).label("total"),
                func.sum(
                    func.case(
                        (Specification.status == SpecificationStatus.IN_REVIEW, 1),
                        else_=0,
                    )
                ).label("in_review"),
                func.sum(
                    func.case(
                        (Specification.status == SpecificationStatus.APPROVED, 1),
                        else_=0,
                    )
                ).label("approved"),
                func.sum(
                    func.case(
                        (Specification.status == SpecificationStatus.REJECTED, 1),
                        else_=0,
                    )
                ).label("rejected"),
            )
            if project_id:
                specs_query = specs_query.where(Specification.project_id == project_id)

            specs_result = await db.execute(specs_query)
            specs_stats = specs_result.first()

            # Получаем статистику по тестовым случаям
            test_cases_query = select(func.count(TestCase.id).label("total"))
            if project_id:
                test_cases_query = test_cases_query.where(
                    TestCase.project_id == project_id
                )

            test_cases_result = await db.execute(test_cases_query)
            total_test_cases = test_cases_result.scalar() or 0

            # Получаем статистику по результатам тестов
            test_results_query = select(
                func.sum(
                    func.case((TestResult.status == TestStatus.PASSED, 1), else_=0)
                ).label("passed"),
                func.sum(
                    func.case((TestResult.status == TestStatus.FAILED, 1), else_=0)
                ).label("failed"),
                func.sum(
                    func.case((TestResult.status == TestStatus.NOT_STARTED, 1), else_=0)
                ).label("pending"),
            )
            if project_id:
                # Фильтруем через требования проекта
                test_results_query = test_results_query.join(
                    Requirement, TestResult.requirement_id == Requirement.id
                ).where(Requirement.project_id == project_id)

            test_results_result = await db.execute(test_results_query)
            test_results_stats = test_results_result.first()

            # Получаем статистику по планам тестирования
            test_plans_query = select(
                func.count(TestPlan.id).label("total"),
                func.sum(func.case((TestPlan.status == "active", 1), else_=0)).label(
                    "active"
                ),
                func.sum(func.case((TestPlan.status == "completed", 1), else_=0)).label(
                    "completed"
                ),
            )
            if project_id:
                test_plans_query = test_plans_query.where(
                    TestPlan.project_id == project_id
                )

            test_plans_result = await db.execute(test_plans_query)
            test_plans_stats = test_plans_result.first()

            # Вычисляем метрики
            total_tests = (
                test_results_stats.passed
                + test_results_stats.failed
                + test_results_stats.pending
                if test_results_stats
                else 0
            )
            test_coverage = (
                total_test_cases
                / max(1, await self._get_total_requirements(db, project_id))
            ) * 100
            pass_rate = (
                (test_results_stats.passed / max(1, total_tests)) * 100
                if test_results_stats
                else 0
            )
            review_completion_rate = (
                (
                    (specs_stats.approved + specs_stats.rejected)
                    / max(1, specs_stats.total)
                )
                * 100
                if specs_stats
                else 0
            )

            dashboard_data = {
                "specifications": {
                    "total": specs_stats.total or 0,
                    "in_review": specs_stats.in_review or 0,
                    "approved": specs_stats.approved or 0,
                    "rejected": specs_stats.rejected or 0,
                },
                "test_cases": {
                    "total": total_test_cases,
                    "passed": test_results_stats.passed or 0,
                    "failed": test_results_stats.failed or 0,
                    "pending": test_results_stats.pending or 0,
                },
                "test_plans": {
                    "total": test_plans_stats.total or 0,
                    "active": test_plans_stats.active or 0,
                    "completed": test_plans_stats.completed or 0,
                },
                "reports": {
                    "generated_today": 0,  # TODO: Implement when reports tracking is available
                    "total_this_month": 0,
                },
                "metrics": {
                    "test_coverage": round(test_coverage, 2),
                    "defect_density": (
                        round(
                            test_results_stats.failed / max(1, total_test_cases) * 100,
                            2,
                        )
                        if test_results_stats
                        else 0.0
                    ),
                    "review_completion_rate": round(review_completion_rate, 2),
                },
            }

            logger.info(f"Quality dashboard data retrieved for user {current_user.id}")
            return dashboard_data

        except Exception as e:
            raise self._handle_error(e, "get_quality_dashboard")

    async def _get_total_requirements(
        self, db: AsyncSession, project_id: Optional[int] = None
    ) -> int:
        """Вспомогательный метод для получения общего количества требований."""
        requirements_query = select(func.count(Requirement.id))
        if project_id:
            requirements_query = requirements_query.where(
                Requirement.project_id == project_id
            )

        result = await db.execute(requirements_query)
        return result.scalar() or 0

    async def get_quality_metrics(
        self,
        db: AsyncSession,
        current_user: User,
        project_id: Optional[int] = None,
        metric_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Получить метрики качества."""
        try:
            self._log_operation(
                "get_quality_metrics",
                {
                    "user_id": current_user.id,
                    "project_id": project_id,
                    "metric_type": metric_type,
                },
            )

            # Получаем тестовые метрики
            test_metrics = await self._get_test_metrics(db, project_id)

            # Получаем метрики дефектов
            defect_metrics = await self._get_defect_metrics(db, project_id)

            # Получаем метрики ревью
            review_metrics = await self._get_review_metrics(db, project_id)

            # Получаем метрики соответствия
            compliance_metrics = await self._get_compliance_metrics(db, project_id)

            metrics = {
                "test_metrics": test_metrics,
                "defect_metrics": defect_metrics,
                "review_metrics": review_metrics,
                "compliance_metrics": compliance_metrics,
            }

            # Фильтруем по типу метрики, если указан
            if metric_type and metric_type in metrics:
                metrics = {metric_type: metrics[metric_type]}

            logger.info(f"Quality metrics retrieved for user {current_user.id}")
            return metrics

        except Exception as e:
            raise self._handle_error(e, "get_quality_metrics")

    async def _get_test_metrics(self, db: AsyncSession, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить тестовые метрики."""
        # Общее количество тестов
        total_tests_query = select(func.count(TestCase.id))
        if project_id:
            total_tests_query = total_tests_query.where(TestCase.project_id == project_id)
        
        total_tests_result = await db.execute(total_tests_query)
        total_tests = total_tests_result.scalar() or 0

        # Автоматизированные тесты
        automated_tests_query = select(func.count(TestCase.id)).where(TestCase.is_automated == True)
        if project_id:
            automated_tests_query = automated_tests_query.where(TestCase.project_id == project_id)
        
        automated_tests_result = await db.execute(automated_tests_query)
        automated_tests = automated_tests_result.scalar() or 0

        # Результаты тестов
        test_results_query = select(
            func.count(TestResult.id).label("total_executions"),
            func.sum(func.case((TestResult.status == TestStatus.PASSED, 1), else_=0)).label("passed"),
            func.sum(func.case((TestResult.status == TestStatus.FAILED, 1), else_=0)).label("failed")
        )
        if project_id:
            test_results_query = test_results_query.join(
                Requirement, TestResult.requirement_id == Requirement.id
            ).where(Requirement.project_id == project_id)

        test_results_result = await db.execute(test_results_query)
        test_results = test_results_result.first()

        total_executions = test_results.total_executions or 0
        passed_tests = test_results.passed or 0
        
        return {
            "total_tests": total_tests,
            "test_execution_rate": round((total_executions / max(1, total_tests)) * 100, 2),
            "test_pass_rate": round((passed_tests / max(1, total_executions)) * 100, 2),
            "automated_test_coverage": round((automated_tests / max(1, total_tests)) * 100, 2)
        }

    async def _get_defect_metrics(self, db: AsyncSession, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить метрики дефектов."""
        # Считаем проваленные тесты как дефекты
        defects_query = select(
            func.count(TestResult.id).label("total_defects"),
            func.sum(func.case((TestResult.status == TestStatus.FAILED, 1), else_=0)).label("open_defects")
        )
        if project_id:
            defects_query = defects_query.join(
                Requirement, TestResult.requirement_id == Requirement.id
            ).where(Requirement.project_id == project_id)

        defects_result = await db.execute(defects_query)
        defects = defects_result.first()

        total_test_cases = await self._get_total_test_cases(db, project_id)
        
        return {
            "total_defects": defects.open_defects or 0,
            "open_defects": defects.open_defects or 0,
            "defect_resolution_time": 0.0,  # TODO: Implement when defect tracking is available
            "defect_density": round((defects.open_defects or 0) / max(1, total_test_cases) * 1000, 2)
        }

    async def _get_review_metrics(self, db: AsyncSession, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить метрики ревью."""
        specs_query = select(
            func.count(Specification.id).label("total_specs"),
            func.sum(func.case((Specification.status == SpecificationStatus.APPROVED, 1), else_=0)).label("approved"),
            func.sum(func.case((Specification.status.in_([SpecificationStatus.APPROVED, SpecificationStatus.REJECTED]), 1), else_=0)).label("reviewed")
        )
        if project_id:
            specs_query = specs_query.where(Specification.project_id == project_id)

        specs_result = await db.execute(specs_query)
        specs = specs_result.first()

        total_specs = specs.total_specs or 0
        reviewed_specs = specs.reviewed or 0
        approved_specs = specs.approved or 0

        return {
            "specifications_reviewed": reviewed_specs,
            "review_completion_time": 0.0,  # TODO: Implement when review time tracking is available
            "review_approval_rate": round((approved_specs / max(1, reviewed_specs)) * 100, 2)
        }

    async def _get_compliance_metrics(self, db: AsyncSession, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить метрики соответствия."""
        total_requirements = await self._get_total_requirements(db, project_id)
        
        # Покрытие требований тестами
        requirements_with_tests_query = select(func.count(func.distinct(TestCase.requirement_id))).where(
            TestCase.requirement_id.isnot(None)
        )
        if project_id:
            requirements_with_tests_query = requirements_with_tests_query.where(TestCase.project_id == project_id)

        requirements_with_tests_result = await db.execute(requirements_with_tests_query)
        requirements_with_tests = requirements_with_tests_result.scalar() or 0

        # Для простоты используем приблизительную оценку для документации
        documentation_completeness = 85.0  # Placeholder

        return {
            "requirements_coverage": round((requirements_with_tests / max(1, total_requirements)) * 100, 2),
            "traceability_completeness": round((requirements_with_tests / max(1, total_requirements)) * 100, 2),
            "documentation_completeness": documentation_completeness
        }

    async def _get_total_test_cases(self, db: AsyncSession, project_id: Optional[int] = None) -> int:
        """Получить общее количество тестовых случаев."""
        test_cases_query = select(func.count(TestCase.id))
        if project_id:
            test_cases_query = test_cases_query.where(TestCase.project_id == project_id)
        
        result = await db.execute(test_cases_query)
        return result.scalar() or 0

    async def check_quality_permissions(
        self,
        db: AsyncSession,
        current_user: User,
        action: str,
        resource_id: Optional[int] = None,
    ) -> bool:
        """Проверить разрешения для операций качества."""
        try:
            # Базовые разрешения для разных действий
            permission_map = {
                "read": ["viewer", "tester", "analyst", "manager", "admin"],
                "create": ["tester", "analyst", "manager", "admin"],
                "update": ["tester", "analyst", "manager", "admin"],
                "delete": ["manager", "admin"],
                "execute": ["tester", "analyst", "manager", "admin"],
                "approve": ["manager", "admin"],
                "review": ["analyst", "manager", "admin"]
            }

            # Получаем роли пользователя
            user_roles = []
            if hasattr(current_user, 'roles') and current_user.roles:
                user_roles = [role.name.lower() for role in current_user.roles]
            
            # Если нет ролей, предоставляем базовый доступ на чтение
            if not user_roles:
                return action in ["read"]

            # Проверяем разрешения
            required_roles = permission_map.get(action, [])
            has_permission = any(role in required_roles for role in user_roles)

            logger.info(f"Permission check for action '{action}': {has_permission} (user roles: {user_roles})")
            return has_permission

        except Exception as e:
            logger.error(f"Error checking quality permissions: {e}")
            return False


from .base import ServiceFactory

ServiceFactory.register_service("quality_service", QualityService)
# Глобальный экземпляр сервиса
quality_service = QualityService()

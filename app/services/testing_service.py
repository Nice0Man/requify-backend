"""
Testing Service - сервис для управления тестированием.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime

from .base import BaseService
from app.models.user import User
from app.models.test_case import (
    TestCase,
    TestCaseStatus,
    TestPlan,
    TestExecution,
    ExecutionStatus,
)
from app.models.test_result import TestResult, TestStatus
from app.crud.test_case import test_case as crud_test_case
from app.crud.test_result import test_result as crud_test_result
from app.api.v1.domains.quality.testing.schemas import (
    TestCaseCreateRequest,
    TestCaseUpdateRequest,
    TestResultCreateRequest,
    TestResultUpdateRequest,
)
from app.utils.logger import logger


class TestingService(BaseService):
    """
    Сервис для операций тестирования.
    """

    def get_service_name(self) -> str:
        return "TestingService"

    # === Test Cases ===

    async def create_test_case(
        self, db: AsyncSession, test_case_data: Dict[str, Any], current_user: User
    ) -> Dict[str, Any]:
        """Создать тест-кейс."""
        try:
            self._log_operation(
                "create_test_case",
                {"user_id": current_user.id, "name": test_case_data.get("name")},
            )

            # Подготавливаем данные для создания тестового случая
            create_data = TestCaseCreateRequest(
                name=test_case_data.get("name", ""),
                description=test_case_data.get("description"),
                type=test_case_data.get("type", "functional"),
                priority=test_case_data.get("priority", "medium"),
                status=test_case_data.get("status", "draft"),
                preconditions=test_case_data.get("preconditions"),
                test_steps=test_case_data.get("test_steps"),
                expected_result=test_case_data.get("expected_result"),
                test_data=test_case_data.get("test_data"),
                tags=test_case_data.get("tags"),
                estimated_duration=test_case_data.get("estimated_duration"),
                is_automated=test_case_data.get("is_automated", False),
                automation_script=test_case_data.get("automation_script"),
                project_id=test_case_data.get("project_id"),
                requirement_id=test_case_data.get("requirement_id"),
                test_plan_id=test_case_data.get("test_plan_id"),
                author_id=current_user.id,
                external_id=test_case_data.get("external_id"),
                parent_id=test_case_data.get("parent_id"),
                version=test_case_data.get("version", "1.0.0"),
            )

            # Создаем тестовый случай через CRUD
            test_case = await crud_test_case.create(db, obj_in=create_data)

            logger.info(f"Test case created: {test_case.id}")

            return {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "type": test_case.type.value,
                "status": test_case.status.value,
                "priority": test_case.priority.value,
                "project_id": test_case.project_id,
                "requirement_id": test_case.requirement_id,
                "test_plan_id": test_case.test_plan_id,
                "author_id": test_case.author_id,
                "created_at": test_case.created_at,
                "updated_at": test_case.updated_at,
            }

        except Exception as e:
            raise self._handle_error(e, "create_test_case")

    async def get_test_cases(
        self,
        db: AsyncSession,
        current_user: User,
        project_id: Optional[int] = None,
        requirement_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """Получить список тест-кейсов."""
        try:
            self._log_operation(
                "get_test_cases", {"user_id": current_user.id, "project_id": project_id}
            )

            skip = (page - 1) * size

            # Получаем тестовые случаи в зависимости от фильтров
            if requirement_id:
                test_cases = await crud_test_case.get_by_requirement(
                    db, requirement_id=requirement_id, skip=skip, limit=size
                )
            elif project_id:
                test_cases = await crud_test_case.get_by_project(
                    db, project_id=project_id, status=status, skip=skip, limit=size
                )
            else:
                test_cases = await crud_test_case.get_multi(db, skip=skip, limit=size)

            # Преобразуем в словари для ответа
            test_cases_data = []
            for tc in test_cases:
                test_cases_data.append(
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "description": tc.description,
                        "type": tc.type.value,
                        "status": tc.status.value,
                        "priority": tc.priority.value,
                        "project_id": tc.project_id,
                        "requirement_id": tc.requirement_id,
                        "test_plan_id": tc.test_plan_id,
                        "author_id": tc.author_id,
                        "is_automated": tc.is_automated,
                        "is_active": tc.is_active,
                        "estimated_duration": tc.estimated_duration,
                        "tags": tc.tags,
                        "created_at": tc.created_at,
                        "updated_at": tc.updated_at,
                    }
                )

            # Подсчитываем общее количество
            total_query = select(func.count(TestCase.id))
            if requirement_id:
                total_query = total_query.where(
                    TestCase.requirement_id == requirement_id
                )
            elif project_id:
                total_query = total_query.where(TestCase.project_id == project_id)
                if status:
                    total_query = total_query.where(TestCase.status == status)

            total_result = await db.execute(total_query)
            total = total_result.scalar() or 0

            return {
                "test_cases": test_cases_data,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size if total > 0 else 0,
            }

        except Exception as e:
            raise self._handle_error(e, "get_test_cases")

    async def get_test_case(
        self, db: AsyncSession, test_case_id: int, current_user: User
    ) -> Optional[Dict[str, Any]]:
        """Получить тест-кейс по ID."""
        try:
            self._log_operation(
                "get_test_case",
                {"user_id": current_user.id, "test_case_id": test_case_id},
            )

            test_case = await crud_test_case.get(db, id=test_case_id)
            if not test_case:
                return None

            return {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "type": test_case.type.value,
                "status": test_case.status.value,
                "priority": test_case.priority.value,
                "preconditions": test_case.preconditions,
                "test_steps": test_case.test_steps,
                "expected_result": test_case.expected_result,
                "test_data": test_case.test_data,
                "tags": test_case.tags,
                "estimated_duration": test_case.estimated_duration,
                "is_automated": test_case.is_automated,
                "automation_script": test_case.automation_script,
                "is_active": test_case.is_active,
                "project_id": test_case.project_id,
                "requirement_id": test_case.requirement_id,
                "test_plan_id": test_case.test_plan_id,
                "author_id": test_case.author_id,
                "external_id": test_case.external_id,
                "version": test_case.version,
                "parent_id": test_case.parent_id,
                "created_at": test_case.created_at,
                "updated_at": test_case.updated_at,
                "is_ready_for_execution": test_case.is_ready_for_execution,
                "executions_count": test_case.executions_count,
            }

        except Exception as e:
            raise self._handle_error(e, "get_test_case")

    async def update_test_case(
        self,
        db: AsyncSession,
        test_case_id: int,
        update_data: Dict[str, Any],
        current_user: User,
    ) -> Optional[Dict[str, Any]]:
        """Обновить тест-кейс."""
        try:
            self._log_operation(
                "update_test_case",
                {"user_id": current_user.id, "test_case_id": test_case_id},
            )

            # Получаем существующий тестовый случай
            existing_test_case = await crud_test_case.get(db, id=test_case_id)
            if not existing_test_case:
                return None

            # Создаем объект для обновления
            update_obj = TestCaseUpdateRequest(**update_data)

            # Обновляем тестовый случай
            updated_test_case = await crud_test_case.update(
                db, db_obj=existing_test_case, obj_in=update_obj
            )

            logger.info(f"Test case updated: {updated_test_case.id}")

            return {
                "id": updated_test_case.id,
                "name": updated_test_case.name,
                "description": updated_test_case.description,
                "type": updated_test_case.type.value,
                "status": updated_test_case.status.value,
                "priority": updated_test_case.priority.value,
                "project_id": updated_test_case.project_id,
                "requirement_id": updated_test_case.requirement_id,
                "test_plan_id": updated_test_case.test_plan_id,
                "author_id": updated_test_case.author_id,
                "created_at": updated_test_case.created_at,
                "updated_at": updated_test_case.updated_at,
            }

        except Exception as e:
            raise self._handle_error(e, "update_test_case")

    async def delete_test_case(
        self, db: AsyncSession, test_case_id: int, current_user: User
    ) -> bool:
        """Удалить тест-кейс."""
        try:
            self._log_operation(
                "delete_test_case",
                {"user_id": current_user.id, "test_case_id": test_case_id},
            )

            # Проверяем существование тестового случая
            test_case = await crud_test_case.get(db, id=test_case_id)
            if not test_case:
                return False

            # Удаляем тестовый случай
            await crud_test_case.remove(db, id=test_case_id)

            logger.info(f"Test case deleted: {test_case_id}")
            return True

        except Exception as e:
            raise self._handle_error(e, "delete_test_case")

    # === Test Results ===

    async def create_test_result(
        self, db: AsyncSession, result_data: Dict[str, Any], current_user: User
    ) -> Dict[str, Any]:
        """Создать результат теста."""
        try:
            self._log_operation(
                "create_test_result",
                {
                    "user_id": current_user.id,
                    "requirement_id": result_data.get("requirement_id"),
                },
            )

            # Подготавливаем данные для создания результата теста
            create_data = TestResultCreateRequest(
                status=result_data.get("status", "not_started"),
                notes=result_data.get("notes"),
                requirement_id=result_data["requirement_id"],
                tester_id=current_user.id,
                external_id=result_data.get("external_id"),
                started_at=result_data.get("started_at"),
                completed_at=result_data.get("completed_at"),
            )

            # Создаем результат теста через CRUD
            test_result = await crud_test_result.create(db, obj_in=create_data)

            logger.info(f"Test result created: {test_result.id}")

            return {
                "id": test_result.id,
                "status": test_result.status.value,
                "notes": test_result.notes,
                "requirement_id": test_result.requirement_id,
                "tester_id": test_result.tester_id,
                "external_id": test_result.external_id,
                "started_at": test_result.started_at,
                "completed_at": test_result.completed_at,
                "created_at": test_result.created_at,
                "updated_at": test_result.updated_at,
            }

        except Exception as e:
            raise self._handle_error(e, "create_test_result")

    async def get_test_results(
        self,
        db: AsyncSession,
        current_user: User,
        requirement_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """Получить список результатов тестов."""
        try:
            self._log_operation(
                "get_test_results",
                {"user_id": current_user.id, "requirement_id": requirement_id},
            )

            skip = (page - 1) * size

            # Получаем результаты тестов в зависимости от фильтров
            if requirement_id:
                test_results = await crud_test_result.get_by_requirement(
                    db, requirement_id=requirement_id, skip=skip, limit=size
                )
            elif status:
                test_results = await crud_test_result.get_by_status(
                    db, status=status, skip=skip, limit=size
                )
            else:
                test_results = await crud_test_result.get_multi(
                    db, skip=skip, limit=size
                )

            # Преобразуем в словари для ответа
            results_data = []
            for tr in test_results:
                results_data.append(
                    {
                        "id": tr.id,
                        "status": tr.status.value,
                        "notes": tr.notes,
                        "requirement_id": tr.requirement_id,
                        "tester_id": tr.tester_id,
                        "external_id": tr.external_id,
                        "started_at": tr.started_at,
                        "completed_at": tr.completed_at,
                        "created_at": tr.created_at,
                        "updated_at": tr.updated_at,
                    }
                )

            # Подсчитываем общее количество
            total_query = select(func.count(TestResult.id))
            if requirement_id:
                total_query = total_query.where(
                    TestResult.requirement_id == requirement_id
                )
            elif status:
                total_query = total_query.where(TestResult.status == status)

            total_result = await db.execute(total_query)
            total = total_result.scalar() or 0

            return {
                "test_results": results_data,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size if total > 0 else 0,
            }

        except Exception as e:
            raise self._handle_error(e, "get_test_results")

    # === Test Plans ===

    async def create_test_plan(
        self, db: AsyncSession, plan_data: Dict[str, Any], current_user: User
    ) -> Dict[str, Any]:
        """Создать тест-план."""
        try:
            self._log_operation(
                "create_test_plan",
                {"user_id": current_user.id, "name": plan_data.get("name")},
            )

            # Создаем новый план тестирования
            test_plan = TestPlan(
                name=plan_data.get("name", ""),
                description=plan_data.get("description"),
                status=plan_data.get("status", "draft"),
                project_id=plan_data["project_id"],
                author_id=current_user.id,
                planned_start_date=plan_data.get("planned_start_date"),
                planned_end_date=plan_data.get("planned_end_date"),
            )

            db.add(test_plan)
            await db.commit()
            await db.refresh(test_plan)

            logger.info(f"Test plan created: {test_plan.id}")

            return {
                "id": test_plan.id,
                "name": test_plan.name,
                "description": test_plan.description,
                "status": test_plan.status,
                "project_id": test_plan.project_id,
                "author_id": test_plan.author_id,
                "planned_start_date": test_plan.planned_start_date,
                "planned_end_date": test_plan.planned_end_date,
                "actual_start_date": test_plan.actual_start_date,
                "actual_end_date": test_plan.actual_end_date,
                "created_at": test_plan.created_at,
                "updated_at": test_plan.updated_at,
            }

        except Exception as e:
            raise self._handle_error(e, "create_test_plan")

    async def get_testing_statistics(
        self,
        db: AsyncSession,
        current_user: User,
        project_id: Optional[int] = None,
        release_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Получить статистику тестирования."""
        try:
            self._log_operation(
                "get_testing_statistics",
                {"user_id": current_user.id, "project_id": project_id},
            )

            # Получаем статистику тестовых случаев
            test_case_stats = await crud_test_case.get_statistics(
                db, project_id=project_id
            )

            # Получаем статистику результатов тестов
            test_result_stats = await crud_test_result.get_test_summary(
                db, project_id=project_id
            )

            # Подсчитываем количество тест-планов
            test_plans_query = select(func.count(TestPlan.id))
            if project_id:
                test_plans_query = test_plans_query.where(
                    TestPlan.project_id == project_id
                )

            test_plans_result = await db.execute(test_plans_query)
            test_plans_count = test_plans_result.scalar() or 0

            # Подсчитываем покрытие требований тестами
            # Количество требований, для которых есть тестовые случаи
            from app.models.requirement import Requirement

            requirements_with_tests_query = select(
                func.count(func.distinct(TestCase.requirement_id))
            ).where(TestCase.requirement_id.isnot(None))
            if project_id:
                requirements_with_tests_query = requirements_with_tests_query.where(
                    TestCase.project_id == project_id
                )

            requirements_with_tests_result = await db.execute(
                requirements_with_tests_query
            )
            requirements_with_tests = requirements_with_tests_result.scalar() or 0

            # Общее количество требований в проекте
            total_requirements_query = select(func.count(Requirement.id))
            if project_id:
                total_requirements_query = total_requirements_query.where(
                    Requirement.project_id == project_id
                )

            total_requirements_result = await db.execute(total_requirements_query)
            total_requirements = total_requirements_result.scalar() or 0

            # Вычисляем покрытие требований
            requirements_coverage = (
                (requirements_with_tests / total_requirements * 100)
                if total_requirements > 0
                else 0.0
            )

            stats = {
                "test_cases": {
                    "total": test_case_stats.get("total", 0),
                    "automated": test_case_stats.get("automated_count", 0),
                    "manual": test_case_stats.get("total", 0)
                    - test_case_stats.get("automated_count", 0),
                    "by_status": test_case_stats.get("by_status", {}),
                    "by_type": test_case_stats.get("by_type", {}),
                    "by_priority": test_case_stats.get("by_priority", {}),
                    "automation_percentage": test_case_stats.get(
                        "automation_percentage", 0.0
                    ),
                },
                "test_execution": {
                    "total_runs": test_result_stats.get("total_tests", 0),
                    "passed": test_result_stats.get("passed_tests", 0),
                    "failed": test_result_stats.get("failed_tests", 0),
                    "blocked": test_result_stats.get("blocked_tests", 0),
                    "pass_rate": test_result_stats.get("pass_rate", 0.0),
                },
                "test_plans": {"total": test_plans_count},
                "coverage": {
                    "requirements_coverage": round(requirements_coverage, 2),
                    "requirements_with_tests": requirements_with_tests,
                    "total_requirements": total_requirements,
                },
            }

            logger.info(f"Testing statistics retrieved for user {current_user.id}")
            return stats

        except Exception as e:
            raise self._handle_error(e, "get_testing_statistics")


from .base import ServiceFactory

ServiceFactory.register_service("testing_service", TestingService)

# Глобальный экземпляр сервиса
testing_service = TestingService()

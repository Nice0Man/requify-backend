"""
Testing Router.

API endpoints для операций с тестированием.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.common.responses import (
    create_response,
    error_response,
    success_response,
    not_found_response,
    forbidden_response,
    unauthorized_response,
)

from typing import List, Optional
from app.api.dependencies.core.auth import get_current_user
from app.api.dependencies.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.permissions.quality import (
    require_testing_access,
    require_testing_create,
    require_testing_execute,
)
from app.models.user import User
from app.services.testing_service import testing_service

from .schemas import (
    TestCaseCreateRequest,
    TestCaseUpdateRequest,
    TestCaseResponse,
    TestCaseDetailResponse,
    TestCaseListResponse,
    TestResultCreateRequest,
    TestResultUpdateRequest,
    TestResultResponse,
    TestResultListResponse,
    TestPlanCreateRequest,
    TestPlanUpdateRequest,
    TestPlanResponse,
    TestPlanDetailResponse,
    TestPlanListResponse,
    TestCaseFilterRequest,
    TestResultFilterRequest,
    TestingStatisticsResponse,
    TestingExportRequest,
    TestingExportResponse,
)

router = APIRouter(prefix="/testing", tags=["testing"])

# === Test Case Endpoints ===


@router.post("/test-cases", response_model=TestCaseResponse)
async def create_test_case(
    request: TestCaseCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_create),
):
    """Создание нового тест-кейса."""
    try:
        test_case_data = request.model_dump()
        result = await testing_service.create_test_case(
            db=db, test_case_data=test_case_data, current_user=current_user
        )
        return success_response(data=result, message="Test case created successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to create test case: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/test-cases", response_model=TestCaseListResponse)
async def get_test_cases(
    db: AsyncSession = Depends(get_db),
    project_id: Optional[int] = None,
    requirement_id: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Получение списка тест-кейсов."""
    try:
        result = await testing_service.get_test_cases(
            db=db,
            current_user=current_user,
            project_id=project_id,
            requirement_id=requirement_id,
            page=page,
            size=size,
        )
        return success_response(data=result)
    except Exception as e:
        return error_response(
            message=f"Failed to get test cases: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/test-cases/{test_case_id}", response_model=TestCaseDetailResponse)
async def get_test_case(
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Получение детальной информации о тест-кейсе."""
    try:
        test_case = await testing_service.get_test_case(
            db=db, test_case_id=test_case_id, current_user=current_user
        )
        if not test_case:
            return not_found_response(message="Test case not found")
        return success_response(data=test_case)
    except Exception as e:
        return error_response(
            message=f"Failed to get test case: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.put("/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: int,
    request: TestCaseUpdateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Обновление тест-кейса."""
    try:
        update_data = request.model_dump(exclude_unset=True)
        result = await testing_service.update_test_case(
            db=db,
            test_case_id=test_case_id,
            update_data=update_data,
            current_user=current_user,
        )
        if not result:
            return not_found_response(message="Test case not found")
        return success_response(data=result, message="Test case updated successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to update test case: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.delete("/test-cases/{test_case_id}")
async def delete_test_case(
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Удаление тест-кейса."""
    try:
        success = await testing_service.delete_test_case(
            db=db, test_case_id=test_case_id, current_user=current_user
        )
        if not success:
            return not_found_response(message="Test case not found")
        return success_response(message="Test case deleted successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to delete test case: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# === Test Result Endpoints ===


@router.post("/test-results", response_model=TestResultResponse)
async def create_test_result(
    request: TestResultCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Создание результата выполнения теста."""
    try:
        result_data = request.model_dump()
        result = await testing_service.create_test_result(
            db=db, result_data=result_data, current_user=current_user
        )
        return success_response(data=result, message="Test result created successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to create test result: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/test-results", response_model=TestResultListResponse)
async def get_test_results(
    db: AsyncSession = Depends(get_db),
    test_case_id: Optional[int] = None,
    test_plan_id: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Получение списка результатов тестов."""
    try:
        result = await testing_service.get_test_results(
            db=db,
            current_user=current_user,
            test_case_id=test_case_id,
            page=page,
            size=size,
        )
        return success_response(data=result)
    except Exception as e:
        return error_response(
            message=f"Failed to get test results: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/test-results/{result_id}", response_model=TestResultResponse)
async def get_test_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Получение результата теста."""
    try:
        from app.crud.test_result import test_result as crud_test_result

        test_result = await crud_test_result.get(db, id=result_id)
        if not test_result:
            return not_found_response(message="Test result not found")

        result_data = {
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

        return success_response(
            data=result_data, message="Test result retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to get test result: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.put("/test-results/{result_id}", response_model=TestResultResponse)
async def update_test_result(
    result_id: int,
    request: TestResultUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Обновление результата теста."""
    try:
        from app.crud.test_result import test_result as crud_test_result

        # Проверяем существование результата теста
        existing_result = await crud_test_result.get(db, id=result_id)
        if not existing_result:
            return not_found_response(message="Test result not found")

        # Обновляем результат теста
        update_data = request.model_dump(exclude_unset=True)
        updated_result = await crud_test_result.update(
            db, db_obj=existing_result, obj_in=update_data
        )

        result_data = {
            "id": updated_result.id,
            "status": updated_result.status.value,
            "notes": updated_result.notes,
            "requirement_id": updated_result.requirement_id,
            "tester_id": updated_result.tester_id,
            "external_id": updated_result.external_id,
            "started_at": updated_result.started_at,
            "completed_at": updated_result.completed_at,
            "created_at": updated_result.created_at,
            "updated_at": updated_result.updated_at,
        }

        return success_response(
            data=result_data, message="Test result updated successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to update test result: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# === Test Plan Endpoints ===


@router.post("/test-plans", response_model=TestPlanResponse)
async def create_test_plan(
    request: TestPlanCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Создание тест-плана."""
    try:
        plan_data = request.model_dump()
        result = await testing_service.create_test_plan(
            db=db, plan_data=plan_data, current_user=current_user
        )
        return success_response(data=result, message="Test plan created successfully")
    except Exception as e:
        return error_response(
            message=f"Failed to create test plan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/test-plans", response_model=TestPlanListResponse)
async def get_test_plans(
    db: AsyncSession = Depends(get_db),
    project_id: Optional[int] = None,
    release_id: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Получение списка тест-планов."""
    try:
        from app.models.test_case import TestPlan
        from sqlalchemy import select, func

        skip = (page - 1) * size

        # Строим запрос с фильтрами
        query = select(TestPlan)
        if project_id:
            query = query.where(TestPlan.project_id == project_id)

        # Получаем планы тестирования
        query = query.offset(skip).limit(size).order_by(TestPlan.created_at.desc())
        result = await db.execute(query)
        test_plans = result.scalars().all()

        # Подсчитываем общее количество
        total_query = select(func.count(TestPlan.id))
        if project_id:
            total_query = total_query.where(TestPlan.project_id == project_id)

        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        # Форматируем данные для ответа
        plans_data = []
        for plan in test_plans:
            plans_data.append(
                {
                    "id": plan.id,
                    "name": plan.name,
                    "description": plan.description,
                    "status": plan.status,
                    "project_id": plan.project_id,
                    "author_id": plan.author_id,
                    "planned_start_date": plan.planned_start_date,
                    "planned_end_date": plan.planned_end_date,
                    "created_at": plan.created_at,
                    "updated_at": plan.updated_at,
                }
            )

        response_data = {
            "test_plans": plans_data,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if total > 0 else 0,
        }

        return success_response(
            data=response_data, message="Test plans retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to get test plans: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/test-plans/{plan_id}", response_model=TestPlanDetailResponse)
async def get_test_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Получение детальной информации о тест-плане."""
    try:
        from app.models.test_case import TestPlan
        from sqlalchemy import select

        # Получаем план тестирования
        query = select(TestPlan).where(TestPlan.id == plan_id)
        result = await db.execute(query)
        test_plan = result.scalar_one_or_none()

        if not test_plan:
            return not_found_response(message="Test plan not found")

        plan_data = {
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

        return success_response(
            data=plan_data, message="Test plan retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to get test plan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.put("/test-plans/{plan_id}", response_model=TestPlanResponse)
async def update_test_plan(
    plan_id: int,
    request: TestPlanUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Обновление тест-плана."""
    try:
        from app.models.test_case import TestPlan
        from sqlalchemy import select

        # Получаем план тестирования
        query = select(TestPlan).where(TestPlan.id == plan_id)
        result = await db.execute(query)
        test_plan = result.scalar_one_or_none()

        if not test_plan:
            return not_found_response(message="Test plan not found")

        # Обновляем поля
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(test_plan, field, value)

        await db.commit()
        await db.refresh(test_plan)

        plan_data = {
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

        return success_response(
            data=plan_data, message="Test plan updated successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to update test plan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.delete("/test-plans/{plan_id}")
async def delete_test_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Удаление тест-плана."""
    try:
        from app.models.test_case import TestPlan
        from sqlalchemy import select

        # Получаем план тестирования
        query = select(TestPlan).where(TestPlan.id == plan_id)
        result = await db.execute(query)
        test_plan = result.scalar_one_or_none()

        if not test_plan:
            return not_found_response(message="Test plan not found")

        # Удаляем план тестирования
        await db.delete(test_plan)
        await db.commit()

        return success_response(
            data={"deleted_id": plan_id}, message="Test plan deleted successfully"
        )
    except Exception as e:
        return error_response(
            message=f"Failed to delete test plan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# === Statistics and Reporting ===


@router.get("/statistics", response_model=TestingStatisticsResponse)
async def get_testing_statistics(
    db: AsyncSession = Depends(get_db),
    project_id: Optional[int] = None,
    release_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Получение статистики по тестированию."""
    try:
        stats = await testing_service.get_testing_statistics(
            db=db,
            current_user=current_user,
            project_id=project_id,
            release_id=release_id,
        )
        return success_response(data=stats)
    except Exception as e:
        return error_response(
            message=f"Failed to get testing statistics: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/export", response_model=TestingExportResponse)
async def export_testing_data(
    request: TestingExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_testing_access),
):
    """Экспорт данных тестирования."""
    try:
        from datetime import datetime
        import uuid

        # Получаем параметры экспорта
        export_data = request.model_dump()
        project_id = export_data.get("project_id")
        export_format = export_data.get("format", "xlsx")
        include_test_cases = export_data.get("include_test_cases", True)
        include_test_results = export_data.get("include_test_results", True)
        include_test_plans = export_data.get("include_test_plans", True)

        # Создаем задачу экспорта (пока что мокаем)
        export_id = str(uuid.uuid4())
        export_status = "in_progress"

        # В реальной реализации здесь бы была логика:
        # 1. Получение данных тестирования из базы
        # 2. Генерация файла в выбранном формате
        # 3. Сохранение файла и создание ссылки для скачивания

        export_data_response = {
            "export_id": export_id,
            "status": export_status,
            "format": export_format,
            "file_size": 0,
            "created_at": datetime.utcnow(),
            "download_url": None,
            "expires_at": None,
            "includes": {
                "test_cases": include_test_cases,
                "test_results": include_test_results,
                "test_plans": include_test_plans,
            },
        }

        return success_response(
            data=export_data_response,
            message="Testing data export initiated successfully",
        )
    except Exception as e:
        return error_response(
            message=f"Failed to export testing data: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

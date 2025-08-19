"""
Разрешения для качества (Quality) домена.
"""

from fastapi import Depends, HTTPException, status
from app.api.dependencies.core.auth import CurrentActiveUserDep
from app.core.constants import Permission
from app.services.permission_service import permission_service
from app.api.dependencies.core.database import SessionDep


async def require_specifications_access(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка доступа к спецификациям."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.VIEW_SPECIFICATIONS
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access specifications",
        )
    return True


async def require_specifications_create(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка разрешения на создание спецификаций."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.CREATE_SPECIFICATION
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create specifications",
        )
    return True


async def require_specifications_edit(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка разрешения на редактирование спецификаций."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.EDIT_SPECIFICATION
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to edit specifications",
        )
    return True


async def require_testing_access(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка доступа к тестированию."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.VIEW_TESTS
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access testing",
        )
    return True


async def require_testing_create(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка разрешения на создание тестов."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.CREATE_TEST
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create tests",
        )
    return True


async def require_testing_execute(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка разрешения на выполнение тестов."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.EXECUTE_TEST
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to execute tests",
        )
    return True


async def require_reports_access(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка доступа к отчетам."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.VIEW_REPORTS
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access reports",
        )
    return True


async def require_reports_generate(
    db: SessionDep,
    current_user: CurrentActiveUserDep,
):
    """Проверка разрешения на генерацию отчетов."""
    has_permission = await permission_service.check_permission(
        db=db, user_id=current_user.id, permission=Permission.GENERATE_REPORT
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to generate reports",
        )
    return True

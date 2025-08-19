"""
Sessions Management Router.

Роутер для управления пользовательскими сессиями.
"""

from fastapi import APIRouter, HTTPException, status, Request
from app.api.dependencies.core.auth import CurrentUserDep
from app.api.dependencies.core.database import SessionDep
from app.api.v1.common.responses import create_response, success_response, error_response
from app.api.v1.domains.auth.schemas import SessionListResponse, SessionInfo
from app.services.auth_service import authentication_service

router = APIRouter()


@router.get("/", summary="List User Sessions")
async def list_sessions(
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Получить список активных сессий пользователя.

    Возвращает информацию о всех активных сессиях текущего пользователя
    включая IP адреса, устройства и время последней активности.
    """
    try:
        # Получаем активные сессии пользователя
        sessions_data = await authentication_service.get_user_sessions(
            db=db,
            user_id=current_user.id
        )
        
        return create_response(
            data=sessions_data,
            message="Sessions retrieved successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Failed to retrieve sessions: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete("/{session_id}", summary="Revoke Session")
async def revoke_session(
    session_id: str,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Отозвать конкретную сессию.

    Завершает указанную сессию и аннулирует связанные токены.
    """
    try:
        # Отзываем конкретную сессию
        await authentication_service.revoke_session(
            db=db,
            user_id=current_user.id,
            session_id=session_id
        )
        
        return create_response(
            data={
                "success": True,
                "message": f"Session {session_id} revoked successfully",
            },
            message="Session revoked successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Failed to revoke session: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.delete("/", summary="Revoke All Sessions")
async def revoke_all_sessions(
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Отозвать все сессии пользователя.

    Завершает все активные сессии пользователя кроме текущей.
    """
    try:
        # Отзываем все сессии кроме текущей
        revoked_count = await authentication_service.revoke_all_user_sessions(
            db=db,
            user_id=current_user.id,
            except_current=True
        )
        
        return create_response(
            data={
                "success": True,
                "revoked_sessions": revoked_count,
                "message": "All other sessions revoked successfully",
            },
            message="All sessions revoked successfully",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Failed to revoke sessions: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
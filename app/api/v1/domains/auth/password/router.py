import datetime
from fastapi import APIRouter, HTTPException, status
from app.api.v1.common.responses import create_response, error_response, success_response, not_found_response, forbidden_response, unauthorized_response
from app.api.dependencies.core.auth import CurrentUserDep
from app.api.dependencies.core.database import SessionDep
from app.api.v1.domains.auth.schemas import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    PasswordResetResponse,
)
from app.services.auth_service import authentication_service
from app.services.password_service import password_service
from app.services.email_service import email_service
from app.crud import user as crud_user
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.core.config import settings
import logging

"""
Password Management Router.

Роутер для операций с паролями: смена, сброс, подтверждение.
"""

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/change", summary="Change Password")
async def change_password(
    change_data: PasswordChangeRequest,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Изменить пароль пользователя.

    - **current_password**: Текущий пароль пользователя
    - **new_password**: Новый пароль (минимум 8 символов)
    - **confirm_password**: Подтверждение пароля
    """
    try:
        # Проверяем текущий пароль
        if not verify_password(change_data.current_password, current_user.hashed_password):
            return unauthorized_response(
                message="Текущий пароль неверен"
            )

        # Проверяем что новый пароль отличается от текущего
        if verify_password(change_data.new_password, current_user.hashed_password):
            return error_response(
                message="Новый пароль должен отличаться от текущего",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Хэшируем новый пароль
        new_password_hash = get_password_hash(change_data.new_password)

        # Обновляем пароль в базе данных
        user_update_data = {
            "hashed_password": new_password_hash,
            "password_changed_at": datetime.utcnow(),
        }
        
        updated_user = await crud_user.update(
            db, 
            db_obj=current_user, 
            obj_in=user_update_data
        )

        # Опционально завершаем другие сессии
        if change_data.logout_other_sessions:
            await authentication_service.revoke_all_user_sessions(
                db=db,
                user_id=current_user.id,
                except_current=True
            )

        # Логируем событие безопасности
        await password_service.log_password_change(
            db=db,
            user_id=current_user.id,
            ip_address=getattr(change_data, 'ip_address', None),
            user_agent=getattr(change_data, 'user_agent', None)
        )

        logger.info(f"Password changed successfully for user {current_user.id}")
        
        return create_response(
            data={
                "success": True,
                "message": "Пароль успешно изменен",
                "other_sessions_revoked": change_data.logout_other_sessions,
            },
            message="Пароль обновлен успешно",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Password change failed for user {current_user.id}: {str(e)}", exc_info=True)
        return error_response(
            message=f"Ошибка при изменении пароля: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/reset", summary="Request Password Reset")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: SessionDep,
):
    """
    Запросить сброс пароля по email.

    - **email**: Email адрес пользователя
    """
    try:
        # Проверяем существует ли пользователь с таким email
        user = await crud_user.get_by_email(db, email=reset_data.email)
        
        # Всегда возвращаем успешный ответ для безопасности 
        # (не раскрываем информацию о существовании email)
        response_message = "Если email существует в системе, вы получите ссылку для сброса пароля."
        
        if user and user.is_active:
            # Генерируем токен сброса пароля
            reset_token = await password_service.create_password_reset_token(
                db=db,
                user_id=user.id,
                email=user.email
            )
            
            # Отправляем email с токеном
            reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
            
            await email_service.send_password_reset_email(
                email=user.email,
                name=user.name,
                reset_link=reset_link,
                token_expires_minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
            )
            
            # Логируем событие безопасности
            await password_service.log_password_reset_request(
                db=db,
                user_id=user.id,
                email=user.email,
                ip_address=getattr(reset_data, 'ip_address', None),
                user_agent=getattr(reset_data, 'user_agent', None)
            )
            
            logger.info(f"Password reset requested for user {user.id}")
        else:
            # Логируем попытку сброса для несуществующего email
            logger.warning(f"Password reset attempted for non-existent email: {reset_data.email}")
        
        response_data = PasswordResetResponse(
            success=True,
            message=response_message,
        )
        
        return create_response(
            data=response_data.model_dump(),
            message="Запрос на сброс пароля обработан успешно",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Password reset request failed for email {reset_data.email}: {str(e)}", exc_info=True)
        return error_response(
            message=f"Ошибка при запросе сброса пароля: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/reset/confirm", summary="Confirm Password Reset")
async def confirm_password_reset(
    confirm_data: PasswordResetConfirm,
    db: SessionDep,
):
    """
    Подтвердить сброс пароля с помощью токена.

    - **token**: Токен сброса пароля
    - **new_password**: Новый пароль (минимум 8 символов)
    - **confirm_password**: Подтверждение пароля
    """
    try:
        # Валидируем токен сброса пароля
        token_data = await password_service.validate_password_reset_token(
            db=db,
            token=confirm_data.token
        )
        
        if not token_data:
            return error_response(
                message="Недействительный или истекший токен сброса пароля",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Получаем пользователя
        user = await crud_user.get(db, id=token_data.user_id)
        if not user or not user.is_active:
            return error_response(
                message="Пользователь не найден или деактивирован",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Проверяем что новый пароль отличается от текущего
        if verify_password(confirm_data.new_password, user.hashed_password):
            return error_response(
                message="Новый пароль должен отличаться от текущего",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Хэшируем новый пароль
        new_password_hash = get_password_hash(confirm_data.new_password)
        
        # Обновляем пароль пользователя
        user_update_data = {
            "hashed_password": new_password_hash,
            "password_changed_at": datetime.utcnow(),
        }
        
        updated_user = await crud_user.update(
            db,
            db_obj=user,
            obj_in=user_update_data
        )
        
        # Аннулируем токен сброса пароля
        await password_service.invalidate_password_reset_token(
            db=db,
            token=confirm_data.token
        )
        
        # Завершаем все сессии пользователя для безопасности
        await authentication_service.revoke_all_user_sessions(
            db=db,
            user_id=user.id,
            except_current=False
        )
        
        # Логируем успешный сброс пароля
        await password_service.log_password_reset_completion(
            db=db,
            user_id=user.id,
            ip_address=getattr(confirm_data, 'ip_address', None),
            user_agent=getattr(confirm_data, 'user_agent', None)
        )
        
        # Отправляем уведомление о смене пароля
        await email_service.send_password_changed_notification(
            email=user.email,
            name=user.name
        )
        
        logger.info(f"Password reset completed successfully for user {user.id}")
        
        return create_response(
            data={
                "success": True,
                "message": "Пароль успешно сброшен",
                "all_sessions_revoked": True,
            },
            message="Пароль обновлен успешно",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Password reset confirmation failed for token {confirm_data.token}: {str(e)}", exc_info=True)
        return error_response(
            message=f"Ошибка при подтверждении сброса пароля: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

"""
Утилиты для создания стандартизированных HTTP ответов.
"""

from typing import Any, Dict, Optional, Union
from fastapi import status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone


def create_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = status.HTTP_200_OK,
    success: bool = True,
    error_code: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> JSONResponse:
    """
    Создает стандартизированный JSON ответ.
    
    Args:
        data: Данные ответа
        message: Сообщение для пользователя
        status_code: HTTP статус код
        success: Флаг успешности операции
        error_code: Код ошибки (для неуспешных ответов)
        headers: Дополнительные HTTP заголовки
        **kwargs: Дополнительные поля для ответа
        
    Returns:
        JSONResponse: Стандартизированный JSON ответ
    """
    content = {
        "success": success,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if data is not None:
        content["data"] = data
        
    if message:
        content["message"] = message
        
    if error_code:
        content["error_code"] = error_code
        
    # Добавляем дополнительные поля
    content.update(kwargs)
    
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers
    )


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = status.HTTP_200_OK,
    **kwargs
) -> JSONResponse:
    """
    Создает успешный ответ.
    
    Args:
        data: Данные ответа
        message: Сообщение об успехе
        status_code: HTTP статус код
        **kwargs: Дополнительные поля
        
    Returns:
        JSONResponse: Успешный ответ
    """
    return create_response(
        data=data,
        message=message,
        status_code=status_code,
        success=True,
        **kwargs
    )


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> JSONResponse:
    """
    Создает ответ с ошибкой.
    
    Args:
        message: Сообщение об ошибке
        status_code: HTTP статус код
        error_code: Код ошибки
        details: Детали ошибки
        **kwargs: Дополнительные поля
        
    Returns:
        JSONResponse: Ответ с ошибкой
    """
    return create_response(
        message=message,
        status_code=status_code,
        success=False,
        error_code=error_code,
        details=details,
        **kwargs
    )


def created_response(
    data: Any,
    message: str = "Resource created successfully",
    **kwargs
) -> JSONResponse:
    """
    Создает ответ о создании ресурса.
    
    Args:
        data: Созданный ресурс
        message: Сообщение о создании
        **kwargs: Дополнительные поля
        
    Returns:
        JSONResponse: Ответ о создании
    """
    return success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED,
        **kwargs
    )


def no_content_response(
    message: str = "Operation completed successfully"
) -> JSONResponse:
    """
    Создает ответ без контента.
    
    Args:
        message: Сообщение об успехе
        
    Returns:
        JSONResponse: Ответ без контента
    """
    return success_response(
        message=message,
        status_code=status.HTTP_204_NO_CONTENT
    )


def not_found_response(
    message: str = "Resource not found",
    resource_type: Optional[str] = None,
    resource_id: Optional[Union[str, int]] = None
) -> JSONResponse:
    """
    Создает ответ о ненайденном ресурсе.
    
    Args:
        message: Сообщение об ошибке
        resource_type: Тип ресурса
        resource_id: ID ресурса
        
    Returns:
        JSONResponse: Ответ о ненайденном ресурсе
    """
    details = {}
    if resource_type:
        details["resource_type"] = resource_type
    if resource_id:
        details["resource_id"] = resource_id
        
    return error_response(
        message=message,
        status_code=status.HTTP_404_NOT_FOUND,
        error_code="RESOURCE_NOT_FOUND",
        details=details if details else None
    )


def validation_error_response(
    message: str = "Validation failed",
    errors: Optional[list] = None
) -> JSONResponse:
    """
    Создает ответ с ошибкой валидации.
    
    Args:
        message: Сообщение об ошибке
        errors: Список ошибок валидации
        
    Returns:
        JSONResponse: Ответ с ошибкой валидации
    """
    return error_response(
        message=message,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        validation_errors=errors
    )


def forbidden_response(
    message: str = "Access forbidden",
    required_permission: Optional[str] = None
) -> JSONResponse:
    """
    Создает ответ о запрете доступа.
    
    Args:
        message: Сообщение об ошибке
        required_permission: Требуемое разрешение
        
    Returns:
        JSONResponse: Ответ о запрете доступа
    """
    details = {}
    if required_permission:
        details["required_permission"] = required_permission
        
    return error_response(
        message=message,
        status_code=status.HTTP_403_FORBIDDEN,
        error_code="ACCESS_FORBIDDEN",
        details=details if details else None
    )


def unauthorized_response(
    message: str = "Authentication required"
) -> JSONResponse:
    """
    Создает ответ о необходимости аутентификации.
    
    Args:
        message: Сообщение об ошибке
        
    Returns:
        JSONResponse: Ответ о необходимости аутентификации
    """
    return error_response(
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code="AUTHENTICATION_REQUIRED"
    )


def conflict_response(
    message: str = "Resource conflict",
    conflict_type: Optional[str] = None
) -> JSONResponse:
    """
    Создает ответ о конфликте ресурсов.
    
    Args:
        message: Сообщение об ошибке
        conflict_type: Тип конфликта
        
    Returns:
        JSONResponse: Ответ о конфликте
    """
    details = {}
    if conflict_type:
        details["conflict_type"] = conflict_type
        
    return error_response(
        message=message,
        status_code=status.HTTP_409_CONFLICT,
        error_code="RESOURCE_CONFLICT",
        details=details if details else None
    )

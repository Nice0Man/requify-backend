"""
Email Verification Router.

Роутер для операций с верификацией email: отправка, подтверждение.
"""

from fastapi import APIRouter, HTTPException, status
from app.api.dependencies.core.auth import CurrentUserDep, OptionalUserDep
from app.api.dependencies.core.database import SessionDep
from app.api.v1.common.responses import create_response, success_response, error_response
from app.api.v1.domains.auth.schemas import (
    EmailVerificationRequest,
    EmailVerificationConfirm,
    EmailVerificationResponse,
)
from app.services.auth_service import authentication_service

router = APIRouter()


@router.post("/verify", summary="Request Email Verification")
async def request_email_verification(
    verification_data: EmailVerificationRequest,
    db: SessionDep,
):
    """
    Запросить отправку письма для верификации email.

    Отправляет письмо с ссылкой для подтверждения email адреса.
    """
    try:
        # TODO: Implement email verification functionality
        # This should:
        # 1. Generate verification token
        # 2. Send verification email
        # 3. Store token with expiration
        
        response_data = EmailVerificationResponse(
            success=True,
            message="Verification email sent successfully",
        )
        
        return create_response(
            data=response_data.model_dump(),
            message="Email verification initiated",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Email verification failed: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/verify/confirm", summary="Confirm Email Verification")
async def confirm_email_verification(
    confirm_data: EmailVerificationConfirm,
    db: SessionDep,
):
    """
    Подтвердить верификацию email по токену.

    Проверяет токен и помечает email как подтвержденный.
    """
    try:
        # TODO: Implement email verification confirmation
        # This should:
        # 1. Validate verification token
        # 2. Check token expiration
        # 3. Update user email verification status
        # 4. Invalidate token
        
        response_data = EmailVerificationResponse(
            success=True,
            message="Email verified successfully",
        )
        
        return create_response(
            data=response_data.model_dump(),
            message="Email verification completed",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Email verification confirmation failed: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/resend", summary="Resend Verification Email")
async def resend_verification_email(
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    Повторно отправить письмо для верификации email.

    Требует аутентификации. Отправляет новое письмо с токеном верификации.
    """
    try:
        if current_user.is_email_verified:
            return error_response(
                message="Email is already verified",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # TODO: Implement resend verification email
        # This should:
        # 1. Invalidate old verification tokens
        # 2. Generate new verification token
        # 3. Send verification email
        
        response_data = EmailVerificationResponse(
            success=True,
            message="Verification email resent successfully",
        )
        
        return create_response(
            data=response_data.model_dump(),
            message="Verification email resent",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return error_response(
            message=f"Failed to resend verification email: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
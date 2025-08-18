"""
Email Verification Schemas.

Схемы для верификации email адресов.
"""

from typing import Optional, TYPE_CHECKING

from pydantic import Field, EmailStr, field_validator

from app.api.v1.common.schemas import (
    BaseSchema,
    ValidationMixin,
)


# === Email Verification Schemas ===


class EmailVerificationRequest(BaseSchema):
    """Схема для запроса верификации email."""

    email: EmailStr = Field(..., description="Email для верификации")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Валидация email."""
        return str(v).lower().strip()


class EmailVerificationResponse(BaseSchema):
    """Схема для ответа после запроса верификации email."""

    message: str = Field(..., description="Сообщение о результате")
    verification_token_sent: bool = Field(
        default=True, description="Отправлен ли токен верификации"
    )


class EmailVerificationConfirm(BaseSchema, ValidationMixin):
    """Схема для подтверждения верификации email."""

    token: str = Field(..., description="Токен верификации email")

    @field_validator("token")
    @classmethod
    def validate_token(cls, v):
        """Валидация токена."""
        if not v or not v.strip():
            raise ValueError("Verification token cannot be empty")
        return v.strip()


class EmailVerificationConfirmResponse(BaseSchema):
    """Схема для ответа после верификации email."""

    message: str = Field(..., description="Сообщение о результате")
    verified: bool = Field(..., description="Успешно ли подтвержден email")



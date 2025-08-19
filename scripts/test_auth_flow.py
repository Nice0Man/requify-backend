#!/usr/bin/env python3
"""
Скрипт для тестирования потока аутентификации.
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import JWTTokenManager, TokenType
from app.core.config import settings


async def test_jwt_token_validation():
    """Тест валидации JWT токенов."""
    print("🔍 Тестирование JWT токен валидации...")

    try:
        # Создаем тестовый токен
        test_payload = {
            "user_id": 1,
            "email": "test@example.com",
            "scopes": ["me", "use_api"],
            "type": TokenType.ACCESS.value,
        }

        # Создаем access токен
        token = JWTTokenManager.create_access_token(
            subject="test@example.com",
            user_id=1,
            scopes=["me", "use_api"],
        )

        print(f"✅ Токен создан: {token[:50]}...")

        # Проверяем токен
        decoded_payload = JWTTokenManager.verify_token(token, TokenType.ACCESS)

        if decoded_payload:
            print("✅ Токен успешно валидирован")
            print(f"  User ID: {decoded_payload.get('user_id')}")
            print(f"  Email: {decoded_payload.get('sub')}")
            print(f"  Scopes: {decoded_payload.get('scopes')}")
            print(f"  Type: {decoded_payload.get('type')}")
            return True
        else:
            print("❌ Токен не прошел валидацию")
            return False

    except Exception as e:
        print(f"❌ Ошибка тестирования токенов: {e}")
        return False


async def test_security_settings():
    """Тест настроек безопасности."""
    print("\n🔧 Проверка настроек безопасности...")

    try:
        # Проверяем основные настройки
        print(f"  Secret key length: {len(settings.security.secret_key)} chars")
        print(f"  Algorithm: {settings.security.algorithm}")
        print(
            f"  Access token expire: {settings.security.access_token_expire_minutes} min"
        )
        print(
            f"  Refresh token expire: {settings.security.refresh_token_expire_days} days"
        )

        # Проверяем длину ключа
        if len(settings.security.secret_key) >= 32:
            print("✅ Secret key имеет достаточную длину")
        else:
            print("⚠️  Secret key слишком короткий")

        return True

    except Exception as e:
        print(f"❌ Ошибка проверки настроек: {e}")
        return False


async def test_token_lifecycle():
    """Тест жизненного цикла токена."""
    print("\n🔄 Тестирование жизненного цикла токена...")

    try:
        # Создаем токен
        token = JWTTokenManager.create_access_token(
            subject="lifecycle@test.com",
            user_id=99,
            scopes=["me", "use_api"],
        )
        print("✅ Токен создан")

        # Декодируем токен
        payload = JWTTokenManager.verify_token(token, TokenType.ACCESS)
        if payload:
            print("✅ Токен декодирован")
        else:
            print("❌ Ошибка декодирования токена")
            return False

        # Проверяем содержимое
        required_fields = ["user_id", "sub", "exp", "type"]
        for field in required_fields:
            if field in payload:
                print(f"✅ Поле '{field}' присутствует")
            else:
                print(f"❌ Поле '{field}' отсутствует")
                return False

        return True

    except Exception as e:
        print(f"❌ Ошибка тестирования жизненного цикла: {e}")
        return False


async def main():
    """Основная функция тестирования."""
    print("🚀 Начинаем тестирование аутентификации...\n")

    results = []

    # Запускаем тесты
    results.append(await test_security_settings())
    results.append(await test_jwt_token_validation())
    results.append(await test_token_lifecycle())

    # Итоговый результат
    passed = sum(results)
    total = len(results)

    print(f"\n📊 Результат тестирования:")
    print(f"  Пройдено: {passed}/{total}")

    if passed == total:
        print("🎉 Все тесты прошли успешно!")
        return 0
    else:
        print("⚠️  Некоторые тесты не прошли")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

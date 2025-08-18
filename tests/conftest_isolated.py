"""
Изолированный conftest для тестов без зависимостей от основного приложения.
"""

import pytest


@pytest.fixture
def mock_email_service():
    """Фикстура мока email сервиса."""
    from tests.test_basic_synthetic import MockEmailService

    return MockEmailService()


@pytest.fixture
def simple_user_factory():
    """Фикстура простой фабрики пользователей."""
    from tests.test_basic_synthetic import SimpleUserFactory

    return SimpleUserFactory


# Простые фикстуры для тестирования
@pytest.fixture
def sample_user_data():
    """Базовые тестовые данные пользователя."""
    return {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
        'name': 'Test User',
        'status': 'active',
        'is_active': True,
        'is_email_verified': True,
    }


@pytest.fixture
def performance_data_small():
    """Небольшой набор данных для тестов производительности."""
    from tests.test_basic_synthetic import SimpleUserFactory

    return SimpleUserFactory.create_batch(100)


@pytest.fixture
def performance_data_large():
    """Большой набор данных для тестов производительности."""
    from tests.test_basic_synthetic import SimpleUserFactory

    return SimpleUserFactory.create_batch(1000)

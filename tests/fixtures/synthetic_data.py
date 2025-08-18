"""
Фикстуры для генерации синтетических данных в тестах.

Содержит фабрики и генераторы для создания тестовых данных,
включая моки внешних сервисов и синтетические данные для нагрузочных тестов.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch

import pytest
from faker import Faker
from factory import Factory, Sequence, LazyAttribute, SubFactory
import factory

from app.models.user import User
from app.models.company import Company
from app.models.project import Project
from app.models.requirement import Requirement
from app.core.security import get_password_hash


# Инициализация Faker с русской локализацией
fake = Faker(['ru_RU', 'en_US'])
Faker.seed(42)  # Фиксированный seed для воспроизводимости


class UserFactory(factory.Factory):
    """Фабрика для создания синтетических пользователей."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    username = factory.LazyAttribute(lambda obj: f"user_{obj.id}_{fake.user_name()}")
    email = factory.LazyAttribute(lambda obj: f"user_{obj.id}@{fake.domain_name()}")
    name = factory.LazyAttribute(lambda _: fake.name())
    status = factory.Iterator(['active', 'inactive', 'pending'])
    auth_provider = factory.Iterator(['local', 'google', 'microsoft'])
    is_email_verified = factory.Iterator([True, False], cycle=True)
    is_active = factory.Iterator([True, False], cycle=True)
    created_at = factory.LazyAttribute(
        lambda _: fake.date_time_between(start_date='-2y', end_date='now')
    )
    updated_at = factory.LazyAttribute(
        lambda obj: obj.created_at + timedelta(days=random.randint(0, 30))
    )
    password_hash = factory.LazyAttribute(lambda _: get_password_hash("test_password"))


class CompanyFactory(factory.Factory):
    """Фабрика для создания синтетических компаний."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyAttribute(lambda _: fake.company())
    description = factory.LazyAttribute(lambda _: fake.catch_phrase())
    website = factory.LazyAttribute(lambda _: fake.url())
    industry = factory.Iterator(
        [
            'Technology',
            'Healthcare',
            'Finance',
            'Education',
            'Manufacturing',
            'Retail',
            'Consulting',
        ]
    )
    size = factory.Iterator(['startup', 'small', 'medium', 'large', 'enterprise'])
    created_at = factory.LazyAttribute(
        lambda _: fake.date_time_between(start_date='-5y', end_date='-1y')
    )


class ProjectFactory(factory.Factory):
    """Фабрика для создания синтетических проектов."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyAttribute(lambda _: f"Project {fake.word().title()}")
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    status = factory.Iterator(
        ['planning', 'active', 'on_hold', 'completed', 'archived']
    )
    priority = factory.Iterator(['low', 'medium', 'high', 'critical'])
    start_date = factory.LazyAttribute(
        lambda _: fake.date_between(start_date='-1y', end_date='now')
    )
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(days=random.randint(30, 365))
    )
    company_id = factory.Sequence(lambda n: random.randint(1, 5))


class RequirementFactory(factory.Factory):
    """Фабрика для создания синтетических требований."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6).rstrip('.'))
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=500))
    type = factory.Iterator(['functional', 'non_functional', 'technical', 'business'])
    priority = factory.Iterator(['low', 'medium', 'high', 'critical'])
    status = factory.Iterator(['draft', 'review', 'approved', 'implemented', 'tested'])
    project_id = factory.Sequence(lambda n: random.randint(1, 10))
    created_by = factory.Sequence(lambda n: random.randint(1, 20))


@pytest.fixture
def synthetic_users():
    """Генерирует список синтетических пользователей."""
    return UserFactory.create_batch(50)


@pytest.fixture
def synthetic_companies():
    """Генерирует список синтетических компаний."""
    return CompanyFactory.create_batch(10)


@pytest.fixture
def synthetic_projects():
    """Генерирует список синтетических проектов."""
    return ProjectFactory.create_batch(25)


@pytest.fixture
def synthetic_requirements():
    """Генерирует список синтетических требований."""
    return RequirementFactory.create_batch(100)


@pytest.fixture
def large_dataset():
    """Генерирует большой набор данных для нагрузочных тестов."""
    return {
        'users': UserFactory.create_batch(1000),
        'companies': CompanyFactory.create_batch(100),
        'projects': ProjectFactory.create_batch(500),
        'requirements': RequirementFactory.create_batch(2000),
    }


class MockEmailService:
    """Мок сервиса электронной почты."""

    def __init__(self):
        self.sent_emails = []
        self.is_configured = True

    async def send_email(self, to: str, subject: str, body: str, **kwargs):
        """Имитирует отправку email."""
        email_data = {
            'to': to,
            'subject': subject,
            'body': body,
            'sent_at': datetime.utcnow(),
            'status': 'sent',
            **kwargs,
        }
        self.sent_emails.append(email_data)
        return True

    def get_sent_emails(self) -> List[Dict]:
        """Возвращает список отправленных emails."""
        return self.sent_emails

    def clear_sent_emails(self):
        """Очищает список отправленных emails."""
        self.sent_emails.clear()


class MockFileStorage:
    """Мок файлового хранилища."""

    def __init__(self):
        self.stored_files = {}
        self.is_configured = True

    async def upload_file(self, file_path: str, content: bytes, **kwargs):
        """Имитирует загрузку файла."""
        file_id = str(uuid.uuid4())
        self.stored_files[file_id] = {
            'path': file_path,
            'content': content,
            'size': len(content),
            'uploaded_at': datetime.utcnow(),
            **kwargs,
        }
        return file_id

    async def download_file(self, file_id: str) -> Optional[bytes]:
        """Имитирует скачивание файла."""
        file_data = self.stored_files.get(file_id)
        return file_data['content'] if file_data else None

    async def delete_file(self, file_id: str) -> bool:
        """Имитирует удаление файла."""
        return self.stored_files.pop(file_id, None) is not None


class MockAuthProvider:
    """Мок провайдера аутентификации."""

    def __init__(self):
        self.valid_tokens = set()
        self.user_data = {}

    def create_token(self, user_id: int, scopes: List[str] = None) -> str:
        """Создает тестовый токен."""
        token = f"test_token_{user_id}_{uuid.uuid4().hex[:8]}"
        self.valid_tokens.add(token)
        self.user_data[token] = {
            'user_id': user_id,
            'scopes': scopes or ['read', 'write'],
            'created_at': datetime.utcnow(),
        }
        return token

    def validate_token(self, token: str) -> Optional[Dict]:
        """Валидирует тестовый токен."""
        return self.user_data.get(token) if token in self.valid_tokens else None

    def revoke_token(self, token: str) -> bool:
        """Отзывает токен."""
        if token in self.valid_tokens:
            self.valid_tokens.remove(token)
            self.user_data.pop(token, None)
            return True
        return False


@pytest.fixture
def mock_email_service():
    """Предоставляет мок сервиса электронной почты."""
    return MockEmailService()


@pytest.fixture
def mock_file_storage():
    """Предоставляет мок файлового хранилища."""
    return MockFileStorage()


@pytest.fixture
def mock_auth_provider():
    """Предоставляет мок провайдера аутентификации."""
    return MockAuthProvider()


@pytest.fixture
def mock_external_services(mock_email_service, mock_file_storage, mock_auth_provider):
    """Предоставляет все моки внешних сервисов."""
    return {
        'email': mock_email_service,
        'storage': mock_file_storage,
        'auth': mock_auth_provider,
    }


class DatabaseSeeder:
    """Утилита для заполнения тестовой базы данных."""

    def __init__(self, session):
        self.session = session

    def seed_basic_data(self):
        """Заполняет базу базовыми данными."""
        companies = CompanyFactory.create_batch(5)
        users = UserFactory.create_batch(20)
        projects = ProjectFactory.create_batch(10)

        # Можно добавить логику создания связанных объектов
        return {'companies': companies, 'users': users, 'projects': projects}

    def seed_large_dataset(self):
        """Заполняет базу большим количеством данных."""
        companies = CompanyFactory.create_batch(50)
        users = UserFactory.create_batch(500)
        projects = ProjectFactory.create_batch(100)
        requirements = RequirementFactory.create_batch(1000)

        return {
            'companies': companies,
            'users': users,
            'projects': projects,
            'requirements': requirements,
        }


@pytest.fixture
def db_seeder(test_db_session):
    """Предоставляет утилиту для заполнения базы данных."""
    return DatabaseSeeder(test_db_session)


@pytest.fixture
def performance_test_data():
    """Данные для тестов производительности."""
    return {
        'small_dataset': {
            'users': UserFactory.create_batch(100),
            'projects': ProjectFactory.create_batch(50),
        },
        'medium_dataset': {
            'users': UserFactory.create_batch(500),
            'projects': ProjectFactory.create_batch(200),
        },
        'large_dataset': {
            'users': UserFactory.create_batch(1000),
            'projects': ProjectFactory.create_batch(500),
        },
    }


@pytest.fixture
def api_test_data():
    """Данные для API тестов."""
    return {
        'valid_user': UserFactory.create(),
        'invalid_user': {
            'username': '',  # Невалидное имя
            'email': 'invalid-email',  # Невалидный email
            'name': 'A' * 256,  # Слишком длинное имя
        },
        'edge_cases': {
            'unicode_name': '测试用户',
            'special_chars': 'user@#$%',
            'very_long_email': 'a' * 100 + '@example.com',
        },
    }


class TimeFreezeMixin:
    """Миксин для фиксации времени в тестах."""

    @staticmethod
    def freeze_time_at(timestamp: datetime):
        """Фиксирует время на указанной метке."""
        return patch('datetime.datetime')

    @staticmethod
    def advance_time_by(seconds: int):
        """Продвигает время на указанное количество секунд."""
        # Можно использовать с freezegun
        pass


@pytest.fixture
def time_utils():
    """Предоставляет утилиты для работы со временем в тестах."""
    return TimeFreezeMixin()


# Маркеры для синтетических данных
def pytest_configure(config):
    """Добавляет маркеры для синтетических данных."""
    config.addinivalue_line("markers", "synthetic: uses synthetic data")
    config.addinivalue_line("markers", "mocked: uses mocked services")
    config.addinivalue_line(
        "markers", "performance_data: uses large synthetic datasets"
    )


# Автоматические фикстуры для моков
@pytest.fixture(autouse=True)
def auto_mock_external_services(monkeypatch):
    """Автоматически мокает внешние сервисы в тестах."""

    # Мокаем только если тест помечен соответствующим маркером
    def mock_external_api_call(*args, **kwargs):
        return {"status": "mocked", "data": "test_data"}

    # Можно добавить автоматическое мокирование
    # monkeypatch.setattr("app.services.external_api.call", mock_external_api_call)
    pass

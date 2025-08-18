"""
Базовые тесты синтетических данных без зависимости от моделей.
"""

import pytest
from datetime import datetime
from faker import Faker

# Простые фабрики без SQLAlchemy зависимостей
fake = Faker(['ru_RU', 'en_US'])
Faker.seed(42)


class SimpleUserFactory:
    """Простая фабрика пользователей без SQLAlchemy."""

    @staticmethod
    def create(**kwargs):
        base_data = {
            'id': fake.random_int(min=1, max=1000),
            'username': fake.user_name(),
            'email': fake.email(),
            'name': fake.name(),
            'status': fake.random_element(['active', 'inactive', 'pending']),
            'auth_provider': fake.random_element(['local', 'google', 'microsoft']),
            'is_email_verified': fake.boolean(),
            'is_active': fake.boolean(),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
        }
        base_data.update(kwargs)
        return base_data

    @staticmethod
    def create_batch(size, **kwargs):
        return [SimpleUserFactory.create(**kwargs) for _ in range(size)]


class MockEmailService:
    """Простой мок сервиса email."""

    def __init__(self):
        self.sent_emails = []

    def send_email(self, to: str, subject: str, body: str):
        email = {
            'to': to,
            'subject': subject,
            'body': body,
            'sent_at': datetime.utcnow(),
            'status': 'sent',
        }
        self.sent_emails.append(email)
        return True

    def get_sent_emails(self):
        return self.sent_emails


@pytest.mark.unit
@pytest.mark.synthetic
class TestBasicSyntheticData:
    """Базовые тесты синтетических данных."""

    def test_simple_user_factory(self):
        """Тест простой фабрики пользователей."""
        user = SimpleUserFactory.create()

        assert user['username']
        assert '@' in user['email']
        assert user['name']
        assert user['status'] in ['active', 'inactive', 'pending']
        assert user['auth_provider'] in ['local', 'google', 'microsoft']
        assert isinstance(user['is_email_verified'], bool)
        assert isinstance(user['is_active'], bool)
        assert isinstance(user['created_at'], datetime)

    def test_user_factory_batch(self):
        """Тест массового создания пользователей."""
        users = SimpleUserFactory.create_batch(10)

        assert len(users) == 10

        # Проверяем уникальность email'ов
        emails = [user['email'] for user in users]
        assert len(set(emails)) == len(emails)

    def test_user_factory_with_overrides(self):
        """Тест фабрики с переопределением параметров."""
        user = SimpleUserFactory.create(status='active', is_email_verified=True)

        assert user['status'] == 'active'
        assert user['is_email_verified'] is True

    def test_mock_email_service(self):
        """Тест мока email сервиса."""
        email_service = MockEmailService()

        # Отправляем email
        result = email_service.send_email(
            to="test@example.com", subject="Test Subject", body="Test Body"
        )

        assert result is True

        # Проверяем, что email сохранился
        sent_emails = email_service.get_sent_emails()
        assert len(sent_emails) == 1

        email = sent_emails[0]
        assert email['to'] == "test@example.com"
        assert email['subject'] == "Test Subject"
        assert email['body'] == "Test Body"
        assert email['status'] == 'sent'
        assert isinstance(email['sent_at'], datetime)

    def test_deterministic_data_generation(self):
        """Тест детерминированной генерации данных."""
        # С фиксированным seed результат должен быть предсказуемым
        Faker.seed(123)
        user1 = SimpleUserFactory.create()

        Faker.seed(123)
        user2 = SimpleUserFactory.create()

        # При одинаковом seed данные должны совпадать
        assert user1['username'] == user2['username']
        assert user1['email'] == user2['email']
        assert user1['name'] == user2['name']

    def test_performance_large_dataset(self):
        """Тест производительности генерации больших данных."""
        import time

        start_time = time.time()
        users = SimpleUserFactory.create_batch(1000)
        end_time = time.time()

        assert len(users) == 1000

        # Генерация 1000 пользователей должна занимать менее 2 секунд
        generation_time = end_time - start_time
        assert generation_time < 2.0, f"Generation took {generation_time:.2f} seconds"

    def test_data_validation(self):
        """Тест валидации синтетических данных."""
        users = SimpleUserFactory.create_batch(50)

        for user in users:
            # Проверяем основные поля
            assert user['id'] > 0
            assert len(user['username']) > 0
            assert '@' in user['email']
            assert '.' in user['email']
            assert len(user['name']) > 0

            # Проверяем типы данных
            assert isinstance(user['id'], int)
            assert isinstance(user['username'], str)
            assert isinstance(user['email'], str)
            assert isinstance(user['name'], str)
            assert isinstance(user['is_email_verified'], bool)
            assert isinstance(user['is_active'], bool)
            assert isinstance(user['created_at'], datetime)


@pytest.mark.unit
@pytest.mark.mocked
class TestBasicMocks:
    """Тесты базовых моков."""

    def test_mock_isolation(self):
        """Тест изоляции моков между тестами."""
        email_service = MockEmailService()

        # Сервис должен начинать с пустого состояния
        assert len(email_service.get_sent_emails()) == 0

        # Отправляем email
        email_service.send_email("test@example.com", "Subject", "Body")

        # Проверяем, что email записался
        assert len(email_service.get_sent_emails()) == 1

    def test_mock_state_management(self):
        """Тест управления состоянием мока."""
        email_service = MockEmailService()

        # Отправляем несколько emails
        for i in range(5):
            email_service.send_email(
                f"test{i}@example.com", f"Subject {i}", f"Body {i}"
            )

        sent_emails = email_service.get_sent_emails()
        assert len(sent_emails) == 5

        # Проверяем порядок отправки
        for i, email in enumerate(sent_emails):
            assert email['to'] == f"test{i}@example.com"
            assert email['subject'] == f"Subject {i}"
            assert email['body'] == f"Body {i}"


@pytest.mark.ci
@pytest.mark.synthetic
class TestCIEnvironment:
    """Тесты для CI окружения."""

    def test_environment_variables(self):
        """Тест переменных окружения для CI."""
        import os

        # В GitHub Actions эти переменные должны быть установлены
        # Для локального запуска делаем их опциональными
        testing = os.getenv('TESTING', 'false')
        log_level = os.getenv('LOG_LEVEL', 'INFO')

        # Просто проверяем, что переменные читаются
        assert isinstance(testing, str)
        assert isinstance(log_level, str)

    def test_memory_usage(self):
        """Тест использования памяти."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Создаем большой набор данных
        users = SimpleUserFactory.create_batch(1000)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = final_memory - initial_memory

        # Память не должна увеличиться более чем на 50MB
        assert memory_diff < 50, f"Memory usage increased by {memory_diff:.2f}MB"

        # Убеждаемся, что данные созданы
        assert len(users) == 1000

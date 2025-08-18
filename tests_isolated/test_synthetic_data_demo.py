"""
Демонстрационный тест синтетических данных и моков.
Изолированный от основной системы проекта.
"""

import pytest
from datetime import datetime
from faker import Faker
import random


# Настройка Faker
fake = Faker(['ru_RU', 'en_US'])
Faker.seed(42)


class UserFactory:
    """Фабрика для создания синтетических пользователей."""
    
    @staticmethod
    def create(**kwargs):
        base_data = {
            'id': fake.random_int(min=1, max=10000),
            'username': fake.user_name(),
            'email': fake.email(),
            'name': fake.name(),
            'status': random.choice(['active', 'inactive', 'pending']),
            'auth_provider': random.choice(['local', 'google', 'microsoft']),
            'is_email_verified': fake.boolean(),
            'is_active': fake.boolean(),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
        }
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def create_batch(size, **kwargs):
        return [UserFactory.create(**kwargs) for _ in range(size)]


class MockEmailService:
    """Мок сервиса электронной почты."""
    
    def __init__(self):
        self.sent_emails = []
        self.is_configured = True
        
    def send_email(self, to: str, subject: str, body: str, **kwargs):
        """Имитирует отправку email."""
        email_data = {
            'to': to,
            'subject': subject,
            'body': body,
            'sent_at': datetime.utcnow(),
            'status': 'sent',
            **kwargs
        }
        self.sent_emails.append(email_data)
        return True
        
    def get_sent_emails(self):
        """Возвращает список отправленных emails."""
        return self.sent_emails


@pytest.mark.unit
class TestSyntheticDataGeneration:
    """Тесты генерации синтетических данных."""
    
    def test_user_factory_creates_valid_data(self):
        """Тест создания валидных данных пользователя."""
        users = UserFactory.create_batch(10)
        
        assert len(users) == 10
        for user in users:
            assert user['username']
            assert '@' in user['email']
            assert user['name']
            assert user['status'] in ['active', 'inactive', 'pending']
            assert user['auth_provider'] in ['local', 'google', 'microsoft']
            assert isinstance(user['is_email_verified'], bool)
            assert isinstance(user['is_active'], bool)
            
    def test_synthetic_data_uniqueness(self):
        """Тест уникальности синтетических данных."""
        users = UserFactory.create_batch(20)
        
        usernames = [user['username'] for user in users]
        emails = [user['email'] for user in users]
        
        # Проверяем уникальность (может быть небольшие повторения из-за Faker)
        assert len(set(usernames)) >= len(usernames) * 0.9  # 90% уникальности
        assert len(set(emails)) >= len(emails) * 0.9


@pytest.mark.unit
class TestMockServices:
    """Тесты моков внешних сервисов."""
    
    def test_mock_email_service(self):
        """Тест мока сервиса электронной почты."""
        email_service = MockEmailService()
        
        # Отправляем тестовый email
        result = email_service.send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Test Body"
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


@pytest.mark.performance
class TestPerformanceWithSyntheticData:
    """Тесты производительности с синтетическими данными."""
    
    def test_user_creation_performance(self):
        """Тест производительности создания пользователей."""
        import time
        
        # Тест малого набора данных
        start_time = time.time()
        small_users = UserFactory.create_batch(100)
        small_time = time.time() - start_time
        
        assert len(small_users) == 100
        assert small_time < 1.0  # Должно быть меньше 1 секунды
        
        # Тест среднего набора данных
        start_time = time.time()
        medium_users = UserFactory.create_batch(500)
        medium_time = time.time() - start_time
        
        assert len(medium_users) == 500
        assert medium_time < 3.0  # Должно быть меньше 3 секунд
        
    def test_memory_usage_with_large_dataset(self):
        """Тест использования памяти с большими наборами данных."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Создаем большой набор данных
            users = UserFactory.create_batch(1000)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = final_memory - initial_memory
            
            assert len(users) == 1000
            # Проверяем, что память не превышает 50MB
            assert memory_diff < 50, f"Memory usage too high: {memory_diff}MB"
            
        except ImportError:
            # Если psutil не установлен, просто создаем данные
            users = UserFactory.create_batch(1000)
            assert len(users) == 1000


@pytest.mark.integration
class TestSyntheticDataIntegration:
    """Интеграционные тесты с синтетическими данными."""
    
    def test_large_dataset_generation(self):
        """Тест генерации большого набора данных."""
        large_dataset = {
            'users': UserFactory.create_batch(100),
            'companies': UserFactory.create_batch(10),  # Используем ту же фабрику для простоты
        }
        
        assert len(large_dataset['users']) == 100
        assert len(large_dataset['companies']) == 10
        
        # Проверяем, что данные валидны
        for user in large_dataset['users'][:5]:  # Проверяем первые 5
            assert user['username']
            assert '@' in user['email']


@pytest.mark.ci
class TestCIEnvironment:
    """Специальные тесты для CI окружения."""
    
    def test_ci_environment_setup(self):
        """Тест настройки CI окружения."""
        import os
        
        # Проверяем переменные окружения для CI
        testing = os.getenv('TESTING', 'false')
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Просто проверяем, что переменные читаются
        assert isinstance(testing, str)
        assert isinstance(log_level, str)
        
    def test_synthetic_data_deterministic(self):
        """Тест детерминированности синтетических данных."""
        # При фиксированном seed результат должен быть предсказуемым
        Faker.seed(123)
        user1 = UserFactory.create()
        
        Faker.seed(123) 
        user2 = UserFactory.create()
        
        # При одинаковом seed основные данные должны совпадать
        assert user1['username'] == user2['username']
        assert user1['email'] == user2['email']
        assert user1['name'] == user2['name']
        
    def test_mocks_isolation(self):
        """Тест изоляции моков между тестами."""
        email_service = MockEmailService()
        
        # Проверяем, что моки начинают с чистого состояния
        sent_emails = email_service.get_sent_emails()
        assert len(sent_emails) == 0
        
        # Отправляем email
        email_service.send_email("test@example.com", "Test", "Body")
        
        # Проверяем, что email записался
        sent_emails = email_service.get_sent_emails()
        assert len(sent_emails) == 1


if __name__ == "__main__":
    # Можно запустить напрямую
    import sys
    pytest.main([__file__] + sys.argv[1:])

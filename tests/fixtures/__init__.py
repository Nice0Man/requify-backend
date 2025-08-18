"""
Пакет фикстур для тестирования Requify Backend.

Содержит общие фикстуры, фабрики данных и моки сервисов.
"""

from .synthetic_data import (
    UserFactory,
    CompanyFactory,
    ProjectFactory,
    RequirementFactory,
    MockEmailService,
    MockFileStorage,
    MockAuthProvider,
    DatabaseSeeder,
)

__all__ = [
    'UserFactory',
    'CompanyFactory', 
    'ProjectFactory',
    'RequirementFactory',
    'MockEmailService',
    'MockFileStorage',
    'MockAuthProvider',
    'DatabaseSeeder',
]

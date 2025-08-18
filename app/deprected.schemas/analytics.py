"""
Analytics Root Schemas.

Корневые схемы для аналитики - реэкспорт из поддоменов.
"""

# Реэкспорт схем из поддоменов
from app.api.v1.domains.analytics.dashboard.schemas import *
from app.api.v1.domains.analytics.metrics.schemas import *
from app.api.v1.domains.analytics.reports.schemas import *


__all__ = [
    # Dashboard schemas будут добавлены автоматически из dashboard.schemas
    # Metrics schemas будут добавлены автоматически из metrics.schemas
    # Reports schemas будут добавлены автоматически из reports.schemas
]

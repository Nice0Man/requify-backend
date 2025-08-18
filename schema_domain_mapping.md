# Schema to Domain Mapping

## Текущая структура доменов:
- auth/ - Аутентификация (уже есть схемы)
- analytics/ - Аналитика (dashboard уже есть)  
- collaboration/ - Совместная работа (comments уже есть)
- identity/ - Управление пользователями (users уже есть)
- organizations/ - Организации (companies уже есть)
- projects/ - Проекты (пустые роутеры)
- quality/ - Качество (пустые роутеры)
- configuration/ - Конфигурация (пустые роутеры)
- system/ - Системные функции (пустые роутеры)

## Mapping существующих схем из app/schemas/:

### auth (уже есть схемы в домене)
- ✅ auth.py -> domains/auth/schemas.py (уже есть, нужно объединить)
- ✅ token.py -> domains/auth/schemas.py (уже есть, нужно объединить)

### analytics (частично есть)  
- ✅ analytics.py -> domains/analytics/schemas.py (добавить в основной)
- ✅ dashboard.py -> domains/analytics/dashboard/schemas.py (уже есть, нужно объединить)

### collaboration (частично есть)
- ✅ comment.py -> domains/collaboration/comments/schemas.py (уже есть, нужно объединить)
- 📦 activity.py -> domains/collaboration/activity/schemas.py (нужно дополнить)
- 📦 notification.py -> domains/collaboration/notifications/schemas.py (нужно дополнить)
- 📦 relationship.py -> domains/collaboration/relationships/schemas.py (нужно дополнить)
- 📦 relationship_types.py -> domains/collaboration/relationships/schemas.py (объединить)

### identity (частично есть)
- ✅ user.py -> domains/identity/users/schemas.py (уже есть, нужно объединить)
- 📦 user_profile.py -> domains/identity/profiles/schemas.py (нужно дополнить)
- 📦 enhanced_role.py -> domains/identity/roles/schemas.py (нужно дополнить)
- 📦 role_hierarchy.py -> domains/identity/role_hierarchy/schemas.py (создать файл)

### organizations (частично есть)
- ✅ company.py -> domains/organizations/companies/schemas.py (уже есть, нужно объединить)
- 📦 company_branding.py -> domains/organizations/companies/schemas.py (объединить)
- 📦 company_contact.py -> domains/organizations/companies/schemas.py (объединить)
- 📦 company_settings.py -> domains/organizations/companies/schemas.py (объединить)  
- 📦 company_subscription.py -> domains/organizations/subscriptions/schemas.py (создать файл)
- 📦 department.py -> domains/organizations/departments/schemas.py (нужно дополнить)
- 📦 team.py -> domains/organizations/teams/schemas.py (нужно дополнить)

### projects (пустые роутеры - нужно создать схемы)
- 📦 project.py -> domains/projects/core/schemas.py (создать файл)
- 📦 requirement.py -> domains/projects/requirements/schemas.py (создать файл)
- 📦 requirement_priorities.py -> domains/projects/requirements/schemas.py (объединить)
- 📦 requirement_statuses.py -> domains/projects/requirements/schemas.py (объединить)
- 📦 requirement_types.py -> domains/projects/requirements/schemas.py (объединить)
- 📦 requirement_group.py -> domains/projects/requirements/schemas.py (объединить)
- 📦 requirement_group_version.py -> domains/projects/requirements/schemas.py (объединить)
- 📦 release.py -> domains/projects/releases/schemas.py (создать файл)

### quality (пустые роутеры - нужно создать схемы)
- 📦 test_case.py -> domains/quality/testing/schemas.py (создать роутер и схемы)
- 📦 test_plan.py -> domains/quality/testing/schemas.py (объединить)
- 📦 test_result.py -> domains/quality/testing/schemas.py (объединить)
- 📦 specification.py -> domains/quality/specifications/schemas.py (создать роутер и схемы)
- 📦 spec.py -> domains/quality/specifications/schemas.py (объединить)
- 📦 report.py -> domains/quality/reports/schemas.py (создать роутер и схемы)
- 📦 trace_matrix.py -> domains/quality/reports/schemas.py (объединить)

### configuration (пустые роутеры - нужно создать схемы)
- 📦 settings.py -> domains/configuration/settings/schemas.py (создать роутер и схемы)

### Общие схемы (остаются в app/schemas/)
- ✅ base.py -> остается как есть (базовые классы)
- ✅ common.py -> остается как есть (общие схемы)

## Легенда:
- ✅ Схемы уже есть в домене, нужно объединить
- 📦 Нужно создать или дополнить схемы в домене

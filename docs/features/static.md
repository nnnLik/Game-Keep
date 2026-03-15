# Статика

Загрузка аватаров, раздача файлов по `/uploads`.

## Backend

| Компонент | Файл |
|-----------|------|
| get_uploads_dir, get_avatars_dir, setup_static_files | [backend/src/utils/static.py](../../backend/src/utils/static.py) |
| build_app (монтирует /uploads) | [backend/src/utils/app.py](../../backend/src/utils/app.py) |
| Сохранение аватара в CompleteRegistrationService | [backend/src/services/auth/complete_registration_service.py](../../backend/src/services/auth/complete_registration_service.py) |

## Frontend

| Компонент | Файл |
|-----------|------|
| Загрузка аватара (complete-registration) | [frontend/app/pages/complete-registration.vue](../../frontend/app/pages/complete-registration.vue) |
| Отображение аватара в профиле (apiBase + /uploads/) | [frontend/app/pages/index.vue](../../frontend/app/pages/index.vue) |

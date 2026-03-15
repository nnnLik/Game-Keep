# Профиль

Профиль пользователя: аватар, имя, тег, дата регистрации, табы с играми по стейтам.

## Backend

| Компонент | Файл |
|-----------|------|
| API GET /users/me | [backend/src/api/me.py](../../backend/src/api/me.py) |
| MeService | [backend/src/services/users/me_service.py](../../backend/src/services/users/me_service.py) |
| MeResponseDTO (username, tag, avatar_url, is_registration_complete) | [backend/src/dtos/users.py](../../backend/src/dtos/users.py) |

## Frontend

| Компонент | Файл |
|-----------|------|
| fetchMe | [frontend/app/api/users.api.ts](../../frontend/app/api/users.api.ts) |
| Страница профиля (/, index) | [frontend/app/pages/index.vue](../../frontend/app/pages/index.vue) |
| Константы табов (TABS, TAB_*_CLASSES) | [frontend/app/constants/profile.ts](../../frontend/app/constants/profile.ts) |
| Layout с сайдбаром | [frontend/app/layouts/default.vue](../../frontend/app/layouts/default.vue) |

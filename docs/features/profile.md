# Профиль

Профиль пользователя: аватар, баннер, имя, тег, дата регистрации, табы с играми по стейтам.

## Backend

| Компонент | Файл |
|-----------|------|
| API GET /users/me | [backend/src/api/me.py](../../backend/src/api/me.py) |
| API PATCH /users/me/banner | [backend/src/api/me.py](../../backend/src/api/me.py) |
| API DELETE /users/me/banner | [backend/src/api/me.py](../../backend/src/api/me.py) |
| MeService | [backend/src/services/users/me_service.py](../../backend/src/services/users/me_service.py) |
| BannerService | [backend/src/services/users/banner_service.py](../../backend/src/services/users/banner_service.py) |
| MeResponseDTO (username, tag, avatar_url, banner_url, is_registration_complete) | [backend/src/dtos/users.py](../../backend/src/dtos/users.py) |

## Frontend

| Компонент | Файл |
|-----------|------|
| fetchMe, uploadBanner, deleteBanner | [frontend/app/api/users.api.ts](../../frontend/app/api/users.api.ts) |
| Страница профиля (/, index) | [frontend/app/pages/index.vue](../../frontend/app/pages/index.vue) |
| BannerEditor (Fabric.js) | [frontend/app/components/BannerEditor.vue](../../frontend/app/components/BannerEditor.vue) |
| Константы табов (TABS, TAB_*_CLASSES) | [frontend/app/constants/profile.ts](../../frontend/app/constants/profile.ts) |
| Layout с сайдбаром | [frontend/app/layouts/default.vue](../../frontend/app/layouts/default.vue) |

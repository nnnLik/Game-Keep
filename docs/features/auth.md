# Авторизация

Логин, двухшаговая регистрация (email+пароль → имя+тег+аватар), refresh токенов.

## Backend

| Компонент | Файл |
|-----------|------|
| API (login, register, register-start, complete-registration, refresh) | [backend/src/api/auth.py](../../backend/src/api/auth.py) |
| DTO (Login, Register, Token, CompleteRegistration) | [backend/src/dtos/auth.py](../../backend/src/dtos/auth.py) |
| LoginService | [backend/src/services/auth/login_service.py](../../backend/src/services/auth/login_service.py) |
| RegisterService (legacy, полная регистрация) | [backend/src/services/auth/register_service.py](../../backend/src/services/auth/register_service.py) |
| RegisterStartService (шаг 1: email+пароль) | [backend/src/services/auth/register_start_service.py](../../backend/src/services/auth/register_start_service.py) |
| CompleteRegistrationService (шаг 2: имя, тег, аватар) | [backend/src/services/auth/complete_registration_service.py](../../backend/src/services/auth/complete_registration_service.py) |
| RefreshTokenService | [backend/src/services/auth/refresh_token_service.py](../../backend/src/services/auth/refresh_token_service.py) |
| CreatePasswordService, CreateTokenService | [backend/src/services/auth/](../../backend/src/services/auth/) |
| UserDAO | [backend/src/daos/auth/user_dao.py](../../backend/src/daos/auth/user_dao.py) |
| get_current_user | [backend/src/infra/auth.py](../../backend/src/infra/auth.py) |

## Frontend

| Компонент | Файл |
|-----------|------|
| API (login, registerStart, completeRegistration, refreshTokens) | [frontend/app/api/auth.api.ts](../../frontend/app/api/auth.api.ts) |
| Auth store (токены) | [frontend/app/stores/auth.ts](../../frontend/app/stores/auth.ts) |
| API client (401 → refresh → retry) | [frontend/app/api/base.client.ts](../../frontend/app/api/base.client.ts) |
| Middleware (редирект, проверка is_registration_complete) | [frontend/app/middleware/auth.global.ts](../../frontend/app/middleware/auth.global.ts) |
| Страница логина | [frontend/app/pages/login.vue](../../frontend/app/pages/login.vue) |
| Страница регистрации (шаг 1) | [frontend/app/pages/register.vue](../../frontend/app/pages/register.vue) |
| Страница завершения регистрации (шаг 2) | [frontend/app/pages/complete-registration.vue](../../frontend/app/pages/complete-registration.vue) |

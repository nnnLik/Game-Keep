# GameTracker (Game&Keep)

Трекер игр: профиль пользователя, коллекция игр по стейтам (backlog, in progress, completed, abandoned), добавление из Steam.

**Стек:** FastAPI + SQLite (backend), Nuxt 4 + Nuxt UI (frontend).

---

## Структура проекта

| Часть | Путь | Описание |
|-------|------|----------|
| Backend | [backend/](../backend/) | FastAPI, SQLAlchemy, Alembic |
| Frontend | [frontend/](../frontend/) | Nuxt 4, Nuxt UI, Pinia |
| Backend src | [backend/src/](../backend/src/) | API, сервисы, DAO, модели |

---

## Фичи

| Фича | Описание |
|------|----------|
| [Авторизация](features/auth.md) | Логин, регистрация (2 шага), refresh токенов |
| [Профиль](features/profile.md) | Профиль пользователя, аватар, список игр по табам |
| [Игры](features/games.md) | Добавление игры, загрузка из Steam, стейты |
| [Статика](features/static.md) | Загрузка аватаров, раздача файлов |

---

## Запуск

```bash
# Backend
cd backend && uv run src/main.py

# Frontend
cd frontend && pnpm dev
```

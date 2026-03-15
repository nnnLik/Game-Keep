# User Model & Auth Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Изменить модель User (username не уникален, добавить tag и email), обновить регистрацию и вход по email+пароль.

**Architecture:** Одна миграция Alembic добавляет email и tag, снимает unique с username. Pydantic-валидация в DTO. UserDAO — get_by_email, get_by_tag. Регистрация проверяет уникальность tag и email, возвращает отдельные ошибки.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Pydantic, Nuxt 3, Nuxt UI

---

## Task 1: Миграция — добавить email и tag, снять unique с username

**Files:**
- Create: `backend/src/migrations/versions/2026_03_15_XXXX_add_email_tag_to_user.py`
- Modify: `backend/src/models/user.py`

**Step 1: Обновить модель User**

В `backend/src/models/user.py`:
- Убрать `unique=True` у username
- Добавить `email: Mapped[str]` — unique, index
- Добавить `tag: Mapped[str]` — unique, index, String(15)

**Step 2: Создать миграцию**

```bash
cd backend && uv run alembic -c src/alembic.ini revision --autogenerate -m "add email and tag to user"
```

Проверить сгенерированную миграцию: должна добавлять колонки email и tag, убирать unique с username. При необходимости отредактировать вручную.

**Step 3: Применить миграцию**

```bash
cd backend && uv run alembic -c src/alembic.ini upgrade head
```

**Step 4: Commit**

```bash
git add backend/src/models/user.py backend/src/migrations/
git commit -m "feat: add email and tag to user, remove username unique"
```

---

## Task 2: DTO — валидация RegisterRequestDTO и LoginRequestDTO

**Files:**
- Modify: `backend/src/dtos/auth.py`

**Step 1: Обновить DTO**

```python
from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequestDTO(BaseModel):
    username: str
    tag: str
    email: EmailStr
    password: str

    @field_validator('username')
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError('Username must be at least 5 characters')
        return v

    @field_validator('tag')
    @classmethod
    def tag_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 3 or len(v) > 15:
            raise ValueError('Tag must be 3-15 characters')
        if not re.fullmatch(r'[a-z0-9]+', v):
            raise ValueError('Tag must contain only letters and digits')
        return v

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class LoginRequestDTO(BaseModel):
    email: EmailStr
    password: str
```

Добавить `email-validator` в prod dependencies в `backend/pyproject.toml`:
```
"email-validator>=2.0.0",
```

**Step 2: Commit**

```bash
git add backend/src/dtos/auth.py backend/pyproject.toml
git commit -m "feat: add validation for register and login DTOs"
```

---

## Task 3: UserDAO — get_by_email, get_by_tag, обновить create

**Files:**
- Modify: `backend/src/daos/auth/user_dao.py`

**Step 1: Обновить UserDAO**

```python
async def get_by_email(self, email: str) -> User | None:
    result = await self._session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_by_tag(self, tag: str) -> User | None:
    tag_lower = tag.strip().lower()
    result = await self._session.execute(select(User).where(User.tag == tag_lower))
    return result.scalar_one_or_none()

async def create(self, username: str, tag: str, email: str, password_hash: str) -> User:
    user = User(
        username=username,
        tag=tag.strip().lower(),
        email=email,
        password=password_hash,
    )
    self._session.add(user)
    await self._session.flush()
    await self._session.refresh(user)
    return user
```

Удалить или оставить `get_by_username` если нужен для других целей (пока можно оставить).

**Step 2: Commit**

```bash
git add backend/src/daos/auth/user_dao.py
git commit -m "feat: add get_by_email, get_by_tag, update create in UserDAO"
```

---

## Task 4: RegisterService — проверка tag и email, отдельные ошибки

**Files:**
- Modify: `backend/src/services/auth/register_service.py`
- Modify: `backend/src/dtos/auth.py` (если нужны новые исключения)

**Step 1: Добавить TagAlreadyTakenError и EmailAlreadyTakenError**

В `register_service.py`:
```python
class TagAlreadyTakenError(RegisterServiceError):
    pass

class EmailAlreadyTakenError(RegisterServiceError):
    pass
```

**Step 2: Обновить execute**

```python
async def execute(self, request: RegisterRequestDTO) -> TokenResponseDTO:
    existing_tag = await self._user_dao.get_by_tag(request.tag)
    if existing_tag:
        raise self.TagAlreadyTakenError

    existing_email = await self._user_dao.get_by_email(request.email)
    if existing_email:
        raise self.EmailAlreadyTakenError

    password_hash = self._create_password.execute(request.password)
    user = await self._user_dao.create(
        request.username,
        request.tag,
        request.email,
        password_hash,
    )
    access_token, refresh_token = self._create_token.execute(user.id)
    return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)
```

**Step 3: Commit**

```bash
git add backend/src/services/auth/register_service.py
git commit -m "feat: register checks tag and email uniqueness separately"
```

---

## Task 5: LoginService — вход по email

**Files:**
- Modify: `backend/src/services/auth/login_service.py`

**Step 1: Заменить get_by_username на get_by_email**

```python
user = await self._user_dao.get_by_email(request.email)
```

**Step 2: Commit**

```bash
git add backend/src/services/auth/login_service.py
git commit -m "feat: login by email instead of username"
```

---

## Task 6: API auth — обработка новых ошибок регистрации

**Files:**
- Modify: `backend/src/api/auth.py`

**Step 1: Добавить обработку TagAlreadyTakenError и EmailAlreadyTakenError**

```python
except RegisterService.TagAlreadyTakenError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Tag already taken',
    ) from e
except RegisterService.EmailAlreadyTakenError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Email already taken',
    ) from e
```

Удалить обработку `UserAlreadyExistsError` (или оставить для обратной совместимости — лучше удалить).

**Step 2: Commit**

```bash
git add backend/src/api/auth.py
git commit -m "feat: return specific errors for tag and email conflicts"
```

---

## Task 7: Frontend — auth.api.ts (типы и вызовы)

**Files:**
- Modify: `frontend/app/api/auth.api.ts`

**Step 1: Обновить интерфейсы**

```typescript
export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  username: string
  tag: string
  email: string
  password: string
}
```

**Step 2: Обновить register()**

```typescript
export async function register(baseURL: string, payload: RegisterPayload) {
  return $fetch<TokenResponse>(ApiEndpoint.Auth.REGISTER, {
    baseURL,
    method: 'POST',
    body: payload,
  })
}
```

**Step 3: Commit**

```bash
git add frontend/app/api/auth.api.ts
git commit -m "feat: update auth API types for email/tag"
```

---

## Task 8: Frontend — страница регистрации

**Files:**
- Modify: `frontend/app/pages/register.vue`

**Step 1: Добавить поля tag и email, обновить валидацию**

Форма: username (≥5), tag (3–15, a-z0-9), email, password (≥8).
Порядок полей: username, tag, email, password.
Показывать ошибки с бэкенда: "Tag already taken", "Email already taken" и т.д.

**Step 2: Commit**

```bash
git add frontend/app/pages/register.vue
git commit -m "feat: add tag and email to registration form"
```

---

## Task 9: Frontend — страница входа

**Files:**
- Modify: `frontend/app/pages/login.vue`

**Step 1: Заменить username на email**

- form.username → form.email
- placeholder "Email"
- autocomplete="email"

**Step 2: Commit**

```bash
git add frontend/app/pages/login.vue
git commit -m "feat: login by email instead of username"
```

---

## Task 10: Проверка и финальный коммит

**Step 1: Запустить бэкенд и проверить**

```bash
cd backend && uv run python -m uvicorn src.main:app --reload
```

**Step 2: Запустить фронтенд**

```bash
cd frontend && npm run dev
```

**Step 3: Ручная проверка**

- Регистрация с username, tag, email, password
- Ошибка при занятом tag
- Ошибка при занятом email
- Вход по email + пароль

**Step 4: Commit README/docs если нужно**

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-03-15-user-auth-implementation.md`.

**Два варианта выполнения:**

**1. Subagent-Driven (эта сессия)** — запускаю subagent на каждую задачу, проверяю между шагами.

**2. Parallel Session (отдельно)** — открыть новую сессию с executing-plans, выполнять план батчами с чекпоинтами.

Какой вариант предпочитаешь?

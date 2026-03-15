# Profile Banner Editor — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Добавить редактор баннера профиля: рисование на Fabric.js, хранение на бекенде, hover-иконки палитры и корзины.

**Architecture:** Backend — PATCH/DELETE для баннера, хранение в `uploads/banners/`. Frontend — модалка с Fabric.js, баннер в профиле с overlay при hover.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Nuxt 4, Fabric.js, Nuxt UI.

---

## Task 1: Backend — миграция и модель User

**Files:**
- Modify: `backend/src/models/user.py`
- Create: `backend/src/migrations/versions/2026_03_15_XXXX_add_banner_url_to_user.py`

**Step 1: Добавить поле banner_url в модель User**

```python
# backend/src/models/user.py — добавить после avatar_url
banner_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
```

**Step 2: Создать миграцию**

```bash
cd backend && uv run alembic -c src/alembic.ini revision --autogenerate -m "add banner_url to user"
```

**Step 3: Проверить сгенерированную миграцию**

Убедиться, что в upgrade есть `op.add_column('user', sa.Column('banner_url', sa.String(512), nullable=True))`.

**Step 4: Применить миграцию**

```bash
cd backend && uv run alembic -c src/alembic.ini upgrade head
```

**Step 5: Commit**

```bash
git add backend/src/models/user.py backend/src/migrations/
git commit -m "feat: add banner_url to User model"
```

---

## Task 2: Backend — static utils для banners

**Files:**
- Modify: `backend/src/utils/static.py`

**Step 1: Добавить get_banners_dir и создание папки**

```python
# В get_uploads_dir() добавить:
(p / 'banners').mkdir(exist_ok=True)

# Добавить функцию:
def get_banners_dir() -> str:
    return str(Path(get_uploads_dir()) / 'banners')
```

**Step 2: Commit**

```bash
git add backend/src/utils/static.py
git commit -m "feat: add get_banners_dir for banner storage"
```

---

## Task 3: Backend — UserDAO update_banner

**Files:**
- Modify: `backend/src/daos/auth/user_dao.py`

**Step 1: Добавить методы update_banner и clear_banner**

```python
async def update_banner(self, user_id: UUID, banner_url: str) -> User | None:
    user = await self.get_by_id(user_id)
    if not user:
        return None
    user.banner_url = banner_url
    await self._session.flush()
    await self._session.refresh(user)
    return user

async def clear_banner(self, user_id: UUID) -> User | None:
    user = await self.get_by_id(user_id)
    if not user:
        return None
    user.banner_url = None
    await self._session.flush()
    await self._session.refresh(user)
    return user
```

**Step 2: Commit**

```bash
git add backend/src/daos/auth/user_dao.py
git commit -m "feat: add update_banner and clear_banner to UserDAO"
```

---

## Task 4: Backend — BannerService

**Files:**
- Create: `backend/src/services/users/banner_service.py`

**Step 1: Создать BannerService**

```python
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Self
from uuid import UUID

from fastapi import UploadFile

from daos.auth.user_dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.static import get_banners_dir


@dataclass
class BannerService:
    _user_dao: UserDAO

    MAX_SIZE: ClassVar[int] = 2 * 1024 * 1024  # 2 MB

    class BannerTooLargeError(Exception):
        pass

    class InvalidFormatError(Exception):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    async def upload(self, user_id: UUID, file: UploadFile) -> str:
        if not file.filename or not file.filename.lower().endswith('.png'):
            raise self.InvalidFormatError
        content = await file.read()
        if len(content) > self.MAX_SIZE:
            raise self.BannerTooLargeError
        banners_dir = Path(get_banners_dir())
        filename = f'{user_id}.png'
        (banners_dir / filename).write_bytes(content)
        banner_url = f'banners/{filename}'
        await self._user_dao.update_banner(user_id, banner_url)
        return banner_url

    async def delete(self, user_id: UUID) -> None:
        banners_dir = Path(get_banners_dir())
        path = banners_dir / f'{user_id}.png'
        if path.exists():
            path.unlink()
        await self._user_dao.clear_banner(user_id)
```

**Step 2: Commit**

```bash
git add backend/src/services/users/banner_service.py
git commit -m "feat: add BannerService for upload/delete"
```

---

## Task 5: Backend — API endpoints и MeResponseDTO

**Files:**
- Modify: `backend/src/api/me.py`
- Modify: `backend/src/dtos/users.py`
- Modify: `backend/src/services/users/me_service.py`

**Step 1: Добавить banner_url в MeResponseDTO**

```python
# backend/src/dtos/users.py — в MeResponseDTO
banner_url: str | None
```

**Step 2: Добавить banner_url в MeService.execute**

```python
# backend/src/services/users/me_service.py
banner_url=user.banner_url,
```

**Step 3: Добавить PATCH и DELETE в me.py**

```python
# backend/src/api/me.py
from fastapi import File, UploadFile
from services.users.banner_service import BannerService

# После импортов
@router.patch('/me/banner', response_model=MeResponseDTO)
async def update_banner(
    current_user: CurrentUserDep,
    session: SessionDep,
    banner: UploadFile = File(...),
) -> MeResponseDTO:
    service = BannerService.build(session)
    try:
        await service.upload(current_user.id, banner)
    except BannerService.BannerTooLargeError:
        raise HTTPException(400, 'Banner too large (max 2 MB)')
    except BannerService.InvalidFormatError:
        raise HTTPException(400, 'Only PNG allowed')
    return await MeService.build(session).execute(current_user.id)

@router.delete('/me/banner', response_model=MeResponseDTO)
async def delete_banner(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MeResponseDTO:
    await BannerService.build(session).delete(current_user.id)
    return await MeService.build(session).execute(current_user.id)
```

**Step 4: Commit**

```bash
git add backend/src/api/me.py backend/src/dtos/users.py backend/src/services/users/me_service.py
git commit -m "feat: add PATCH/DELETE /users/me/banner, banner_url in MeResponse"
```

---

## Task 6: Frontend — API и константы

**Files:**
- Modify: `frontend/app/constants/api.ts`
- Modify: `frontend/app/api/users.api.ts`

**Step 1: Добавить эндпоинты**

```typescript
// frontend/app/constants/api.ts — в Users
ME_BANNER: '/users/me/banner',
```

**Step 2: Добавить banner_url в MeResponse и функции**

```typescript
// frontend/app/api/users.api.ts
export interface MeResponse {
  // ... existing
  banner_url: string | null
}

export async function uploadBanner(api: ApiClient, file: Blob) {
  const formData = new FormData()
  formData.append('banner', file)
  return api<MeResponse>(ApiEndpoint.Users.ME_BANNER, {
    method: 'PATCH',
    body: formData,
  })
}

export async function deleteBanner(api: ApiClient) {
  return api<MeResponse>(ApiEndpoint.Users.ME_BANNER, {
    method: 'DELETE',
  })
}
```

**Step 3: Commit**

```bash
git add frontend/app/constants/api.ts frontend/app/api/users.api.ts
git commit -m "feat: add uploadBanner, deleteBanner, banner_url in MeResponse"
```

---

## Task 7: Frontend — Fabric.js и BannerEditor

**Files:**
- Modify: `frontend/package.json` (pnpm add fabric)
- Create: `frontend/app/components/BannerEditor.vue`

**Step 1: Установить fabric**

```bash
cd frontend && pnpm add fabric
```

**Step 2: Создать BannerEditor.vue**

Компонент модалки с:
- ref на canvas
- Fabric.Canvas при mount, загрузка initialImageUrl если есть
- Инструменты: pencil, eraser, line, rect, circle
- Палитра цветов (12 цветов)
- Размер кисти (3–4 варианта)
- Zoom −/+
- Undo, Redo, Clear
- Кнопки «Отмена», «СОЗДАТЬ»
- При «СОЗДАТЬ» — canvas.toDataURL('image/png') → emit с Blob

**Step 3: Commit**

```bash
git add frontend/package.json frontend/app/components/BannerEditor.vue
git commit -m "feat: add BannerEditor with Fabric.js"
```

---

## Task 8: Frontend — интеграция в index.vue

**Files:**
- Modify: `frontend/app/pages/index.vue`

**Step 1: Обновить баннер**

- Показывать img или background-image если banner_url
- При hover — overlay с иконкой палитры (справа внизу), корзиной (справа от палитры, только если banner_url)
- Клик по палитре → открыть BannerEditor с initialImageUrl
- Клик по корзине → confirm → deleteBanner → обновить user

**Step 2: Добавить BannerEditor и логику**

- showBannerEditor ref
- openBannerEditor(initialUrl?)
- onBannerCreated(blob) → uploadBanner → обновить user
- onBannerDeleted → deleteBanner → обновить user

**Step 3: Добавить bannerFullUrl**

Аналогично avatarFullUrl: `apiBase + /uploads/ + banner_url`

**Step 4: Commit**

```bash
git add frontend/app/pages/index.vue
git commit -m "feat: integrate BannerEditor in profile page"
```

---

## Task 9: Обновить docs/features/profile.md

**Files:**
- Modify: `docs/features/profile.md`

**Step 1: Добавить описание баннера и API**

- banner_url в MeResponseDTO
- PATCH /users/me/banner, DELETE /users/me/banner
- BannerEditor, uploadBanner, deleteBanner

**Step 2: Commit**

```bash
git add docs/features/profile.md
git commit -m "docs: update profile feature with banner"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-03-15-profile-banner-implementation.md`.

**Два варианта выполнения:**

**1. Subagent-Driven (эта сессия)** — запускаю subagent на каждую задачу, проверяю между задачами.

**2. Параллельная сессия** — открыть новую сессию с executing-plans, выполнять батчами с чекпоинтами.

**Какой вариант?**

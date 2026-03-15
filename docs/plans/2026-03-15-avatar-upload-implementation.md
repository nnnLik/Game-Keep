# Avatar Upload Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Добавить возможность менять аватар на главной: клик по аватару (с hover-иконкой) → выбор файла → загрузка. Обновлять аватары в постах ленты при смене без перезагрузки.

**Architecture:** Backend — PATCH /users/me/avatar (25 МБ, jpg/png/gif/webp). Frontend — hover overlay на аватаре (index), uploadAvatar API, useAvatarChange. Feed — fetchMe + подписка на avatarVersion, обновление post.author.avatar_url для своих постов.

**Tech Stack:** FastAPI, SQLAlchemy, Nuxt 4, Nuxt UI.

---

## Task 1: Backend — UserDAO update_avatar

**Files:**
- Modify: `backend/src/daos/auth/user_dao.py`

**Step 1: Добавить метод update_avatar**

```python
# После update_banner, перед clear_banner:
async def update_avatar(self, user_id: UUID, avatar_url: str) -> User | None:
    user = await self.get_by_id(user_id)
    if not user:
        return None
    user.avatar_url = avatar_url
    await self._session.flush()
    await self._session.refresh(user)
    return user
```

**Step 2: Commit**

```bash
git add backend/src/daos/auth/user_dao.py
git commit -m "feat: add update_avatar to UserDAO"
```

---

## Task 2: Backend — UpdateAvatarService

**Files:**
- Create: `backend/src/services/users/update_avatar_service.py`

**Step 1: Создать UpdateAvatarService**

Логика как в CompleteRegistrationService (строки 92–102): ALLOWED_EXTENSIONS = jpg, jpeg, png, gif, webp; MAX_SIZE = 25 MB. Сохранение в `avatars/{user_id}.{ext}`. Вызов `user_dao.update_avatar`.

```python
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Self
from uuid import UUID

from fastapi import UploadFile

from daos.auth.user_dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession
from utils.static import get_avatars_dir


@dataclass
class UpdateAvatarService:
    _user_dao: UserDAO

    ALLOWED_EXTENSIONS: ClassVar[frozenset[str]] = frozenset({'jpg', 'jpeg', 'png', 'gif', 'webp'})
    MAX_SIZE: ClassVar[int] = 25 * 1024 * 1024  # 25 MB

    class AvatarInvalidFormatError(Exception):
        pass

    class AvatarTooLargeError(Exception):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    async def execute(self, user_id: UUID, avatar: UploadFile) -> str:
        if not avatar or not avatar.filename:
            raise self.AvatarInvalidFormatError
        ext = Path(avatar.filename).suffix.lower().lstrip('.')
        if ext not in self.ALLOWED_EXTENSIONS:
            raise self.AvatarInvalidFormatError
        content = await avatar.read()
        if len(content) > self.MAX_SIZE:
            raise self.AvatarTooLargeError
        avatars_dir = Path(get_avatars_dir())
        filename = f'{user_id}.{ext}'
        (avatars_dir / filename).write_bytes(content)
        avatar_url = f'avatars/{filename}'
        await self._user_dao.update_avatar(user_id, avatar_url)
        return avatar_url
```

**Step 2: Commit**

```bash
git add backend/src/services/users/update_avatar_service.py
git commit -m "feat: add UpdateAvatarService"
```

---

## Task 3: Backend — PATCH /users/me/avatar

**Files:**
- Modify: `backend/src/api/me.py`

**Step 1: Добавить эндпоинт**

```python
# Импорт:
from services.users.update_avatar_service import UpdateAvatarService

# После update_banner, перед delete_banner:
@router.patch('/me/avatar', response_model=MeResponseDTO)
async def update_avatar(
    current_user: CurrentUserDep,
    session: SessionDep,
    avatar: UploadFile = File(...),
) -> MeResponseDTO:
    service = UpdateAvatarService.build(session)
    try:
        await service.execute(current_user.id, avatar)
    except UpdateAvatarService.AvatarInvalidFormatError:
        raise HTTPException(
            400,
            f'Неверный формат аватара. Допустимы: {", ".join(UpdateAvatarService.ALLOWED_EXTENSIONS)}',
        )
    except UpdateAvatarService.AvatarTooLargeError:
        raise HTTPException(400, 'Аватар слишком большой (макс. 25 МБ)')
    return await MeService.build(session).execute(current_user.id)
```

**Step 2: Commit**

```bash
git add backend/src/api/me.py
git commit -m "feat: add PATCH /users/me/avatar endpoint"
```

---

## Task 4: Frontend — API и константы

**Files:**
- Modify: `frontend/app/constants/api.ts`
- Modify: `frontend/app/api/users.api.ts`

**Step 1: Добавить ME_AVATAR в ApiEndpoint**

```typescript
// frontend/app/constants/api.ts — в Users добавить:
ME_AVATAR: '/users/me/avatar',
```

**Step 2: Добавить uploadAvatar**

```typescript
// frontend/app/api/users.api.ts — после uploadBanner:
export async function uploadAvatar(api: ApiClient, file: File) {
  const formData = new FormData()
  formData.append('avatar', file)
  return api<MeResponse>(ApiEndpoint.Users.ME_AVATAR, {
    method: 'PATCH',
    body: formData,
  })
}
```

**Step 3: Commit**

```bash
git add frontend/app/constants/api.ts frontend/app/api/users.api.ts
git commit -m "feat: add uploadAvatar API"
```

---

## Task 5: Frontend — hover и загрузка аватара на index

**Files:**
- Modify: `frontend/app/pages/index.vue`

**Step 1: Импорт uploadAvatar**

В блоке `const { fetchMe, fetchMyGames, uploadBanner, deleteBanner }` добавить `uploadAvatar`.

**Step 2: Добавить ref для input и обработчики**

```typescript
const avatarInputRef = ref<HTMLInputElement | null>(null)
const avatarUploading = ref(false)

function openAvatarPicker() {
  avatarInputRef.value?.click()
}

async function onAvatarFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || avatarUploading.value) return
  if (!file.type.startsWith('image/')) {
    toast.add({ title: 'Выберите изображение (jpg, png, gif, webp)', color: 'error' })
    return
  }
  if (file.size > 25 * 1024 * 1024) {
    toast.add({ title: 'Файл не более 25 МБ', color: 'error' })
    return
  }
  avatarUploading.value = true
  try {
    const updated = await uploadAvatar($api, file)
    user.value = updated
    useAvatarChange().emitAvatarChange()
    toast.add({ title: 'Аватар обновлён', color: 'success' })
  } catch (err: unknown) {
    const d = (err as { data?: { detail?: string } })?.data?.detail
    toast.add({ title: 'Ошибка', description: typeof d === 'string' ? d : 'Не удалось загрузить', color: 'error' })
  } finally {
    avatarUploading.value = false
  }
}
```

**Step 3: Обернуть блок аватара в group, добавить overlay и input**

Заменить блок аватара (строки ~386–397) на:

```vue
<div
  class="group relative -mt-20 flex size-36 shrink-0 items-center justify-center overflow-hidden self-start rounded-full border-4 border-gray-950 bg-gray-600"
  aria-label="Аватар"
>
  <input
    ref="avatarInputRef"
    type="file"
    accept="image/jpeg,image/png,image/gif,image/webp"
    class="hidden"
    @change="onAvatarFileChange"
  />
  <img
    v-if="avatarFullUrl(user.avatar_url)"
    :src="avatarFullUrl(user.avatar_url) ?? ''"
    :alt="user.username ?? 'Аватар'"
    class="size-full object-cover"
  />
  <Icon v-else name="lucide:user" class="size-20 text-gray-400" />
  <div
    class="absolute inset-0 flex items-center justify-center rounded-full bg-black/0 opacity-0 transition group-hover:bg-black/40 group-hover:opacity-100"
  >
    <button
      type="button"
      class="flex size-10 items-center justify-center rounded-full bg-gray-800/90 text-white transition hover:bg-gray-700 disabled:opacity-50"
      aria-label="Изменить аватар"
      :disabled="avatarUploading"
      @click.stop="openAvatarPicker"
    >
      <Icon name="lucide:camera" class="size-5" />
    </button>
  </div>
</div>
```

**Step 4: Commit**

```bash
git add frontend/app/pages/index.vue
git commit -m "feat: add avatar upload on index page"
```

---

## Task 6: Frontend — события в ленте

**Files:**
- Modify: `frontend/app/pages/feed.vue`

**Step 1: Импорт fetchMe**

```typescript
import { fetchMe } from '~/api/users.api'
```

**Step 2: Добавить currentUser и подписку**

```typescript
const currentUser = ref<Awaited<ReturnType<typeof fetchMe>> | null>(null)
const { avatarVersion } = useAvatarChange()

watch(avatarVersion, async () => {
  if (!currentUser.value?.tag || posts.value.length === 0) return
  try {
    const me = await fetchMe($api)
    currentUser.value = me
    const newAvatar = me.avatar_url
    for (const post of posts.value) {
      if (post.author?.tag === me.tag) {
        post.author.avatar_url = newAvatar
      }
    }
  } catch {
    // ignore
  }
})
```

**Step 3: Загружать currentUser в onMounted**

В первом onMounted, перед loadFeed():

```typescript
try {
  currentUser.value = await fetchMe($api)
} catch {
  // not authenticated or error
}
loadFeed()
```

**Step 4: Commit**

```bash
git add frontend/app/pages/feed.vue
git commit -m "feat: update feed post avatars on avatar change"
```

---

## Task 7: Ручная проверка

**Step 1: Запустить backend и frontend**

```bash
cd backend && uv run uvicorn main:app --reload
cd frontend && npm run dev
```

**Step 2: Проверить**

- Войти, открыть главную
- Навести на аватар → иконка камеры
- Клик → выбор файла → загрузка → toast «Аватар обновлён»
- Открыть ленту → свои посты показывают новый аватар
- Сменить аватар снова, оставаясь на ленте → аватары в постах обновляются без перезагрузки

**Step 3: Commit (если всё ок)**

```bash
git add -A && git status
git commit -m "chore: verify avatar upload flow"  # если есть незакоммиченные изменения
```

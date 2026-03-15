# Коллекционеры — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Вкладка «Коллекционеры» со списком пользователей (сортировка по games_count), cursor-based пагинация, переход в профиль `/users/[tag]`.

**Architecture:** Backend — `GET /users` с limit/cursor, сервис ListUsersService, UserDAO.get_list_with_games_count. Frontend — страница `/collectors`, пункт в сайдбаре, API fetchUsersList. Профиль по тегу уже есть (`/@[tag]`), добавляем алиас `/users/[tag]` для единообразия.

**Tech Stack:** FastAPI, SQLAlchemy, Nuxt 3, Vue 3, Tailwind.

---

## Phase 1: Backend — API списка пользователей

### Task 1: DTO UsersListResponseDTO

**Files:**
- Modify: `backend/src/dtos/users.py`

**Step 1: Добавить DTO**

В конец `backend/src/dtos/users.py`:

```python
class UserListItemDTO(BaseModel):
    tag: str | None
    username: str | None
    avatar_url: str | None
    games_count: int


class UsersListResponseDTO(BaseModel):
    items: list[UserListItemDTO]
    next_cursor: str | None
    has_more: bool
```

**Step 2: Commit**

```bash
git add backend/src/dtos/users.py
git commit -m "feat: add UsersListResponseDTO and UserListItemDTO"
```

---

### Task 2: UserDAO — get_list_with_games_count

**Files:**
- Modify: `backend/src/daos/auth/user_dao.py`

**Step 1: Добавить метод**

Импорт: `from sqlalchemy import select, func`

В `UserDAO` добавить:

```python
async def get_list_with_games_count(
    self,
    limit: int,
    cursor_games_count: int | None = None,
    cursor_user_id: UUID | None = None,
) -> list[tuple[User, int]]:
    """Возвращает [(user, games_count), ...] для пользователей с is_registration_complete и >= 1 игры.
    Сортировка: games_count DESC, user_id ASC.
    Курсор: (cursor_games_count, cursor_user_id) — исключить строки до этой позиции."""
    from models.user_game import UserGame

    subq = (
        select(User.id, func.count(UserGame.id).label('games_count'))
        .select_from(User)
        .join(UserGame, User.id == UserGame.user_id)
        .where(User.is_registration_complete == True)
        .group_by(User.id)
        .having(func.count(UserGame.id) >= 1)
    ).subquery()

    stmt = (
        select(User, subq.c.games_count)
        .join(subq, User.id == subq.c.id)
        .order_by(subq.c.games_count.desc(), User.id.asc())
    )

    if cursor_games_count is not None and cursor_user_id is not None:
        stmt = stmt.where(
            (subq.c.games_count < cursor_games_count)
            | ((subq.c.games_count == cursor_games_count) & (User.id > cursor_user_id))
        )

    stmt = stmt.limit(limit + 1)
    result = await self._session.execute(stmt)
    rows = list(result.all())
    return rows
```

**Step 2: Commit**

```bash
git add backend/src/daos/auth/user_dao.py
git commit -m "feat: add get_list_with_games_count to UserDAO"
```

---

### Task 3: ListUsersService

**Files:**
- Create: `backend/src/services/users/list_users_service.py`

**Step 1: Создать сервис**

```python
import base64
import json
from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.auth.user_dao import UserDAO
from dtos.users import UserListItemDTO, UsersListResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ListUsersService:
    _user_dao: UserDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_dao=UserDAO.build(session))

    def _encode_cursor(self, games_count: int, user_id: UUID) -> str:
        payload = {"g": games_count, "u": str(user_id)}
        return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    def _decode_cursor(self, cursor: str) -> tuple[int, UUID] | None:
        try:
            raw = base64.urlsafe_b64decode(cursor.encode())
            data = json.loads(raw.decode())
            return (data["g"], UUID(data["u"]))
        except Exception:
            return None

    async def execute(
        self,
        limit: int = 20,
        cursor: str | None = None,
    ) -> UsersListResponseDTO:
        limit = max(1, min(100, limit))
        cursor_games_count, cursor_user_id = (None, None)
        if cursor:
            decoded = self._decode_cursor(cursor)
            if decoded:
                cursor_games_count, cursor_user_id = decoded

        rows = await self._user_dao.get_list_with_games_count(
            limit=limit + 1,
            cursor_games_count=cursor_games_count,
            cursor_user_id=cursor_user_id,
        )

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        items = [
            UserListItemDTO(
                tag=u.tag,
                username=u.username,
                avatar_url=u.avatar_url,
                games_count=gc,
            )
            for u, gc in rows
        ]

        next_cursor = None
        if has_more and rows:
            last_user, last_gc = rows[-1]
            next_cursor = self._encode_cursor(last_gc, last_user.id)

        return UsersListResponseDTO(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
        )
```

**Step 2: Commit**

```bash
git add backend/src/services/users/list_users_service.py
git commit -m "feat: add ListUsersService for cursor pagination"
```

---

### Task 4: API GET /users

**Files:**
- Modify: `backend/src/api/me.py`

**Step 1: Добавить endpoint**

Импорт: `from services.users.list_users_service import ListUsersService`

В начале файла добавить импорт: `from fastapi import Query`

Перед `@router.get('/me'` добавить:

```python
@router.get('', response_model=UsersListResponseDTO)
async def list_users(
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(None),
) -> UsersListResponseDTO:
    service = ListUsersService.build(session)
    return await service.execute(limit=limit, cursor=cursor)
```

Добавить импорт `ListUsersService` и `UsersListResponseDTO` из dtos.users.

**Step 2: Проверить порядок роутов**

Важно: `GET /users` (пустой путь) должен быть зарегистрирован. Роутер имеет prefix `/users`, поэтому `''` даёт `GET /users`. Роут `/me` — `GET /users/me`. FastAPI сопоставляет по специфичности, `''` и `me` не конфликтуют.

**Step 3: Commit**

```bash
git add backend/src/api/me.py
git commit -m "feat: add GET /users for collectors list"
```

---

## Phase 2: Frontend — страница и навигация

### Task 5: API endpoint и fetchUsersList

**Files:**
- Modify: `frontend/app/constants/api.ts`
- Modify: `frontend/app/api/users.api.ts`

**Step 1: Добавить endpoint**

В `ApiEndpoint.Users`:

```ts
LIST: '/users',
```

**Step 2: Добавить интерфейсы и функцию**

В `frontend/app/api/users.api.ts`:

```ts
export interface UserListItem {
  tag: string | null
  username: string | null
  avatar_url: string | null
  games_count: number
}

export interface UsersListResponse {
  items: UserListItem[]
  next_cursor: string | null
  has_more: boolean
}

export async function fetchUsersList(
  api: ApiClient,
  params?: { limit?: number; cursor?: string | null }
) {
  const searchParams = new URLSearchParams()
  if (params?.limit) searchParams.set('limit', String(params.limit))
  if (params?.cursor) searchParams.set('cursor', params.cursor)
  const query = searchParams.toString()
  const url = query ? `${ApiEndpoint.Users.LIST}?${query}` : ApiEndpoint.Users.LIST
  return api<UsersListResponse>(url)
}
```

**Step 3: Commit**

```bash
git add frontend/app/constants/api.ts frontend/app/api/users.api.ts
git commit -m "feat: add fetchUsersList API"
```

---

### Task 6: Страница /collectors

**Files:**
- Create: `frontend/app/pages/collectors.vue`

**Step 1: Создать страницу**

```vue
<script setup lang="ts">
import { fetchUsersList } from '~/api/users.api'
import type { UserListItem } from '~/api/users.api'

definePageMeta({
  layout: 'default',
})

const { $api } = useNuxtApp()
const config = useRuntimeConfig()

const users = ref<UserListItem[]>([])
const nextCursor = ref<string | null>(null)
const hasMore = ref(false)
const loading = ref(true)
const loadMoreLoading = ref(false)
const error = ref<string | null>(null)

function avatarFullUrl(avatarUrl: string | null | undefined): string | null {
  if (!avatarUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${avatarUrl}`
}

async function loadInitial() {
  loading.value = true
  error.value = null
  try {
    const res = await fetchUsersList($api, { limit: 20 })
    users.value = res.items
    nextCursor.value = res.next_cursor
    hasMore.value = res.has_more
  } catch {
    error.value = 'Не удалось загрузить список'
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!nextCursor.value || loadMoreLoading.value) return
  loadMoreLoading.value = true
  try {
    const res = await fetchUsersList($api, { limit: 20, cursor: nextCursor.value })
    users.value = [...users.value, ...res.items]
    nextCursor.value = res.next_cursor
    hasMore.value = res.has_more
  } catch {
    useToast().add({ title: 'Ошибка загрузки', color: 'error' })
  } finally {
    loadMoreLoading.value = false
  }
}

onMounted(loadInitial)
</script>

<template>
  <div>
    <h1 class="text-4xl font-bold text-white mb-8">Коллекционеры</h1>

    <div v-if="loading" class="text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="flex flex-col gap-4">
      <p class="text-red-400">{{ error }}</p>
      <UButton variant="soft" @click="loadInitial">Повторить</UButton>
    </div>
    <template v-else>
      <ul class="flex flex-col gap-2">
        <li v-for="u in users" :key="u.tag ?? ''">
          <NuxtLink
            :to="u.tag ? `/users/${u.tag}` : '#'"
            class="flex items-center gap-4 rounded-lg bg-gray-800/50 px-4 py-3 transition-colors hover:bg-gray-800"
          >
            <div
              class="flex size-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gray-600"
            >
              <img
                v-if="avatarFullUrl(u.avatar_url)"
                :src="avatarFullUrl(u.avatar_url) ?? ''"
                :alt="u.username ?? 'Аватар'"
                class="size-full object-cover"
              />
              <Icon v-else name="lucide:user" class="size-7 text-gray-400" />
            </div>
            <div class="flex-1 min-w-0">
              <span class="font-medium text-white block truncate">{{ u.username ?? 'Без имени' }}</span>
              <span v-if="u.tag" class="text-gray-400 text-sm">@{{ u.tag }}</span>
            </div>
            <span class="text-gray-400 text-sm shrink-0">
              {{ u.games_count }} {{ u.games_count === 1 ? 'игра' : u.games_count < 5 ? 'игры' : 'игр' }}
            </span>
          </NuxtLink>
        </li>
        <li v-if="users.length === 0" class="py-8 text-center text-gray-500">
          Пока никого нет
        </li>
      </ul>

      <div v-if="hasMore" class="mt-6">
        <UButton
          variant="soft"
          color="neutral"
          :loading="loadMoreLoading"
          block
          @click="loadMore"
        >
          Загрузить ещё
        </UButton>
      </div>
    </template>
  </div>
</template>
```

**Step 2: Commit**

```bash
git add frontend/app/pages/collectors.vue
git commit -m "feat: add collectors page"
```

---

### Task 7: Пункт «Коллекционеры» в сайдбаре

**Files:**
- Modify: `frontend/app/layouts/default.vue`

**Step 1: Добавить ссылку**

После ссылки на Лента, перед `</nav>`:

```vue
<NuxtLink
  to="/collectors"
  class="flex items-center gap-4 rounded-full px-5 py-4 text-lg text-white hover:bg-gray-800/50 transition-colors"
  active-class="!bg-gray-800"
>
  <Icon name="lucide:users" class="size-7 shrink-0" />
  Коллекционеры
</NuxtLink>
```

**Step 2: Commit**

```bash
git add frontend/app/layouts/default.vue
git commit -m "feat: add Collectors nav item"
```

---

### Task 8: Страница /users/[tag]

**Files:**
- Create: `frontend/app/pages/users/[tag].vue`

**Step 1: Создать страницу**

Скопировать логику из `app/pages/@[tag].vue`, заменить ссылку «Назад» на `/collectors`:

```vue
<script setup lang="ts">
import {
  DEFAULT_GAME_STATE,
  TAB_ACTIVE_CLASSES,
  TAB_BADGE_CLASSES,
  TAB_ICON_CLASSES,
  TABS,
} from '~/constants'
import { fetchProfileByTag } from '~/api/users.api'
import type { ProfileByTagResponse } from '~/api/users.api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const tag = computed(() => String(route.params.tag))
const { $api } = useNuxtApp()

const profile = ref<ProfileByTagResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

type TabId = (typeof TABS)[number]['id']
const activeTab = ref<TabId>(DEFAULT_GAME_STATE)

const filteredGames = computed(() => {
  if (!profile.value) return []
  if (activeTab.value === 'favorites') {
    return profile.value.games.filter((g) => g.is_favorite)
  }
  return profile.value.games.filter((g) => g.state === activeTab.value)
})

const tabCounts = computed(() => {
  const counts: Record<string, number> = {}
  if (!profile.value) return counts
  for (const t of TABS) {
    if (t.id === 'favorites') {
      counts[t.id] = profile.value.games.filter((g) => g.is_favorite).length
    } else {
      counts[t.id] = profile.value.games.filter((g) => g.state === t.id).length
    }
  }
  return counts
})

const config = useRuntimeConfig()

function avatarFullUrl(avatarUrl: string | null | undefined): string | null {
  if (!avatarUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${avatarUrl}`
}

function bannerFullUrl(bannerUrl: string | null | undefined): string | null {
  if (!bannerUrl) return null
  const base = (config.public.apiBase as string) || ''
  return `${base.replace(/\/$/, '')}/uploads/${bannerUrl}`
}

function formatRegistrationDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const date = new Date(iso)
  const month = date.toLocaleDateString('ru-RU', { month: 'long' })
  const year = date.getFullYear()
  return `${month} ${year} г.`
}

onMounted(async () => {
  try {
    profile.value = await fetchProfileByTag($api, tag.value)
  } catch (e: unknown) {
    const err = e as { statusCode?: number }
    if (err?.statusCode === 404) {
      error.value = 'Пользователь не найден'
    } else {
      error.value = 'Не удалось загрузить профиль'
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="mb-4">
      <NuxtLink
        to="/collectors"
        class="inline-flex items-center gap-2 text-gray-400 transition hover:text-white"
      >
        <Icon name="lucide:arrow-left" class="size-4" />
        Назад к коллекционерам
      </NuxtLink>
    </div>

    <div v-if="loading" class="text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="flex flex-col gap-4">
      <p class="text-red-400">{{ error }}</p>
      <NuxtLink to="/collectors" class="text-emerald-400 hover:underline">
        Вернуться к коллекционерам
      </NuxtLink>
    </template>
    <template v-else-if="profile">
      <!-- Остальной шаблон как в @[tag].vue -->
      <div class="mb-10">
        <div
          class="relative h-40 w-full rounded-t-2xl bg-gray-700/50 bg-cover bg-center"
          :style="
            bannerFullUrl(profile.banner_url)
              ? { backgroundImage: `url(${bannerFullUrl(profile.banner_url)})` }
              : {}
          "
          aria-label="Баннер профиля"
        />
        <div
          class="relative -mt-20 flex size-36 shrink-0 items-center justify-center overflow-hidden self-start rounded-full border-4 border-gray-950 bg-gray-600"
          aria-label="Аватар"
        >
          <img
            v-if="avatarFullUrl(profile.avatar_url)"
            :src="avatarFullUrl(profile.avatar_url) ?? ''"
            :alt="profile.username ?? 'Аватар'"
            class="size-full object-cover"
          />
          <Icon v-else name="lucide:user" class="size-20 text-gray-400" />
        </div>
        <div class="mt-4 flex flex-col gap-1">
          <div class="flex items-baseline gap-2">
            <h1 class="text-2xl font-bold text-white">
              {{ profile.username ?? 'Удалённый пользователь' }}
            </h1>
            <span v-if="profile.tag" class="text-gray-400">@{{ profile.tag }}</span>
          </div>
          <div
            v-if="profile.created_at"
            class="flex items-center gap-2 text-gray-400"
          >
            <Icon name="lucide:calendar" class="size-4 shrink-0" />
            <span>Регистрация: {{ formatRegistrationDate(profile.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="mb-6">
        <div class="flex gap-1 border-b border-gray-700" role="tablist">
          <button
            v-for="tab in TABS"
            :key="tab.id"
            type="button"
            role="tab"
            :aria-selected="activeTab === tab.id"
            class="flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors"
            :class="
              activeTab === tab.id
                ? TAB_ACTIVE_CLASSES[tab.colorKey]
                : 'border-transparent text-gray-400 hover:text-gray-300'
            "
            @click="activeTab = tab.id"
          >
            <Icon
              :name="tab.icon"
              class="size-4 shrink-0"
              :class="activeTab === tab.id ? TAB_ICON_CLASSES[tab.colorKey] : ''"
            />
            <span>{{ tab.label }}</span>
            <span
              class="rounded-full px-2 py-0.5 text-xs"
              :class="
                activeTab === tab.id
                  ? TAB_BADGE_CLASSES[tab.colorKey]
                  : 'bg-gray-700/80 text-gray-400'
              "
            >
              {{ tabCounts[tab.id] }}
            </span>
          </button>
        </div>
      </div>

      <ul class="flex flex-col gap-2">
        <li v-for="game in filteredGames" :key="game.id">
          <NuxtLink
            :to="`/games/${game.id}`"
            class="flex items-center gap-4 rounded-lg bg-gray-800/50 px-4 py-3 transition-colors hover:bg-gray-800"
          >
            <div
              class="flex size-14 shrink-0 items-center justify-center overflow-hidden rounded bg-gray-600"
              aria-hidden
            >
              <img
                v-if="game.image_url"
                :src="game.image_url"
                :alt="game.name"
                class="h-full w-full object-cover"
              />
              <Icon v-else name="lucide:gamepad-2" class="size-7 text-gray-400" />
            </div>
            <span class="font-medium text-white">{{ game.name }}</span>
            <Icon
              v-if="game.is_favorite"
              name="lucide:heart"
              class="ml-auto size-4 shrink-0 fill-red-500 text-red-500"
            />
          </NuxtLink>
        </li>
        <li v-if="filteredGames.length === 0" class="py-8 text-center text-gray-500">
          В этой категории пока нет игр
        </li>
      </ul>
    </template>
  </div>
</template>
```

**Step 2: Commit**

```bash
git add frontend/app/pages/users/[tag].vue
git commit -m "feat: add /users/[tag] profile page"
```

---

## Phase 3: Проверка

### Task 9: Ручная проверка

**Step 1: Запустить backend**

```bash
cd backend && uv run src/main.py
```

**Step 2: Запустить frontend**

```bash
cd frontend && pnpm dev
```

**Step 3: Проверить**

- Открыть `/collectors` — список пользователей
- Нажать «Загрузить ещё» (если есть данные)
- Клик по пользователю → `/users/[tag]`
- 404 → сообщение + ссылка на коллекционеров

**Step 4: Commit (если всё ок)**

```bash
git status
git add -A
git commit -m "chore: collectors feature complete"
```

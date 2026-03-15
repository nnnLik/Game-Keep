# Create Game Form Improvements — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Улучшить форму создания игры: шире модалка, кнопки (Отмена слева), layout «картинка слева — данные справа», genres/developers/publishers из Steam API.

**Architecture:** Backend: FetchSteamGameService возвращает genres/developers/publishers; UserGame хранит JSON; CreateGameService принимает новые поля. Frontend: CreateGameModal — max-w-3xl, grid layout, кнопки justify-between.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Nuxt 4, Vue 3

---

## Task 1: Backend — миграция user_game (genres, developers, publishers)

**Files:**
- Create: `backend/src/migrations/versions/2026_03_15_XXXX-add_genres_developers_publishers_to_user_game.py`

**Step 1: Создать миграцию**

```bash
cd backend && uv run alembic revision -m "add genres developers publishers to user_game"
```

**Step 2: Заполнить upgrade/downgrade**

В созданном файле миграции (добавить `import sqlalchemy as sa` если нет):

```python
def upgrade() -> None:
    op.add_column('user_game', sa.Column('genres', sa.Text(), nullable=True))
    op.add_column('user_game', sa.Column('developers', sa.Text(), nullable=True))
    op.add_column('user_game', sa.Column('publishers', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('user_game', 'publishers')
    op.drop_column('user_game', 'developers')
    op.drop_column('user_game', 'genres')
```

**Step 3: Применить миграцию**

```bash
cd backend && uv run alembic upgrade head
```

Expected: Success

**Step 4: Commit**

```bash
git add backend/src/migrations/
git commit -m "feat(backend): add genres, developers, publishers to user_game"
```

---

## Task 2: Backend — модель UserGame

**Files:**
- Modify: `backend/src/models/user_game.py`

**Step 1: Добавить колонки**

```python
# После steam_app_id добавить:
genres: Mapped[str | None] = mapped_column(String(2048), nullable=True)  # JSON
developers: Mapped[str | None] = mapped_column(String(1024), nullable=True)  # JSON
publishers: Mapped[str | None] = mapped_column(String(1024), nullable=True)  # JSON
```

**Step 2: Проверка**

```bash
cd backend/src && uv run python -c "from models.user_game import UserGame; print('OK')"
```

**Step 3: Commit**

```bash
git add backend/src/models/user_game.py
git commit -m "feat(backend): UserGame model genres, developers, publishers"
```

---

## Task 3: Backend — FetchSteamGameService и FetchSteamResponseDTO

**Files:**
- Modify: `backend/src/services/games/fetch_steam_game_service.py`
- Modify: `backend/src/dtos/games.py`

**Step 1: Обновить FetchSteamResponseDTO**

В `backend/src/dtos/games.py`:

```python
from pydantic import BaseModel


class GenreDTO(BaseModel):
    id: str
    description: str


class FetchSteamResponseDTO(BaseModel):
    name: str
    image_url: str | None
    steam_app_id: str
    genres: list[GenreDTO] = []
    developers: list[str] = []
    publishers: list[str] = []
```

**Step 2: Обновить FetchSteamGameResult и execute**

В `backend/src/services/games/fetch_steam_game_service.py`:

```python
from dtos.games import GenreDTO

@dataclass
class FetchSteamGameResult:
    name: str
    image_url: str | None
    steam_app_id: str
    genres: list[GenreDTO]
    developers: list[str]
    publishers: list[str]
```

В методе `execute`, заменить `return FetchSteamGameResult(...)`:

```python
genres = [
    GenreDTO(id=str(g.get('id', '')), description=str(g.get('description', '')))
    for g in (game_detail_dto.genres or [])
    if isinstance(g, dict)
]
developers = list(game_detail_dto.developers or [])
publishers = list(game_detail_dto.publishers or [])

return FetchSteamGameResult(
    name=game_detail_dto.name,
    image_url=game_detail_dto.header_image,
    steam_app_id=app_id,
    genres=genres,
    developers=developers,
    publishers=publishers,
)
```

**Step 3: Обновить API user_games**

В `backend/src/api/user_games.py` в `fetch_steam_game`:

```python
return FetchSteamResponseDTO(
    name=result.name,
    image_url=result.image_url,
    steam_app_id=result.steam_app_id,
    genres=[GenreDTO(id=g.id, description=g.description) for g in result.genres],
    developers=result.developers,
    publishers=result.publishers,
)
```

**Step 4: Проверка**

```bash
curl -X POST http://localhost:9999/users/me/games/fetch-steam \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"steam_url":"https://store.steampowered.com/app/2050650/"}'
```

Expected: JSON с name, image_url, steam_app_id, genres, developers, publishers

**Step 5: Commit**

```bash
git add backend/src/dtos/games.py backend/src/services/games/fetch_steam_game_service.py backend/src/api/user_games.py
git commit -m "feat(backend): fetch-steam returns genres, developers, publishers"
```

---

## Task 4: Backend — CreateGameRequestDTO, UserGameDAO, CreateGameService, GameResponseDTO

**Files:**
- Modify: `backend/src/dtos/users.py`
- Modify: `backend/src/daos/games/user_game_dao.py`
- Modify: `backend/src/services/users/create_game_service.py`
- Modify: `backend/src/services/users/my_games_service.py`
- Modify: `backend/src/api/user_games.py`

**Step 1: CreateGameRequestDTO**

В `backend/src/dtos/users.py` добавить в `CreateGameRequestDTO`:

```python
genres: list[dict[str, str]] | None = None  # [{"id":"1","description":"Action"}]
developers: list[str] | None = None
publishers: list[str] | None = None
```

**Step 2: GameResponseDTO**

В `backend/src/dtos/users.py` добавить в `GameResponseDTO`:

```python
genres: list[dict[str, str]] | None = None
developers: list[str] | None = None
publishers: list[str] | None = None
```

**Step 3: UserGameDAO.create**

В `backend/src/daos/games/user_game_dao.py` добавить параметры и в UserGame:

```python
import json

# В create():
genres: str | None = None,
developers: str | None = None,
publishers: str | None = None,

# В UserGame():
genres=genres,
developers=developers,
publishers=publishers,
```

**Step 4: CreateGameService**

В `backend/src/services/users/create_game_service.py`:

```python
import json

# В execute() при вызове dao.create добавить:
genres=json.dumps(data.genres) if data.genres else None,
developers=json.dumps(data.developers) if data.developers else None,
publishers=json.dumps(data.publishers) if data.publishers else None,
```

**Step 5: MyGamesService**

В `backend/src/services/users/my_games_service.py` в GameResponseDTO:

```python
import json

GameResponseDTO(
    ...
    genres=json.loads(g.genres) if g.genres else None,
    developers=json.loads(g.developers) if g.developers else None,
    publishers=json.loads(g.publishers) if g.publishers else None,
)
```

**Step 6: Проверка**

```bash
curl -X POST http://localhost:9999/users/me/games \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","state":"backlog","genres":[{"id":"1","description":"Action"}],"developers":["Capcom"],"publishers":["Capcom"]}'
```

**Step 7: Commit**

```bash
git add backend/src/dtos/users.py backend/src/daos/games/user_game_dao.py backend/src/services/users/create_game_service.py backend/src/services/users/my_games_service.py
git commit -m "feat(backend): create game accepts genres, developers, publishers"
```

---

## Task 5: Frontend — API типы и CreateGamePayload

**Files:**
- Modify: `frontend/app/api/users.api.ts`

**Step 1: Обновить интерфейсы**

```typescript
export interface GenreItem {
  id: string
  description: string
}

export interface FetchSteamResponse {
  name: string
  image_url: string | null
  steam_app_id: string
  genres: GenreItem[]
  developers: string[]
  publishers: string[]
}

export interface GameResponse {
  id: number
  name: string
  image_url: string | null
  steam_app_id: string | null
  state: string
  is_favorite: boolean
  genres: GenreItem[] | null
  developers: string[] | null
  publishers: string[] | null
}

export interface CreateGamePayload {
  name: string
  image_url?: string | null
  steam_app_id?: string | null
  state: string
  is_favorite?: boolean
  genres?: GenreItem[] | null
  developers?: string[] | null
  publishers?: string[] | null
}
```

**Step 2: Commit**

```bash
git add frontend/app/api/users.api.ts
git commit -m "feat(frontend): API types for genres, developers, publishers"
```

---

## Task 6: Frontend — CreateGameModal UI (размер, кнопки шаг 1)

**Files:**
- Modify: `frontend/app/components/CreateGameModal.vue`

**Step 1: Размер модалки**

Заменить `max-w-lg` на `max-w-3xl` в div модалки (строка ~197).

**Step 2: Кнопки шаг 1**

Заменить блок кнопок (строки ~260-283):

```html
<div class="flex justify-between gap-2">
  <button
    type="button"
    class="rounded-lg px-4 py-2 text-gray-400 hover:text-white"
    @click="closeWithDraft"
  >
    Отмена
  </button>
  <div class="flex gap-2">
    <button
      type="button"
      class="rounded-lg px-4 py-2 text-gray-300 hover:text-white"
      @click="goToStep2"
    >
      Пропустить
    </button>
    <button
      type="button"
      :disabled="fetching"
      class="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
      @click="goToStep2"
    >
      {{ fetching ? 'Загрузка...' : 'Далее' }}
    </button>
  </div>
</div>
```

**Step 3: Commit**

```bash
git add frontend/app/components/CreateGameModal.vue
git commit -m "feat(frontend): modal max-w-3xl, step1 buttons justify-between"
```

---

## Task 7: Frontend — CreateGameModal форма (grid layout, genres, developers, publishers)

**Files:**
- Modify: `frontend/app/components/CreateGameModal.vue`

**Step 1: Расширить form и draft**

В `form` reactive добавить:
```typescript
genres: [] as { id: string; description: string }[],
developers: [] as string[],
publishers: [] as string[],
```

В `goToStep2` после `form.name = data.name` и т.д. добавить:
```typescript
form.genres = data.genres ?? []
form.developers = data.developers ?? []
form.publishers = data.publishers ?? []
```

В `closeWithDraft` emit добавить genres, developers, publishers.

В watch initialDraft добавить восстановление genres, developers, publishers.

**Step 2: Заменить шаг 2 на grid layout**

Левая колонка: картинка + URL. Правая: name, genres (теги), developers, publishers, state, is_favorite.

```html
<div class="grid grid-cols-1 gap-4 md:grid-cols-[minmax(160px,200px)_1fr]">
  <!-- Левая колонка -->
  <div class="flex flex-col gap-3">
    <div class="aspect-[460/215] w-full overflow-hidden rounded-lg bg-gray-700">
      <img v-if="form.image_url" :src="form.image_url" alt="Обложка" class="h-full w-full object-contain" @error="form.image_url = null" />
      <div v-else class="flex h-full w-full items-center justify-center">
        <Icon name="lucide:image" class="size-12 text-gray-500" />
      </div>
    </div>
    <div>
      <label for="steam-url-form" class="mb-1 block text-xs text-gray-500">Ссылка Steam</label>
      <input
        id="steam-url-form"
        v-model="steamUrl"
        type="url"
        :placeholder="STEAM_URL_PLACEHOLDER"
        class="w-full rounded-lg border border-gray-600 bg-gray-800 px-4 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
      />
    </div>
  </div>
  <!-- Правая колонка -->
  <div class="flex flex-col gap-4">
    <div>
      <label for="game-name" class="mb-1 block text-xs text-gray-500">Название</label>
      <input id="game-name" v-model="form.name" ... />
    </div>
    <div v-if="form.genres?.length">
      <span class="mb-1 block text-xs text-gray-500">Жанры</span>
      <div class="flex flex-wrap gap-1">
        <span v-for="g in form.genres" :key="g.id" class="rounded bg-gray-700 px-2 py-0.5 text-xs text-gray-300">{{ g.description }}</span>
      </div>
    </div>
    <div v-if="form.developers?.length">
      <span class="mb-1 block text-xs text-gray-500">Разработчик</span>
      <p class="text-sm text-gray-300">{{ form.developers.join(', ') }}</p>
    </div>
    <div v-if="form.publishers?.length">
      <span class="mb-1 block text-xs text-gray-500">Издатель</span>
      <p class="text-sm text-gray-300">{{ form.publishers.join(', ') }}</p>
    </div>
    <div>
      <label for="game-state" ...>Статус</label>
      <select id="game-state" v-model="form.state" ...>...</select>
    </div>
    <label class="flex items-center gap-2">
      <input v-model="form.is_favorite" type="checkbox" ... />
      <span class="text-sm text-gray-300">В избранное</span>
    </label>
  </div>
</div>
```

**Step 3: Кнопки шаг 2 и 3 — justify-between**

Отмена слева, Назад + Далее/Добавить справа.

**Step 4: submit — передать genres, developers, publishers**

```typescript
await createGame($api, {
  name,
  image_url: form.image_url || undefined,
  steam_app_id: form.steam_app_id || undefined,
  state: form.state,
  is_favorite: form.is_favorite,
  genres: form.genres?.length ? form.genres : undefined,
  developers: form.developers?.length ? form.developers : undefined,
  publishers: form.publishers?.length ? form.publishers : undefined,
})
```

**Step 5: Проверка**

Открыть модалку, ввести Steam URL, нажать Далее — проверить grid, genres, developers, publishers. Создать игру — проверить в API/БД.

**Step 6: Commit**

```bash
git add frontend/app/components/CreateGameModal.vue
git commit -m "feat(frontend): create game form grid layout, genres, developers, publishers"
```

---

## Порядок выполнения

1. Task 1 (миграция)
2. Task 2 (модель)
3. Task 3 (fetch-steam)
4. Task 4 (create game backend)
5. Task 5 (frontend API types)
6. Task 6 (modal size, step1 buttons)
7. Task 7 (form layout, genres, developers, publishers)

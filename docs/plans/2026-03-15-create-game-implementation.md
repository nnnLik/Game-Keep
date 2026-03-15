# Create Game Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Добавить создание игры через FAB + модальное окно с черновиком в localStorage.

**Architecture:** Backend: CreateGameService → UserGameDAO.create. API: POST /users/me/games. Frontend: FAB на странице профиля, модалка с формой, draft в localStorage.

**Tech Stack:** FastAPI, SQLAlchemy, Nuxt 4, Vue 3, Pinia

---

## Task 1: Backend — DTO и CreateGameService

**Files:**
- Modify: `backend/src/dtos/users.py`
- Create: `backend/src/services/users/create_game_service.py`

**Step 1: Добавить CreateGameRequestDTO**

В `backend/src/dtos/users.py`:

```python
class CreateGameRequestDTO(BaseModel):
    name: str
    state: str  # backlog | in_progress | completed | abandoned
    is_favorite: bool = False
```

**Step 2: Создать CreateGameService**

`backend/src/services/users/create_game_service.py`:

```python
from dataclasses import dataclass
from typing import Self
from uuid import UUID

from daos.games.user_game_dao import UserGameDAO
from dtos.users import CreateGameRequestDTO, GameResponseDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class CreateGameService:
    _user_game_dao: UserGameDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_user_game_dao=UserGameDAO.build(session))

    async def execute(
        self,
        user_id: UUID,
        data: CreateGameRequestDTO,
    ) -> GameResponseDTO:
        import constants.game
        state = constants.game.GameStateEnum(data.state)
        game = await self._user_game_dao.create(
            user_id=user_id,
            name=data.name.strip(),
            state=state,
            is_favorite=data.is_favorite,
        )
        return GameResponseDTO(
            id=game.id,
            name=game.name,
            state=game.state.value,
            is_favorite=game.is_favorite,
        )
```

**Step 3: Проверка**

```bash
cd backend/src && uv run python -c "from services.users.create_game_service import CreateGameService; print('OK')"
```

---

## Task 2: Backend — POST /users/me/games

**Files:**
- Modify: `backend/src/api/users.py`

**Step 1: Добавить эндпоинт**

```python
from dtos.users import CreateGameRequestDTO

@router.post('/me/games', response_model=GameResponseDTO)
async def create_game(
    data: CreateGameRequestDTO,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> GameResponseDTO:
    from services.users.create_game_service import CreateGameService
    return await CreateGameService.build(session).execute(current_user.id, data)
```

**Step 2: Добавить валидацию name в DTO**

В `CreateGameRequestDTO`:

```python
from pydantic import field_validator

@field_validator('name')
@classmethod
def name_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
        raise ValueError('Name is required')
    return v.strip()
```

**Step 3: Проверка**

```bash
curl -X POST http://localhost:9999/users/me/games \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Game","state":"backlog","is_favorite":false}'
```

Ожидается: 200, JSON с id, name, state, is_favorite.

---

## Task 3: Frontend — API createGame

**Files:**
- Modify: `frontend/app/constants/api.ts` (ME_GAMES уже есть)
- Modify: `frontend/app/api/users.api.ts`

**Step 1: Добавить createGame**

В `frontend/app/api/users.api.ts`:

```typescript
export interface CreateGamePayload {
  name: string
  state: string
  is_favorite?: boolean
}

export async function createGame(api: ApiClient, payload: CreateGamePayload) {
  return api<GameResponse>(ApiEndpoint.Users.ME_GAMES, {
    method: 'POST',
    body: payload,
  })
}
```

---

## Task 4: Frontend — CreateGameModal компонент

**Files:**
- Create: `frontend/app/components/CreateGameModal.vue`

**Step 1: Создать компонент**

Пропсы: `modelValue` (boolean — открыта/закрыта), `initialDraft` (опционально).
Эмиты: `update:modelValue`, `created` (после успешного создания).

Поля формы: name (input), state (select), is_favorite (checkbox).
Кнопки: Отмена, Добавить.
При закрытии без submit — emit `draft` с данными (родитель сохранит в localStorage).
При submit — вызов createGame, emit `created`, закрытие.

Секция «Дополнительно» — collapsed div с текстом «Скоро: картинка, ссылки, рейтинг» (placeholder).

**Step 2: Константы для state options**

Использовать `TABS` из `~/constants/profile` (без favorites) для опций select.

---

## Task 5: Frontend — FAB и интеграция на index.vue

**Files:**
- Modify: `frontend/app/pages/index.vue`

**Step 1: Добавить state**

```typescript
const DRAFT_KEY = 'gametrack_create_game_draft'
const showCreateModal = ref(false)

function openCreateModal() {
  const draft = localStorage.getItem(DRAFT_KEY)
  // pass draft to modal if exists
  showCreateModal.value = true
}

function onModalClose(draft?: { name: string; state: string; is_favorite: boolean }) {
  showCreateModal.value = false
  if (draft && (draft.name || draft.state)) {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft))
  }
}

function onGameCreated() {
  localStorage.removeItem(DRAFT_KEY)
  // refetch games
  fetchMyGames($api).then((g) => { games.value = g })
}
```

**Step 2: Добавить FAB**

В template, внутри `v-else-if="user"`, после списка игр:

```html
<button
  type="button"
  class="fixed bottom-6 right-6 z-40 flex size-14 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg transition hover:bg-emerald-500"
  aria-label="Добавить игру"
  @click="openCreateModal"
>
  <Icon name="lucide:plus" class="size-6" />
</button>
```

**Step 3: Добавить CreateGameModal**

```html
<CreateGameModal
  :model-value="showCreateModal"
  :initial-draft="restoredDraft"
  @update:model-value="showCreateModal = $event"
  @draft="onModalClose($event)"
  @created="onGameCreated"
/>
```

При открытии модалки читать draft из localStorage и передавать как `initialDraft`. После `@draft` — сохранять. После `@created` — очищать и обновлять список.

---

## Task 6: CreateGameModal — логика draft и submit

**Files:**
- Modify: `frontend/app/components/CreateGameModal.vue`

**Step 1: При открытии**

Если передан `initialDraft` — подставить в форму (name, state, is_favorite).

**Step 2: При закрытии (overlay, Escape, Отмена)**

Если форма не пустая — emit `draft` с текущими значениями. Родитель сохранит в localStorage.

**Step 3: При submit**

Валидация: name не пустое. Вызов createGame. При успехе — emit `created`, закрыть. При ошибке — показать сообщение.

**Step 4: Обработка Escape**

```vue
@keydown.escape="closeWithoutSubmit"
```

---

## Порядок выполнения

1. Task 1 (DTO + CreateGameService)
2. Task 2 (POST endpoint)
3. Task 3 (createGame API)
4. Task 4 (CreateGameModal component)
5. Task 5 (FAB + integration)
6. Task 6 (draft logic refinement)

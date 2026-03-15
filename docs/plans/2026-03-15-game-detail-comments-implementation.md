# Game Detail + Comments Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Страница игры `/games/:id` с полной информацией, счётчиком просмотров и блоком комментариев (дерево, лайки/дизлайки).

**Architecture:** Backend — FastAPI + SQLAlchemy; публичный `GET /games/:id` с инкрементом view_count; отдельный роутер для games; модели GameComment, GameCommentVote. Frontend — Nuxt 3, страницы `pages/games/[id].vue` и `pages/@[tag].vue`, API клиент для games.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Nuxt 3, Vue 3, Tailwind, Nuxt UI.

---

## Phase 1: view_count + GET /games/:id

### Task 1: Добавить view_count в UserGame

**Files:**
- Modify: `backend/src/models/user_game.py`
- Create: `backend/src/migrations/versions/YYYY_MM_DD_HHMM-<hash>_add_view_count_to_user_game.py`

**Step 1: Добавить поле в модель**

В `backend/src/models/user_game.py` после `is_favorite`:

```python
view_count: Mapped[int] = mapped_column(default=0, nullable=False)
```

**Step 2: Создать миграцию**

```bash
cd backend && alembic revision -m "add view_count to user_game"
```

В `upgrade()`:
```python
op.add_column('user_game', sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'))
```

В `downgrade()`:
```python
op.drop_column('user_game', 'view_count')
```

**Step 3: Применить миграцию**

```bash
cd backend && alembic upgrade head
```

**Step 4: Commit**

```bash
git add backend/src/models/user_game.py backend/src/migrations/versions/*view_count*
git commit -m "feat: add view_count to UserGame"
```

---

### Task 2: DAO get_by_id + increment_view_count

**Files:**
- Modify: `backend/src/daos/games/user_game_dao.py`

**Step 1: Добавить методы**

```python
async def get_by_id(self, game_id: int) -> UserGame | None:
    result = await self._session.execute(select(UserGame).where(UserGame.id == game_id))
    return result.scalar_one_or_none()

async def increment_view_count(self, game: UserGame) -> None:
    game.view_count += 1
    await self._session.flush()
```

**Step 2: Commit**

```bash
git add backend/src/daos/games/user_game_dao.py
git commit -m "feat: add get_by_id and increment_view_count to UserGameDAO"
```

---

### Task 3: DTO GameDetailResponseDTO

**Files:**
- Create: `backend/src/dtos/games.py` (если нет) или Modify: `backend/src/dtos/users.py`

**Step 1: Добавить DTO**

В `backend/src/dtos/games.py` или отдельном файле:

```python
from pydantic import BaseModel
import constants.game

class GameOwnerDTO(BaseModel):
    username: str | None
    tag: str | None
    avatar_url: str | None

class GameDetailResponseDTO(BaseModel):
    id: int
    name: str
    image_url: str | None
    steam_app_id: str | None
    state: constants.game.GameStateEnum
    is_favorite: bool
    genres: list[dict[str, str]] | None = None
    developers: list[str] | None = None
    publishers: list[str] | None = None
    release_date: str | None = None
    note: str | None = None
    date_started: date | None = None
    date_finished: date | None = None
    hours_played: float | None = None
    view_count: int
    owner: GameOwnerDTO
```

**Step 2: Commit**

```bash
git add backend/src/dtos/games.py
git commit -m "feat: add GameDetailResponseDTO"
```

---

### Task 4: GetGameService

**Files:**
- Create: `backend/src/services/games/get_game_service.py`

**Step 1: Реализовать сервис**

```python
from dataclasses import dataclass
from typing import Self

from daos.games.user_game_dao import UserGameDAO
from dtos.games import GameDetailResponseDTO, GameOwnerDTO
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GetGameService:
    _dao: UserGameDAO

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_dao=UserGameDAO.build(session))

    def _genres_to_response(self, genres):
        if not genres:
            return None
        strings = [s if isinstance(s, str) else s.get('description', '') for s in genres]
        return [{'id': str(i), 'description': s} for i, s in enumerate(strings) if s] or None

    async def execute(self, game_id: int) -> GameDetailResponseDTO | None:
        game = await self._dao.get_by_id(game_id)
        if not game:
            return None
        await self._dao.increment_view_count(game)
        user = game.user
        return GameDetailResponseDTO(
            id=game.id,
            name=game.name,
            image_url=game.image_url,
            steam_app_id=game.steam_app_id,
            state=game.state,
            is_favorite=game.is_favorite,
            genres=self._genres_to_response(game.genres),
            developers=game.developers,
            publishers=game.publishers,
            release_date=game.release_date,
            note=game.note,
            date_started=game.date_started,
            date_finished=game.date_finished,
            hours_played=game.hours_played,
            view_count=game.view_count,
            owner=GameOwnerDTO(
                username=user.username,
                tag=user.tag,
                avatar_url=user.avatar_url,
            ),
        )
```

**Step 2: Commit**

```bash
git add backend/src/services/games/get_game_service.py
git commit -m "feat: add GetGameService"
```

---

### Task 5: API GET /games/:id

**Files:**
- Create: `backend/src/api/games.py`
- Modify: `backend/src/utils/app.py`

**Step 1: Создать роутер**

```python
from fastapi import APIRouter, Depends, HTTPException, status

from services.games.get_game_service import GetGameService
from infra.db import get_db
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/games', tags=['games'])
SessionDep = Annotated[AsyncSession, Depends(get_db)]

@router.get('/{game_id}')
async def get_game(game_id: int, session: SessionDep):
    service = GetGameService.build(session)
    result = await service.execute(game_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Game not found')
    return result
```

**Step 2: Подключить роутер в app.py**

```python
from api.games import router as games_router
# ...
app.include_router(games_router)
```

**Step 3: Добавить relationship user в UserGame (eager load)**

Проверить, что в `UserGame` есть `user = relationship('User', ...)` и при `get_by_id` загружается user. Если нет — добавить в select:

```python
from sqlalchemy.orm import selectinload
stmt = select(UserGame).options(selectinload(UserGame.user)).where(UserGame.id == game_id)
```

**Step 4: Commit**

```bash
git add backend/src/api/games.py backend/src/utils/app.py backend/src/daos/games/user_game_dao.py
git commit -m "feat: add GET /games/:id"
```

---

### Task 6: Frontend API + страница игры

**Files:**
- Modify: `frontend/app/constants/api.ts`
- Create: `frontend/app/api/games.api.ts`
- Create: `frontend/app/pages/games/[id].vue`

**Step 1: Добавить endpoint**

В `api.ts`:
```typescript
Games: {
  BY_ID: (id: number) => `/games/${id}`,
},
```

**Step 2: Создать games.api.ts**

```typescript
import { api } from '~/api/base.client'
import { ApiEndpoint } from '~/constants/api'

export interface GameDetailResponse {
  id: number
  name: string
  image_url: string | null
  steam_app_id: string | null
  state: string
  is_favorite: boolean
  genres: { id: string; description: string }[] | null
  developers: string[] | null
  publishers: string[] | null
  release_date: string | null
  note: string | null
  date_started: string | null
  date_finished: string | null
  hours_played: number | null
  view_count: number
  owner: { username: string | null; tag: string | null; avatar_url: string | null }
}

export async function fetchGame(apiClient: any, id: number) {
  return api<GameDetailResponse>(ApiEndpoint.Games.BY_ID(id))
}
```

**Step 3: Создать страницу games/[id].vue**

- Layout: кнопка «Назад» (NuxtLink на `/` или `/@owner.tag`)
- Блок игры: картинка, название, жанры, разработчик, издатель, release_date, стейт, избранное, заметка, даты, часы, **view_count**
- Пока без комментариев

**Step 4: Commit**

```bash
git add frontend/app/constants/api.ts frontend/app/api/games.api.ts frontend/app/pages/games/[id].vue
git commit -m "feat: add game detail page with view_count"
```

---

### Task 7: Ссылка на игру со списка

**Files:**
- Modify: `frontend/app/pages/index.vue`

**Step 1: Обернуть li в NuxtLink**

```vue
<NuxtLink :to="`/games/${game.id}`" class="...">
  ...
</NuxtLink>
```

**Step 2: Commit**

```bash
git add frontend/app/pages/index.vue
git commit -m "feat: link game list items to game detail"
```

---

## Phase 2: Комментарии (Backend)

### Task 8: Модели GameComment, GameCommentVote

**Files:**
- Create: `backend/src/models/game_comment.py`
- Create: `backend/src/models/game_comment_vote.py`
- Create: миграция

**Step 1: GameComment**

```python
# game_comment.py
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.mixins import IntPkMixin

class GameComment(Base, IntPkMixin):
    __tablename__ = 'game_comment'
    game_id: Mapped[int] = mapped_column(ForeignKey('user_game.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('game_comment.id', ondelete='CASCADE'), nullable=True, index=True)
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    # created_at через mixin если есть, иначе добавить

    game = relationship('UserGame', back_populates='comments')
    user = relationship('User', back_populates='game_comments')
    parent = relationship('GameComment', remote_side='GameComment.id', back_populates='children')
    children = relationship('GameComment', back_populates='parent')
    votes = relationship('GameCommentVote', back_populates='comment', cascade='all, delete-orphan')
```

**Step 2: GameCommentVote**

```python
# game_comment_vote.py
# comment_id, user_id, is_like (bool), unique(comment_id, user_id, is_like) — или composite
# Один пользователь может иметь и like и dislike на один комментарий
```

**Step 3: Добавить relationship в UserGame, User**

**Step 4: Миграция**

**Step 5: Commit**

---

### Task 9–12: DAO, DTO, Services, API для комментариев

(Аналогично структуре выше: GameCommentDAO, CommentResponseDTO, GetCommentsService, CreateCommentService, VoteCommentService, эндпоинты GET/POST comments, POST vote.)

---

## Phase 3: Комментарии (Frontend)

### Task 13–15: UI комментариев, дерево, лайки/дизлайки

---

## Phase 4: Страница /@tag

### Task 16: GET /users/by-tag/:tag + страница @[tag].vue

---

## Execution Handoff

План сохранён в `docs/plans/2026-03-15-game-detail-comments-implementation.md`.

**Варианты выполнения:**

1. **Subagent-Driven (эта сессия)** — запуск subagent на каждую задачу, проверка между задачами.
2. **Отдельная сессия** — открыть новую сессию с executing-plans, выполнять батчами с чекпоинтами.

**Какой вариант предпочитаешь?**

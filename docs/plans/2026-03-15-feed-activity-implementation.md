# Feed & Activity Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Лента `/feed` и вкладка «Активности» в профиле. Посты из действий: создание игры, добавление/снятие из избранного. Лайки/дизлайки на постах, комментарии в постах «добавил игру».

**Architecture:** Backend — Activity, ActivityVote модели; создание Activity в CreateGameService и UpdateGameService; FeedService, ActivityVoteService; GET /feed, GET /users/by-tag/:tag/activity, POST /activities/:id/vote. Frontend — feed.vue с бесконечным скроллом, FeedPost компонент, Activity tab в профиле.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Nuxt 3, Vue 3, Tailwind, Nuxt UI.

---

## Phase 1: Backend — модели Activity, ActivityVote

### Task 1: Модель Activity и enum ActionType

**Files:**
- Create: `backend/src/constants/activity.py`
- Create: `backend/src/models/activity.py`
- Create: `backend/src/models/activity_vote.py`

**Step 1: Создать enum**

```python
# backend/src/constants/activity.py
from enum import StrEnum

class ActivityActionType(StrEnum):
    GAME_CREATED = "game_created"
    FAVORITE_ADDED = "favorite_added"
    FAVORITE_REMOVED = "favorite_removed"
```

**Step 2: Модель Activity**

```python
# backend/src/models/activity.py
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from constants.activity import ActivityActionType
from models.base import Base
from models.mixins import IntPkMixin


class Activity(Base, IntPkMixin):
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[ActivityActionType] = mapped_column(
        Enum(ActivityActionType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    user_game_id: Mapped[int] = mapped_column(
        ForeignKey("user_game.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="activities")
    user_game = relationship("UserGame", back_populates="activities")
    votes = relationship(
        "ActivityVote",
        back_populates="activity",
        cascade="all, delete-orphan",
    )
```

**Step 3: Модель ActivityVote**

```python
# backend/src/models/activity_vote.py
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.mixins import IntPkMixin


class ActivityVote(Base, IntPkMixin):
    __table_args__ = (
        UniqueConstraint("activity_id", "user_id", "is_like", name="uq_activity_user_is_like"),
    )

    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activity.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False)

    activity = relationship("Activity", back_populates="votes")
```

**Step 4: Добавить relationships в User и UserGame**

В `backend/src/models/user.py` добавить:
```python
activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
```

В `backend/src/models/user_game.py` добавить:
```python
activities = relationship("Activity", back_populates="user_game", cascade="all, delete-orphan")
```

**Step 5: Добавить импорт в migrations/env.py**

```python
import models.activity
import models.activity_vote
```

**Step 6: Миграция**

```bash
cd backend && alembic revision -m "add activity and activity_vote"
```

В `upgrade()`:
```python
op.create_table(
    "activity",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("user_id", sa.UUID(), nullable=False),
    sa.Column("action_type", sa.String(32), nullable=False),
    sa.Column("user_game_id", sa.Integer(), nullable=False),
    sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
    sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["user_game_id"], ["user_game.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
)
op.create_index("ix_activity_user_id", "activity", ["user_id"])
op.create_index("ix_activity_user_game_id", "activity", ["user_game_id"])
op.create_index("ix_activity_created_at", "activity", ["created_at"])

op.create_table(
    "activity_vote",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("activity_id", sa.Integer(), nullable=False),
    sa.Column("user_id", sa.UUID(), nullable=False),
    sa.Column("is_like", sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(["activity_id"], ["activity.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("activity_id", "user_id", "is_like", name="uq_activity_user_is_like"),
)
op.create_index("ix_activity_vote_activity_id", "activity_vote", ["activity_id"])
op.create_index("ix_activity_vote_user_id", "activity_vote", ["user_id"])
```

В `downgrade()`:
```python
op.drop_table("activity_vote")
op.drop_table("activity")
```

**Step 7: Применить миграцию и commit**

```bash
cd backend && alembic upgrade head
git add backend/src/constants/activity.py backend/src/models/activity.py backend/src/models/activity_vote.py backend/src/models/user.py backend/src/models/user_game.py backend/src/migrations/env.py backend/src/migrations/versions/*activity*
git commit -m "feat: add Activity and ActivityVote models"
```

---

## Phase 2: Создание Activity в сервисах

### Task 2: ActivityDAO

**Files:**
- Create: `backend/src/daos/activity.py`

**Step 1: Реализовать DAO**

```python
# backend/src/daos/activity.py
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from constants.activity import ActivityActionType
from models.activity import Activity


@dataclass
class ActivityDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> "ActivityDAO":
        return cls(_session=session)

    async def create(
        self,
        user_id: UUID,
        action_type: ActivityActionType,
        user_game_id: int,
    ) -> Activity:
        activity = Activity(
            user_id=user_id,
            action_type=action_type,
            user_game_id=user_game_id,
        )
        self._session.add(activity)
        await self._session.flush()
        await self._session.refresh(activity)
        return activity
```

**Step 2: Commit**

```bash
git add backend/src/daos/activity.py
git commit -m "feat: add ActivityDAO"
```

---

### Task 3: CreateActivity в CreateGameService

**Files:**
- Modify: `backend/src/services/users/create_game_service.py`

**Step 1: Импорт и инжект ActivityDAO**

```python
from constants.activity import ActivityActionType
from daos.activity import ActivityDAO
```

**Step 2: В build() добавить ActivityDAO**

```python
@classmethod
def build(cls, session: AsyncSession) -> Self:
    return cls(
        _user_game_dao=UserGameDAO.build(session),
        _activity_dao=ActivityDAO.build(session),
    )
```

**Step 3: В execute() после create вызвать activity_dao.create**

После `game = await self._user_game_dao.create(...)` добавить:
```python
await self._activity_dao.create(
    user_id=user_id,
    action_type=ActivityActionType.GAME_CREATED,
    user_game_id=game.id,
)
```

**Step 4: Commit**

```bash
git add backend/src/services/users/create_game_service.py
git commit -m "feat: create Activity on game creation"
```

---

### Task 4: CreateActivity в UpdateGameService при смене is_favorite

**Files:**
- Modify: `backend/src/services/users/update_game_service.py`

**Step 1: Добавить ActivityDAO в build()**

```python
@classmethod
def build(cls, session: AsyncSession) -> Self:
    return cls(
        _user_game_dao=UserGameDAO.build(session),
        _activity_dao=ActivityDAO.build(session),
    )
```

**Step 2: В execute() перед update — проверить is_favorite и создать Activity**

```python
# В execute(), перед game = await self._user_game_dao.update(...):
if "is_favorite" in kwargs:
    old_game = await self._user_game_dao.get_by_id(game_id)
    if (
        old_game
        and old_game.user_id == user_id
        and old_game.is_favorite != kwargs["is_favorite"]
    ):
        action = (
            ActivityActionType.FAVORITE_ADDED
            if kwargs["is_favorite"]
            else ActivityActionType.FAVORITE_REMOVED
        )
        await self._activity_dao.create(
            user_id=user_id,
            action_type=action,
            user_game_id=game_id,
        )
```

**Step 3: Commit**

```bash
git add backend/src/services/users/update_game_service.py
git commit -m "feat: create Activity on favorite toggle"
```

---

## Phase 3: Feed и Activity API

### Task 5: DTOs для Feed

**Files:**
- Modify: `backend/src/dtos/games.py` (или создать `backend/src/dtos/feed.py`)

**Step 1: Добавить FeedPostDTO**

```python
# backend/src/dtos/feed.py (или в games.py)
from datetime import datetime

from pydantic import BaseModel

from constants.activity import ActivityActionType


class FeedPostAuthorDTO(BaseModel):
    username: str | None
    tag: str | None
    avatar_url: str | None


class FeedPostGameDTO(BaseModel):
    id: int
    name: str
    image_url: str | None
    state: str


class FeedPostDTO(BaseModel):
    id: int
    action_type: ActivityActionType
    created_at: datetime
    author: FeedPostAuthorDTO
    game: FeedPostGameDTO
    like_count: int
    dislike_count: int
    current_user_voted: dict  # liked, disliked
    comments: list | None = None  # CommentResponseDTO для game_created
    comments_total: int | None = None
```

**Step 2: Commit**

```bash
git add backend/src/dtos/feed.py
git commit -m "feat: add FeedPostDTO"
```

---

### Task 6: ActivityDAO — get_feed_page, get_activity_page

**Files:**
- Modify: `backend/src/daos/activity.py`

**Step 1: Добавить методы**

```python
async def get_feed_page(
    self,
    limit: int = 20,
    cursor: int | None = None,
) -> tuple[list[Activity], int | None]:
    """Возвращает (activities, next_cursor). cursor = id последнего поста."""
    stmt = (
        select(Activity)
        .options(
            selectinload(Activity.user),
            selectinload(Activity.user_game),
            selectinload(Activity.votes),
        )
        .order_by(Activity.created_at.desc(), Activity.id.desc())
        .limit(limit + 1)
    )
    if cursor is not None:
        stmt = stmt.where(Activity.id < cursor)
    result = await self._session.execute(stmt)
    rows = list(result.scalars().all())
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
        next_cursor = rows[-1].id
    else:
        next_cursor = None
    return rows, next_cursor

async def get_activity_page_by_user_tag(
    self,
    user_tag: str,
    limit: int = 20,
    cursor: int | None = None,
) -> tuple[list[Activity], int | None]:
    """То же, но фильтр по user.tag."""
    from models.user import User

    stmt = (
        select(Activity)
        .join(User, Activity.user_id == User.id)
        .where(User.tag == user_tag)
        .options(
            selectinload(Activity.user),
            selectinload(Activity.user_game),
            selectinload(Activity.votes),
        )
        .order_by(Activity.created_at.desc(), Activity.id.desc())
        .limit(limit + 1)
    )
    if cursor is not None:
        stmt = stmt.where(Activity.id < cursor)
    result = await self._session.execute(stmt)
    rows = list(result.scalars().all())
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
        next_cursor = rows[-1].id
    else:
        next_cursor = None
    return rows, next_cursor
```

**Step 2: Commit**

```bash
git add backend/src/daos/activity.py
git commit -m "feat: add get_feed_page and get_activity_page"
```

---

### Task 7: FeedService

**Files:**
- Create: `backend/src/services/feed/feed_service.py`

**Step 1: Реализовать сервис**

Сервис:
- принимает ActivityDAO, UserGameDAO, GameCommentDAO
- get_feed(page, limit, current_user_id) -> list[FeedPostDTO], next_cursor
- get_activity_page(user_tag, ...) -> то же
- для каждой Activity: собрать author, game, like_count, dislike_count, current_user_voted
- для game_created: добавить первые 2–3 комментария (root), comments_total

**Step 2: Commit**

```bash
git add backend/src/services/feed/feed_service.py
git commit -m "feat: add FeedService"
```

---

### Task 8: API GET /feed и GET /users/by-tag/:tag/activity

**Files:**
- Create: `backend/src/api/feed.py`
- Modify: `backend/src/utils/app.py` (или main)

**Step 1: Роутер feed**

```python
# backend/src/api/feed.py
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from dtos.feed import FeedPostDTO
from infra.auth import get_current_user
from infra.db import get_db
from models.user import User
from services.feed.feed_service import FeedService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/feed", tags=["feed"])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=dict)  # { items: list[FeedPostDTO], next_cursor: int | None }
async def get_feed(
    current_user: CurrentUserDep,
    session: SessionDep,
    cursor: int | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
):
    service = FeedService.build(session)
    items, next_cursor = await service.execute_feed(
        current_user_id=current_user.id,
        cursor=cursor,
        limit=limit,
    )
    return {"items": items, "next_cursor": next_cursor, "has_more": next_cursor is not None}
```

**Step 2: Роут activity**

Добавить в `backend/src/api/me.py` (router prefix /users):
```python
@router.get("/by-tag/{tag}/activity", response_model=dict)
async def get_user_activity(
    tag: str,
    current_user: CurrentUserDep,
    session: SessionDep,
    cursor: int | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
):
    service = FeedService.build(session)
    items, next_cursor = await service.execute_activity_page(
        user_tag=tag,
        current_user_id=current_user.id,
        cursor=cursor,
        limit=limit,
    )
    return {"items": items, "next_cursor": next_cursor, "has_more": next_cursor is not None}
```

**Step 3: Роутер activities для vote**

Создать `backend/src/api/activities.py`:
```python
router = APIRouter(prefix="/activities", tags=["activities"])
@router.post("/{activity_id}/vote")
async def vote_activity(...)
```

**Step 4: Подключить роутеры**

```python
from api.feed import router as feed_router
from api.activities import router as activities_router
app.include_router(feed_router)
app.include_router(activities_router)
```

**Step 5: Commit**

```bash
git add backend/src/api/feed.py backend/src/utils/app.py
git commit -m "feat: add GET /feed and GET /users/by-tag/:tag/activity"
```

---

## Phase 4: Vote Activity

### Task 9: ActivityVoteDAO

**Files:**
- Create: `backend/src/daos/activity_vote.py`

**Step 1: Реализовать add_vote, remove_vote, get_user_votes**

По аналогии с GameCommentDAO.

**Step 2: Commit**

```bash
git add backend/src/daos/activity_vote.py
git commit -m "feat: add ActivityVoteDAO"
```

---

### Task 10: VoteActivityService

**Files:**
- Create: `backend/src/services/feed/vote_activity_service.py`

**Step 1: Реализовать сервис**

```python
async def execute(self, activity_id: int, user_id: UUID, is_like: bool) -> None:
    # Проверить activity существует
    # Toggle: если уже есть такой vote — удалить, иначе добавить
```

**Step 2: Commit**

```bash
git add backend/src/services/feed/vote_activity_service.py
git commit -m "feat: add VoteActivityService"
```

---

### Task 11: POST /activities/:id/vote

**Files:**
- Create: `backend/src/api/activities.py`
- Modify: `backend/src/utils/app.py`

**Step 1: Создать роутер activities**

```python
@router.post("/activities/{activity_id}/vote")
async def vote_activity(
    activity_id: int,
    data: VoteRequestDTO,  # is_like
    current_user: CurrentUserDep,
    session: SessionDep,
):
    service = VoteActivityService.build(session)
    try:
        await service.execute(activity_id, current_user.id, data.is_like)
    except VoteActivityService.ActivityNotFoundError:
        raise HTTPException(404, "Activity not found")
```

**Step 2: Commit**

```bash
git add backend/src/api/feed.py
git commit -m "feat: add POST /activities/:id/vote"
```

---

## Phase 5: Frontend

### Task 12: API clients

**Files:**
- Modify: `frontend/app/constants/api.ts`
- Create: `frontend/app/api/feed.api.ts`

**Step 1: Endpoints**

```typescript
Feed: {
  LIST: '/feed',
  ACTIVITY: (tag: string) => `/users/by-tag/${tag}/activity`,
  VOTE: (id: number) => `/activities/${id}/vote`,
},
```

**Step 2: fetchFeed, fetchActivity, voteActivity**

**Step 3: Commit**

```bash
git add frontend/app/constants/api.ts frontend/app/api/feed.api.ts
git commit -m "feat: add feed API client"
```

---

### Task 13: Страница /feed

**Files:**
- Modify: `frontend/app/pages/feed.vue`

**Step 1: Auth guard**

Проверка currentUser, редирект на логин если нет.

**Step 2: Бесконечный скролл**

- IntersectionObserver на sentinel внизу
- loadMore при видимости
- cursor: next_cursor из ответа

**Step 3: Рендер постов**

- FeedPostGameCreated — автор, картинка, текст «@tag добавил [игра] в [стейт]», первые 2–3 комментария, «Показать ещё», форма комментария
- FeedPostFavorite — автор, текст «@tag пометил/убрал [игра] в/из Избранного»
- Лайки/дизлайки под каждым постом

**Step 4: Commit**

```bash
git add frontend/app/pages/feed.vue
git commit -m "feat: implement feed page with infinite scroll"
```

---

### Task 14: Компоненты FeedPost

**Files:**
- Create: `frontend/app/components/FeedPost.vue`
- Create: `frontend/app/components/FeedPostGameCreated.vue` (или слоты внутри FeedPost)
- Create: `frontend/app/components/FeedPostFavorite.vue`

**Step 1: FeedPost**

Props: post. Слоты или v-if по action_type.

**Step 2: Форма комментария**

Использовать createComment из games.api.

**Step 3: «Показать ещё»**

При клике — загрузить все комментарии или перейти на /games/:id.

**Step 4: Commit**

```bash
git add frontend/app/components/FeedPost*.vue
git commit -m "feat: add FeedPost components"
```

---

### Task 15: Вкладка «Активности» в профиле

**Files:**
- Modify: `frontend/app/pages/users/[tag].vue`
- Modify: `frontend/app/pages/index.vue`

**Step 1: При activeSection === 'activities'**

Загружать данные с fetchActivity(tag). Тот же FeedPost компонент.

**Step 2: Бесконечный скролл**

Аналогично feed.

**Step 3: Commit**

```bash
git add frontend/app/pages/users/[tag].vue frontend/app/pages/index.vue
git commit -m "feat: implement Activity tab in profile"
```

---

### Task 16: Ссылка на ленту в навигации

**Files:**
- Modify: `frontend/app/layouts/default.vue` (или навбар)

**Step 1: Добавить ссылку «Лента» на /feed**

**Step 2: Commit**

```bash
git add frontend/app/layouts/default.vue
git commit -m "feat: add feed link to navigation"
```

---

## Phase 6: Миграция и seed (опционально)

### Task 17: Backfill Activity для существующих UserGame

**Files:**
- Create: `backend/scripts/backfill_activity.py` (или migration)

**Step 1: Скрипт**

Для каждого UserGame создать Activity(game_created) с created_at = user_game.created_at (если есть).

**Step 2: Запустить**

```bash
cd backend && python scripts/backfill_activity.py
```

**Step 3: Commit**

```bash
git add backend/scripts/backfill_activity.py
git commit -m "chore: add backfill script for activity"
```

---

## Execution Handoff

План сохранён в `docs/plans/2026-03-15-feed-activity-implementation.md`.

**Варианты выполнения:**

1. **Subagent-Driven (эта сессия)** — запуск subagent на каждую задачу, проверка между задачами.
2. **Отдельная сессия** — открыть новую сессию с executing-plans, выполнять батчами с чекпоинтами.

**Какой вариант предпочитаешь?**

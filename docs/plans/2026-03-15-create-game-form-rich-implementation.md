# Create Game Form Rich — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Расширить форму создания игры: max-w-6xl, min-h контента, release_date, кастомные жанры, заметка, date_started, date_finished, hours_played.

**Architecture:** Backend: FetchSteamGameService + release_date; UserGame + 5 новых полей; миграция. Frontend: CreateGameModal — размер, min-h, новые поля, кастомные жанры, date inputs, hours input.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Nuxt 4, Vue 3

---

## Task 1: Backend — миграция user_game (release_date, note, date_started, date_finished, hours_played)

**Files:**
- Create: `backend/src/migrations/versions/YYYY_MM_DD_HHMM-xxx_add_rich_fields_to_user_game.py`

**Step 1: Создать миграцию**

```bash
cd backend && uv run alembic -c src/alembic.ini revision -m "add release_date note date_started date_finished hours_played to user_game"
```

**Step 2: Заполнить upgrade/downgrade**

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    op.add_column('user_game', sa.Column('release_date', sa.String(64), nullable=True))
    op.add_column('user_game', sa.Column('note', sa.String(512), nullable=True))
    op.add_column('user_game', sa.Column('date_started', sa.Date(), nullable=True))
    op.add_column('user_game', sa.Column('date_finished', sa.Date(), nullable=True))
    op.add_column('user_game', sa.Column('hours_played', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('user_game', 'hours_played')
    op.drop_column('user_game', 'date_finished')
    op.drop_column('user_game', 'date_started')
    op.drop_column('user_game', 'note')
    op.drop_column('user_game', 'release_date')
```

**Step 3: Применить**

```bash
cd backend && uv run alembic -c src/alembic.ini upgrade head
```

---

## Task 2: Backend — модель UserGame

**Files:**
- Modify: `backend/src/models/user_game.py`

**Step 1: Добавить импорт Date, Float**

```python
from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, String
```

**Step 2: Добавить колонки**

Добавить `from datetime import date` в импорты.

```python
release_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
note: Mapped[str | None] = mapped_column(String(512), nullable=True)
date_started: Mapped[date | None] = mapped_column(Date, nullable=True)
date_finished: Mapped[date | None] = mapped_column(Date, nullable=True)
hours_played: Mapped[float | None] = mapped_column(Float, nullable=True)
```

---

## Task 3: Backend — FetchSteamGameService + release_date

**Files:**
- Modify: `backend/src/services/games/fetch_steam_game_service.py`
- Modify: `backend/src/dtos/games.py`
- Modify: `backend/src/api/user_games.py`

**Step 1: FetchSteamResponseDTO**

В `backend/src/dtos/games.py` добавить `release_date: str | None = None`

**Step 2: FetchSteamGameResult**

В fetch_steam_game_service.py добавить `release_date: str | None` в dataclass.

**Step 3: execute**

Извлечь `release_date = game_detail_dto.release_date.get('date') if isinstance(game_detail_dto.release_date, dict) else None` и передать в `FetchSteamGameResult`.

**Step 4: API**

В fetch_steam_game вернуть `release_date=result.release_date`.

---

## Task 4: Backend — CreateGameRequestDTO, UserGameDAO, CreateGameService, GameResponseDTO

**Files:**
- Modify: `backend/src/dtos/users.py`
- Modify: `backend/src/daos/games/user_game_dao.py`
- Modify: `backend/src/services/users/create_game_service.py`
- Modify: `backend/src/services/users/my_games_service.py`
- Modify: `backend/src/api/user_games.py`

**Step 1: CreateGameRequestDTO**

Добавить: `release_date`, `note` (max 500), `date_started`, `date_finished`, `hours_played` (все Optional). Валидация note: max_length=500, hours_played: ge=0.

**Step 2: GameResponseDTO**

Добавить те же поля.

**Step 3: UserGameDAO.create**

Добавить параметры и передать в UserGame.

**Step 4: CreateGameService**

Принимать и сохранять новые поля. round(hours_played, 1) при сохранении.

**Step 5: MyGamesService**

В GameResponseDTO передать новые поля.

**Step 6: API create_game**

Передать новые поля в CreateGameService.

---

## Task 5: Frontend — API типы и FetchSteamResponse

**Files:**
- Modify: `frontend/app/api/users.api.ts`

**Step 1: FetchSteamResponse**

Добавить `release_date: string | null`

**Step 2: CreateGamePayload, GameResponse**

Добавить: `release_date`, `note`, `date_started` (YYYY-MM-DD), `date_finished`, `hours_played`

---

## Task 6: Frontend — CreateGameModal размер и min-h

**Files:**
- Modify: `frontend/app/components/CreateGameModal.vue`

**Step 1: max-w-6xl**

Заменить `max-w-3xl` на `max-w-6xl`.

**Step 2: min-h контента**

Обернуть контент каждого шага (поле URL + кнопки, форма, шаг 3) в div с `min-h-[420px]` или добавить класс к контейнеру контента.

---

## Task 7: Frontend — release_date, note, date_started, date_finished, hours_played

**Files:**
- Modify: `frontend/app/components/CreateGameModal.vue`

**Step 1: form**

Добавить в form: `release_date`, `note`, `date_started`, `date_finished`, `hours_played`.

**Step 2: goToStep2**

При fetchSteamGame подставлять `form.release_date = data.release_date ?? null`.

**Step 3: UI**

В правой колонке шага 2:
- release_date: read-only текст, если есть
- note: textarea, maxlength=500, placeholder «Заметка или отзыв»
- date_started: input type="date" + кнопка «Сегодня»
- date_finished: input type="date" + кнопка «Сегодня»
- hours_played: input type="number" step="0.1" min="0"

**Step 4: submit**

Передавать все поля в createGame.

**Step 5: draft**

Сохранять и восстанавливать новые поля.

---

## Task 8: Frontend — кастомные жанры

**Files:**
- Modify: `frontend/app/components/CreateGameModal.vue`

**Step 1: Логика**

- `customGenreInput` ref для input
- `showCustomGenreInput` ref для показа/скрытия
- Кнопка «+» рядом с жанрами Steam
- По клику — показать input
- Ввод 3–10 символов, Enter или кнопка «Добавить» — добавить в form.genres (как {id: `custom-${Date.now()}`, description: value})
- Валидация: 3–10 символов, без дубликатов

**Step 2: UI**

Рядом с тегами жанров: кнопка +, при фокусе — input. Теги с крестиком для удаления (кастомные можно удалять).

**Step 3: Backend**

Жанры уже отправляются как list[dict]. Кастомные добавляются в тот же список. При сохранении CreateGameService извлекает description — кастомные жанры сохранятся как строки в genres.

---

## Порядок выполнения

1. Task 1 (миграция)
2. Task 2 (модель)
3. Task 3 (fetch-steam release_date)
4. Task 4 (create game backend)
5. Task 5 (frontend API types)
6. Task 6 (modal size)
7. Task 7 (новые поля)
8. Task 8 (кастомные жанры)

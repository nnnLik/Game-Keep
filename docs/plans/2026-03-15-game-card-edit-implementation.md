# Game Card Edit & Delete Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add edit (all fields) and delete for game cards. Edit via modal, delete with confirmation on game page. Edit button on game page and in index list for owner.

**Architecture:** Backend: PATCH (extend for full update), DELETE /users/me/games/:id. Frontend: GameFormFields component, EditGameModal, refactor CreateGameModal. Buttons on game page and index.

**Tech Stack:** FastAPI, SQLAlchemy, Nuxt 3, Vue 3, Nuxt UI

---

## Phase 1: Backend

### Task 1: Add UpdateGameRequestDTO and UpdateGameService

**Files:**
- Modify: `backend/src/dtos/users.py`
- Create: `backend/src/services/users/update_game_service.py`
- Modify: `backend/src/daos/games/user_game_dao.py`

**Step 1:** Add `UpdateGameRequestDTO` to `backend/src/dtos/users.py` (after CreateGameRequestDTO):

```python
class UpdateGameRequestDTO(BaseModel):
    name: str
    image_url: str | None = None
    steam_app_id: str | None = None
    state: str
    is_favorite: bool = False
    genres: list[dict[str, str]] | None = None
    developers: list[str] | None = None
    publishers: list[str] | None = None
    release_date: str | None = None
    note: str | None = None
    date_started: date | None = None
    date_finished: date | None = None
    hours_played: float | None = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name is required')
        return v.strip()

    @field_validator('state')
    @classmethod
    def state_valid(cls, v: str) -> str:
        if v not in {e.value for e in constants.game.GameStateEnum}:
            raise ValueError('Invalid state')
        return v
```

**Step 2:** Add `update()` to `backend/src/daos/games/user_game_dao.py`:

```python
async def update(
    self,
    game_id: int,
    user_id: UUID,
    *,
    name: str,
    state: constants.game.GameStateEnum,
    is_favorite: bool = False,
    image_url: str | None = None,
    steam_app_id: str | None = None,
    genres: list[str] | None = None,
    developers: list[str] | None = None,
    publishers: list[str] | None = None,
    release_date: str | None = None,
    note: str | None = None,
    date_started: date | None = None,
    date_finished: date | None = None,
    hours_played: float | None = None,
) -> UserGame | None:
    stmt = select(UserGame).where(
        UserGame.id == game_id,
        UserGame.user_id == user_id,
    )
    result = await self._session.execute(stmt)
    game = result.scalar_one_or_none()
    if game is None:
        return None
    game.name = name
    game.state = state
    game.is_favorite = is_favorite
    game.image_url = image_url
    game.steam_app_id = steam_app_id
    game.genres = genres if genres is not None else game.genres
    game.developers = developers if developers is not None else game.developers
    game.publishers = publishers if publishers is not None else game.publishers
    game.release_date = release_date
    game.note = note
    game.date_started = date_started
    game.date_finished = date_finished
    game.hours_played = round(hours_played, 1) if hours_played is not None else None
    await self._session.flush()
    await self._session.refresh(game)
    return game
```

**Step 3:** Create `backend/src/services/users/update_game_service.py` (mirror CreateGameService logic for genres/developers/publishers, call dao.update).

**Step 4:** Commit: `feat(backend): add UpdateGameRequestDTO, update_game_service, dao.update`

---

### Task 2: Add DeleteGameService and DELETE endpoint

**Files:**
- Create: `backend/src/services/users/delete_game_service.py`
- Modify: `backend/src/daos/games/user_game_dao.py`
- Modify: `backend/src/api/user_games.py`

**Step 1:** Add `delete()` to UserGameDAO (delete by id + user_id, return bool).

**Step 2:** Create DeleteGameService (execute game_id, user_id → raise NotFound if not found).

**Step 3:** Add `DELETE /games/{game_id}` in user_games router, return 204.

**Step 4:** Commit: `feat(backend): add DELETE /users/me/games/:id`

---

### Task 3: Extend PATCH to support full update

**Files:**
- Modify: `backend/src/api/user_games.py`

**Step 1:** Change PATCH handler to accept `UpdateGameRequestDTO` (in addition to or replacing UpdateGameFavoriteRequestDTO). If full payload provided, call UpdateGameService. Keep backward compat: if only `is_favorite` in body, could use UpdateGameFavoriteService — or merge into UpdateGameService.

**Step 2:** Use single `UpdateGameRequestDTO` for PATCH. All fields required for full update (edit form sends all). Call UpdateGameService.

**Step 3:** Remove or deprecate UpdateGameFavoriteService — fold into UpdateGameService (is_favorite is a field in UpdateGameRequestDTO).

**Step 4:** Commit: `feat(backend): PATCH /users/me/games/:id accepts full update`

---

## Phase 2: Frontend — GameFormFields

### Task 4: Extract GameFormFields component

**Files:**
- Create: `frontend/app/components/GameFormFields.vue`
- Modify: `frontend/app/components/CreateGameModal.vue`

**Step 1:** Create `GameFormFields.vue` with props: `modelValue` (form object), `steamUrl`, `stateOptions`. Emit: `update:modelValue`, `update:steamUrl`. Include: image preview, steam URL input, name, genres, release_date (readonly), developers (readonly), publishers (readonly), state select, note textarea, date_started, date_finished, hours_played. Expose `addCustomGenre`, `removeGenre` via emits or slot.

**Step 2:** Refactor CreateGameModal step 2 to use `<GameFormFields v-model="form" v-model:steam-url="steamUrl" :state-options="STATE_OPTIONS" />`.

**Step 3:** Commit: `refactor(frontend): extract GameFormFields from CreateGameModal`

---

### Task 5: Add updateGame and deleteGame API

**Files:**
- Modify: `frontend/app/api/users.api.ts`
- Modify: `frontend/app/constants/api.ts` (if needed)

**Step 1:** Add `updateGame(api, gameId, payload)` — PATCH with UpdateGamePayload (same shape as CreateGamePayload).

**Step 2:** Add `deleteGame(api, gameId)` — DELETE.

**Step 3:** Commit: `feat(frontend): add updateGame, deleteGame API`

---

### Task 6: Create EditGameModal

**Files:**
- Create: `frontend/app/components/EditGameModal.vue`

**Step 1:** Create EditGameModal with props: `modelValue` (boolean), `game` (GameDetailResponse). Use GameFormFields. On mount/open, populate form from game. Submit → updateGame → emit `updated` with new game data → close.

**Step 2:** Wire up validation (name required, etc.) same as CreateGameModal.

**Step 3:** Commit: `feat(frontend): add EditGameModal`

---

### Task 7: Add Edit and Delete buttons on game page

**Files:**
- Modify: `frontend/app/pages/games/[id].vue`

**Step 1:** In hero block (where isOwnGame shows heart), add Edit button (pencil icon) and Delete button (trash icon) for owner. Edit opens EditGameModal. Delete opens UModal/UAlertDialog with "Удалить игру? Действие необратимо" and Cancel/Delete buttons.

**Step 2:** On EditGameModal `updated`, set `game.value = payload`. On delete confirm, call deleteGame, navigate to `/`.

**Step 3:** Commit: `feat(frontend): edit and delete buttons on game page`

---

### Task 8: Add Edit button in index list

**Files:**
- Modify: `frontend/app/pages/index.vue`

**Step 1:** In game card NuxtLink, add edit icon button (stop propagation so it doesn't navigate). On click, navigate to `/games/:id` with query `?edit=1` or open EditGameModal — simpler: navigate to game page with `?edit=1`, game page reads query and opens modal on mount.

**Step 2:** In games/[id].vue, onMounted check `route.query.edit === '1'` and isOwnGame → open EditGameModal.

**Step 3:** Commit: `feat(frontend): edit button in index list, open modal via ?edit=1`

---

## Phase 3: Verification

### Task 9: Manual test

**Steps:**
1. Create game, open game page, click Edit, change fields, Save — verify updates.
2. Click Delete, confirm — verify redirect to / and game removed.
3. On index, click edit icon on game card — verify navigates to game page and opens modal.
4. Edit and save from modal — verify game updates.

---

## Execution

Plan saved. Two options:

1. **Subagent-Driven (this session)** — dispatch subagent per task, review between tasks.
2. **Parallel Session** — open new session with executing-plans, batch execution.

Which approach?

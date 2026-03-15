# Users & Games API — план реализации

> **Цель:** Отдельный users API с эндпоинтами `me` и `games`. Путь без uuid, пользователь определяется по JWT.

---

## Архитектура

**Структура роутов:**
- `GET /users/me` — данные текущего пользователя
- `GET /users/me/games` — игры текущего пользователя (query: `state`, `is_favorite`)

**Авторизация:** Bearer token в заголовке `Authorization`. User ID извлекается из `sub` в JWT.

---

## Модели данных

### UserGame (игра в коллекции пользователя)

| Поле       | Тип   | Описание                          |
|------------|-------|-----------------------------------|
| id         | UUID  | PK                                |
| user_id    | UUID  | FK → User                         |
| name       | str   | Название игры                     |
| state      | str   | backlog \| in_progress \| completed \| abandoned |
| is_favorite| bool  | В избранном                       |
| created_at | datetime | Авто                             |

**Индексы:** user_id, (user_id, state), (user_id, is_favorite)

---

## Задачи

### Task 1: GetCurrentUser dependency

**Файлы:** `backend/src/infra/auth.py` (создать)

**Логика:**
- Извлечь `Authorization: Bearer <token>`
- Декодировать JWT, проверить `type == 'access'`
- Вернуть `user_id` (UUID) или raise 401
- Опционально: загрузить User из БД и вернуть объект (для `/me`)

**Зависимости:** `get_db`, `UserDAO.get_by_id`

---

### Task 2: UserDAO.get_by_id

**Файл:** `backend/src/daos/auth/user_dao.py`

```python
async def get_by_id(self, user_id: UUID) -> User | None:
    result = await self._session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

---

### Task 3: Модель UserGame + миграция

**Файлы:**
- `backend/src/models/user_game.py` (создать)
- `backend/src/models/__init__.py` (если есть — экспорт)
- Миграция Alembic

**UserGame:**
- Наследует Base, UUIDPKMixin, CreatedAtMixin
- state: String(20), nullable=False
- is_favorite: Boolean, default False
- name: String(255)
- user_id: FK User.id, ondelete CASCADE

**Константы state:** `backend/src/models/user_game.py` — enum или Literal.

---

### Task 4: UserGameDAO

**Файл:** `backend/src/daos/games/user_game_dao.py` (создать)

**Методы:**
- `get_by_user(user_id, state?, is_favorite?)` — список UserGame с фильтрами
- `create(user_id, name, state, is_favorite)` — добавить игру

---

### Task 5: DTO

**Файл:** `backend/src/dtos/users.py` (создать)

- `MeResponseDTO`: id, username, tag, email (без password)
- `GameResponseDTO`: id, name, state, is_favorite, created_at
- `GamesListResponseDTO`: list[GameResponseDTO] или просто list

---

### Task 6: Users API router

**Файл:** `backend/src/api/users.py` (создать)

```python
router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=MeResponseDTO)
async def me(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MeResponseDTO:
    ...

@router.get('/me/games', response_model=list[GameResponseDTO])
async def my_games(
    current_user: CurrentUserDep,
    session: SessionDep,
    state: Literal['backlog', 'in_progress', 'completed', 'abandoned'] | None = None,
    is_favorite: bool | None = None,
) -> list[GameResponseDTO]:
    ...
```

**CurrentUserDep:** `Annotated[User, Depends(get_current_user)]`

---

### Task 7: get_current_user dependency

**Файл:** `backend/src/infra/auth.py`

- `get_current_user(Authorization: str, session: SessionDep) -> User`
- Декодирует JWT, получает user_id
- Загружает User через UserDAO.get_by_id
- Если не найден или токен невалиден → 401

---

### Task 8: Подключение роутера

**Файл:** `backend/src/main.py`

```python
from api.users import router as users_router
app.include_router(users_router)
```

---

## Порядок выполнения

1. Task 2 (UserDAO.get_by_id)
2. Task 7 (get_current_user)
3. Task 5 (DTO)
4. Task 6 (Users API) — только `/me` сначала
5. Task 8 (подключение)
6. Task 3 (UserGame + миграция)
7. Task 4 (UserGameDAO)
8. Task 6 — добавить `/me/games`

---

## Query-параметры `/me/games`

| Параметр   | Тип   | Описание                    |
|------------|-------|-----------------------------|
| state      | str   | backlog, in_progress, completed, abandoned |
| is_favorite| bool  | true / false                |

Можно комбинировать. Без параметров — все игры пользователя.

---

## Зависимости

- `auth` router уже есть
- JWT: `sub` = user_id (str), `type` = 'access'
- CORS уже настроен

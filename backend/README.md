FastAPI backend с асинхронным SQLite, SQLAlchemy, Alembic. Шаблон минималистичной архитектуры.

## Структура проекта

```
root/
├── pyproject.toml
├── vars/
│   └── .env
└── src/
    ├── main.py
    ├── alembic.ini
    ├── api/
    │   └── auth.py
    ├── conf/
    │   └── settings.py
    ├── daos/
    │   └── auth/
    │       └── user_dao.py
    ├── dtos/
    │   └── auth.py
    ├── infra/
    │   └── db.py
    ├── migrations/
    │   ├── env.py
    │   └── versions/
    ├── models/
    │   ├── base.py
    │   ├── user.py
    │   └── mixins/
    └── services/
        └── auth/
            ├── verify_password_service.py
            ├── create_password_service.py
            ├── create_token_service.py
            ├── login_service.py
            └── register_service.py
```

## Правила архитектуры

### 1. API (эндпоинты)

**Правило:** Только вызов сервиса, обработка ошибок, возврат ответа. Никаких операций с БД.

```python
@router.post('/login', response_model=TokenResponseDTO)
async def login(data: LoginRequestDTO, session: SessionDep) -> TokenResponseDTO:
    service = LoginService.build(session)
    try:
        return await service.execute(data)
    except LoginService.InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
        ) from e
```

### 2. Сервисы

**Правило:** Dataclass с `build()` и одним публичным методом `execute()`. Запросы в БД только через DAO.

**Сервис с DAO (доменная логика):**

```python
@dataclass
class RegisterService:
    _user_dao: UserDAO
    _create_password: CreatePasswordService
    _create_token: CreateTokenService

    class RegisterServiceError(Exception):
        pass

    class UserAlreadyExistsError(RegisterServiceError):
        pass

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(
            _user_dao=UserDAO.build(session),
            _create_password=CreatePasswordService.build(),
            _create_token=CreateTokenService.build(),
        )

    async def execute(self, request: RegisterRequestDTO) -> TokenResponseDTO:
        existing = await self._user_dao.get_by_username(request.username)
        if existing:
            raise self.UserAlreadyExistsError
        password_hash = self._create_password.execute(request.password)
        user = await self._user_dao.create(request.username, password_hash)
        token = self._create_token.execute(user.id)
        return TokenResponseDTO(access_token=token)
```

**Чистый сервис (без DAO):**

```python
@dataclass
class VerifyPasswordService:
    @classmethod
    def build(cls) -> Self:
        return cls()

    def execute(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
```

### 3. DAO

**Правило:** Один DAO на домен. Все запросы к БД только здесь. Создаётся через `build(session)`.

```python
@dataclass
class UserDAO:
    _session: AsyncSession

    @classmethod
    def build(cls, session: AsyncSession) -> Self:
        return cls(_session=session)

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, username: str, password_hash: str) -> User:
        user = User(username=username, password=password_hash)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user
```

### 4. Ошибки сервисов

**Правило:** Базовый `*ServiceError` и конкретные наследники — внутри класса сервиса. API ловит и маппит в HTTP.

```python
class LoginServiceError(Exception):
    pass

class InvalidCredentialsError(LoginServiceError):
    pass
```

В API: `except LoginService.InvalidCredentialsError`

### 5. Транзакции

**Правило:** Request-scoped. `get_db` коммитит при успехе, откатывает при исключении.

```python
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 6. DTO

**Правило:** Request — `*RequestDTO`, Response — `*ResponseDTO`. Pydantic BaseModel.

```python
class LoginRequestDTO(BaseModel):
    username: str
    password: str

class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = 'bearer'
```

## Запуск

```bash
cd src
uv run python main.py
```

Миграции:

```bash
uv run alembic -c src/alembic.ini revision --autogenerate -m "created user model"
```

```bash
uv run alembic -c src/alembic.ini upgrade head
```



## Добавление нового домена

1. `daos/<domain>/` — DAO с `build(session)` и методами доступа к БД
2. `services/<domain>/` — сервисы, по одному файлу на операцию
3. `dtos/<domain>.py` — Request/Response DTO
4. `api/<domain>.py` — роутер с эндпоинтами
5. Подключить роутер в `main.py`

# Игры

Коллекция игр пользователя: добавление вручную или по ссылке Steam, стейты (backlog, in progress, completed, abandoned), избранное.

## Backend

| Компонент | Файл |
|-----------|------|
| API (GET/POST /users/me/games, POST fetch-steam) | [backend/src/api/user_games.py](../../backend/src/api/user_games.py) |
| CreateGameService | [backend/src/services/users/create_game_service.py](../../backend/src/services/users/create_game_service.py) |
| MyGamesService | [backend/src/services/users/my_games_service.py](../../backend/src/services/users/my_games_service.py) |
| FetchSteamGameService | [backend/src/services/games/fetch_steam_game_service.py](../../backend/src/services/games/fetch_steam_game_service.py) |
| UserGameDAO | [backend/src/daos/games/user_game_dao.py](../../backend/src/daos/games/user_game_dao.py) |
| DTO (Steam API response) | [backend/src/dtos/steam_api.py](../../backend/src/dtos/steam_api.py) |
| DTO (CreateGame, GameResponse, FetchSteam) | [backend/src/dtos/games.py](../../backend/src/dtos/games.py), [backend/src/dtos/users.py](../../backend/src/dtos/users.py) |
| GameState enum | [backend/src/constants/game.py](../../backend/src/constants/game.py) |

## Frontend

| Компонент | Файл |
|-----------|------|
| API (fetchMyGames, fetchSteamGame, createGame) | [frontend/app/api/users.api.ts](../../frontend/app/api/users.api.ts) |
| Модалка создания игры (3 шага) | [frontend/app/components/CreateGameModal.vue](../../frontend/app/components/CreateGameModal.vue) |
| Константы (Steam URL, стейты, ошибки) | [frontend/app/constants/games.ts](../../frontend/app/constants/games.ts) |

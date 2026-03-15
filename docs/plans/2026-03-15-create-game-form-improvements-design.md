# Create Game Form — Improvements Design

## Цель

Сделать форму создания игры богаче и удобнее: шире модалка, логичная раскладка кнопок, layout «картинка слева — данные справа», сбор genres/developers/publishers из Steam API.

## Решения

### UI/UX

**Модалка**
- Размер: `max-w-3xl` (~768px)
- Прокрутка: `max-h-[90vh] overflow-y-auto`

**Шаг 1 (ссылка Steam)**
- Кнопки: **Отмена** слева, **Пропустить** и **Далее** справа (`justify-between`)
- Отмена — `text-gray-400`, без акцента
- Пропустить и Далее — рядом справа, Далее — зелёная

**Шаг 2 (форма)**
- Grid: `grid-cols-[minmax(160px,200px)_1fr]`, на мобилке `grid-cols-1`
- Левая колонка: картинка (aspect-ratio или фикс. высота) + под ней поле URL Steam
- Правая колонка: name, genres (теги), developers, publishers, state, is_favorite
- Genres, developers, publishers — read-only, из Steam (или пусто, если без Steam)
- Кнопки: Назад | Отмена | Далее — Отмена слева, остальные справа

**Шаг 3 (оценка)**
- Заглушка «Скоро»
- Кнопки: Назад | Отмена | Добавить — та же раскладка

### Backend

**FetchSteamGameService**
- Возвращает: `name`, `image_url`, `steam_app_id`, `genres`, `developers`, `publishers`
- `genres`: `[{id: string, description: string}]` — как в Steam API
- `developers`: `string[]`
- `publishers`: `string[]`

**FetchSteamResponseDTO** (games.py)
- Добавить поля: `genres`, `developers`, `publishers`

**UserGame (модель)**
- `genres` — JSON (SQLite: `Text` + `json.dumps`/`json.loads`)
- `developers` — JSON `string[]`
- `publishers` — JSON `string[]`

**CreateGameRequestDTO**
- Добавить: `genres`, `developers`, `publishers` (все опциональные)

**CreateGameService / UserGameDAO**
- Принимать и сохранять новые поля

**GameResponseDTO**
- Добавить: `genres`, `developers`, `publishers` в ответ

**Миграция**
- Добавить колонки `genres`, `developers`, `publishers` в `user_game`

### Data Flow

1. Шаг 1: ввод URL → `fetch-steam` → ответ с name, image_url, steam_app_id, genres, developers, publishers
2. Шаг 2: форма заполняется из ответа; genres/developers/publishers read-only (если есть Steam)
3. Без Steam (Пропустить): genres, developers, publishers пустые
4. Submit: `createGame` отправляет все поля

**Черновик (draft)**
- Сохранять в localStorage: genres, developers, publishers
- При восстановлении — подставлять в форму

### Ошибки

- Steam API недоступен → переход на шаг 2 с пустой формой, steam_url сохранён
- Валидация name — без изменений
- При ошибке create — показывать сообщение, модалку не закрывать

### Frontend API

- `FetchSteamResponse`: genres, developers, publishers
- `CreateGamePayload`: genres, developers, publishers
- `GameResponse`: genres, developers, publishers

### Отложено

- Серии/франшизы (Resident Evil и т.п.) — Steam API не предоставляет; добавить позже

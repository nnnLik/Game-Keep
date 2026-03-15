# Create Game Form — Rich Design (v2)

## Цель

Расширить форму создания игры: больше модалка, одинаковый размер на всех этапах, release_date из Steam, кастомные жанры, заметка, даты игры, часы.

## Решения

### UI/UX

**Модалка**
- Размер: `max-w-6xl` (~1152px)
- Контент: `min-h-[420px]` — одинаковый размер на всех шагах
- Прокрутка: `max-h-[90vh] overflow-y-auto`

**Шаг 1**
- Поле URL, кнопки внизу
- Контент-блок с `min-h-[420px]`

**Шаг 2**
- Grid: картинка + URL слева, данные справа
- Поля: name, release_date, genres (Steam + кастомные), developers, publishers, state, is_favorite, note, date_started, date_finished, hours_played

**Шаг 3**
- Заглушка «Оценка» + кнопка «Добавить»
- Тот же `min-h-[420px]`

### Новые поля

**release_date**
- Из Steam API (`release_date.date`, напр. "Mar 23, 2023")
- Хранится как строка
- Read-only, если есть Steam

**Кастомные жанры**
- Кнопка «+» рядом с жанрами Steam
- Input 3–10 символов, Enter или «Добавить»
- Теги с возможностью удаления
- Валидация: 3–10 символов, без дубликатов

**Заметка (note)**
- Textarea, max 500 символов
- Опционально

**date_started, date_finished**
- `input type="date"` + кнопка «Сегодня»
- Опционально

**hours_played**
- `input type="number"` step=0.1, min=0, 1 знак после запятой
- Опционально

### Backend

**FetchSteamGameService / FetchSteamResponseDTO**
- `release_date: str | None` — из `release_date.date`

**UserGame (модель)**
- `release_date: str | None`
- `note: str | None` — max 500
- `date_started: date | None`
- `date_finished: date | None`
- `hours_played: float | None`

**CreateGameRequestDTO / GameResponseDTO**
- release_date, note, date_started, date_finished, hours_played

**Валидация**
- note: max 500
- hours_played: >= 0, 1 decimal
- dates: валидные

### Data Flow

- fetch-steam возвращает release_date
- Форма: genres = Steam + кастомные
- Draft: все новые поля
- createGame отправляет все поля

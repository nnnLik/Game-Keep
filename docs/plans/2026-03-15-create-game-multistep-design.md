# Create Game — Multi-step Design

## Цель

Многоступенчатое создание игры: ссылка Steam → загрузка данных → форма с карточками. Прогресс-бар + иконки.

## Решения

### Шаги

1. **Ссылка Steam** — ввод URL, кнопка «Далее». Бэкенд вызывает Steam API, возвращает name, image_url, steam_url.
2. **Форма** — карточки: Картинка (превью + URL), Основное (name, steam_url), Стейт (state, is_favorite), Оценка (заглушка).

### Модель UserGame

- name, image_url?, steam_url?, state, is_favorite

### API

- `POST /users/me/games/fetch-steam` — body: `{ steam_url }`, ответ: `{ name, image_url, steam_url }`
- `POST /users/me/games` — создание с полями name, image_url?, steam_url?, state, is_favorite

### UI

- Прогресс-бар сверху: иконка link → полоска → иконка gamepad
- Карточки: border, padding, заголовки секций
- При ошибке Steam — переход на шаг 2 с пустой формой, steam_url = введённый URL

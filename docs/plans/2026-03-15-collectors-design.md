# Коллекционеры — дизайн

Вкладка «Коллекционеры»: список пользователей, отсортированных по количеству игр, с cursor-based пагинацией. Клик → профиль `/users/[tag]`.

## Обзор

- **Страница:** `/collectors` — список пользователей
- **Навигация:** пункт «Коллекционеры» в сайдбаре
- **Профиль:** `/users/[tag]` — уже есть в worktree (GetProfileByTagService, API `/users/by-tag/{tag}`)
- **Доступ:** публичный (без авторизации)

## API

### GET /users

**Query:**
| Параметр | Тип | Default | Описание |
|----------|-----|---------|----------|
| limit | int | 20 | Размер страницы (1–100) |
| cursor | string | — | Курсор для следующей страницы |

**Ответ:**
```json
{
  "items": [
    {
      "tag": "john",
      "username": "John",
      "avatar_url": "avatars/xxx.png",
      "games_count": 42
    }
  ],
  "next_cursor": "eyJ..." | null,
  "has_more": true
}
```

**Курсор:** составной ключ `(games_count, user_id)`, base64-encoded. Сортировка: `games_count DESC`, `user_id ASC`.

**Фильтр:** только `is_registration_complete = true` и хотя бы 1 игра.

## Frontend

- **Страница `/collectors`:** заголовок, список карточек, кнопка «Загрузить ещё»
- **Карточка:** аватар, username, @tag, games_count. Клик → `/users/[tag]`
- **Пагинация:** при `has_more` — кнопка, запрос с `next_cursor`, append к списку

## Ошибки

- API 400/500 → сообщение + «Повторить»
- 404 профиль → «Пользователь не найден» + ссылка на коллекционеров

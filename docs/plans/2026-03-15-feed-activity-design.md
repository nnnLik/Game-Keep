# Лента и активность пользователя — дизайн

## Цель

Реализовать ленту действий всех коллекционеров (`/feed`) и вкладку «Активности» в профиле пользователя. Посты формируются из действий: создание карточки игры, добавление/снятие из избранного. У постов — лайки/дизлайки и комментарии (для постов «добавил игру»).

## Контекст

- **Лента** — `/feed`, только для авторизованных, бесконечный скролл.
- **Активность** — та же лента, отфильтрованная по автору (вкладка в профиле `/users/[tag]` и `/`).
- **Действия:** `game_created`, `favorite_added`, `favorite_removed`.
- **Пост «добавил игру»:** автор, картинка, текст «@tag добавил [игра] в [стейт]», первые 2–3 комментария + «Показать ещё», форма добавления комментария.
- **Пост «избранное»:** короткий текст «@tag пометил/убрал [игра] в/из Избранного».
- **Лайки/дизлайки** на постах — по аналогии с комментариями.

## Архитектура

### Модели

**Activity** — одна запись на каждое действие:
- `id`, `user_id`, `action_type` (enum), `user_game_id`, `created_at`

**ActivityVote** — лайк/дизлайк на пост:
- `activity_id`, `user_id`, `is_like`; unique(activity_id, user_id, is_like)

### Создание Activity

- **CreateGameService** — после создания UserGame создаёт Activity(game_created).
- **UpdateGameService** — при изменении is_favorite создаёт Activity(favorite_added | favorite_removed).

### API

- `GET /feed?cursor=&limit=` — лента (auth)
- `GET /users/by-tag/:tag/activity?cursor=&limit=` — активность пользователя (auth)
- `POST /activities/:id/vote` — лайк/дизлайк (auth)

Комментарии — существующий `POST /games/:id/comments`.

### Frontend

- `/feed` — auth guard, бесконечный скролл, компонент поста.
- Профиль — вкладка «Активности» использует тот же компонент, данные с `/users/by-tag/:tag/activity`.

## Поток данных

1. Пользователь создаёт игру → CreateGameService → UserGame + Activity(game_created).
2. Пользователь меняет is_favorite → UpdateGameService → Activity(favorite_added | favorite_removed).
3. Лента загружает GET /feed → посты с пагинацией по cursor.
4. Пользователь ставит лайк → POST /activities/:id/vote.
5. Пользователь пишет комментарий под постом → POST /games/:id/comments (существующий).

## Формат поста (API)

```ts
interface FeedPost {
  id: number
  action_type: 'game_created' | 'favorite_added' | 'favorite_removed'
  created_at: string
  author: { username: string | null; tag: string | null; avatar_url: string | null }
  game: { id: number; name: string; image_url: string | null; state: string }
  like_count: number
  dislike_count: number
  current_user_voted: { liked: boolean; disliked: boolean }
  comments?: CommentResponse[]  // только game_created, первые 2–3
  comments_total?: number
}
```

## Ошибки

- Неавторизованный доступ к /feed → редирект на логин.
- Удалённая игра — пост остаётся, ссылка может вести на 404.
- Удалённый пользователь — «Удалённый пользователь» в UI.

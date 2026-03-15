# User Model & Auth — Design

## Цель

Изменить модель пользователя и процесс регистрации/входа: username не уникален, добавлены уникальные tag и email, вход по email+пароль.

## Модель User

| Поле     | Тип  | Ограничения                                      |
|----------|------|--------------------------------------------------|
| username | str  | 5–255 символов, не уникален                      |
| tag      | str  | 3–15 символов, только a-z0-9, уникален (lowercase) |
| email    | str  | валидный email, уникален                         |
| password | str  | хэш, мин. 8 символов до хэширования             |

## Регистрация

- **Поля:** username, tag, email, password
- **Валидация:** username ≥5, tag 3–15 a-z0-9, email формат, password ≥8
- **Уникальность:** tag и email — при занятом возвращать отдельные сообщения
- **Тег:** хранить в lowercase, проверка уникальности case-insensitive

## Вход

- **Поля:** email, password
- **Логика:** поиск по email, проверка пароля

## API

- `POST /auth/register`: `{ username, tag, email, password }`
- `POST /auth/login`: `{ email, password }`
- Ошибки: `Tag already taken`, `Email already taken` — 400 с понятным detail

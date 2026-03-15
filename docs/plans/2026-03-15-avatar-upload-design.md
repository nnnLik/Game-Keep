# Avatar Upload — Design

## Цель

Позволить пользователю менять аватар на главной странице. При наведении на аватар — иконка редактирования, клик открывает выбор файла. После загрузки — обновление аватара в ленте без перезагрузки всей ленты.

## Решения

### Backend

- **API:** `PATCH /users/me/avatar` — multipart/form-data, `avatar: UploadFile` (обязательный).
- **Сервис:** `UpdateAvatarService` — валидация форматов (jpg, jpeg, png, gif, webp), лимит 25 МБ, сохранение в `avatars/{user_id}.{ext}` (перезапись при повторной загрузке).
- **UserDAO:** метод `update_avatar(user_id, avatar_url)` — обновление только `avatar_url`.
- **Ответ:** `MeResponseDTO` (как у `PATCH /me/banner`).
- **Ошибки:** 400 — неверный формат, слишком большой файл (сообщения на русском).

### Frontend — загрузка (index)

- **UI:** блок аватара с `group` и hover-оверлеем (как у баннера). При наведении — иконка `lucide:camera` или `lucide:palette`, клик — скрытый `<input type="file" accept="image/*">`.
- **Валидация:** формат image/*, ≤25 МБ.
- **Загрузка:** `uploadAvatar($api, file)` → `PATCH /users/me/avatar`, toast при успехе/ошибке, `emitAvatarChange()`, обновление `user.value` из ответа.

### Frontend — лента

- **feed.vue:** `fetchMe` при монтировании (для `currentUser.tag`).
- **Подписка:** на `avatarVersion` — при изменении пройти по `posts`, для постов с `post.author.tag === currentUser.tag` обновить `post.author.avatar_url` на новый (из `fetchMe`).

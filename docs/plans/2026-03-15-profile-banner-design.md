# Profile Banner Editor — Design

## Цель

Позволить пользователю рисовать баннер профиля во вкладке «Профиль». Баннер хранится на бекенде. При наведении на баннер — иконка палитры (и корзина, если баннер есть). Редактор на Fabric.js.

## Решения

### Backend

- **Модель User:** поле `banner_url: str | None` (аналогично `avatar_url`).
- **Миграция Alembic:** добавить колонку `banner_url`.
- **Хранение:** `uploads/banners/{user_id}.png`. Папка `banners` создаётся при setup.
- **API:**
  - `PATCH /users/me/banner` — multipart/form-data, PNG, лимит 2 MB.
  - `DELETE /users/me/banner` — удаление баннера.
- **MeResponseDTO, MeService:** добавить `banner_url`.

### Frontend

- **Баннер в профиле:** блок `h-40 w-full rounded-t-2xl`. Если `banner_url` — фон через `background-image`. При hover — overlay с иконками: палитра (lucide:palette) справа внизу, корзина (lucide:trash-2) справа от палитры (только если баннер есть).
- **Редактор (модалка):** Fabric.js, инструменты: карандаш, ластик, линия, прямоугольник, круг. Размер кисти, палитра, zoom, undo/redo, clear. Кнопки: «Отмена», «СОЗДАТЬ».
- **При наличии баннера:** загружать в редактор как фон. При клике на корзину — `confirm("Удалить баннер?")` → DELETE.

### Размер холста

900×300 px (соотношение 3:1).

### Ошибки

- Лимит 2 MB. Toast при ошибке загрузки/удаления.

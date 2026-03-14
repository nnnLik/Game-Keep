# Gametrack — Frontend

Nuxt 4 + Nuxt UI + TypeScript.

## Стек

- **Nuxt 4** — Vue-фреймворк
- **@nuxt/ui** — UI-компоненты (Reka UI + Tailwind)
- **@nuxt/icon** — иконки Iconify
- **@nuxt/fonts** — оптимизация шрифтов
- **@nuxt/image** — оптимизация изображений
- **@nuxt/devtools** — инструменты разработки

## Запуск

```bash
pnpm install
pnpm dev
```

Приложение: http://localhost:3000

## Конфиг

Nuxt использует `runtimeConfig`: значения из `nuxt.config.ts` переопределяются env-переменными `NUXT_PUBLIC_*`.

- `NUXT_PUBLIC_API_BASE` — URL API (дефолт: `http://localhost:9999`)
- `.env` — локальные переопределения (в .gitignore)

## Структура

- `app/pages/` — страницы (/, /feed, /login, /register)
- `app/layouts/` — default (с сайдбаром), auth (центрированная форма)
- `app/api/base.client.ts` — createApiClient: общая логика 401 → refresh → retry
- `app/api/auth.api.ts` — login, register, refreshTokens (auth-домен)
- `app/plugins/api.client.ts` — провайдит `$api`
- `app/stores/auth.ts` — Pinia store для токенов
- `app/middleware/auth.global.ts` — редирект на /login если нет токена

**Авторизованные запросы:** используй `$api` вместо `$fetch` — токен подставится, 401 обработается автоматически.

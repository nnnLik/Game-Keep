/** localStorage ключ черновика создания игры */
export const CREATE_GAME_DRAFT_KEY = 'gametrack_create_game_draft' as const

/** Дефолтный стейт при создании игры */
export const DEFAULT_GAME_STATE = 'backlog' as const

/** Базовый URL страницы игры в Steam */
export const STEAM_APP_URL_BASE = 'https://store.steampowered.com/app' as const

/** URL store.steampowered.com/app/{appid} */
export const STEAM_APP_URL_REGEX =
  /^https?:\/\/store\.steampowered\.com\/app\/(\d+)(?:\/|$)/i

export function buildSteamAppUrl(appId: string): string {
  return `${STEAM_APP_URL_BASE}/${appId}/`
}

export function isValidSteamAppUrl(url: string): boolean {
  return STEAM_APP_URL_REGEX.test(url.trim())
}

/** Placeholder для поля Steam URL */
export const STEAM_URL_PLACEHOLDER =
  'https://store.steampowered.com/app/...' as const

/** Подпись для опционального поля Steam */
export const STEAM_URL_OPTIONAL_LABEL = '(опционально)' as const

/** Сообщения об ошибках */
export const CreateGameErrors = {
  STEAM_URL_INVALID:
    'Некорректная ссылка. Нужен формат: store.steampowered.com/app/123',
  FETCH_FAILED: 'Не удалось загрузить данные',
  NAME_REQUIRED: 'Введите название игры',
  CREATE_FAILED: 'Не удалось добавить игру',
} as const

/** Placeholder для поля названия игры */
export const GAME_NAME_PLACEHOLDER = 'Название игры' as const

/** Placeholder для поля ссылки на картинку */
export const IMAGE_URL_PLACEHOLDER = 'Ссылка на картинку' as const

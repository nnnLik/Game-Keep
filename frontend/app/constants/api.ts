export const ApiEndpoint = {
  Auth: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REGISTER_START: '/auth/register-start',
    COMPLETE_REGISTRATION: '/auth/complete-registration',
    REFRESH: '/auth/refresh',
  },
  Users: {
    ME: '/users/me',
    ME_BANNER: '/users/me/banner',
    ME_GAMES: '/users/me/games',
    ME_GAMES_FETCH_STEAM: '/users/me/games/fetch-steam',
  },
} as const

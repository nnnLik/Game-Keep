export const ApiEndpoint = {
  Auth: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
  },
  Users: {
    ME: '/users/me',
    ME_GAMES: '/users/me/games',
  },
} as const

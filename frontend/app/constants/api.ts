export const ApiEndpoint = {
  Auth: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REGISTER_START: '/auth/register-start',
    COMPLETE_REGISTRATION: '/auth/complete-registration',
    REFRESH: '/auth/refresh',
  },
  Games: {
    BY_ID: (id: number) => `/games/${id}`,
    COMMENTS: (id: number) => `/games/${id}/comments`,
    COMMENT_VOTE: (gameId: number, commentId: number) =>
      `/games/${gameId}/comments/${commentId}/vote`,
  },
  Users: {
    BY_TAG: (tag: string) => `/users/by-tag/${tag}`,
    ME: '/users/me',
    ME_BANNER: '/users/me/banner',
    ME_GAMES: '/users/me/games',
    ME_GAMES_FETCH_STEAM: '/users/me/games/fetch-steam',
  },
} as const

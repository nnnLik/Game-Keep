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
  Feed: {
    LIST: '/feed',
    ACTIVITY: (tag: string) => `/users/by-tag/${tag}/activity`,
    VOTE: (id: number) => `/activities/${id}/vote`,
  },
  Users: {
    LIST: '/users',
    BY_TAG: (tag: string) => `/users/by-tag/${tag}`,
    ME: '/users/me',
    ME_AVATAR: '/users/me/avatar',
    ME_BANNER: '/users/me/banner',
    ME_GAMES: '/users/me/games',
    ME_GAME: (id: number) => `/users/me/games/${id}`,
    ME_GAMES_FETCH_STEAM: '/users/me/games/fetch-steam',
  },
} as const

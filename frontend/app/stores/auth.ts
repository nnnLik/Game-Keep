const cookieOpts = {
  maxAge: 60 * 60 * 24 * 7,
  sameSite: 'lax' as const,
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = useCookie('gametrack_access_token', cookieOpts)
  const refreshToken = useCookie('gametrack_refresh_token', cookieOpts)

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
  }

  return {
    accessToken,
    refreshToken,
    isAuthenticated,
    setTokens,
    clearTokens,
  }
})

import { ApiEndpoint } from '~/constants/api'

export interface TokenResponse {
  access_token: string
  refresh_token: string
}

export interface LoginPayload {
  username: string
  password: string
}

export async function refreshTokens(baseURL: string): Promise<boolean> {
  const authStore = useAuthStore()
  const token = authStore.refreshToken
  if (!token) return false

  try {
    const res = await $fetch<TokenResponse>(ApiEndpoint.Auth.REFRESH, {
      baseURL,
      method: 'POST',
      body: { refresh_token: token },
    })
    authStore.setTokens(res.access_token, res.refresh_token)
    return true
  } catch {
    return false
  }
}

export async function login(baseURL: string, payload: LoginPayload) {
  return $fetch<TokenResponse>(ApiEndpoint.Auth.LOGIN, {
    baseURL,
    method: 'POST',
    body: payload,
  })
}

export async function register(baseURL: string, payload: LoginPayload) {
  return $fetch<TokenResponse>(ApiEndpoint.Auth.REGISTER, {
    baseURL,
    method: 'POST',
    body: payload,
  })
}

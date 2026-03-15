import { ApiEndpoint } from '~/constants/api'

export async function registerStart(baseURL: string, payload: RegisterStartPayload) {
  return $fetch<TokenResponse>(ApiEndpoint.Auth.REGISTER_START, {
    baseURL,
    method: 'POST',
    body: payload,
  })
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  username: string
  tag: string
  email: string
  password: string
}

export interface RegisterStartPayload {
  email: string
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

export async function register(baseURL: string, payload: RegisterPayload) {
  return $fetch<TokenResponse>(ApiEndpoint.Auth.REGISTER, {
    baseURL,
    method: 'POST',
    body: payload,
  })
}

export async function completeRegistration(
  api: import('./base.client').ApiClient,
  payload: { username: string; tag: string; avatar?: File }
) {
  const formData = new FormData()
  formData.append('username', payload.username)
  formData.append('tag', payload.tag)
  if (payload.avatar) {
    formData.append('avatar', payload.avatar)
  }
  return api<{ ok: boolean }>(ApiEndpoint.Auth.COMPLETE_REGISTRATION, {
    method: 'POST',
    body: formData,
  })
}

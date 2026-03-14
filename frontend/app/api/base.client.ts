import { ApiEndpoint } from '~/constants/api'
import { refreshTokens } from './auth.api'

export type ApiClient = <T = unknown>(
  url: string,
  options?: Parameters<typeof $fetch<T>>[1]
) => Promise<T>

export function createApiClient(baseURL: string): ApiClient {
  const router = useRouter()

  return async function apiFetch<T>(
    url: string,
    options?: Parameters<typeof $fetch<T>>[1]
  ): Promise<T> {
    const authStore = useAuthStore()
    const isRefreshRequest = url === ApiEndpoint.Auth.REFRESH
    const hasToken = !!authStore.accessToken

    const doRequest = async (token?: string | null) => {
      const headers = new Headers(
        (options?.headers as Record<string, string>) || {}
      )
      if (token) headers.set('Authorization', `Bearer ${token}`)
      return $fetch<T>(url, {
        ...options,
        baseURL,
        headers: Object.fromEntries(headers),
      })
    }

    try {
      return await doRequest(authStore.accessToken ?? undefined)
    } catch (e: unknown) {
      const err = e as { statusCode?: number }
      if (err?.statusCode === 401 && !isRefreshRequest && hasToken) {
        const refreshed = await refreshTokens(baseURL)
        if (refreshed) return await doRequest(authStore.accessToken ?? undefined)
        authStore.clearTokens()
        await router.push('/login')
      }
      throw e
    }
  }
}

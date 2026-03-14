export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase as string
  const api = createApiClient(baseURL)

  return {
    provide: {
      api,
    },
  }
})

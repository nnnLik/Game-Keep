export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore()
  const isAuthPage = to.path === '/login' || to.path === '/register'
  const isCompleteRegistration = to.path === '/complete-registration'
  const isPublicPage = to.path === '/collectors' || to.path.startsWith('/users/')

  if (!authStore.isAuthenticated) {
    if (isPublicPage) return
    if (!isAuthPage && !isCompleteRegistration) return navigateTo('/login')
    if (isCompleteRegistration) return navigateTo('/register')
    return
  }

  if (isAuthPage && !isCompleteRegistration) {
    return navigateTo('/')
  }

  if (isCompleteRegistration) return

  const { $api } = useNuxtApp()
  try {
    const me = await $api<{ is_registration_complete: boolean }>('/users/me')
    if (!me.is_registration_complete) {
      return navigateTo('/complete-registration')
    }
  } catch {
    // 401 — редирект на логин в api client
  }
})

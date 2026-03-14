export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  const isAuthPage = to.path === '/login' || to.path === '/register'

  if (!authStore.isAuthenticated && !isAuthPage) {
    return navigateTo('/login')
  }
  if (authStore.isAuthenticated && isAuthPage) {
    return navigateTo('/')
  }
})

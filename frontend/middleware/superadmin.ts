import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(() => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }
  if (!auth.isSuperAdmin) {
    return navigateTo('/dashboard')
  }
})

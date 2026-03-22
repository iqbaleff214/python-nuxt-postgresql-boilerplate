// Client-side plugin: initializes WebSocket notifications for authenticated users.
export default defineNuxtPlugin(async (_nuxtApp) => {
  const authStore = useAuthStore()
  const notifStore = useNotificationsStore()

  if (authStore.isAuthenticated) {
    // Fetch initial unread count
    await notifStore.fetchUnreadCount().catch(() => {})

    // Connect WebSocket
    const { connect } = useNotifications()
    nextTick(() => connect())
  }
})

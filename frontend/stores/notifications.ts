import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Notification, PaginatedResponse, ApiResponse } from '~/types'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const page = ref(1)
  const total = ref(0)
  const pages = ref(1)

  async function fetchNotifications(opts?: { page?: number; unread_only?: boolean }) {
    const api = useApi()
    const params: Record<string, any> = {
      page: opts?.page ?? 1,
      per_page: 20,
    }
    if (opts?.unread_only) {
      params.unread_only = true
    }

    const response = await api.get<Notification[]>('/notifications', { params })

    if (response.success && response.data) {
      notifications.value = response.data as unknown as Notification[]
      if (response.meta) {
        page.value = response.meta.page
        total.value = response.meta.total
        pages.value = response.meta.total_pages
      }
    }
  }

  async function fetchUnreadCount() {
    const api = useApi()
    const response = await api.get<{ count: number }>('/notifications/unread-count')
    if (response.success && response.data) {
      unreadCount.value = response.data.count
    }
  }

  async function markRead(id: string) {
    const api = useApi()
    const response = await api.patch(`/notifications/${id}/read`)
    if (response.success) {
      const notif = notifications.value.find((n) => n.id === id)
      if (notif && !notif.read_at) {
        notif.read_at = new Date().toISOString()
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }
  }

  async function markAllRead() {
    const api = useApi()
    const response = await api.patch('/notifications/read-all')
    if (response.success) {
      notifications.value.forEach((n) => {
        if (!n.read_at) n.read_at = new Date().toISOString()
      })
      unreadCount.value = 0
    }
  }

  function addNotification(n: Notification) {
    notifications.value.unshift(n)
    if (!n.read_at) unreadCount.value++
  }

  return {
    notifications,
    unreadCount,
    page,
    total,
    pages,
    fetchNotifications,
    fetchUnreadCount,
    markRead,
    markAllRead,
    addNotification,
  }
})

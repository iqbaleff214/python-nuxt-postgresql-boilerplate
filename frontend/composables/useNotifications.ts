import { useAuthStore } from '~/stores/auth'
import { useNotificationsStore } from '~/stores/notifications'

export function useNotifications() {
  const authStore = useAuthStore()
  const notifStore = useNotificationsStore()
  const toast = useToast()

  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_ATTEMPTS = 10

  function connect() {
    if (!authStore.accessToken) return
    if (typeof window === 'undefined') return
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return

    const config = useRuntimeConfig()
    const wsBase = config.public.wsBase as string

    try {
      ws = new WebSocket(`${wsBase}/ws/notifications?token=${authStore.accessToken}`)

      ws.onopen = () => {
        reconnectAttempts = 0
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          // Ignore server-side ping keepalive messages
          if (message.type === 'ping') return
          notifStore.addNotification(message)
          toast.success(message.title)
        } catch {
          // ignore parse errors
        }
      }

      ws.onclose = (event) => {
        ws = null
        // Code 4001 = auth error, do not reconnect
        if (event.code !== 4001 && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts++
          const delay = Math.min(3000 * reconnectAttempts, 30000)
          reconnectTimer = setTimeout(connect, delay)
        }
      }

      ws.onerror = () => {
        ws?.close()
      }
    } catch {
      // WebSocket connection failed
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.close(1000, 'Client disconnecting')
      ws = null
    }
    reconnectAttempts = 0
  }

  function sendPing() {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('ping')
    }
  }

  return { connect, disconnect, sendPing }
}

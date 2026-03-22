import { ref } from 'vue'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
}

const toasts = ref<Toast[]>([])

export function useToast() {
  function add(type: Toast['type'], message: string, duration = 4000) {
    const id = Math.random().toString(36).substring(2, 9)
    const toast: Toast = { id, type, message, duration }
    toasts.value.push(toast)
    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
  }

  function remove(id: string) {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  return {
    toasts,
    success: (msg: string, duration?: number) => add('success', msg, duration),
    error: (msg: string, duration?: number) => add('error', msg, duration),
    info: (msg: string, duration?: number) => add('info', msg, duration),
    warning: (msg: string, duration?: number) => add('warning', msg, duration),
    remove,
  }
}

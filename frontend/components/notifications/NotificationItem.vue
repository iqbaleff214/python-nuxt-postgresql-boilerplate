<script setup lang="ts">
import type { Notification } from '~/types'

interface Props {
  notification: Notification
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), { compact: false })
const emit = defineEmits<{ read: [id: string] }>()

const typeConfig = computed(() => {
  const map: Record<string, { icon: string; color: string; bg: string }> = {
    announcement: {
      icon: 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z',
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
    },
    security: {
      icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
      color: 'text-amber-600',
      bg: 'bg-amber-50',
    },
    system: {
      icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      color: 'text-sky-600',
      bg: 'bg-sky-50',
    },
    default: {
      icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
      color: 'text-slate-600',
      bg: 'bg-slate-50',
    },
  }
  return map[props.notification.type] ?? map.default
})

function timeAgo(dateStr: string) {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div
    :class="[
      'flex gap-3 transition-colors',
      compact ? 'px-4 py-3' : 'p-4',
      !notification.read_at ? 'bg-indigo-50/40' : 'hover:bg-slate-50',
    ]"
    @click="!notification.read_at && emit('read', notification.id)"
  >
    <!-- Icon -->
    <div :class="['flex-shrink-0 flex items-center justify-center rounded-lg h-9 w-9', typeConfig.bg]">
      <svg :class="['h-5 w-5', typeConfig.color]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="typeConfig.icon" />
      </svg>
    </div>

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <div class="flex items-start justify-between gap-2">
        <p :class="['text-sm leading-snug', !notification.read_at ? 'font-semibold text-slate-900' : 'font-medium text-slate-700']">
          {{ notification.title }}
        </p>
        <span class="flex-shrink-0 text-xs text-slate-400">{{ timeAgo(notification.created_at) }}</span>
      </div>
      <p v-if="notification.body && !compact" class="mt-0.5 text-sm text-slate-500 line-clamp-2">
        {{ notification.body }}
      </p>

      <!-- Unread indicator -->
      <span v-if="!notification.read_at" class="mt-1 inline-flex h-1.5 w-1.5 rounded-full bg-indigo-500" />
    </div>
  </div>
</template>

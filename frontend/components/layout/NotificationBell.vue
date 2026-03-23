<script setup lang="ts">
import { useNotificationsStore } from '~/stores/notifications'
import { onClickOutside } from '@vueuse/core'

const notifStore = useNotificationsStore()
const isOpen = ref(false)
const bellRef = ref<HTMLElement | null>(null)

onClickOutside(bellRef, () => { isOpen.value = false })

const recentNotifications = computed(() => notifStore.notifications.slice(0, 5))

async function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (isOpen.value && recentNotifications.value.length === 0) {
    await notifStore.fetchNotifications()
  }
}

async function handleMarkAllRead() {
  await notifStore.markAllRead()
}

async function handleMarkRead(id: string) {
  await notifStore.markRead(id)
}
</script>

<template>
  <div ref="bellRef" class="relative">
    <button
      type="button"
      class="relative flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200"
      @click="toggleDropdown"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      <span
        v-if="notifStore.unreadCount > 0"
        class="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white leading-none"
      >
        {{ notifStore.unreadCount > 99 ? '99+' : notifStore.unreadCount }}
      </span>
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 top-11 z-50 w-80 rounded-xl border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800"
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3 dark:border-slate-700">
          <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Notifications</h3>
          <button
            v-if="notifStore.unreadCount > 0"
            type="button"
            class="text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
            @click="handleMarkAllRead"
          >
            Mark all read
          </button>
        </div>

        <!-- List -->
        <div class="divide-y divide-slate-100 max-h-80 overflow-y-auto dark:divide-slate-700">
          <template v-if="recentNotifications.length > 0">
            <NotificationItem
              v-for="notif in recentNotifications"
              :key="notif.id"
              :notification="notif"
              compact
              class="cursor-pointer"
              @read="handleMarkRead"
            />
          </template>
          <div v-else class="flex flex-col items-center gap-2 py-8">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <p class="text-sm text-slate-400 dark:text-slate-500">No notifications yet</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="border-t border-slate-100 px-4 py-3 dark:border-slate-700">
          <NuxtLink
            to="/notifications"
            class="block text-center text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
            @click="isOpen = false"
          >
            View all notifications
          </NuxtLink>
        </div>
      </div>
    </Transition>
  </div>
</template>

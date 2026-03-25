<script setup lang="ts">
import { useNotificationsStore } from '~/stores/notifications'

const notificationsStore = useNotificationsStore()
const route = useRoute()
const { t } = useI18n()

const navItems = computed(() => [
  {
    label: t('nav.home'),
    to: '/dashboard',
    icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  },
  {
    label: t('nav.alerts'),
    to: '/notifications',
    icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
  },
  {
    label: t('nav.profile'),
    to: '/profile',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  },
  {
    label: t('nav.security'),
    to: '/profile/security',
    icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
  },
])

function isActive(to: string) {
  if (to === '/dashboard') return route.path === to
  return route.path.startsWith(to)
}

const unreadCount = computed(() => notificationsStore.unreadCount)
</script>

<template>
  <nav
    class="fixed bottom-0 left-0 right-0 z-30 border-t border-slate-200 bg-white lg:hidden dark:border-slate-700 dark:bg-slate-900"
    style="padding-bottom: env(safe-area-inset-bottom)"
  >
    <div class="flex items-stretch">
      <NuxtLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :class="[
          'relative flex flex-1 flex-col items-center gap-1 py-2 text-[10px] font-medium transition-colors',
          isActive(item.to)
            ? 'text-indigo-600 dark:text-indigo-400'
            : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200',
        ]"
      >
        <!-- Active indicator -->
        <span
          v-if="isActive(item.to)"
          class="absolute top-0 left-1/2 h-0.5 w-8 -translate-x-1/2 rounded-full bg-indigo-600 dark:bg-indigo-400"
        />

        <!-- Icon wrapper (for badge) -->
        <span class="relative">
          <svg
            :class="['h-5 w-5', isActive(item.to) ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400 dark:text-slate-500']"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
          </svg>

          <!-- Unread badge on Alerts -->
          <span
            v-if="item.to === '/notifications' && unreadCount > 0"
            class="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white"
          >
            {{ unreadCount > 9 ? '9+' : unreadCount }}
          </span>
        </span>

        {{ item.label }}
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useNotificationsStore } from '~/stores/notifications'

definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()

const userName = computed(() => {
  const u = authStore.user
  if (!u) return 'there'
  return u.display_name || u.first_name || 'there'
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return t('dashboard.greetingMorning')
  if (hour < 17) return t('dashboard.greetingAfternoon')
  return t('dashboard.greetingEvening')
})

const recentNotifications = computed(() => notifStore.notifications.slice(0, 3))

onMounted(async () => {
  await Promise.all([
    notifStore.fetchNotifications(),
    notifStore.fetchUnreadCount(),
  ])
})

function timeAgo(dateStr: string) {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (seconds < 60) return t('common.justNow')
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return t('common.minutesAgo', { n: minutes })
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return t('common.hoursAgo', { n: hours })
  return t('common.daysAgo', { n: Math.floor(hours / 24) })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Hero welcome card -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary to-primary-600 p-6 text-white shadow-lg">
      <div class="relative z-10 flex items-center justify-between gap-4">
        <div>
          <p class="text-primary-300 text-sm font-medium">{{ greeting }},</p>
          <h1 class="text-2xl font-bold text-white mt-0.5">{{ userName }}! 👋</h1>
          <p class="mt-1 text-indigo-200 text-sm">
            {{ $t('dashboard.tagline') }}
          </p>
        </div>
        <AppAvatar
          :src="authStore.user?.avatar_url"
          :name="userName"
          size="xl"
          class="ring-4 ring-white/20 flex-shrink-0"
        />
      </div>
      <!-- Decorative circles -->
      <div class="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/10" />
      <div class="absolute -right-4 -bottom-12 h-32 w-32 rounded-full bg-white/10" />
    </div>

    <!-- Stats row -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <AppCard padding="md" shadow="sm">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <div>
            <p class="text-xs font-medium text-slate-500">{{ $t('dashboard.unreadNotifications') }}</p>
            <p class="text-2xl font-bold text-slate-900">{{ notifStore.unreadCount }}</p>
          </div>
        </div>
      </AppCard>

      <AppCard padding="md" shadow="sm">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <p class="text-xs font-medium text-slate-500">{{ $t('dashboard.accountStatus') }}</p>
            <p class="text-sm font-bold text-emerald-600 mt-0.5 capitalize">{{ authStore.user?.status }}</p>
          </div>
        </div>
      </AppCard>

      <AppCard padding="md" shadow="sm">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div>
            <p class="text-xs font-medium text-slate-500">{{ $t('dashboard.twoFASecurity') }}</p>
            <p :class="['text-sm font-bold mt-0.5', authStore.user?.is_2fa_enabled ? 'text-emerald-600' : 'text-amber-600']">
              {{ authStore.user?.is_2fa_enabled ? $t('dashboard.enabled') : $t('dashboard.disabled') }}
            </p>
          </div>
        </div>
      </AppCard>

      <AppCard padding="md" shadow="sm">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-100">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <p class="text-xs font-medium text-slate-500">{{ $t('dashboard.role') }}</p>
            <p class="text-sm font-bold text-slate-700 mt-0.5 capitalize">{{ authStore.user?.role }}</p>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Bottom row -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Quick Links -->
      <AppCard :title="$t('dashboard.quickActions')" :subtitle="$t('dashboard.quickActionsSubtitle')">
        <div class="space-y-2">
          <NuxtLink
            to="/profile"
            class="flex items-center gap-3 rounded-lg p-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
          >
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-900">{{ $t('dashboard.editProfile') }}</p>
              <p class="text-xs text-slate-500">{{ $t('dashboard.editProfileSub') }}</p>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </NuxtLink>

          <NuxtLink
            to="/profile/security"
            class="flex items-center gap-3 rounded-lg p-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
          >
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-900">{{ $t('dashboard.securitySettings') }}</p>
              <p class="text-xs text-slate-500">{{ $t('dashboard.securitySettingsSub') }}</p>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </NuxtLink>

          <NuxtLink
            to="/notifications"
            class="flex items-center gap-3 rounded-lg p-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
          >
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-900">{{ $t('dashboard.notifications') }}</p>
              <p class="text-xs text-slate-500">{{ $t('dashboard.notificationsSub') }}</p>
            </div>
            <span v-if="notifStore.unreadCount > 0" class="flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
              {{ notifStore.unreadCount }}
            </span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </NuxtLink>
        </div>
      </AppCard>

      <!-- Recent Notifications -->
      <AppCard :title="$t('dashboard.recentNotifications')" :subtitle="$t('dashboard.recentNotificationsSubtitle')">
        <div v-if="recentNotifications.length > 0" class="-mx-6 divide-y divide-slate-100">
          <NotificationsNotificationItem
            v-for="notif in recentNotifications"
            :key="notif.id"
            :notification="notif"
            compact
          />
        </div>
        <div v-else class="flex flex-col items-center gap-2 py-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <p class="text-sm text-slate-400">{{ $t('dashboard.noNotifications') }}</p>
        </div>

        <template #footer>
          <NuxtLink to="/notifications" class="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors">
            {{ $t('dashboard.viewAll') }} &rarr;
          </NuxtLink>
        </template>
      </AppCard>
    </div>
  </div>
</template>

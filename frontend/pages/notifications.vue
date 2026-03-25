<script setup lang="ts">
import { useNotificationsStore } from '~/stores/notifications'

definePageMeta({ middleware: 'auth' })

const notifStore = useNotificationsStore()
const toast = useToast()
const { t } = useI18n()

const filter = ref<'all' | 'unread'>('all')
const isLoading = ref(false)

async function loadPage(page: number) {
  isLoading.value = true
  await notifStore.fetchNotifications({
    page,
    unread_only: filter.value === 'unread',
  })
  isLoading.value = false
}

async function handleMarkAllRead() {
  await notifStore.markAllRead()
  toast.success(t('notifications.markedAllRead'))
}

async function handleMarkRead(id: string) {
  await notifStore.markRead(id)
}

watch(filter, () => loadPage(1))

onMounted(() => loadPage(1))
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">{{ $t('notifications.title') }}</h1>
        <p class="mt-0.5 text-sm text-slate-500">
          {{ notifStore.unreadCount > 0 ? $t('notifications.unread', { n: notifStore.unreadCount }) : $t('notifications.allCaughtUp') }}
        </p>
      </div>

      <div class="flex items-center gap-2">
        <AppButton
          v-if="notifStore.unreadCount > 0"
          variant="outline"
          size="sm"
          @click="handleMarkAllRead"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ $t('notifications.markAllRead') }}
        </AppButton>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="flex gap-1 rounded-xl bg-slate-100 p-1 w-fit">
      <button
        v-for="opt in [{ value: 'all', label: $t('notifications.all') }, { value: 'unread', label: $t('notifications.unreadTab') }]"
        :key="opt.value"
        type="button"
        :class="[
          'rounded-lg px-4 py-1.5 text-sm font-medium transition-all',
          filter === opt.value
            ? 'bg-white text-slate-900 shadow-sm'
            : 'text-slate-500 hover:text-slate-700',
        ]"
        @click="filter = opt.value as 'all' | 'unread'"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Notifications list -->
    <div class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div v-if="isLoading" class="divide-y divide-slate-100">
        <div v-for="i in 5" :key="i" class="flex gap-3 px-4 py-4 animate-pulse">
          <div class="h-9 w-9 rounded-lg bg-slate-200 flex-shrink-0" />
          <div class="flex-1 space-y-2">
            <div class="h-4 w-1/2 rounded bg-slate-200" />
            <div class="h-3 w-3/4 rounded bg-slate-200" />
          </div>
        </div>
      </div>

      <div v-else-if="notifStore.notifications.length === 0" class="flex flex-col items-center gap-3 py-16">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <div class="text-center">
          <p class="font-medium text-slate-700">
            {{ filter === 'unread' ? $t('notifications.noUnread') : $t('notifications.noNotifs') }}
          </p>
          <p class="text-sm text-slate-400 mt-0.5">
            {{ filter === 'unread' ? $t('notifications.caughtUp') : $t('notifications.willAppear') }}
          </p>
        </div>
        <button
          v-if="filter === 'unread'"
          type="button"
          class="text-sm font-medium text-indigo-600 hover:text-indigo-700"
          @click="filter = 'all'"
        >
          {{ $t('notifications.viewAll') }}
        </button>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <NotificationsNotificationItem
          v-for="notif in notifStore.notifications"
          :key="notif.id"
          :notification="notif"
          class="cursor-pointer"
          @read="handleMarkRead"
        />
      </div>
    </div>

    <!-- Pagination -->
    <AppPagination
      v-if="notifStore.total > 20"
      :page="notifStore.page"
      :total="notifStore.total"
      :per-page="20"
      @change="loadPage"
    />
  </div>
</template>

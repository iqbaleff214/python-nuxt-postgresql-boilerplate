<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const { t } = useI18n()
const { collapsed, mobileOpen, closeMobile } = useSidebar()

interface NavItem {
  label: string
  to: string
  icon: string
}

const navItems = computed<NavItem[]>(() => [
  {
    label: t('nav.dashboard'),
    to: '/dashboard',
    icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  },
  // {
  //   label: t('nav.notifications'),
  //   to: '/notifications',
  //   icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
  // },
  // {
  //   label: t('nav.profile'),
  //   to: '/profile',
  //   icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  // },
  // {
  //   label: t('nav.security'),
  //   to: '/profile/security',
  //   icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
  // },
])

const adminNavItems = computed<NavItem[]>(() => [
  {
    label: t('nav.users'),
    to: '/admin/users',
    icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
  },
  {
    label: t('nav.announcements'),
    to: '/admin/announcements',
    icon: 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z',
  },
])

function isActive(to: string) {
  if (to === '/dashboard') return route.path === to
  return route.path.startsWith(to)
}
</script>

<template>
  <!-- Mobile overlay -->
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-20 bg-slate-900/50 backdrop-blur-sm lg:hidden"
      @click="closeMobile"
    />
  </Transition>

  <!-- Sidebar -->
  <aside
    :class="[
      'fixed left-0 top-0 z-30 flex h-full w-64 flex-col bg-white border-r border-slate-200 dark:bg-slate-900 dark:border-slate-700',
      'transition-all duration-300 ease-in-out',
      'lg:static lg:h-screen lg:translate-x-0',
      collapsed ? 'lg:w-16' : 'lg:w-64',
      mobileOpen ? 'translate-x-0' : '-translate-x-full',
    ]"
  >
    <!-- Logo -->
    <div
      class="flex h-16 flex-shrink-0 items-center border-b border-slate-200 dark:border-slate-700 transition-all duration-300"
      :class="collapsed ? 'justify-center px-0' : 'gap-3 px-5'"
    >
      <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-primary shadow-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div v-if="!collapsed" class="overflow-hidden">
        <p class="text-base font-bold text-slate-900 dark:text-slate-100 whitespace-nowrap">404NFID</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 whitespace-nowrap">Starter Kit</p>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-4 transition-all duration-300" :class="collapsed ? 'px-2' : 'px-3'">
      <div class="space-y-0.5">
        <p
          v-if="!collapsed"
          class="mb-2 px-3 text-[11px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500"
        >
          {{ $t('nav.main') }}
        </p>
        <div v-else class="mb-2 h-[18px]" />

        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :title="collapsed ? item.label : undefined"
          :class="[
            'flex items-center rounded-lg py-2 text-sm font-medium transition-all duration-150',
            collapsed ? 'justify-center px-0' : 'gap-3 px-3',
            isActive(item.to)
              ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary-300'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200',
          ]"
          @click="closeMobile"
        >
          <svg
            :class="['h-5 w-5 flex-shrink-0', isActive(item.to) ? 'text-primary dark:text-primary-300' : 'text-slate-400 dark:text-slate-500']"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
          </svg>
          <span v-if="!collapsed" class="whitespace-nowrap overflow-hidden">{{ item.label }}</span>
        </NuxtLink>
      </div>

      <!-- Admin section -->
      <div v-if="authStore.isSuperAdmin" class="mt-6 space-y-0.5">
        <p
          v-if="!collapsed"
          class="mb-2 px-3 text-[11px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500"
        >
          {{ $t('nav.administration') }}
        </p>
        <div v-else class="mb-2 h-[18px]" />

        <NuxtLink
          v-for="item in adminNavItems"
          :key="item.to"
          :to="item.to"
          :title="collapsed ? item.label : undefined"
          :class="[
            'flex items-center rounded-lg py-2 text-sm font-medium transition-all duration-150',
            collapsed ? 'justify-center px-0' : 'gap-3 px-3',
            isActive(item.to)
              ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary-300'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200',
          ]"
          @click="closeMobile"
        >
          <svg
            :class="['h-5 w-5 flex-shrink-0', isActive(item.to) ? 'text-primary dark:text-primary-300' : 'text-slate-400 dark:text-slate-500']"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
          </svg>
          <span v-if="!collapsed" class="whitespace-nowrap overflow-hidden">{{ item.label }}</span>
        </NuxtLink>
      </div>
    </nav>

    <!-- Bottom section -->
    <div class="flex-shrink-0 border-t border-slate-200 p-3 dark:border-slate-700">
      <!-- User info -->
      <div
        class="flex items-center rounded-lg px-2 py-2 transition-all duration-300"
        :class="collapsed ? 'justify-center' : 'gap-3'"
        :title="collapsed ? (authStore.user?.display_name || `${authStore.user?.first_name} ${authStore.user?.last_name}`) : undefined"
      >
        <AppAvatar
          :src="authStore.user?.avatar_url"
          :name="authStore.user?.display_name || `${authStore.user?.first_name} ${authStore.user?.last_name}`"
          size="sm"
        />
        <div v-if="!collapsed" class="flex-1 min-w-0">
          <p class="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
            {{ authStore.user?.display_name || `${authStore.user?.first_name} ${authStore.user?.last_name}` }}
          </p>
          <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ authStore.user?.role }}</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { onClickOutside } from '@vueuse/core'

const authStore = useAuthStore()
const router = useRouter()
const userMenuRef = ref<HTMLElement | null>(null)
const isUserMenuOpen = ref(false)

const emit = defineEmits<{ toggleSidebar: [] }>()

onClickOutside(userMenuRef, () => { isUserMenuOpen.value = false })

const userName = computed(() => {
  if (!authStore.user) return 'User'
  return authStore.user.display_name || `${authStore.user.first_name} ${authStore.user.last_name}`
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-slate-200 bg-white px-4 lg:px-6 dark:bg-slate-900 dark:border-slate-700">
    <!-- Mobile menu toggle -->
    <button
      type="button"
      class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700 lg:hidden"
      @click="emit('toggleSidebar')"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>

    <!-- Logo / App name -->
    <NuxtLink to="/dashboard" class="flex items-center gap-2 lg:hidden">
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <span class="text-base font-bold text-slate-900">Loqato</span>
    </NuxtLink>

    <!-- Spacer -->
    <div class="flex-1" />

    <!-- Right side actions -->
    <div class="flex items-center gap-2">
      <!-- Theme Toggle -->
      <ThemeToggle />

      <!-- Notification Bell -->
      <NotificationBell />

      <!-- User Menu -->
      <div ref="userMenuRef" class="relative">
        <button
          type="button"
          class="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-slate-100 dark:hover:bg-slate-700"
          @click="isUserMenuOpen = !isUserMenuOpen"
        >
          <AppAvatar
            :src="authStore.user?.avatar_url"
            :name="userName"
            size="sm"
          />
          <span class="hidden font-medium text-slate-700 sm:block">{{ userName }}</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 scale-95 -translate-y-1"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="isUserMenuOpen"
            class="absolute right-0 top-11 z-50 w-52 rounded-xl border border-slate-200 bg-white shadow-lg py-1 dark:border-slate-700 dark:bg-slate-800"
          >
            <div class="border-b border-slate-100 px-3 pb-2 pt-1.5 dark:border-slate-700">
              <p class="text-xs font-semibold text-slate-900 truncate dark:text-slate-100">{{ userName }}</p>
              <p class="text-xs text-slate-500 truncate dark:text-slate-400">{{ authStore.user?.email }}</p>
            </div>

            <NuxtLink
              to="/profile"
              class="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors dark:text-slate-300 dark:hover:bg-slate-700"
              @click="isUserMenuOpen = false"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profile
            </NuxtLink>

            <NuxtLink
              to="/profile/security"
              class="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors dark:text-slate-300 dark:hover:bg-slate-700"
              @click="isUserMenuOpen = false"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Security
            </NuxtLink>

            <div class="my-1 border-t border-slate-100 dark:border-slate-700" />

            <button
              type="button"
              class="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors dark:hover:bg-red-900/20"
              @click="handleLogout"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign out
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()

// Redirect non-admins
if (!authStore.isSuperAdmin) {
  await navigateTo('/dashboard')
}

const sidebarOpen = ref(false)
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
    <AppSidebar :open="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex min-w-0 flex-1 flex-col">
      <AppHeader @toggle-sidebar="sidebarOpen = !sidebarOpen" />

      <!-- Admin breadcrumb bar -->
      <div class="border-b border-slate-200 bg-white px-4 py-2 lg:px-6 dark:border-slate-700 dark:bg-slate-900">
        <div class="flex items-center gap-2 text-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <span class="rounded bg-amber-50 px-1.5 py-0.5 text-xs font-medium text-amber-700">Admin Area</span>
        </div>
      </div>

      <main class="flex-1 overflow-y-auto">
        <div class="mx-auto max-w-7xl px-4 py-6 pb-20 sm:px-6 lg:px-8 lg:pb-6">
          <slot />
        </div>
      </main>
    </div>

    <!-- Mobile bottom navigation -->
    <AppBottomNav />
  </div>
</template>

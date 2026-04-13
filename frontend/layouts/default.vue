<script setup lang="ts">
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main content area -->
    <div class="flex min-w-0 flex-1 flex-col">
      <!-- Header -->
      <AppHeader />

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto">
        <div class="mx-auto max-w-7xl px-4 py-6 pb-20 sm:px-6 lg:px-8 lg:pb-6">
          <slot />
        </div>
      </main>
    </div>

    <!-- Mobile bottom navigation -->
    <AppBottomNav v-if="false" />
  </div>
</template>

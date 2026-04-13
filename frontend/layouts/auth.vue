<template>
  <div class="min-h-screen bg-[#F5F7FA] flex items-center justify-center p-4">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-1/2 -right-1/4 h-[600px] w-[600px] rounded-full bg-primary/5 blur-3xl" />
      <div class="absolute -bottom-1/2 -left-1/4 h-[600px] w-[600px] rounded-full bg-primary/5 blur-3xl" />
    </div>

    <div class="relative w-full max-w-md">
      <!-- Logo -->
      <div class="mb-8 flex flex-col items-center gap-3 text-center">
        <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-lg">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-primary">404NFID</h1>
          <p class="text-sm text-slate-500">Starter Kit</p>
        </div>
      </div>

      <!-- Card -->
      <div class="rounded-2xl bg-white shadow-xl border border-slate-200 p-8">
        <slot />
      </div>

      <p class="mt-6 text-center text-xs text-slate-400">
        &copy; {{ new Date().getFullYear() }} 404NFID. All rights reserved.
      </p>
    </div>
  </div>
</template>

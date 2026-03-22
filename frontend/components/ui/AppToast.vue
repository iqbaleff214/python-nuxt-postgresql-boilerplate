<script setup lang="ts">
import type { Toast } from '~/composables/useToast'

interface Props {
  toast: Toast
}

const props = defineProps<Props>()
const { remove } = useToast()

const variantConfig = computed(() => {
  const map = {
    success: {
      wrapper: 'bg-white border-l-4 border-emerald-500',
      icon: 'text-emerald-500',
      title: 'text-slate-900',
    },
    error: {
      wrapper: 'bg-white border-l-4 border-red-500',
      icon: 'text-red-500',
      title: 'text-slate-900',
    },
    warning: {
      wrapper: 'bg-white border-l-4 border-amber-500',
      icon: 'text-amber-500',
      title: 'text-slate-900',
    },
    info: {
      wrapper: 'bg-white border-l-4 border-sky-500',
      icon: 'text-sky-500',
      title: 'text-slate-900',
    },
  }
  return map[props.toast.type] ?? map.info
})
</script>

<template>
  <div
    :class="[
      'flex items-start gap-3 rounded-lg shadow-lg px-4 py-3 pointer-events-auto',
      'min-w-[280px] max-w-sm',
      variantConfig.wrapper,
    ]"
    role="alert"
  >
    <div :class="['flex-shrink-0 mt-0.5', variantConfig.icon]">
      <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <svg v-else-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <svg v-else-if="toast.type === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>

    <p :class="['flex-1 text-sm font-medium', variantConfig.title]">{{ toast.message }}</p>

    <button
      type="button"
      class="flex-shrink-0 rounded p-0.5 text-slate-400 hover:text-slate-600 transition-colors"
      @click="remove(toast.id)"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  dismissible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  dismissible: false,
})

const emit = defineEmits<{ dismiss: [] }>()

const visible = ref(true)

const variantConfig = computed(() => {
  const map = {
    success: {
      wrapper: 'bg-emerald-50 border-emerald-200',
      icon: 'text-emerald-500',
      title: 'text-emerald-800',
      body: 'text-emerald-700',
    },
    error: {
      wrapper: 'bg-red-50 border-red-200',
      icon: 'text-red-500',
      title: 'text-red-800',
      body: 'text-red-700',
    },
    warning: {
      wrapper: 'bg-amber-50 border-amber-200',
      icon: 'text-amber-500',
      title: 'text-amber-800',
      body: 'text-amber-700',
    },
    info: {
      wrapper: 'bg-sky-50 border-sky-200',
      icon: 'text-sky-500',
      title: 'text-sky-800',
      body: 'text-sky-700',
    },
  }
  return map[props.variant]
})
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 -translate-y-1"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="visible"
      :class="['flex gap-3 rounded-lg border p-4', variantConfig.wrapper]"
      role="alert"
    >
      <!-- Icon -->
      <div :class="['mt-0.5 flex-shrink-0', variantConfig.icon]">
        <svg v-if="variant === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else-if="variant === 'error'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else-if="variant === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <p v-if="title" :class="['text-sm font-semibold', variantConfig.title]">{{ title }}</p>
        <div :class="['text-sm', variantConfig.body, title ? 'mt-0.5' : '']">
          <slot />
        </div>
      </div>

      <!-- Dismiss -->
      <button
        v-if="dismissible"
        type="button"
        :class="['flex-shrink-0 rounded p-0.5 transition-colors hover:bg-black/10', variantConfig.icon]"
        @click="visible = false; emit('dismiss')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </Transition>
</template>

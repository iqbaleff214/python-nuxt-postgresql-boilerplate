<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  padding: 'md',
  shadow: 'sm',
})

const paddingClasses = computed(() => {
  const map: Record<string, string> = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }
  return map[props.padding] ?? map.md
})

const shadowClasses = computed(() => {
  const map: Record<string, string> = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  }
  return map[props.shadow] ?? map.sm
})
</script>

<template>
  <div :class="['rounded-xl border border-slate-200 bg-white', shadowClasses]">
    <div v-if="title || subtitle || $slots.header" class="border-b border-slate-100 px-6 py-4">
      <slot name="header">
        <h3 v-if="title" class="text-base font-semibold text-slate-900">{{ title }}</h3>
        <p v-if="subtitle" class="mt-0.5 text-sm text-slate-500">{{ subtitle }}</p>
      </slot>
    </div>
    <div :class="paddingClasses">
      <slot />
    </div>
    <div v-if="$slots.footer" class="border-t border-slate-100 px-6 py-4">
      <slot name="footer" />
    </div>
  </div>
</template>

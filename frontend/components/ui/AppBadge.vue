<script setup lang="ts">
interface Props {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'default' | 'indigo'
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
})

const variantClasses = computed(() => {
  const map: Record<string, string> = {
    success: 'bg-emerald-100 text-emerald-700',
    warning: 'bg-amber-100 text-amber-700',
    danger: 'bg-red-100 text-red-700',
    info: 'bg-sky-100 text-sky-700',
    indigo: 'bg-indigo-100 text-indigo-700',
    default: 'bg-slate-100 text-slate-600',
  }
  return map[props.variant] ?? map.default
})

const sizeClasses = computed(() => {
  return props.size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'
})
</script>

<template>
  <span :class="['inline-flex items-center gap-1 rounded-full font-medium', variantClasses, sizeClasses]">
    <slot />
  </span>
</template>

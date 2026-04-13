<script setup lang="ts">
interface Props {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'default' | 'primary' | 'processing' | 'completed' | 'archived'
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
})

const variantClasses = computed(() => {
  const map: Record<string, string> = {
    success:    'bg-emerald-100 text-emerald-700',
    completed:  'bg-emerald-100 text-emerald-700',
    warning:    'bg-amber-100 text-amber-700',
    danger:     'bg-red-100 text-red-700',
    info:       'bg-blue-100 text-blue-700',
    processing: 'bg-blue-100 text-blue-700',
    primary:    'bg-primary/10 text-primary-700',
    archived:   'bg-slate-100 text-slate-500',
    default:    'bg-slate-100 text-slate-600',
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

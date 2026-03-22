<script setup lang="ts">
interface Props {
  src?: string | null
  name?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  shape?: 'circle' | 'rounded'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  shape: 'circle',
})

const sizeClasses = computed(() => {
  const map: Record<string, string> = {
    xs: 'h-6 w-6 text-xs',
    sm: 'h-8 w-8 text-sm',
    md: 'h-10 w-10 text-base',
    lg: 'h-12 w-12 text-lg',
    xl: 'h-16 w-16 text-xl',
  }
  return map[props.size] ?? map.md
})

const shapeClass = computed(() => (props.shape === 'circle' ? 'rounded-full' : 'rounded-lg'))

const initials = computed(() => {
  if (!props.name) return '?'
  const parts = props.name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
})

const colors = [
  'bg-indigo-500',
  'bg-violet-500',
  'bg-sky-500',
  'bg-emerald-500',
  'bg-amber-500',
  'bg-pink-500',
]

const bgColor = computed(() => {
  if (!props.name) return colors[0]
  let hash = 0
  for (let i = 0; i < props.name.length; i++) {
    hash = props.name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
})

const imgError = ref(false)
</script>

<template>
  <div
    :class="[
      'inline-flex flex-shrink-0 items-center justify-center overflow-hidden',
      sizeClasses,
      shapeClass,
    ]"
  >
    <img
      v-if="src && !imgError"
      :src="src"
      :alt="name ?? 'Avatar'"
      class="h-full w-full object-cover"
      @error="imgError = true"
    />
    <span
      v-else
      :class="['flex h-full w-full items-center justify-center font-semibold text-white', bgColor]"
    >
      {{ initials }}
    </span>
  </div>
</template>

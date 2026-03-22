<script setup lang="ts">
interface Props {
  page: number
  total: number
  perPage: number
}

const props = defineProps<Props>()
const emit = defineEmits<{ change: [page: number] }>()

const totalPages = computed(() => Math.ceil(props.total / props.perPage))

const pageNumbers = computed(() => {
  const current = props.page
  const last = totalPages.value
  const delta = 2
  const range: (number | '...')[] = []

  for (let i = Math.max(2, current - delta); i <= Math.min(last - 1, current + delta); i++) {
    range.push(i)
  }

  if (current - delta > 2) range.unshift('...')
  if (current + delta < last - 1) range.push('...')

  range.unshift(1)
  if (last > 1) range.push(last)

  return range
})

const from = computed(() => (props.page - 1) * props.perPage + 1)
const to = computed(() => Math.min(props.page * props.perPage, props.total))
</script>

<template>
  <div v-if="totalPages > 1" class="flex items-center justify-between gap-4">
    <p class="text-sm text-slate-500">
      Showing <span class="font-medium text-slate-700">{{ from }}</span> to
      <span class="font-medium text-slate-700">{{ to }}</span> of
      <span class="font-medium text-slate-700">{{ total }}</span> results
    </p>

    <nav class="flex items-center gap-1">
      <button
        type="button"
        :disabled="page <= 1"
        class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        @click="emit('change', page - 1)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <template v-for="(p, i) in pageNumbers" :key="i">
        <span v-if="p === '...'" class="flex h-8 w-8 items-center justify-center text-sm text-slate-400">
          …
        </span>
        <button
          v-else
          type="button"
          :class="[
            'flex h-8 w-8 items-center justify-center rounded-lg text-sm font-medium transition-colors',
            p === page
              ? 'bg-indigo-600 text-white'
              : 'border border-slate-200 text-slate-600 hover:bg-slate-50',
          ]"
          @click="emit('change', p as number)"
        >
          {{ p }}
        </button>
      </template>

      <button
        type="button"
        :disabled="page >= totalPages"
        class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        @click="emit('change', page + 1)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
interface Column {
  key: string
  label: string
  sortable?: boolean
  class?: string
}

interface Props {
  columns: Column[]
  rows: Record<string, any>[]
  loading?: boolean
  emptyMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  emptyMessage: 'No data found',
})

const emit = defineEmits<{ sort: [key: string] }>()

const skeletonRows = Array.from({ length: 5 })
</script>

<template>
  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
    <div class="overflow-x-auto">
      <table class="w-full divide-y divide-slate-200">
        <thead class="bg-slate-50">
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :class="[
                'px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500',
                col.class ?? '',
                col.sortable ? 'cursor-pointer select-none hover:text-slate-700' : '',
              ]"
              @click="col.sortable && emit('sort', col.key)"
            >
              <div class="flex items-center gap-1">
                {{ col.label }}
                <svg
                  v-if="col.sortable"
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-3.5 w-3.5 text-slate-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                </svg>
              </div>
            </th>
          </tr>
        </thead>

        <tbody class="divide-y divide-slate-100 bg-white">
          <!-- Loading skeleton -->
          <template v-if="loading">
            <tr v-for="i in skeletonRows" :key="i" class="animate-pulse">
              <td v-for="col in columns" :key="col.key" class="px-4 py-3">
                <div class="h-4 rounded bg-slate-200" :class="col.key === 'actions' ? 'w-16' : 'w-full max-w-[180px]'" />
              </td>
            </tr>
          </template>

          <!-- Empty state -->
          <tr v-else-if="rows.length === 0">
            <td :colspan="columns.length" class="px-4 py-12 text-center">
              <div class="flex flex-col items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p class="text-sm text-slate-500">{{ emptyMessage }}</p>
              </div>
            </td>
          </tr>

          <!-- Data rows -->
          <template v-else>
            <tr
              v-for="(row, idx) in rows"
              :key="idx"
              class="transition-colors hover:bg-slate-50/60"
            >
              <td
                v-for="col in columns"
                :key="col.key"
                :class="['px-4 py-3 text-sm text-slate-700', col.class ?? '']"
              >
                <slot :name="col.key" :row="row" :value="row[col.key]">
                  {{ row[col.key] }}
                </slot>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

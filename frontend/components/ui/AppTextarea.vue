<script setup lang="ts">
interface Props {
  label?: string
  error?: string
  hint?: string
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  rows?: number
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
  rows: 4,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputId = computed(() => props.id || `textarea-${Math.random().toString(36).slice(2, 7)}`)
</script>

<template>
  <div class="w-full">
    <label
      v-if="label"
      :for="inputId"
      class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-0.5">*</span>
    </label>

    <textarea
      :id="inputId"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :rows="rows"
      :class="[
        'w-full rounded-lg border px-3 py-2 text-sm text-slate-900 placeholder-slate-400 dark:text-slate-100 dark:placeholder-slate-500',
        'transition-all duration-150 focus:outline-none focus:ring-2 resize-y',
        error
          ? 'border-red-400 bg-red-50 focus:border-red-500 focus:ring-red-500/20 dark:bg-red-900/20 dark:border-red-500'
          : 'border-slate-300 bg-white focus:border-indigo-500 focus:ring-indigo-500/20 dark:border-slate-600 dark:bg-slate-700',
        disabled ? 'bg-slate-100 text-slate-500 cursor-not-allowed dark:bg-slate-800 dark:text-slate-500' : '',
      ]"
      @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />

    <p v-if="error" class="mt-1.5 text-xs text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-xs text-slate-500 dark:text-slate-400">{{ hint }}</p>
  </div>
</template>

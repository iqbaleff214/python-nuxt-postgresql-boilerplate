<script setup lang="ts">
interface Option {
  value: string | number
  label: string
  disabled?: boolean
}

interface Props {
  label?: string
  error?: string
  hint?: string
  modelValue?: string | number
  options: Option[]
  placeholder?: string
  disabled?: boolean
  required?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
  placeholder: 'Select an option',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputId = computed(() => props.id || `select-${Math.random().toString(36).slice(2, 7)}`)
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

    <div class="relative">
      <select
        :id="inputId"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :class="[
          'w-full appearance-none rounded-lg border px-3 py-2 pr-8 text-sm',
          'transition-all duration-150 focus:outline-none focus:ring-2',
          error
            ? 'border-red-400 bg-red-50 focus:border-red-500 focus:ring-red-500/20 text-slate-900 dark:bg-red-900/20 dark:border-red-500 dark:text-slate-100'
            : 'border-slate-300 bg-white focus:border-indigo-500 focus:ring-indigo-500/20 text-slate-900 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100',
          disabled ? 'bg-slate-100 text-slate-500 cursor-not-allowed dark:bg-slate-800 dark:text-slate-500' : '',
        ]"
        @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      >
        <option value="" disabled :selected="!modelValue">{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>

      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2 text-slate-400">
        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <p v-if="error" class="mt-1.5 text-xs text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-xs text-slate-500 dark:text-slate-400">{{ hint }}</p>
  </div>
</template>

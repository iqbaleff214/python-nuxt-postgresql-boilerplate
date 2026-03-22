<script setup lang="ts">
interface Props {
  modelValue?: string
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  complete: [value: string]
}>()

const LENGTH = 6
const digits = ref<string[]>(Array(LENGTH).fill(''))
const inputs = ref<HTMLInputElement[]>([])

watch(
  () => props.modelValue,
  (val) => {
    if (!val) {
      digits.value = Array(LENGTH).fill('')
    }
  }
)

function onInput(index: number, event: Event) {
  const input = event.target as HTMLInputElement
  const val = input.value.replace(/\D/g, '').slice(-1)
  digits.value[index] = val

  if (val && index < LENGTH - 1) {
    inputs.value[index + 1]?.focus()
  }

  emitValue()
}

function onKeydown(index: number, event: KeyboardEvent) {
  if (event.key === 'Backspace') {
    if (!digits.value[index] && index > 0) {
      digits.value[index - 1] = ''
      inputs.value[index - 1]?.focus()
    } else {
      digits.value[index] = ''
    }
    emitValue()
  } else if (event.key === 'ArrowLeft' && index > 0) {
    inputs.value[index - 1]?.focus()
  } else if (event.key === 'ArrowRight' && index < LENGTH - 1) {
    inputs.value[index + 1]?.focus()
  }
}

function onPaste(event: ClipboardEvent) {
  event.preventDefault()
  const text = event.clipboardData?.getData('text/plain') ?? ''
  const cleaned = text.replace(/\D/g, '').slice(0, LENGTH)
  if (!cleaned) return

  for (let i = 0; i < LENGTH; i++) {
    digits.value[i] = cleaned[i] ?? ''
  }

  const nextEmpty = digits.value.findIndex((d) => !d)
  const focusIdx = nextEmpty === -1 ? LENGTH - 1 : nextEmpty
  inputs.value[focusIdx]?.focus()
  emitValue()
}

function emitValue() {
  const value = digits.value.join('')
  emit('update:modelValue', value)
  if (value.length === LENGTH) {
    emit('complete', value)
  }
}

function focus() {
  inputs.value[0]?.focus()
}

defineExpose({ focus })
</script>

<template>
  <div>
    <div class="flex gap-2 justify-center">
      <input
        v-for="(_, index) in digits"
        :key="index"
        :ref="(el) => { if (el) inputs[index] = el as HTMLInputElement }"
        v-model="digits[index]"
        type="text"
        inputmode="numeric"
        maxlength="1"
        :disabled="disabled"
        :class="[
          'h-12 w-12 rounded-lg border text-center text-lg font-semibold',
          'transition-all duration-150 focus:outline-none focus:ring-2',
          error
            ? 'border-red-400 bg-red-50 focus:border-red-500 focus:ring-red-500/20 text-red-700'
            : digits[index]
            ? 'border-indigo-400 bg-indigo-50 focus:border-indigo-500 focus:ring-indigo-500/20 text-indigo-700'
            : 'border-slate-300 bg-white focus:border-indigo-500 focus:ring-indigo-500/20 text-slate-900',
          disabled ? 'cursor-not-allowed bg-slate-100 text-slate-400' : '',
        ]"
        @input="onInput(index, $event)"
        @keydown="onKeydown(index, $event)"
        @paste="onPaste($event)"
        @focus="($event.target as HTMLInputElement).select()"
      />
    </div>
    <p v-if="error" class="mt-2 text-center text-xs text-red-600">{{ error }}</p>
  </div>
</template>

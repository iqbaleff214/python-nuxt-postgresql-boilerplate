<script setup lang="ts">
import { onClickOutside } from '@vueuse/core'

const { locale, setLocale } = useI18n()
const isOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
onClickOutside(menuRef, () => { isOpen.value = false })

const locales = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'id', label: 'Bahasa Indonesia', flag: '🇮🇩' },
]

const current = computed(() => locales.find(l => l.code === locale.value) ?? locales[0])

function select(code: string) {
  setLocale(code as 'en' | 'id')
  isOpen.value = false
}
</script>

<template>
  <div ref="menuRef" class="relative">
    <button
      type="button"
      class="flex h-9 items-center gap-1.5 rounded-lg px-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200"
      :title="$t('language.switchTo')"
      @click="isOpen = !isOpen"
    >
      <span class="text-base leading-none">{{ current.flag }}</span>
      <span class="hidden text-xs font-medium sm:block">{{ current.code.toUpperCase() }}</span>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 top-11 z-50 w-44 rounded-xl border border-slate-200 bg-white shadow-lg py-1 dark:border-slate-700 dark:bg-slate-800"
      >
        <button
          v-for="loc in locales"
          :key="loc.code"
          type="button"
          :class="[
            'flex w-full items-center gap-2.5 px-3 py-2 text-sm transition-colors',
            locale === loc.code
              ? 'text-indigo-600 bg-indigo-50 dark:bg-indigo-900/30 dark:text-indigo-400'
              : 'text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-700',
          ]"
          @click="select(loc.code)"
        >
          <span class="text-base">{{ loc.flag }}</span>
          {{ loc.label }}
          <svg v-if="locale === loc.code" xmlns="http://www.w3.org/2000/svg" class="ml-auto h-4 w-4 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

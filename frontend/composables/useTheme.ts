export type ThemeMode = 'light' | 'dark' | 'system'

function applyTheme(m: ThemeMode) {
  if (typeof window === 'undefined') return
  const isDark =
    m === 'dark' ||
    (m === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.toggle('dark', isDark)
}

export function useTheme() {
  // useState is SSR-safe and shared across all callers within a request
  const mode = useState<ThemeMode>('theme-mode', () => 'system')

  // Sync from localStorage on client (after hydration)
  onMounted(() => {
    const stored = localStorage.getItem('theme-mode') as ThemeMode | null
    if (stored) mode.value = stored
    applyTheme(mode.value)

    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => { if (mode.value === 'system') applyTheme('system') }
    mq.addEventListener('change', handler)
    onUnmounted(() => mq.removeEventListener('change', handler))
  })

  function setMode(m: ThemeMode) {
    mode.value = m
    localStorage.setItem('theme-mode', m)
    applyTheme(m)
  }

  return { mode: readonly(mode), setMode }
}

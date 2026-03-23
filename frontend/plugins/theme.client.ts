// Applies the saved theme class to <html> before Vue hydrates — prevents flash
export default defineNuxtPlugin(() => {
  const stored = localStorage.getItem('theme-mode')
  const isDark =
    stored === 'dark' ||
    ((!stored || stored === 'system') &&
      window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.toggle('dark', isDark)
})

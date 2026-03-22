// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    'pinia-plugin-persistedstate/nuxt',
    '@vueuse/nuxt',
    '@nuxt/icon',
  ],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      wsBase: process.env.NUXT_PUBLIC_WS_BASE || 'ws://localhost:8000',
    },
  },

  typescript: {
    strict: true,
    typeCheck: false,
  },

  css: ['~/assets/css/main.css'],

  components: [
    {
      path: '~/components',
      pathPrefix: true,
    },
  ],

  imports: {
    dirs: ['stores', 'composables'],
  },

  app: {
    pageTransition: { name: 'page', mode: 'out-in' },
  },

  pinia: {
    storesDirs: ['./stores/**'],
  },

  nitro: {
    compressPublicAssets: true,
  },

  compatibilityDate: '2024-11-01',
})

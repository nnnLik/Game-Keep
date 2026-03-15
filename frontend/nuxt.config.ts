export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',

  devtools: {
    enabled: true,

    timeline: {
      enabled: true,
    },
  },

  modules: [
    '@pinia/nuxt',
    '@nuxt/ui',
    '@nuxt/icon',
    '@nuxt/fonts',
    '@nuxt/image',
    '@nuxtjs/color-mode',
  ],

  css: ['~/assets/css/main.css'],

  fonts: {
    families: [
      { name: 'Sora', provider: 'google', weights: [400, 500, 600, 700] },
      { name: 'Outfit', provider: 'google', weights: [600, 700] },
    ],
  },

  colorMode: {
    preference: 'dark',
    fallback: 'dark',
  },

  imports: {
    dirs: ['api'],
  },
  routeRules: {
    '/register/complete': { redirect: '/complete-registration' },
  },

  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:9999',
    },
  },

  vite: {
    optimizeDeps: {
      include: ['@vue/devtools-core', '@vue/devtools-kit'],
    },
  },
})
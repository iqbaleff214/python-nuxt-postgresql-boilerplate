<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <AppToastContainer />
</template>

<script setup lang="ts">
useHead({
  titleTemplate: (title) => title ? `${title} — 404NFID` : 'PythonNuxtStarterkit',
  meta: [
    { name: 'description', content: 'PythonNuxtStarterkit — Modern notification and user management platform' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
  ],
})
</script>

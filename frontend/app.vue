<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <AppToastContainer />
</template>

<script setup lang="ts">
useHead({
  titleTemplate: (title) => title ? `${title} — Loqato` : 'Loqato Channel Manager',
  meta: [
    { name: 'description', content: 'Loqato Channel Manager — Modern notification and user management platform' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
  ],
})
</script>

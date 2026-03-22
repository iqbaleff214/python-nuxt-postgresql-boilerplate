<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()

if (auth.isAuthenticated) {
  await navigateTo('/dashboard')
} else {
  await navigateTo('/login')
}
</script>

<template>
  <div />
</template>

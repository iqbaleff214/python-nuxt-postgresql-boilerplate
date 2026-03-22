<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const api = useApi()
const route = useRoute()

const status = ref<'loading' | 'success' | 'error'>('loading')
const errorMessage = ref('')

onMounted(async () => {
  const token = route.query.token as string

  if (!token) {
    status.value = 'error'
    errorMessage.value = 'Verification token is missing. Please check your email link.'
    return
  }

  const response = await api.post('/auth/verify-email', { token })

  if (response.success) {
    status.value = 'success'
  } else {
    status.value = 'error'
    errorMessage.value = response.message || 'Email verification failed. The link may be expired or invalid.'
  }
})
</script>

<template>
  <div class="text-center">
    <!-- Loading -->
    <div v-if="status === 'loading'" class="flex flex-col items-center gap-4">
      <AppSpinner size="lg" />
      <div>
        <h2 class="text-xl font-bold text-slate-900">Verifying your email</h2>
        <p class="mt-1 text-sm text-slate-500">Please wait a moment...</p>
      </div>
    </div>

    <!-- Success -->
    <div v-else-if="status === 'success'" class="flex flex-col items-center gap-4">
      <div class="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-9 w-9 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-slate-900">Email verified!</h2>
        <p class="mt-1 text-sm text-slate-500">Your email has been successfully verified. You can now sign in.</p>
      </div>
      <NuxtLink to="/login">
        <AppButton variant="primary" size="lg">
          Sign in to your account
        </AppButton>
      </NuxtLink>
    </div>

    <!-- Error -->
    <div v-else class="flex flex-col items-center gap-4">
      <div class="flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-9 w-9 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-slate-900">Verification failed</h2>
        <p class="mt-1 text-sm text-slate-500">{{ errorMessage }}</p>
      </div>
      <div class="flex gap-3">
        <NuxtLink to="/login">
          <AppButton variant="secondary">Back to login</AppButton>
        </NuxtLink>
        <NuxtLink to="/register">
          <AppButton variant="primary">Create new account</AppButton>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

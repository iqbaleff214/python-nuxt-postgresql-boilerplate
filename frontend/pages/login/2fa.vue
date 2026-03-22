<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'auth', middleware: 'mfa' })

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const otpValue = ref('')
const recoveryCode = ref('')
const useRecovery = ref(false)
const isSubmitting = ref(false)
const error = ref('')

async function handleSubmit() {
  const code = useRecovery.value ? recoveryCode.value.trim() : otpValue.value
  if (!code || (!useRecovery.value && code.length !== 6)) {
    error.value = useRecovery.value ? 'Please enter your recovery code' : 'Please enter the 6-digit code'
    return
  }

  error.value = ''
  isSubmitting.value = true

  try {
    await authStore.verify2fa(code, useRecovery.value)
    toast.success('Authentication successful!')
    router.push('/dashboard')
  } catch (err: any) {
    error.value = err.message || 'Verification failed. Please try again.'
    otpValue.value = ''
  } finally {
    isSubmitting.value = false
  }
}

function toggleRecovery() {
  useRecovery.value = !useRecovery.value
  error.value = ''
  otpValue.value = ''
  recoveryCode.value = ''
}

watch(otpValue, (val) => {
  if (val.length === 6) handleSubmit()
})
</script>

<template>
  <div>
    <div class="mb-6 text-center">
      <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-slate-900">Two-factor authentication</h2>
      <p class="mt-1 text-sm text-slate-500">
        {{ useRecovery ? 'Enter one of your recovery codes' : 'Enter the 6-digit code from your authenticator app' }}
      </p>
    </div>

    <AppAlert v-if="error" variant="error" class="mb-4" dismissible @dismiss="error = ''">
      {{ error }}
    </AppAlert>

    <form class="space-y-5" @submit.prevent="handleSubmit">
      <div v-if="!useRecovery">
        <AuthOtpInput
          v-model="otpValue"
          :disabled="isSubmitting"
          :error="error && otpValue.length > 0 ? '' : undefined"
        />
      </div>

      <div v-else>
        <AppInput
          v-model="recoveryCode"
          label="Recovery code"
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          :disabled="isSubmitting"
        />
      </div>

      <AppButton
        type="submit"
        variant="primary"
        size="lg"
        class="w-full"
        :loading="isSubmitting"
        :disabled="useRecovery ? !recoveryCode.trim() : otpValue.length !== 6"
      >
        Verify
      </AppButton>
    </form>

    <div class="mt-4 space-y-2 text-center">
      <button
        type="button"
        class="block w-full text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
        @click="toggleRecovery"
      >
        {{ useRecovery ? 'Use authenticator app instead' : 'Use a recovery code instead' }}
      </button>
      <NuxtLink
        to="/login"
        class="block text-sm text-slate-500 hover:text-slate-700 transition-colors"
      >
        &larr; Back to login
      </NuxtLink>
    </div>
  </div>
</template>

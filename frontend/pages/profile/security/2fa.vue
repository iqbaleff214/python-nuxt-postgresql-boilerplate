<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { TwoFASetupResponse, RecoveryCodesResponse } from '~/types'

definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const api = useApi()
const toast = useToast()
const router = useRouter()

const step = ref<1 | 2 | 3>(1)
const isLoading = ref(false)
const isVerifying = ref(false)

const setupData = ref<TwoFASetupResponse | null>(null)
const recoveryCodes = ref<string[]>([])
const otpCode = ref('')
const otpError = ref('')
const codesCopied = ref(false)

// Determine if this is regenerating recovery codes
const isRegenerate = computed(() => authStore.user?.is_2fa_enabled)

onMounted(async () => {
  if (!isRegenerate.value) {
    await initSetup()
  } else {
    // Just regenerate recovery codes
    step.value = 2
    await regenCodes()
  }
})

async function initSetup() {
  isLoading.value = true
  const response = await api.post<TwoFASetupResponse>('/profile/me/2fa/setup')
  if (response.success && response.data) {
    setupData.value = response.data
    recoveryCodes.value = response.data.recovery_codes ?? []
  } else {
    toast.error(response.message || 'Failed to initialize 2FA setup')
    router.push('/profile/security')
  }
  isLoading.value = false
}

async function regenCodes() {
  isLoading.value = true
  const response = await api.post<RecoveryCodesResponse>('/profile/me/2fa/recovery-codes')
  if (response.success && response.data) {
    recoveryCodes.value = response.data.recovery_codes
    step.value = 3
  } else {
    toast.error(response.message || 'Failed to regenerate codes')
    router.push('/profile/security')
  }
  isLoading.value = false
}

async function verifyAndEnable() {
  if (otpCode.value.length !== 6) {
    otpError.value = 'Please enter the 6-digit code'
    return
  }

  isVerifying.value = true
  otpError.value = ''

  const response = await api.post('/profile/me/2fa/verify', { totp_code: otpCode.value })

  if (response.success) {
    recoveryCodes.value = (response.data as any)?.recovery_codes ?? recoveryCodes.value
    await authStore.fetchMe()
    step.value = 3
  } else {
    otpError.value = response.message || 'Invalid code. Please try again.'
    otpCode.value = ''
  }
  isVerifying.value = false
}

async function copyAllCodes() {
  const text = recoveryCodes.value.join('\n')
  await navigator.clipboard.writeText(text)
  codesCopied.value = true
  toast.success('Recovery codes copied!')
  setTimeout(() => { codesCopied.value = false }, 3000)
}

function finish() {
  router.push('/profile/security')
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-slate-900">
        {{ isRegenerate ? 'Regenerate recovery codes' : 'Set up two-factor authentication' }}
      </h1>
      <p class="mt-0.5 text-sm text-slate-500">
        {{ isRegenerate ? 'Generate new recovery codes for your account' : 'Follow the steps to enable 2FA on your account' }}
      </p>
    </div>

    <!-- Step indicator (only for new setup) -->
    <div v-if="!isRegenerate" class="flex items-center gap-2">
      <template v-for="s in [1, 2, 3]" :key="s">
        <div :class="[
          'flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-all',
          step >= s ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-400',
        ]">
          <svg v-if="step > s" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
          </svg>
          <span v-else>{{ s }}</span>
        </div>
        <div v-if="s < 3" :class="['h-0.5 flex-1 transition-all', step > s ? 'bg-indigo-600' : 'bg-slate-200']" />
      </template>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex items-center justify-center py-16">
      <AppSpinner size="lg" />
    </div>

    <!-- Step 1: Scan QR code -->
    <AppCard v-else-if="step === 1 && !isRegenerate" title="Step 1: Scan QR code" subtitle="Use your authenticator app to scan this code">
      <div class="space-y-4">
        <div v-if="setupData" class="flex flex-col items-center gap-4">
          <div class="rounded-xl border-2 border-slate-200 p-3 bg-white">
            <img
              :src="setupData.qr_code_url"
              alt="QR Code"
              class="h-48 w-48"
            />
          </div>

          <div class="w-full rounded-lg bg-slate-50 border border-slate-200 p-3">
            <p class="mb-1 text-xs font-medium text-slate-500">Can't scan? Enter this code manually:</p>
            <p class="font-mono text-sm text-slate-800 break-all select-all">{{ setupData.secret }}</p>
          </div>

          <AppAlert variant="info" class="w-full">
            Open your authenticator app (Google Authenticator, Authy, etc.) and scan this QR code or enter the key manually.
          </AppAlert>
        </div>

        <div class="flex justify-end">
          <AppButton variant="primary" @click="step = 2">
            I've scanned it &rarr;
          </AppButton>
        </div>
      </div>
    </AppCard>

    <!-- Step 2: Enter TOTP code -->
    <AppCard v-else-if="step === 2 && !isRegenerate" title="Step 2: Verify your setup" subtitle="Enter the 6-digit code from your authenticator app">
      <div class="space-y-5">
        <AuthOtpInput
          v-model="otpCode"
          :disabled="isVerifying"
          :error="otpError"
        />

        <div class="flex items-center justify-between gap-3">
          <AppButton variant="ghost" @click="step = 1">
            &larr; Back
          </AppButton>
          <AppButton
            variant="primary"
            :loading="isVerifying"
            :disabled="otpCode.length !== 6"
            @click="verifyAndEnable"
          >
            Verify and enable
          </AppButton>
        </div>
      </div>
    </AppCard>

    <!-- Step 3: Recovery codes -->
    <AppCard v-else-if="step === 3" title="Save your recovery codes" subtitle="Store these codes somewhere safe">
      <div class="space-y-4">
        <AppAlert variant="warning">
          <strong>Important:</strong> Save these recovery codes now. You won't be able to see them again. If you lose access to your authenticator app, you can use these codes to sign in.
        </AppAlert>

        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div class="grid grid-cols-2 gap-2">
            <div
              v-for="code in recoveryCodes"
              :key="code"
              class="rounded-lg bg-white border border-slate-200 px-3 py-2 font-mono text-sm text-slate-700 text-center"
            >
              {{ code }}
            </div>
          </div>
        </div>

        <div class="flex flex-wrap gap-3">
          <AppButton variant="outline" @click="copyAllCodes">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            {{ codesCopied ? 'Copied!' : 'Copy all codes' }}
          </AppButton>
        </div>

        <div class="border-t border-slate-200 pt-4 flex justify-end">
          <AppButton variant="primary" @click="finish">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            I've saved my codes
          </AppButton>
        </div>
      </div>
    </AppCard>
  </div>
</template>

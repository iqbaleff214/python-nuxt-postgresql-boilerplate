<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const api = useApi()
const toast = useToast()
const router = useRouter()

const isRegenerate = computed(() => authStore.user?.is_2fa_enabled)

// ── Setup flow state ──────────────────────────────────────────────────────────
const step = ref<1 | 2 | 3>(1)
const isLoading = ref(false)
const isVerifying = ref(false)
const setupToken = ref('')
const qrCodeSrc = ref('')
const manualSecret = ref('')
const recoveryCodes = ref<string[]>([])
const otpCode = ref('')
const otpError = ref('')
const codesCopied = ref(false)

// ── Regen flow state ──────────────────────────────────────────────────────────
const regenPassword = ref('')
const regenOtp = ref('')
const regenOtpError = ref('')
const isRegening = ref(false)
const regenDone = ref(false)

onMounted(async () => {
  if (!isRegenerate.value) {
    await initSetup()
  }
})

async function initSetup() {
  isLoading.value = true
  const response = await api.get<{
    setup_token: string
    qr_code_base64: string
    secret: string
    otpauth_uri: string
  }>('/profile/2fa/setup')

  if (response.success && response.data) {
    setupToken.value = response.data.setup_token
    qrCodeSrc.value = response.data.qr_code_base64
    manualSecret.value = response.data.secret
  } else {
    toast.error(response.message || 'Failed to initialize 2FA setup')
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

  const response = await api.post<{ recovery_codes: string[] }>('/profile/2fa/enable', {
    setup_token: setupToken.value,
    code: otpCode.value,
  })

  if (response.success && response.data) {
    recoveryCodes.value = response.data.recovery_codes
    await authStore.fetchMe()
    step.value = 3
  } else {
    otpError.value = response.message || 'Invalid code. Please try again.'
    otpCode.value = ''
  }
  isVerifying.value = false
}

async function handleRegen() {
  if (!regenPassword.value) {
    toast.error('Please enter your password')
    return
  }
  if (regenOtp.value.length !== 6) {
    regenOtpError.value = 'Please enter the 6-digit code from your authenticator app'
    return
  }

  isRegening.value = true
  regenOtpError.value = ''

  const response = await api.post<{ recovery_codes: string[] }>('/profile/2fa/regenerate-codes', {
    password: regenPassword.value,
    code: regenOtp.value,
  })

  if (response.success && response.data) {
    recoveryCodes.value = response.data.recovery_codes
    regenDone.value = true
  } else {
    toast.error(response.message || 'Failed to regenerate codes')
  }
  isRegening.value = false
}

async function copyAllCodes() {
  await navigator.clipboard.writeText(recoveryCodes.value.join('\n'))
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
        {{ isRegenerate ? 'Generate new recovery codes — your old ones will be invalidated.' : 'Follow the steps to enable 2FA on your account.' }}
      </p>
    </div>

    <!-- ── SETUP FLOW ── -->
    <template v-if="!isRegenerate">
      <!-- Step indicator -->
      <div class="flex items-center gap-2">
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

      <div v-if="isLoading" class="flex items-center justify-center py-16">
        <AppSpinner size="lg" />
      </div>

      <!-- Step 1: Scan QR -->
      <AppCard v-else-if="step === 1" title="Step 1: Scan QR code" subtitle="Use your authenticator app to scan this code">
        <div class="space-y-4">
          <div class="flex flex-col items-center gap-4">
            <div class="rounded-xl border-2 border-slate-200 p-3 bg-white">
              <img :src="qrCodeSrc" alt="QR Code" class="h-48 w-48" />
            </div>
            <div class="w-full rounded-lg bg-slate-50 border border-slate-200 p-3">
              <p class="mb-1 text-xs font-medium text-slate-500">Can't scan? Enter this key manually:</p>
              <p class="font-mono text-sm text-slate-800 break-all select-all">{{ manualSecret }}</p>
            </div>
            <AppAlert variant="info" class="w-full">
              Open Google Authenticator, Authy, or any TOTP app and scan this QR code.
            </AppAlert>
          </div>
          <div class="flex justify-end">
            <AppButton variant="primary" @click="step = 2">
              I've scanned it &rarr;
            </AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Step 2: Verify TOTP -->
      <AppCard v-else-if="step === 2" title="Step 2: Verify your setup" subtitle="Enter the 6-digit code from your authenticator app">
        <div class="space-y-5">
          <OtpInput v-model="otpCode" :disabled="isVerifying" :error="otpError" />
          <div class="flex items-center justify-between gap-3">
            <AppButton variant="ghost" @click="step = 1">&larr; Back</AppButton>
            <AppButton
              variant="primary"
              :loading="isVerifying"
              :disabled="otpCode.length !== 6"
              @click="verifyAndEnable"
            >
              Verify &amp; enable
            </AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Step 3: Recovery codes -->
      <AppCard v-else-if="step === 3" title="Save your recovery codes" subtitle="Store these somewhere safe — you won't see them again">
        <div class="space-y-4">
          <AppAlert variant="warning">
            <strong>Important:</strong> If you lose your authenticator app, these codes are the only way back in.
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
              {{ codesCopied ? 'Copied!' : 'Copy all codes' }}
            </AppButton>
          </div>
          <div class="border-t border-slate-200 pt-4 flex justify-end">
            <AppButton variant="primary" @click="finish">
              I've saved my codes
            </AppButton>
          </div>
        </div>
      </AppCard>
    </template>

    <!-- ── REGEN FLOW ── -->
    <template v-else>
      <!-- Confirm identity -->
      <AppCard v-if="!regenDone" title="Confirm your identity" subtitle="Verify who you are before generating new codes">
        <div class="max-w-md space-y-4">
          <AppAlert variant="warning">
            Your existing recovery codes will be <strong>permanently invalidated</strong> and replaced with new ones.
          </AppAlert>

          <AppInput
            v-model="regenPassword"
            label="Current password"
            type="password"
            placeholder="Enter your password"
            required
          />

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700">
              Authenticator code <span class="text-red-500">*</span>
            </label>
            <OtpInput v-model="regenOtp" :error="regenOtpError" />
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <AppButton variant="secondary" @click="router.push('/profile/security')">Cancel</AppButton>
            <AppButton variant="primary" :loading="isRegening" @click="handleRegen">
              Generate new codes
            </AppButton>
          </div>
        </div>
      </AppCard>

      <!-- New codes -->
      <AppCard v-else title="Your new recovery codes" subtitle="Save these — your old codes no longer work">
        <div class="space-y-4">
          <AppAlert variant="warning">
            <strong>Save these now.</strong> You won't be able to see them again.
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
              {{ codesCopied ? 'Copied!' : 'Copy all codes' }}
            </AppButton>
          </div>
          <div class="border-t border-slate-200 pt-4 flex justify-end">
            <AppButton variant="primary" @click="finish">Done</AppButton>
          </div>
        </div>
      </AppCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const api = useApi()
const toast = useToast()
const router = useRouter()

// Change password
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const passwordErrors = reactive({ current_password: '', new_password: '', confirm_password: '' })
const isSavingPassword = ref(false)
const passwordSuccess = ref(false)

async function handleChangePassword() {
  // Reset errors
  Object.assign(passwordErrors, { current_password: '', new_password: '', confirm_password: '' })
  let valid = true

  if (!passwordForm.current_password) {
    passwordErrors.current_password = 'Current password is required'
    valid = false
  }
  if (passwordForm.new_password.length < 8) {
    passwordErrors.new_password = 'New password must be at least 8 characters'
    valid = false
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordErrors.confirm_password = 'Passwords do not match'
    valid = false
  }
  if (!valid) return

  isSavingPassword.value = true
  const response = await api.post('/auth/change-password', {
    current_password: passwordForm.current_password,
    new_password: passwordForm.new_password,
  })

  if (response.success) {
    passwordSuccess.value = true
    Object.assign(passwordForm, { current_password: '', new_password: '', confirm_password: '' })
    toast.success('Password changed successfully')
    setTimeout(() => { passwordSuccess.value = false }, 4000)
  } else {
    passwordErrors.current_password = response.message || 'Failed to change password'
  }
  isSavingPassword.value = false
}

// 2FA management
const isDisabling2fa = ref(false)
const showDisable2faModal = ref(false)
const disable2faPassword = ref('')
const disable2faOtp = ref('')
const disable2faOtpError = ref('')

async function handleDisable2fa() {
  if (!disable2faPassword.value) {
    toast.error('Please enter your password to confirm')
    return
  }
  if (disable2faOtp.value.length !== 6) {
    disable2faOtpError.value = 'Please enter the 6-digit code from your authenticator app'
    return
  }

  isDisabling2fa.value = true
  disable2faOtpError.value = ''
  const response = await api.post('/profile/2fa/disable', {
    password: disable2faPassword.value,
    code: disable2faOtp.value,
  })

  if (response.success) {
    await authStore.fetchMe()
    showDisable2faModal.value = false
    disable2faPassword.value = ''
    disable2faOtp.value = ''
    toast.success('Two-factor authentication disabled')
  } else {
    toast.error(response.message || 'Failed to disable 2FA')
  }
  isDisabling2fa.value = false
}

const newPasswordStrength = computed(() => {
  const p = passwordForm.new_password
  let score = 0
  if (p.length >= 8) score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const strengthLabel = computed(() => ['', 'Very weak', 'Weak', 'Fair', 'Good', 'Strong'][newPasswordStrength.value] ?? '')
const strengthColor = computed(() => ['', 'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-emerald-400', 'bg-emerald-600'][newPasswordStrength.value] ?? '')
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-900">Security</h1>
      <p class="mt-0.5 text-sm text-slate-500">Manage your password and two-factor authentication</p>
    </div>

    <!-- Change Password -->
    <AppCard title="Change password" subtitle="Keep your account secure with a strong password">
      <AppAlert v-if="passwordSuccess" variant="success" class="mb-4" dismissible>
        Password changed successfully!
      </AppAlert>

      <form class="max-w-md space-y-4" @submit.prevent="handleChangePassword">
        <AppInput
          v-model="passwordForm.current_password"
          label="Current password"
          type="password"
          placeholder="Enter current password"
          :error="passwordErrors.current_password"
          required
        />

        <div>
          <AppInput
            v-model="passwordForm.new_password"
            label="New password"
            type="password"
            placeholder="Min. 8 characters"
            :error="passwordErrors.new_password"
            required
          />
          <div v-if="passwordForm.new_password.length > 0" class="mt-2">
            <div class="flex gap-1">
              <div
                v-for="i in 5"
                :key="i"
                :class="['h-1 flex-1 rounded-full transition-all', i <= newPasswordStrength ? strengthColor : 'bg-slate-200']"
              />
            </div>
            <p :class="['mt-1 text-xs', newPasswordStrength >= 4 ? 'text-emerald-600' : 'text-red-500']">{{ strengthLabel }}</p>
          </div>
        </div>

        <AppInput
          v-model="passwordForm.confirm_password"
          label="Confirm new password"
          type="password"
          placeholder="Repeat password"
          :error="passwordErrors.confirm_password"
          required
        />

        <div class="flex justify-end">
          <AppButton type="submit" variant="primary" :loading="isSavingPassword">
            Update password
          </AppButton>
        </div>
      </form>
    </AppCard>

    <!-- Two-Factor Authentication -->
    <AppCard title="Two-factor authentication" subtitle="Add an extra layer of security to your account">
      <div v-if="authStore.user?.is_2fa_enabled" class="space-y-4">
        <div class="flex items-center gap-3 rounded-lg bg-emerald-50 border border-emerald-200 p-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <p class="font-semibold text-emerald-800">2FA is active</p>
              <AppBadge variant="success">Enabled</AppBadge>
            </div>
            <p class="mt-0.5 text-sm text-emerald-700">Your account is protected with two-factor authentication.</p>
          </div>
        </div>

        <div class="flex flex-wrap gap-3">
          <NuxtLink to="/profile/security/2fa">
            <AppButton variant="outline">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Regenerate recovery codes
            </AppButton>
          </NuxtLink>

          <AppButton variant="danger" @click="showDisable2faModal = true">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
            Disable 2FA
          </AppButton>
        </div>
      </div>

      <div v-else class="space-y-4">
        <div class="flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 p-4 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <p class="font-semibold text-amber-800">2FA is not enabled</p>
            <p class="mt-0.5 text-sm text-amber-700">
              Two-factor authentication adds an extra layer of security. Even if your password is compromised, your account stays safe.
            </p>
          </div>
        </div>

        <NuxtLink to="/profile/security/2fa">
          <AppButton variant="primary">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Enable two-factor authentication
          </AppButton>
        </NuxtLink>
      </div>
    </AppCard>

    <!-- Disable 2FA modal -->
    <AppModal v-model="showDisable2faModal" title="Disable two-factor authentication" size="sm">
      <div class="space-y-4">
        <AppAlert variant="warning">
          Disabling 2FA will make your account less secure. You can re-enable it at any time.
        </AppAlert>
        <AppInput
          v-model="disable2faPassword"
          label="Confirm with your password"
          type="password"
          placeholder="Enter your current password"
        />

        <div>
          <label class="mb-1.5 block text-sm font-medium text-slate-700">
            Authenticator code <span class="text-red-500">*</span>
          </label>
          <OtpInput v-model="disable2faOtp" :error="disable2faOtpError" />
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3 justify-end">
          <AppButton variant="secondary" @click="showDisable2faModal = false; disable2faOtpError = ''">Cancel</AppButton>
          <AppButton variant="danger" :loading="isDisabling2fa" @click="handleDisable2fa">
            Disable 2FA
          </AppButton>
        </div>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

definePageMeta({ layout: 'auth' })

const api = useApi()
const route = useRoute()
const router = useRouter()

const token = route.query.token as string

const schema = toTypedSchema(
  z.object({
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string(),
  }).refine((d) => d.password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })
)

const { handleSubmit, errors, isSubmitting } = useForm({ validationSchema: schema })
const { value: password } = useField<string>('password')
const { value: confirmPassword } = useField<string>('confirm_password')

const apiError = ref('')
const success = ref(false)

const passwordStrength = computed(() => {
  const p = password.value ?? ''
  let score = 0
  if (p.length >= 8) score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const strengthLabel = computed(() => {
  return ['', 'Very weak', 'Weak', 'Fair', 'Good', 'Strong'][passwordStrength.value] ?? ''
})

const strengthColor = computed(() => {
  return ['', 'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-emerald-400', 'bg-emerald-600'][passwordStrength.value] ?? ''
})

const onSubmit = handleSubmit(async (values) => {
  if (!token) {
    apiError.value = 'Reset token is missing. Please use the link from your email.'
    return
  }

  apiError.value = ''
  const response = await api.post('/auth/reset-password', {
    token,
    new_password: values.password,
  })

  if (response.success) {
    success.value = true
    setTimeout(() => router.push('/login'), 3000)
  } else {
    apiError.value = response.message || 'Failed to reset password. The link may be expired.'
  }
})
</script>

<template>
  <div>
    <!-- Success -->
    <div v-if="success" class="text-center">
      <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-slate-900">Password reset!</h2>
      <p class="mt-2 text-sm text-slate-500">Your password has been reset successfully. Redirecting you to login...</p>
      <NuxtLink to="/login">
        <AppButton variant="primary" class="mt-4">Go to login</AppButton>
      </NuxtLink>
    </div>

    <!-- Missing token -->
    <div v-else-if="!token" class="text-center">
      <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h2 class="text-xl font-bold text-slate-900">Invalid reset link</h2>
      <p class="mt-2 text-sm text-slate-500">This reset link is invalid or expired. Please request a new one.</p>
      <NuxtLink to="/forgot-password">
        <AppButton variant="primary" class="mt-4">Request new link</AppButton>
      </NuxtLink>
    </div>

    <!-- Form -->
    <div v-else>
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-slate-900">Reset password</h2>
        <p class="mt-1 text-sm text-slate-500">Enter your new password below.</p>
      </div>

      <AppAlert v-if="apiError" variant="error" class="mb-4" dismissible>
        {{ apiError }}
      </AppAlert>

      <form class="space-y-4" @submit="onSubmit">
        <div>
          <AppInput
            v-model="password"
            label="New password"
            type="password"
            placeholder="Min. 8 characters"
            :error="errors.password"
            required
            autocomplete="new-password"
          />
          <div v-if="(password ?? '').length > 0" class="mt-2">
            <div class="flex gap-1">
              <div
                v-for="i in 5"
                :key="i"
                :class="['h-1 flex-1 rounded-full transition-all duration-300', i <= passwordStrength ? strengthColor : 'bg-slate-200']"
              />
            </div>
            <p :class="['mt-1 text-xs', passwordStrength >= 4 ? 'text-emerald-600' : passwordStrength >= 3 ? 'text-amber-600' : 'text-red-500']">
              {{ strengthLabel }}
            </p>
          </div>
        </div>

        <AppInput
          v-model="confirmPassword"
          label="Confirm new password"
          type="password"
          placeholder="Repeat password"
          :error="errors.confirm_password"
          required
          autocomplete="new-password"
        />

        <AppButton type="submit" variant="primary" size="lg" class="w-full" :loading="isSubmitting">
          Reset password
        </AppButton>
      </form>
    </div>
  </div>
</template>

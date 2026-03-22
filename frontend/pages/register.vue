<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

definePageMeta({ layout: 'auth', middleware: 'guest' })

const api = useApi()
const toast = useToast()

const schema = toTypedSchema(
  z.object({
    first_name: z.string().min(1, 'First name is required').max(64),
    last_name: z.string().min(1, 'Last name is required').max(64),
    email: z.string().email('Please enter a valid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string(),
  }).refine((data) => data.password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })
)

const { handleSubmit, errors, isSubmitting } = useForm({ validationSchema: schema })
const { value: firstName } = useField<string>('first_name')
const { value: lastName } = useField<string>('last_name')
const { value: email } = useField<string>('email')
const { value: password } = useField<string>('password')
const { value: confirmPassword } = useField<string>('confirm_password')

const apiError = ref('')
const registered = ref(false)

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
  const labels = ['', 'Very weak', 'Weak', 'Fair', 'Good', 'Strong']
  return labels[passwordStrength.value] ?? ''
})

const strengthColor = computed(() => {
  const colors = ['', 'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-emerald-400', 'bg-emerald-600']
  return colors[passwordStrength.value] ?? ''
})

const onSubmit = handleSubmit(async (values) => {
  apiError.value = ''
  const response = await api.post('/auth/register', {
    first_name: values.first_name,
    last_name: values.last_name,
    email: values.email,
    password: values.password,
  })

  if (response.success) {
    registered.value = true
  } else {
    apiError.value = response.message || 'Registration failed. Please try again.'
  }
})
</script>

<template>
  <div>
    <!-- Success state -->
    <div v-if="registered" class="text-center">
      <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-slate-900">Check your email</h2>
      <p class="mt-2 text-sm text-slate-500">
        We've sent a verification link to your email address. Please check your inbox and click the link to activate your account.
      </p>
      <NuxtLink to="/login" class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to login
      </NuxtLink>
    </div>

    <!-- Registration form -->
    <div v-else>
      <div class="mb-6 text-center">
        <h2 class="text-2xl font-bold text-slate-900">Create account</h2>
        <p class="mt-1 text-sm text-slate-500">Get started with Loqato today</p>
      </div>

      <AppAlert v-if="apiError" variant="error" class="mb-4" dismissible @dismiss="apiError = ''">
        {{ apiError }}
      </AppAlert>

      <form class="space-y-4" @submit="onSubmit">
        <div class="grid grid-cols-2 gap-3">
          <AppInput
            v-model="firstName"
            label="First name"
            placeholder="John"
            :error="errors.first_name"
            required
          />
          <AppInput
            v-model="lastName"
            label="Last name"
            placeholder="Doe"
            :error="errors.last_name"
            required
          />
        </div>

        <AppInput
          v-model="email"
          label="Email address"
          type="email"
          placeholder="you@example.com"
          :error="errors.email"
          required
          autocomplete="email"
        />

        <div>
          <AppInput
            v-model="password"
            label="Password"
            type="password"
            placeholder="Min. 8 characters"
            :error="errors.password"
            required
            autocomplete="new-password"
          />
          <!-- Strength bar -->
          <div v-if="(password ?? '').length > 0" class="mt-2">
            <div class="flex gap-1">
              <div
                v-for="i in 5"
                :key="i"
                :class="[
                  'h-1 flex-1 rounded-full transition-all duration-300',
                  i <= passwordStrength ? strengthColor : 'bg-slate-200',
                ]"
              />
            </div>
            <p :class="['mt-1 text-xs', passwordStrength >= 4 ? 'text-emerald-600' : passwordStrength >= 3 ? 'text-amber-600' : 'text-red-500']">
              {{ strengthLabel }}
            </p>
          </div>
        </div>

        <AppInput
          v-model="confirmPassword"
          label="Confirm password"
          type="password"
          placeholder="Repeat password"
          :error="errors.confirm_password"
          required
          autocomplete="new-password"
        />

        <AppButton
          type="submit"
          variant="primary"
          size="lg"
          class="w-full"
          :loading="isSubmitting"
        >
          Create account
        </AppButton>
      </form>

      <p class="mt-6 text-center text-sm text-slate-500">
        Already have an account?
        <NuxtLink to="/login" class="font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
          Sign in
        </NuxtLink>
      </p>
    </div>
  </div>
</template>

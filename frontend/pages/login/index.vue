<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'auth', middleware: 'guest' })

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const schema = toTypedSchema(
  z.object({
    email: z.string().email('Please enter a valid email address'),
    password: z.string().min(1, 'Password is required'),
  })
)

const { handleSubmit, errors, isSubmitting } = useForm({ validationSchema: schema })
const { value: email } = useField<string>('email')
const { value: password } = useField<string>('password')

const apiError = ref('')

const onSubmit = handleSubmit(async (values) => {
  apiError.value = ''
  try {
    const result = await authStore.login(values.email, values.password)
    if (result.mfaRequired) {
      router.push('/login/2fa')
    } else {
      toast.success('Welcome back!')
      router.push('/dashboard')
    }
  } catch (err: any) {
    apiError.value = err.message || 'Login failed. Please try again.'
  }
})
</script>

<template>
  <div>
    <div class="mb-6 text-center">
      <h2 class="text-2xl font-bold text-slate-900">Sign in</h2>
      <p class="mt-1 text-sm text-slate-500">Welcome back! Please enter your credentials.</p>
    </div>

    <AppAlert v-if="apiError" variant="error" class="mb-4" dismissible @dismiss="apiError = ''">
      {{ apiError }}
    </AppAlert>

    <form class="space-y-4" @submit="onSubmit">
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
          placeholder="••••••••"
          :error="errors.password"
          required
          autocomplete="current-password"
        />
        <div class="mt-1 text-right">
          <NuxtLink to="/forgot-password" class="text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
            Forgot password?
          </NuxtLink>
        </div>
      </div>

      <AppButton
        type="submit"
        variant="primary"
        size="lg"
        class="w-full"
        :loading="isSubmitting"
      >
        Sign in
      </AppButton>
    </form>

    <p class="mt-6 text-center text-sm text-slate-500">
      Don't have an account?
      <NuxtLink to="/register" class="font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
        Create account
      </NuxtLink>
    </p>
  </div>
</template>

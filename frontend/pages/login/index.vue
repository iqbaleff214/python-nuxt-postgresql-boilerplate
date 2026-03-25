<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'auth', middleware: 'guest' })

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()
const { t } = useI18n()

const schema = computed(() => toTypedSchema(
  z.object({
    email: z.string().email(t('validation.emailInvalid')),
    password: z.string().min(1, t('validation.passwordRequired')),
  })
))

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
      toast.success(t('auth.login.welcomeBack'))
      router.push('/dashboard')
    }
  } catch (err: any) {
    apiError.value = err.message || t('auth.login.failed')
  }
})
</script>

<template>
  <div>
    <div class="mb-6 text-center">
      <h2 class="text-2xl font-bold text-slate-900">{{ $t('auth.login.title') }}</h2>
      <p class="mt-1 text-sm text-slate-500">{{ $t('auth.login.subtitle') }}</p>
    </div>

    <AppAlert v-if="apiError" variant="error" class="mb-4" dismissible @dismiss="apiError = ''">
      {{ apiError }}
    </AppAlert>

    <form class="space-y-4" @submit="onSubmit">
      <AppInput
        v-model="email"
        :label="$t('auth.login.email')"
        type="email"
        placeholder="you@example.com"
        :error="errors.email"
        required
        autocomplete="email"
      />

      <div>
        <AppInput
          v-model="password"
          :label="$t('auth.login.password')"
          type="password"
          placeholder="••••••••"
          :error="errors.password"
          required
          autocomplete="current-password"
        />
        <div class="mt-1 text-right">
          <NuxtLink to="/forgot-password" class="text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
            {{ $t('auth.login.forgotPassword') }}
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
        {{ $t('auth.login.submit') }}
      </AppButton>
    </form>

    <p class="mt-6 text-center text-sm text-slate-500">
      {{ $t('auth.login.noAccount') }}
      <NuxtLink to="/register" class="font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
        {{ $t('auth.login.createAccount') }}
      </NuxtLink>
    </p>
  </div>
</template>

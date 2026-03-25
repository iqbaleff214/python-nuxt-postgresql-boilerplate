<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

definePageMeta({ layout: 'auth', middleware: 'guest' })

const api = useApi()
const { t } = useI18n()

const schema = computed(() => toTypedSchema(
  z.object({
    email: z.string().email(t('validation.emailInvalid')),
  })
))

const { handleSubmit, errors, isSubmitting } = useForm({ validationSchema: schema })
const { value: email } = useField<string>('email')

const submitted = ref(false)
const apiError = ref('')

const onSubmit = handleSubmit(async (values) => {
  apiError.value = ''
  const response = await api.post('/auth/forgot-password', { email: values.email })

  if (response.success) {
    submitted.value = true
  } else {
    // Still show success to prevent email enumeration
    submitted.value = true
  }
})
</script>

<template>
  <div>
    <div v-if="submitted" class="text-center">
      <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <h2 class="text-2xl font-bold text-slate-900">{{ $t('auth.forgotPassword.checkEmail') }}</h2>
      <p class="mt-2 text-sm text-slate-500">{{ $t('auth.forgotPassword.emailSent') }}</p>
      <NuxtLink to="/login" class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        {{ $t('auth.forgotPassword.backToLogin') }}
      </NuxtLink>
    </div>

    <div v-else>
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-slate-900">{{ $t('auth.forgotPassword.title') }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ $t('auth.forgotPassword.subtitle') }}</p>
      </div>

      <AppAlert v-if="apiError" variant="error" class="mb-4" dismissible>
        {{ apiError }}
      </AppAlert>

      <form class="space-y-4" @submit="onSubmit">
        <AppInput
          v-model="email"
          :label="$t('auth.forgotPassword.email')"
          type="email"
          placeholder="you@example.com"
          :error="errors.email"
          required
        />

        <AppButton
          type="submit"
          variant="primary"
          size="lg"
          class="w-full"
          :loading="isSubmitting"
        >
          {{ $t('auth.forgotPassword.submit') }}
        </AppButton>
      </form>

      <p class="mt-4 text-center">
        <NuxtLink to="/login" class="text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
          &larr; {{ $t('auth.forgotPassword.backToLogin') }}
        </NuxtLink>
      </p>
    </div>
  </div>
</template>

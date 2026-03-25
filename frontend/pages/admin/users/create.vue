<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

definePageMeta({ middleware: 'superadmin', layout: 'admin' })

const api = useApi()
const toast = useToast()
const router = useRouter()
const { t } = useI18n()

const schema = computed(() => toTypedSchema(
  z.object({
    email: z.string().email(t('validation.emailInvalid')),
    first_name: z.string().min(1, t('validation.firstNameRequired')),
    last_name: z.string().min(1, t('validation.lastNameRequired')),
    role: z.enum(['user', 'superadmin']),
    password: z.string().min(8, t('validation.passwordMin')),
  })
))

const { handleSubmit, errors, isSubmitting } = useForm({
  validationSchema: schema,
  initialValues: { role: 'user' as const },
})

const { value: email } = useField<string>('email')
const { value: firstName } = useField<string>('first_name')
const { value: lastName } = useField<string>('last_name')
const { value: role } = useField<'user' | 'superadmin'>('role')
const { value: password } = useField<string>('password')

const apiError = ref('')

const roleOptions = computed(() => [
  { value: 'user', label: t('admin.users.user') },
  { value: 'superadmin', label: t('admin.users.superadmin') },
])

const onSubmit = handleSubmit(async (values) => {
  apiError.value = ''
  const response = await api.post('/admin/users', values)

  if (response.success) {
    toast.success(t('admin.createUser.success'))
    router.push('/admin/users')
  } else {
    apiError.value = response.message || t('admin.createUser.failed')
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <NuxtLink to="/admin/users">
        <AppButton variant="ghost" size="sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          {{ $t('common.back') }}
        </AppButton>
      </NuxtLink>
      <div>
        <h1 class="text-2xl font-bold text-slate-900">{{ $t('admin.createUser.title') }}</h1>
        <p class="mt-0.5 text-sm text-slate-500">{{ $t('admin.createUser.subtitle') }}</p>
      </div>
    </div>

    <div class="max-w-2xl">
      <AppCard :title="$t('admin.createUser.userInfo')">
        <AppAlert v-if="apiError" variant="error" class="mb-4" dismissible @dismiss="apiError = ''">
          {{ apiError }}
        </AppAlert>

        <form class="space-y-4" @submit="onSubmit">
          <div class="grid grid-cols-2 gap-4">
            <AppInput
              v-model="firstName"
              :label="$t('admin.createUser.firstName')"
              placeholder="John"
              :error="errors.first_name"
              required
            />
            <AppInput
              v-model="lastName"
              :label="$t('admin.createUser.lastName')"
              placeholder="Doe"
              :error="errors.last_name"
              required
            />
          </div>

          <AppInput
            v-model="email"
            :label="$t('admin.createUser.email')"
            type="email"
            placeholder="user@example.com"
            :error="errors.email"
            required
          />

          <AppSelect
            v-model="role"
            :label="$t('admin.createUser.role')"
            :options="roleOptions"
            :error="errors.role"
            required
          />

          <AppInput
            v-model="password"
            :label="$t('admin.createUser.tempPassword')"
            type="password"
            :placeholder="$t('auth.register.passwordPlaceholder')"
            :error="errors.password"
            :hint="$t('admin.createUser.tempPasswordHint')"
            required
          />

          <div class="flex gap-3 justify-end border-t border-slate-100 pt-4">
            <NuxtLink to="/admin/users">
              <AppButton variant="secondary">{{ $t('common.cancel') }}</AppButton>
            </NuxtLink>
            <AppButton type="submit" variant="primary" :loading="isSubmitting">
              {{ $t('admin.createUser.submit') }}
            </AppButton>
          </div>
        </form>
      </AppCard>
    </div>
  </div>
</template>

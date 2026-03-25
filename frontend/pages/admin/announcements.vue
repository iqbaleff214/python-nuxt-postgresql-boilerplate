<script setup lang="ts">
definePageMeta({ middleware: 'superadmin', layout: 'admin' })

const api = useApi()
const toast = useToast()
const { t } = useI18n()

const form = reactive({
  title: '',
  message: '',
  target_role: '' as '' | 'user' | 'superadmin',
})

const isSending = ref(false)
const apiError = ref('')
const showConfirmModal = ref(false)
const sent = ref(false)

const targetOptions = computed(() => [
  { value: '', label: t('admin.announcements.allUsers') },
  { value: 'user', label: t('admin.announcements.regularOnly') },
  { value: 'superadmin', label: t('admin.announcements.adminsOnly') },
])

function validateForm() {
  if (!form.title.trim()) return t('admin.announcements.titleRequired')
  if (!form.message.trim()) return t('admin.announcements.messageRequired')
  return null
}

function handleSend() {
  const err = validateForm()
  if (err) {
    apiError.value = err
    return
  }
  apiError.value = ''
  showConfirmModal.value = true
}

async function confirmSend() {
  isSending.value = true
  showConfirmModal.value = false

  const body: Record<string, any> = {
    title: form.title,
    message: form.message,
  }
  if (form.target_role) body.target_role = form.target_role

  const response = await api.post('/admin/announcements', body)

  if (response.success) {
    sent.value = true
    toast.success(t('admin.announcements.success'))
  } else {
    apiError.value = response.message || t('admin.announcements.failed')
  }
  isSending.value = false
}

function resetForm() {
  Object.assign(form, { title: '', message: '', target_role: '' })
  sent.value = false
  apiError.value = ''
}

const confirmTarget = computed(() => {
  if (form.target_role === 'user') return t('admin.announcements.regularTarget')
  if (form.target_role === 'superadmin') return t('admin.announcements.adminTarget')
  return t('admin.announcements.allUsersTarget')
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-900">{{ $t('admin.announcements.title') }}</h1>
      <p class="mt-0.5 text-sm text-slate-500">{{ $t('admin.announcements.subtitle') }}</p>
    </div>

    <!-- Success state -->
    <AppCard v-if="sent">
      <div class="flex flex-col items-center gap-4 py-8">
        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="text-center">
          <h3 class="text-lg font-bold text-slate-900">{{ $t('admin.announcements.sentTitle') }}</h3>
          <p class="mt-1 text-sm text-slate-500">{{ $t('admin.announcements.sentMsg') }}</p>
        </div>
        <AppButton variant="primary" @click="resetForm">{{ $t('admin.announcements.sendAnother') }}</AppButton>
      </div>
    </AppCard>

    <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Form -->
      <AppCard :title="$t('admin.announcements.compose')">
        <AppAlert v-if="apiError" variant="error" class="mb-4" dismissible @dismiss="apiError = ''">
          {{ apiError }}
        </AppAlert>

        <form class="space-y-4" @submit.prevent="handleSend">
          <AppInput
            v-model="form.title"
            :label="$t('admin.announcements.announcementTitle')"
            :placeholder="$t('admin.announcements.titlePlaceholder')"
            required
          />

          <AppSelect
            v-model="form.target_role"
            :label="$t('admin.announcements.sendTo')"
            :options="targetOptions"
          />

          <AppTextarea
            v-model="form.message"
            :label="$t('admin.announcements.message')"
            :placeholder="$t('admin.announcements.messagePlaceholder')"
            :rows="6"
            required
          />

          <div class="flex justify-end border-t border-slate-100 pt-4">
            <AppButton
              type="submit"
              variant="primary"
              :loading="isSending"
              :disabled="!form.title.trim() || !form.message.trim()"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              {{ $t('admin.announcements.send') }}
            </AppButton>
          </div>
        </form>
      </AppCard>

      <!-- Preview -->
      <div class="space-y-4">
        <AppCard :title="$t('admin.announcements.preview')">
          <div v-if="form.title || form.message" class="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
            <div class="flex items-start gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 flex-shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-indigo-900">{{ form.title || $t('admin.announcements.announcementTitle') + '...' }}</p>
                <p class="mt-1 text-sm text-indigo-700 whitespace-pre-wrap">{{ form.message || $t('admin.announcements.messagePlaceholder') }}</p>
                <div class="mt-2 flex items-center gap-2">
                  <AppBadge variant="indigo" size="sm">{{ $t('admin.announcements.announcement') }}</AppBadge>
                  <span class="text-xs text-indigo-500">{{ $t('admin.announcements.justNow') }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center gap-2 py-8 text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <p class="text-sm">{{ $t('admin.announcements.previewEmpty') }}</p>
          </div>
        </AppCard>

        <!-- Info card -->
        <AppCard padding="md">
          <div class="flex gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-sky-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="text-sm text-slate-600">
              <p class="font-semibold text-slate-800">{{ $t('admin.announcements.howItWorks') }}</p>
              <ul class="mt-1 space-y-1 text-xs text-slate-500">
                <li>• {{ $t('admin.announcements.info1') }}</li>
                <li>• {{ $t('admin.announcements.info2') }}</li>
                <li>• {{ $t('admin.announcements.info3') }}</li>
                <li>• {{ $t('admin.announcements.info4') }}</li>
              </ul>
            </div>
          </div>
        </AppCard>
      </div>
    </div>

    <!-- Confirm modal -->
    <AppModal v-model="showConfirmModal" :title="$t('admin.announcements.confirmTitle')" size="sm">
      <div class="space-y-3">
        <p class="text-sm text-slate-600">
          {{ $t('admin.announcements.confirmMsg', { target: confirmTarget }) }}
        </p>
        <div class="rounded-lg bg-slate-50 p-3 text-sm">
          <p class="font-semibold text-slate-900">{{ form.title }}</p>
          <p class="mt-1 text-slate-600 text-xs">{{ form.message }}</p>
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3 justify-end">
          <AppButton variant="secondary" @click="showConfirmModal = false">{{ $t('common.cancel') }}</AppButton>
          <AppButton variant="primary" :loading="isSending" @click="confirmSend">
            {{ $t('admin.announcements.sendNow') }}
          </AppButton>
        </div>
      </template>
    </AppModal>
  </div>
</template>

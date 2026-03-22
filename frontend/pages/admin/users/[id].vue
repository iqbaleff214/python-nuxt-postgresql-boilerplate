<script setup lang="ts">
import type { User } from '~/types'

definePageMeta({ middleware: 'superadmin', layout: 'admin' })

const api = useApi()
const toast = useToast()
const route = useRoute()
const router = useRouter()

const userId = route.params.id as string
const user = ref<User | null>(null)
const isLoading = ref(true)
const activeTab = ref<'details' | 'status'>('details')

// Form
const form = reactive({
  first_name: '',
  last_name: '',
  display_name: '',
  bio: '',
  role: '' as 'user' | 'superadmin',
})
const isSaving = ref(false)
const formError = ref('')

// Status
const showStatusModal = ref(false)
const pendingStatus = ref<'active' | 'inactive' | 'banned' | null>(null)
const isChangingStatus = ref(false)
const showDeleteModal = ref(false)
const isDeleting = ref(false)

async function fetchUser() {
  isLoading.value = true
  const response = await api.get<User>(`/admin/users/${userId}`)

  if (response.success && response.data) {
    user.value = response.data
    Object.assign(form, {
      first_name: response.data.first_name,
      last_name: response.data.last_name,
      display_name: response.data.display_name ?? '',
      bio: response.data.bio ?? '',
      role: response.data.role,
    })
  } else {
    toast.error('User not found')
    router.push('/admin/users')
  }
  isLoading.value = false
}

async function handleSave() {
  isSaving.value = true
  formError.value = ''

  const response = await api.patch(`/admin/users/${userId}`, form)

  if (response.success) {
    await fetchUser()
    toast.success('User updated successfully')
  } else {
    formError.value = response.message || 'Failed to update user'
  }
  isSaving.value = false
}

function confirmStatusChange(status: 'active' | 'inactive' | 'banned') {
  pendingStatus.value = status
  showStatusModal.value = true
}

async function handleStatusChange() {
  if (!pendingStatus.value) return
  isChangingStatus.value = true

  const response = await api.patch(`/admin/users/${userId}/status`, { status: pendingStatus.value })

  if (response.success) {
    await fetchUser()
    showStatusModal.value = false
    toast.success(`User ${pendingStatus.value} successfully`)
  } else {
    toast.error(response.message || 'Failed to change status')
  }
  isChangingStatus.value = false
}

async function handleDelete() {
  isDeleting.value = true
  const response = await api.delete(`/admin/users/${userId}`)

  if (response.success) {
    toast.success('User deleted')
    router.push('/admin/users')
  } else {
    toast.error(response.message || 'Failed to delete user')
    isDeleting.value = false
  }
}

const statusActions = computed(() => {
  if (!user.value) return []
  const all = [
    { status: 'active' as const, label: 'Activate', variant: 'primary' as const, icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
    { status: 'inactive' as const, label: 'Deactivate', variant: 'secondary' as const, icon: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' },
    { status: 'banned' as const, label: 'Ban', variant: 'danger' as const, icon: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' },
  ]
  return all.filter((a) => a.status !== user.value?.status)
})

onMounted(fetchUser)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start gap-3">
      <NuxtLink to="/admin/users">
        <AppButton variant="ghost" size="sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Users
        </AppButton>
      </NuxtLink>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex items-center justify-center py-16">
      <AppSpinner size="lg" />
    </div>

    <template v-else-if="user">
      <!-- User header card -->
      <AppCard padding="md">
        <div class="flex flex-wrap items-center gap-4">
          <AppAvatar :src="user.avatar_url" :name="`${user.first_name} ${user.last_name}`" size="lg" />
          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-bold text-slate-900">{{ user.first_name }} {{ user.last_name }}</h2>
            <p class="text-sm text-slate-500">{{ user.email }}</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <AppBadge :variant="user.role === 'superadmin' ? 'indigo' : 'default'">{{ user.role }}</AppBadge>
              <AppBadge :variant="user.status === 'active' ? 'success' : user.status === 'banned' ? 'danger' : 'warning'">
                {{ user.status }}
              </AppBadge>
              <AppBadge v-if="user.is_email_verified" variant="success">Email verified</AppBadge>
              <AppBadge v-else variant="warning">Email unverified</AppBadge>
              <AppBadge v-if="user.is_2fa_enabled" variant="info">2FA enabled</AppBadge>
            </div>
          </div>
          <div class="text-right text-sm text-slate-500">
            <p>Joined {{ new Date(user.created_at).toLocaleDateString() }}</p>
            <p>Last login: {{ user.last_login_at ? new Date(user.last_login_at).toLocaleString() : 'Never' }}</p>
          </div>
        </div>
      </AppCard>

      <!-- Tabs -->
      <div class="flex gap-1 rounded-xl bg-slate-100 p-1 w-fit">
        <button
          v-for="tab in [{ value: 'details', label: 'Details' }, { value: 'status', label: 'Status Management' }]"
          :key="tab.value"
          type="button"
          :class="[
            'rounded-lg px-4 py-1.5 text-sm font-medium transition-all',
            activeTab === tab.value ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700',
          ]"
          @click="activeTab = tab.value as 'details' | 'status'"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Details tab -->
      <div v-if="activeTab === 'details'">
        <AppCard title="Edit user details" class="max-w-2xl">
          <AppAlert v-if="formError" variant="error" class="mb-4" dismissible @dismiss="formError = ''">
            {{ formError }}
          </AppAlert>

          <form class="space-y-4" @submit.prevent="handleSave">
            <div class="grid grid-cols-2 gap-4">
              <AppInput v-model="form.first_name" label="First name" required />
              <AppInput v-model="form.last_name" label="Last name" required />
            </div>
            <AppInput v-model="form.display_name" label="Display name" />
            <AppSelect v-model="form.role" label="Role" :options="[{ value: 'user', label: 'User' }, { value: 'superadmin', label: 'Superadmin' }]" />
            <AppTextarea v-model="form.bio" label="Bio" :rows="3" />

            <div class="flex justify-end border-t border-slate-100 pt-4">
              <AppButton type="submit" variant="primary" :loading="isSaving">Save changes</AppButton>
            </div>
          </form>
        </AppCard>
      </div>

      <!-- Status tab -->
      <div v-else class="space-y-4 max-w-2xl">
        <AppCard title="Account status" subtitle="Change this user's account status">
          <div class="flex flex-wrap gap-3">
            <AppButton
              v-for="action in statusActions"
              :key="action.status"
              :variant="action.variant"
              @click="confirmStatusChange(action.status)"
            >
              {{ action.label }} user
            </AppButton>
          </div>

          <div class="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
            <p><strong>Current status:</strong>
              <span :class="[
                'ml-1 capitalize font-medium',
                user.status === 'active' ? 'text-emerald-600' : user.status === 'banned' ? 'text-red-600' : 'text-amber-600'
              ]">{{ user.status }}</span>
            </p>
          </div>
        </AppCard>

        <AppCard>
          <div class="flex items-start justify-between gap-4 rounded-lg border border-red-200 bg-red-50 p-4">
            <div>
              <p class="font-semibold text-red-800">Delete user</p>
              <p class="mt-0.5 text-sm text-red-700">Permanently delete this user and all their data.</p>
            </div>
            <AppButton variant="danger" size="sm" @click="showDeleteModal = true">Delete</AppButton>
          </div>
        </AppCard>
      </div>
    </template>

    <!-- Status change confirmation -->
    <AppModal v-model="showStatusModal" title="Confirm status change" size="sm">
      <p class="text-sm text-slate-600">
        Are you sure you want to set this user's status to
        <strong class="capitalize">{{ pendingStatus }}</strong>?
      </p>
      <template #footer>
        <div class="flex gap-3 justify-end">
          <AppButton variant="secondary" @click="showStatusModal = false">Cancel</AppButton>
          <AppButton variant="primary" :loading="isChangingStatus" @click="handleStatusChange">
            Confirm
          </AppButton>
        </div>
      </template>
    </AppModal>

    <!-- Delete confirmation -->
    <AppModal v-model="showDeleteModal" title="Delete user" size="sm">
      <AppAlert variant="error">This will permanently delete the user and all associated data.</AppAlert>
      <template #footer>
        <div class="flex gap-3 justify-end">
          <AppButton variant="secondary" @click="showDeleteModal = false">Cancel</AppButton>
          <AppButton variant="danger" :loading="isDeleting" @click="handleDelete">Delete user</AppButton>
        </div>
      </template>
    </AppModal>
  </div>
</template>

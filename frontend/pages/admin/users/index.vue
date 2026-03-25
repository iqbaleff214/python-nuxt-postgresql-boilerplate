<script setup lang="ts">
import type { User, PaginatedResponse } from '~/types'

definePageMeta({ middleware: 'superadmin', layout: 'admin' })

const api = useApi()
const toast = useToast()
const { t } = useI18n()

const users = ref<User[]>([])
const isLoading = ref(false)
const currentPage = ref(1)
const totalUsers = ref(0)
const perPage = 20

const search = ref('')
const filterRole = ref('')
const filterStatus = ref('')

const showDeleteModal = ref(false)
const userToDelete = ref<User | null>(null)
const isDeleting = ref(false)

const columns = computed(() => [
  { key: 'name', label: t('admin.users.colName') },
  { key: 'email', label: t('admin.users.colEmail') },
  { key: 'role', label: t('admin.users.colRole') },
  { key: 'status', label: t('admin.users.colStatus') },
  { key: 'verified', label: t('admin.users.colVerified') },
  { key: 'last_login', label: t('admin.users.colLastLogin') },
  { key: 'actions', label: t('admin.users.colActions'), class: 'text-right' },
])

const roleOptions = computed(() => [
  { value: '', label: t('admin.users.allRoles') },
  { value: 'user', label: t('admin.users.user') },
  { value: 'superadmin', label: t('admin.users.superadmin') },
])

const statusOptions = computed(() => [
  { value: '', label: t('admin.users.allStatuses') },
  { value: 'active', label: t('admin.users.active') },
  { value: 'inactive', label: t('admin.users.inactive') },
  { value: 'banned', label: t('admin.users.banned') },
])

async function fetchUsers() {
  isLoading.value = true
  const params: Record<string, any> = {
    page: currentPage.value,
    per_page: perPage,
  }
  if (search.value) params.search = search.value
  if (filterRole.value) params.role = filterRole.value
  if (filterStatus.value) params.status = filterStatus.value

  const response = await api.get<User[]>('/admin/users', { params })

  if (response.success) {
    users.value = (response.data as unknown as User[]) ?? []
    totalUsers.value = response.meta?.total ?? 0
  }
  isLoading.value = false
}

const debouncedFetch = useDebounceFn(fetchUsers, 350)

watch([filterRole, filterStatus], () => {
  currentPage.value = 1
  fetchUsers()
})

watch(search, () => {
  currentPage.value = 1
  debouncedFetch()
})

function confirmDelete(user: User) {
  userToDelete.value = user
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!userToDelete.value) return
  isDeleting.value = true

  const response = await api.delete(`/admin/users/${userToDelete.value.id}`)

  if (response.success) {
    toast.success(t('admin.users.deleteSuccess'))
    showDeleteModal.value = false
    userToDelete.value = null
    fetchUsers()
  } else {
    toast.error(response.message || t('admin.users.deleteFailed'))
  }
  isDeleting.value = false
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return t('admin.users.never')
  return new Date(dateStr).toLocaleDateString()
}

onMounted(fetchUsers)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">{{ $t('admin.users.title') }}</h1>
        <p class="mt-0.5 text-sm text-slate-500">{{ $t('admin.users.totalUsers', { n: totalUsers }) }}</p>
      </div>
      <NuxtLink to="/admin/users/create">
        <AppButton variant="primary">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {{ $t('admin.users.createUser') }}
        </AppButton>
      </NuxtLink>
    </div>

    <!-- Filters -->
    <AppCard padding="sm">
      <div class="flex flex-col gap-3 sm:flex-row">
        <div class="relative flex-1">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            v-model="search"
            type="text"
            :placeholder="$t('admin.users.searchPlaceholder')"
            class="w-full rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          />
        </div>

        <AppSelect v-model="filterRole" :options="roleOptions" class="sm:w-40" />
        <AppSelect v-model="filterStatus" :options="statusOptions" class="sm:w-40" />
      </div>
    </AppCard>

    <!-- Table -->
    <AppTable :columns="columns" :rows="users" :loading="isLoading" :empty-message="$t('admin.users.noUsersFound')">
      <template #name="{ row }">
        <div class="flex items-center gap-3">
          <AppAvatar :src="row.avatar_url" :name="`${row.first_name} ${row.last_name}`" size="sm" />
          <div>
            <p class="font-medium text-slate-900">{{ row.first_name }} {{ row.last_name }}</p>
            <p v-if="row.display_name" class="text-xs text-slate-500">{{ row.display_name }}</p>
          </div>
        </div>
      </template>

      <template #email="{ row }">
        <span class="text-slate-600">{{ row.email }}</span>
      </template>

      <template #role="{ row }">
        <AppBadge :variant="row.role === 'superadmin' ? 'indigo' : 'default'">
          {{ row.role }}
        </AppBadge>
      </template>

      <template #status="{ row }">
        <AppBadge :variant="row.status === 'active' ? 'success' : row.status === 'banned' ? 'danger' : 'warning'">
          {{ row.status }}
        </AppBadge>
      </template>

      <template #verified="{ row }">
        <div class="flex items-center gap-1.5">
          <div :class="['h-2 w-2 rounded-full', row.is_email_verified ? 'bg-emerald-500' : 'bg-slate-300']" />
          <span :class="row.is_email_verified ? 'text-emerald-700' : 'text-slate-500'">
            {{ row.is_email_verified ? $t('common.yes') : $t('common.no') }}
          </span>
        </div>
      </template>

      <template #last_login="{ row }">
        <span class="text-slate-500">{{ formatDate(row.last_login_at) }}</span>
      </template>

      <template #actions="{ row }">
        <div class="flex items-center justify-end gap-2">
          <NuxtLink :to="`/admin/users/${row.id}`">
            <AppButton variant="ghost" size="sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {{ $t('admin.users.view') }}
            </AppButton>
          </NuxtLink>
          <AppButton variant="ghost" size="sm" class="text-red-600 hover:bg-red-50" @click="confirmDelete(row as User)">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </AppButton>
        </div>
      </template>
    </AppTable>

    <!-- Pagination -->
    <AppPagination
      v-if="totalUsers > perPage"
      :page="currentPage"
      :total="totalUsers"
      :per-page="perPage"
      @change="(p) => { currentPage = p; fetchUsers() }"
    />

    <!-- Delete modal -->
    <AppModal v-model="showDeleteModal" :title="$t('admin.users.deleteTitle')" size="sm">
      <div class="space-y-3">
        <p class="text-sm text-slate-600">
          {{ $t('admin.users.deleteConfirm', { name: `${userToDelete?.first_name} ${userToDelete?.last_name}` }) }}
        </p>
        <AppAlert variant="error">{{ $t('admin.users.deleteWarning') }}</AppAlert>
      </div>
      <template #footer>
        <div class="flex gap-3 justify-end">
          <AppButton variant="secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</AppButton>
          <AppButton variant="danger" :loading="isDeleting" @click="handleDelete">{{ $t('admin.users.deleteTitle') }}</AppButton>
        </div>
      </template>
    </AppModal>
  </div>
</template>

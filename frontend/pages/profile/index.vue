<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const api = useApi()
const toast = useToast()

const form = reactive({
  first_name: authStore.user?.first_name ?? '',
  last_name: authStore.user?.last_name ?? '',
  display_name: authStore.user?.display_name ?? '',
  bio: authStore.user?.bio ?? '',
})

const isSaving = ref(false)
const formError = ref('')
const avatarPreview = ref<string | null>(null)
const avatarFile = ref<File | null>(null)
const isUploadingAvatar = ref(false)
const showDeleteModal = ref(false)
const showEmailModal = ref(false)
const newEmail = ref('')
const deleteConfirmText = ref('')

async function handleSave() {
  isSaving.value = true
  formError.value = ''

  const response = await api.patch('/profile/me', form)

  if (response.success) {
    await authStore.fetchMe()
    toast.success('Profile updated successfully')
  } else {
    formError.value = response.message || 'Failed to update profile'
  }
  isSaving.value = false
}

function handleAvatarChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    toast.error('Please select an image file')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    toast.error('Image must be less than 5MB')
    return
  }

  avatarFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => { avatarPreview.value = e.target?.result as string }
  reader.readAsDataURL(file)
}

async function uploadAvatar() {
  if (!avatarFile.value) return
  isUploadingAvatar.value = true

  const formData = new FormData()
  formData.append('avatar', avatarFile.value)

  const authStore2 = useAuthStore()
  try {
    const response = await $fetch<any>('/profile/me/avatar', {
      method: 'POST',
      baseURL: useRuntimeConfig().public.apiBase as string,
      headers: { Authorization: `Bearer ${authStore2.accessToken}` },
      body: formData,
    })
    if (response.success) {
      await authStore.fetchMe()
      avatarFile.value = null
      avatarPreview.value = null
      toast.success('Avatar updated!')
    }
  } catch {
    toast.error('Failed to upload avatar')
  }
  isUploadingAvatar.value = false
}

async function handleDeleteAccount() {
  if (deleteConfirmText.value !== 'DELETE') {
    toast.error('Please type DELETE to confirm')
    return
  }

  const response = await api.delete('/profile/me')
  if (response.success) {
    await authStore.logout()
    navigateTo('/login')
  } else {
    toast.error(response.message || 'Failed to delete account')
  }
}

const displayName = computed(() => authStore.user?.display_name || `${authStore.user?.first_name} ${authStore.user?.last_name}`)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-900">Profile</h1>
      <p class="mt-0.5 text-sm text-slate-500">Manage your personal information</p>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Avatar section -->
      <div class="lg:col-span-1">
        <AppCard title="Profile photo">
          <div class="flex flex-col items-center gap-4">
            <div class="relative group">
              <AppAvatar
                :src="avatarPreview || authStore.user?.avatar_url"
                :name="displayName"
                size="xl"
                class="h-24 w-24 text-3xl"
              />
              <label
                class="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 opacity-0 group-hover:opacity-100 cursor-pointer transition-opacity"
                title="Change avatar"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <input type="file" accept="image/*" class="sr-only" @change="handleAvatarChange" />
              </label>
            </div>

            <div class="text-center">
              <p class="font-semibold text-slate-900">{{ displayName }}</p>
              <AppBadge :variant="authStore.user?.role === 'superadmin' ? 'indigo' : 'default'" class="mt-1">
                {{ authStore.user?.role }}
              </AppBadge>
            </div>

            <div v-if="avatarFile" class="w-full space-y-2">
              <p class="text-xs text-center text-slate-500">{{ avatarFile.name }}</p>
              <div class="flex gap-2">
                <AppButton variant="secondary" size="sm" class="flex-1" @click="avatarFile = null; avatarPreview = null">
                  Cancel
                </AppButton>
                <AppButton variant="primary" size="sm" class="flex-1" :loading="isUploadingAvatar" @click="uploadAvatar">
                  Upload
                </AppButton>
              </div>
            </div>
            <p v-else class="text-xs text-slate-400 text-center">Click on avatar to change photo<br>Max 5MB, JPG/PNG</p>
          </div>

          <!-- Account info -->
          <div class="mt-4 space-y-2 rounded-lg bg-slate-50 p-3 text-sm">
            <div class="flex justify-between">
              <span class="text-slate-500">Email</span>
              <div class="flex items-center gap-2">
                <span class="text-slate-700 text-xs truncate max-w-[150px]">{{ authStore.user?.email }}</span>
                <AppBadge v-if="authStore.user?.is_email_verified" variant="success" size="sm">Verified</AppBadge>
                <AppBadge v-else variant="warning" size="sm">Unverified</AppBadge>
              </div>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Member since</span>
              <span class="text-slate-700">{{ authStore.user?.created_at ? new Date(authStore.user.created_at).toLocaleDateString() : '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Last login</span>
              <span class="text-slate-700 text-xs">{{ authStore.user?.last_login_at ? new Date(authStore.user.last_login_at).toLocaleString() : 'Never' }}</span>
            </div>
          </div>
        </AppCard>
      </div>

      <!-- Profile form -->
      <div class="lg:col-span-2 space-y-6">
        <AppCard title="Personal information" subtitle="Update your profile details">
          <AppAlert v-if="formError" variant="error" class="mb-4" dismissible @dismiss="formError = ''">
            {{ formError }}
          </AppAlert>

          <form class="space-y-4" @submit.prevent="handleSave">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <AppInput
                v-model="form.first_name"
                label="First name"
                placeholder="John"
                required
              />
              <AppInput
                v-model="form.last_name"
                label="Last name"
                placeholder="Doe"
                required
              />
            </div>

            <AppInput
              v-model="form.display_name"
              label="Display name"
              placeholder="How you'd like to appear"
              hint="This name will be shown publicly"
            />

            <AppTextarea
              v-model="form.bio"
              label="Bio"
              placeholder="Tell us a little about yourself..."
              :rows="3"
              hint="Up to 500 characters"
            />

            <div class="flex justify-end">
              <AppButton type="submit" variant="primary" :loading="isSaving">
                Save changes
              </AppButton>
            </div>
          </form>
        </AppCard>

        <!-- Danger Zone -->
        <AppCard>
          <div class="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div class="flex-1">
              <p class="font-semibold text-red-800">Danger Zone</p>
              <p class="mt-0.5 text-sm text-red-700">Permanently delete your account and all associated data.</p>
            </div>
            <AppButton variant="danger" size="sm" @click="showDeleteModal = true">
              Delete account
            </AppButton>
          </div>
        </AppCard>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <AppModal v-model="showDeleteModal" title="Delete account" size="sm">
      <div class="space-y-4">
        <AppAlert variant="error">
          This action is <strong>irreversible</strong>. All your data will be permanently deleted.
        </AppAlert>
        <AppInput
          v-model="deleteConfirmText"
          label="Type DELETE to confirm"
          placeholder="DELETE"
        />
      </div>
      <template #footer>
        <div class="flex gap-3 justify-end">
          <AppButton variant="secondary" @click="showDeleteModal = false">Cancel</AppButton>
          <AppButton
            variant="danger"
            :disabled="deleteConfirmText !== 'DELETE'"
            @click="handleDeleteAccount"
          >
            Delete my account
          </AppButton>
        </div>
      </template>
    </AppModal>
  </div>
</template>

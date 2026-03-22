import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginResponse, RefreshResponse, ApiResponse } from '~/types'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const user = ref<User | null>(null)
    const accessToken = ref<string | null>(null)
    const mfaChallengeToken = ref<string | null>(null)

    const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
    const isSuperAdmin = computed(() => user.value?.role === 'superadmin')

    const config = useRuntimeConfig()
    const baseURL = config.public.apiBase as string

    async function login(email: string, password: string): Promise<{ mfaRequired: boolean }> {
      const response = await $fetch<ApiResponse<LoginResponse>>('/auth/login', {
        method: 'POST',
        baseURL,
        body: { email, password },
      })

      if (!response.success || !response.data) {
        throw new Error(response.message || 'Login failed')
      }

      if (response.data.requires_2fa && response.data.mfa_challenge_token) {
        mfaChallengeToken.value = response.data.mfa_challenge_token
        return { mfaRequired: true }
      }

      if (!response.data.access_token) {
        throw new Error('Login failed: no access token returned')
      }

      accessToken.value = response.data.access_token
      await fetchMe()
      return { mfaRequired: false }
    }

    async function verify2fa(code: string, isRecoveryCode = false): Promise<void> {
      if (!mfaChallengeToken.value) {
        throw new Error('No MFA challenge token')
      }

      const body = { mfa_challenge_token: mfaChallengeToken.value, code }

      const response = await $fetch<ApiResponse<LoginResponse>>('/auth/verify-2fa', {
        method: 'POST',
        baseURL,
        body,
      })

      if (!response.success || !response.data?.access_token) {
        throw new Error(response.message || '2FA verification failed')
      }

      accessToken.value = response.data.access_token
      mfaChallengeToken.value = null
      await fetchMe()
    }

    async function logout(): Promise<void> {
      try {
        if (accessToken.value) {
          await $fetch('/auth/logout', {
            method: 'POST',
            baseURL,
            headers: { Authorization: `Bearer ${accessToken.value}` },
          })
        }
      } catch {
        // ignore errors on logout
      } finally {
        user.value = null
        accessToken.value = null
        mfaChallengeToken.value = null
      }
    }

    async function refreshToken(): Promise<string | null> {
      try {
        const response = await $fetch<ApiResponse<RefreshResponse>>('/auth/refresh', {
          method: 'POST',
          baseURL,
          credentials: 'include',
        })

        if (response.success && response.data?.access_token) {
          accessToken.value = response.data.access_token
          return response.data.access_token
        }
        return null
      } catch {
        return null
      }
    }

    async function fetchMe(): Promise<void> {
      if (!accessToken.value) return

      const response = await $fetch<ApiResponse<User>>('/profile/me', {
        baseURL,
        headers: { Authorization: `Bearer ${accessToken.value}` },
      })

      if (response.success && response.data) {
        user.value = response.data
      }
    }

    function setTokens(access: string): void {
      accessToken.value = access
    }

    return {
      user,
      accessToken,
      mfaChallengeToken,
      isAuthenticated,
      isSuperAdmin,
      login,
      verify2fa,
      logout,
      refreshToken,
      fetchMe,
      setTokens,
    }
  },
  { persist: true }
)

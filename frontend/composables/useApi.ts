import type { ApiResponse } from '~/types'

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'

interface FetchOptions {
  headers?: Record<string, string>
  params?: Record<string, any>
  [key: string]: any
}

export function useApi() {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase as string

  async function getAuthStore() {
    const { useAuthStore } = await import('~/stores/auth')
    return useAuthStore()
  }

  async function request<T = any>(
    method: HttpMethod,
    path: string,
    body?: any,
    options: FetchOptions = {}
  ): Promise<ApiResponse<T>> {
    const authStore = await getAuthStore()

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    }

    if (authStore.accessToken) {
      headers['Authorization'] = `Bearer ${authStore.accessToken}`
    }

    const fetchOptions: any = {
      method,
      baseURL,
      headers,
      ...options,
    }

    if (body !== undefined) {
      fetchOptions.body = body
    }

    try {
      const response = await $fetch<ApiResponse<T>>(path, fetchOptions)
      return response
    } catch (err: any) {
      const status = err?.response?.status ?? err?.status

      if (status === 401) {
        // Try to refresh token
        try {
          const newToken = await authStore.refreshToken()
          if (newToken) {
            headers['Authorization'] = `Bearer ${newToken}`
            fetchOptions.headers = headers
            const retryResponse = await $fetch<ApiResponse<T>>(path, fetchOptions)
            return retryResponse
          }
        } catch {
          // Refresh failed — logout
          authStore.logout()
          await navigateTo('/login')
        }
      }

      // Return error in standard format
      const message =
        err?.data?.message ||
        err?.message ||
        'An unexpected error occurred'
      return {
        success: false,
        message,
        data: null,
      }
    }
  }

  return {
    get: <T = any>(path: string, options?: FetchOptions) =>
      request<T>('GET', path, undefined, options),

    post: <T = any>(path: string, body?: any, options?: FetchOptions) =>
      request<T>('POST', path, body, options),

    patch: <T = any>(path: string, body?: any, options?: FetchOptions) =>
      request<T>('PATCH', path, body, options),

    put: <T = any>(path: string, body?: any, options?: FetchOptions) =>
      request<T>('PUT', path, body, options),

    delete: <T = any>(path: string, options?: FetchOptions) =>
      request<T>('DELETE', path, undefined, options),
  }
}

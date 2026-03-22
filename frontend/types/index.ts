export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  display_name: string | null
  bio: string | null
  avatar_url: string | null
  role: 'user' | 'superadmin'
  status: 'active' | 'inactive' | 'banned'
  is_email_verified: boolean
  is_2fa_enabled: boolean
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export interface Notification {
  id: string
  user_id: string
  type: string
  title: string
  body: string | null
  read_at: string | null
  created_at: string
}

export interface PaginatedResponse<T> {
  success: boolean
  message: string
  data: T[]
  meta: { page: number; per_page: number; total: number; total_pages: number }
}

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data: T | null
  meta?: any
}

export interface LoginResponse {
  access_token?: string
  requires_2fa?: boolean
  mfa_challenge_token?: string
}

export interface RefreshResponse {
  access_token: string
}

export interface RecoveryCodesResponse {
  recovery_codes: string[]
}

export interface TwoFASetupResponse {
  secret: string
  qr_code_url: string
  recovery_codes: string[]
}

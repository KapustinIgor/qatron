import { apiClient } from './client'

export interface LoginCredentials {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  organization_id: number
  created_at: string
  updated_at?: string
}

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  register: async (data: {
    email: string
    username: string
    password: string
    organization_id: number
  }): Promise<void> => {
    await apiClient.post('/auth/register', data)
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },
}

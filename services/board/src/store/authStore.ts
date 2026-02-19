import { create } from 'zustand'

interface AuthState {
  token: string | null
  isAuthenticated: boolean
  setToken: (token: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('qatron-token') : null,
  isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('qatron-token') : false,
  setToken: (token) => {
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('qatron-token', token)
      } else {
        localStorage.removeItem('qatron-token')
      }
    }
    set({ token, isAuthenticated: !!token })
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('qatron-token')
    }
    set({ token: null, isAuthenticated: false })
  },
}))

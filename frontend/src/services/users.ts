import api from './api'
import { User } from '@/types'

export interface PasswordChangeData {
  current_password: string
  new_password: string
}

export interface ProfileUpdateData {
  nome?: string
  email?: string
}

export interface CreateUserData {
  nome: string
  email: string
  password: string
  role: 'admin' | 'operator' | 'viewer'
  status: 'pending' | 'active' | 'inactive'
  fiscal_id?: number | null
}

export const usersApi = {
  list: async (): Promise<User[]> => {
    const response = await api.get('/users')
    return response.data
  },

  getPendingCount: async (): Promise<number> => {
    const response = await api.get('/users/pending-count')
    return response.data.count
  },

  create: async (data: CreateUserData): Promise<User> => {
    const response = await api.post('/users', data)
    return response.data
  },

  update: async (id: number, data: Partial<User>): Promise<User> => {
    const response = await api.put(`/users/${id}`, data)
    return response.data
  },

  approve: async (id: number): Promise<{ message: string }> => {
    const response = await api.post(`/users/${id}/approve`)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`)
  },

  changePassword: async (data: PasswordChangeData): Promise<{ message: string }> => {
    const response = await api.post('/users/change-password', data)
    return response.data
  },

  updateProfile: async (data: ProfileUpdateData): Promise<User> => {
    const response = await api.put('/users/me', data)
    return response.data
  },
}

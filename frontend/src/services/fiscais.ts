import api from './api'
import { Fiscal, PaginatedResponse } from '@/types'

interface ListParams {
  skip?: number
  limit?: number
  search?: string
  ativo?: boolean
}

export const fiscaisApi = {
  list: async (params: ListParams = {}): Promise<PaginatedResponse<Fiscal>> => {
    const { data } = await api.get('/fiscais', { params })
    return data
  },

  getAtivos: async (): Promise<Fiscal[]> => {
    const { data } = await api.get('/fiscais/ativos')
    return data
  },

  getById: async (id: number): Promise<Fiscal> => {
    const { data } = await api.get(`/fiscais/${id}`)
    return data
  },

  create: async (fiscal: Omit<Fiscal, 'id' | 'created_at' | 'updated_at'>): Promise<Fiscal> => {
    const { data } = await api.post('/fiscais', fiscal)
    return data
  },

  update: async (id: number, fiscal: Partial<Fiscal>): Promise<Fiscal> => {
    const { data } = await api.put(`/fiscais/${id}`, fiscal)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/fiscais/${id}`)
  },
}

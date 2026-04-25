import api from './api'
import { Cessionario, PaginatedResponse } from '@/types'

interface ListParams {
  skip?: number
  limit?: number
  search?: string
  situacao?: string
  atividade?: string
}

export const cessionariosApi = {
  list: async (params: ListParams = {}): Promise<PaginatedResponse<Cessionario>> => {
    const { data } = await api.get('/cessionarios', { params })
    return data
  },

  getById: async (id: number): Promise<Cessionario> => {
    const { data } = await api.get(`/cessionarios/${id}`)
    return data
  },

  create: async (cessionario: Omit<Cessionario, 'id' | 'created_at' | 'updated_at'>): Promise<Cessionario> => {
    const { data } = await api.post('/cessionarios', cessionario)
    return data
  },

  update: async (id: number, cessionario: Partial<Cessionario>): Promise<Cessionario> => {
    const { data } = await api.put(`/cessionarios/${id}`, cessionario)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/cessionarios/${id}`)
  },

  getAtividades: async (): Promise<string[]> => {
    const { data } = await api.get('/cessionarios/atividades')
    return data
  },
}

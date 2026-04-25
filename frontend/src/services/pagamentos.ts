import api from './api'
import { Pagamento, PaginatedResponse } from '@/types'

interface ListParams {
  skip?: number
  limit?: number
  search?: string
  periodicidade?: string
  data_inicio?: string
  data_fim?: string
}

export const pagamentosApi = {
  list: async (params: ListParams = {}): Promise<PaginatedResponse<Pagamento>> => {
    const { data } = await api.get('/pagamentos', { params })
    return data
  },

  getByCessionario: async (cessionarioId: number): Promise<Pagamento[]> => {
    const { data } = await api.get(`/pagamentos/cessionario/${cessionarioId}`)
    return data
  },

  create: async (pagamento: Omit<Pagamento, 'id' | 'created_at'>): Promise<Pagamento> => {
    const { data } = await api.post('/pagamentos', pagamento)
    return data
  },

  update: async (id: number, pagamento: Partial<Pagamento>): Promise<Pagamento> => {
    const { data } = await api.put(`/pagamentos/${id}`, pagamento)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/pagamentos/${id}`)
  },
}

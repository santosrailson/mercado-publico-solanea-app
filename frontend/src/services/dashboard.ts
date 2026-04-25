import api from './api'
import { DashboardKPIs, ChartData } from '@/types'

export const dashboardApi = {
  getKPIs: async (): Promise<DashboardKPIs> => {
    const { data } = await api.get('/dashboard/kpis')
    return data
  },

  getArrecadacaoChart: async (): Promise<ChartData> => {
    const { data } = await api.get('/dashboard/charts/arrecadacao')
    return data
  },

  getSituacaoChart: async (): Promise<ChartData> => {
    const { data } = await api.get('/dashboard/charts/situacao')
    return data
  },

  getTopCessionarios: async (limit: number = 5): Promise<Array<{ nome: string; box: string; total: number }>> => {
    const { data } = await api.get('/dashboard/top-cessionarios', { params: { limit } })
    return data
  },

  getAtividadesRecentes: async (limit: number = 10): Promise<Array<any>> => {
    const { data } = await api.get('/dashboard/atividades-recentes', { params: { limit } })
    return data
  },
}

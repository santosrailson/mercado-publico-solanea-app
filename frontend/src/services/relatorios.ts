import api from './api'
import { RelatorioFiltros } from '@/types'

export const relatoriosApi = {
  exportar: async (filtros: RelatorioFiltros): Promise<Blob> => {
    const { data } = await api.post('/relatorios/exportar', filtros, {
      responseType: 'blob',
    })
    return data
  },

  gerarCertidao: async (cessionarioId: number): Promise<Blob> => {
    const { data } = await api.get(`/relatorios/certidao/${cessionarioId}`, {
      responseType: 'blob',
    })
    return data
  },
}

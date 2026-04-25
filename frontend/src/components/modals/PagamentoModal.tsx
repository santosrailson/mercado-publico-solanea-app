import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { pagamentosApi } from '@/services/pagamentos'
import { cessionariosApi } from '@/services/cessionarios'
import { Pagamento } from '@/types'

interface PagamentoModalProps {
  isOpen: boolean
  onClose: () => void
  pagamento?: Pagamento | null
}

export function PagamentoModal({ isOpen, onClose, pagamento }: PagamentoModalProps) {
  const queryClient = useQueryClient()
  const isEditing = !!pagamento
  
  const getMesAnoAtual = () => {
    const hoje = new Date()
    return `${String(hoje.getMonth() + 1).padStart(2, '0')}/${hoje.getFullYear()}`
  }

  const [formData, setFormData] = useState({
    cessionario_id: '',
    valor: '',
    data_pagamento: new Date().toISOString().split('T')[0],
    periodicidade: 'Mensal' as 'Mensal' | 'Semanal' | 'Quinzenal' | 'Único',
    referencia_mes: getMesAnoAtual(),
    observacoes: '',
  })

  const { data: cessionarios, isLoading: isLoadingCessionarios, error } = useQuery({
    queryKey: ['cessionarios-select'],
    queryFn: () => cessionariosApi.list({ limit: 100 }),
    enabled: isOpen,
  })

  // Debug
  console.log('Modal isOpen:', isOpen)
  console.log('Cessionarios data:', cessionarios)
  console.log('Error:', error)

  // Preencher formulário quando estiver editando
  useEffect(() => {
    if (pagamento) {
      setFormData({
        cessionario_id: pagamento.cessionario_id?.toString() || '',
        valor: pagamento.valor?.toString() || '',
        data_pagamento: pagamento.data_pagamento 
          ? new Date(pagamento.data_pagamento).toISOString().split('T')[0]
          : new Date().toISOString().split('T')[0],
        periodicidade: pagamento.periodicidade || 'Mensal',
        referencia_mes: pagamento.referencia_mes || '',
        observacoes: pagamento.observacoes || '',
      })
    } else {
      // Reset ao abrir para criar novo
      setFormData({
        cessionario_id: '',
        valor: '',
        data_pagamento: new Date().toISOString().split('T')[0],
        periodicidade: 'Mensal',
        referencia_mes: getMesAnoAtual(),
        observacoes: '',
      })
    }
  }, [pagamento, isOpen])

  const createMutation = useMutation({
    mutationFn: pagamentosApi.create,
    onSuccess: () => {
      toast.success('Pagamento registrado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['pagamentos'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      onClose()
    },
    onError: () => toast.error('Erro ao registrar pagamento'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Pagamento> }) =>
      pagamentosApi.update(id, data),
    onSuccess: () => {
      toast.success('Pagamento atualizado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['pagamentos'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      onClose()
    },
    onError: () => toast.error('Erro ao atualizar pagamento'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.cessionario_id) {
      toast.error('Selecione um cessionário')
      return
    }
    if (!formData.valor || parseFloat(formData.valor) <= 0) {
      toast.error('Informe um valor válido')
      return
    }
    if (!formData.referencia_mes) {
      toast.error('Informe a referência (Mês/Ano)')
      return
    }
    
    const data = {
      cessionario_id: parseInt(formData.cessionario_id),
      valor: parseFloat(formData.valor),
      data_pagamento: new Date(formData.data_pagamento).toISOString(),
      periodicidade: formData.periodicidade,
      referencia_mes: formData.referencia_mes || null,
      observacoes: formData.observacoes || null,
    }
    
    if (isEditing && pagamento) {
      updateMutation.mutate({ id: pagamento.id, data })
    } else {
      createMutation.mutate(data as any)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? 'Editar Pagamento' : 'Registrar Pagamento'}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-[var(--text2)] mb-1">
            Cessionário *
          </label>
          {isLoadingCessionarios ? (
            <div className="input text-[var(--muted)]">Carregando cessionários...</div>
          ) : error ? (
            <div className="input text-red-400">Erro ao carregar cessionários</div>
          ) : (
            <select
              value={formData.cessionario_id}
              onChange={(e) => setFormData({ ...formData, cessionario_id: e.target.value })}
              className="input"
              disabled={isEditing}
            >
              <option value="">
                {cessionarios?.items.length === 0 
                  ? 'Nenhum cessionário cadastrado' 
                  : 'Selecione um cessionário'}
              </option>
              {cessionarios?.items.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nome} {c.numero_box ? `(Box ${c.numero_box})` : ''}
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Valor *
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={formData.valor}
              onChange={(e) => setFormData({ ...formData, valor: e.target.value })}
              className="input"
              placeholder="0,00"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Data do Pagamento *
            </label>
            <input
              type="date"
              value={formData.data_pagamento}
              onChange={(e) => setFormData({ ...formData, data_pagamento: e.target.value })}
              className="input"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Periodicidade
            </label>
            <select
              value={formData.periodicidade}
              onChange={(e) => setFormData({ ...formData, periodicidade: e.target.value as any })}
              className="input"
            >
              <option value="Mensal">Mensal</option>
              <option value="Semanal">Semanal</option>
              <option value="Quinzenal">Quinzenal</option>
              <option value="Único">Único</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Referência (Mês/Ano) *
            </label>
            <input
              type="text"
              value={formData.referencia_mes}
              onChange={(e) => setFormData({ ...formData, referencia_mes: e.target.value })}
              className="input"
              placeholder="01/2024"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text2)] mb-1">
            Observações
          </label>
          <textarea
            value={formData.observacoes}
            onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
            className="input min-h-[80px] resize-none"
            placeholder="Observações opcionais..."
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button 
            type="submit" 
            isLoading={createMutation.isPending || updateMutation.isPending}
          >
            {isEditing ? 'Atualizar' : 'Registrar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { cessionariosApi } from '@/services/cessionarios'
import { Cessionario } from '@/types'

interface CessionarioModalProps {
  isOpen: boolean
  onClose: () => void
  cessionario?: Cessionario | null
}

export function CessionarioModal({ isOpen, onClose, cessionario }: CessionarioModalProps) {
  const queryClient = useQueryClient()
  const isEditing = !!cessionario
  
  const [formData, setFormData] = useState({
    nome: '',
    numero_box: '',
    atividade: '',
    telefone: '',
    situacao: 'Regular' as 'Regular' | 'Irregular',
    valor_referencia: '',
    periodicidade_referencia: 'Mensal' as 'Mensal' | 'Semanal' | 'Quinzenal' | 'Único',
    observacoes: '',
  })

  // Preencher formulário quando estiver editando
  useEffect(() => {
    if (cessionario) {
      setFormData({
        nome: cessionario.nome || '',
        numero_box: cessionario.numero_box || '',
        atividade: cessionario.atividade || '',
        telefone: cessionario.telefone || '',
        situacao: cessionario.situacao || 'Regular',
        valor_referencia: cessionario.valor_referencia?.toString() || '',
        periodicidade_referencia: cessionario.periodicidade_referencia || 'Mensal',
        observacoes: cessionario.observacoes || '',
      })
    } else {
      // Reset ao abrir para criar novo
      setFormData({
        nome: '',
        numero_box: '',
        atividade: '',
        telefone: '',
        situacao: 'Regular',
        valor_referencia: '',
        periodicidade_referencia: 'Mensal',
        observacoes: '',
      })
    }
  }, [cessionario, isOpen])

  const createMutation = useMutation({
    mutationFn: cessionariosApi.create,
    onSuccess: () => {
      toast.success('Cessionário cadastrado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['cessionarios'] })
      onClose()
    },
    onError: () => toast.error('Erro ao cadastrar cessionário'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Cessionario> }) =>
      cessionariosApi.update(id, data),
    onSuccess: () => {
      toast.success('Cessionário atualizado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['cessionarios'] })
      onClose()
    },
    onError: () => toast.error('Erro ao atualizar cessionário'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.nome.trim()) {
      toast.error('Nome é obrigatório')
      return
    }
    
    const data = {
      ...formData,
      valor_referencia: parseFloat(formData.valor_referencia) || 0,
    }
    
    if (isEditing && cessionario) {
      updateMutation.mutate({ id: cessionario.id, data })
    } else {
      createMutation.mutate(data as any)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? 'Editar Cessionário' : 'Novo Cessionário'}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-[var(--text2)] mb-1">
            Nome completo *
          </label>
          <input
            type="text"
            value={formData.nome}
            onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
            className="input"
            placeholder="Nome do cessionário"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Nº do Box/Ponto
            </label>
            <input
              type="text"
              value={formData.numero_box}
              onChange={(e) => setFormData({ ...formData, numero_box: e.target.value })}
              className="input"
              placeholder="ex.: 152"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Atividade
            </label>
            <input
              type="text"
              value={formData.atividade}
              onChange={(e) => setFormData({ ...formData, atividade: e.target.value })}
              className="input"
              placeholder="ex.: Feirante"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Telefone
            </label>
            <input
              type="text"
              value={formData.telefone}
              onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
              className="input"
              placeholder="(83) 99999-9999"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Situação
            </label>
            <select
              value={formData.situacao}
              onChange={(e) => setFormData({ ...formData, situacao: e.target.value as 'Regular' | 'Irregular' })}
              className="input"
            >
              <option value="Regular">Regular</option>
              <option value="Irregular">Irregular</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Valor de Referência
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.valor_referencia}
              onChange={(e) => setFormData({ ...formData, valor_referencia: e.target.value })}
              className="input"
              placeholder="0,00"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Periodicidade
            </label>
            <select
              value={formData.periodicidade_referencia}
              onChange={(e) => setFormData({ ...formData, periodicidade_referencia: e.target.value as any })}
              className="input"
            >
              <option value="Mensal">Mensal</option>
              <option value="Semanal">Semanal</option>
              <option value="Quinzenal">Quinzenal</option>
              <option value="Único">Único</option>
            </select>
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
            {isEditing ? 'Atualizar' : 'Salvar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
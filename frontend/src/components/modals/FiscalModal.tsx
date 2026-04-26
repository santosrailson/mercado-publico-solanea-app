import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { fiscaisApi } from '@/services/fiscais'
import { Fiscal } from '@/types'

interface FiscalModalProps {
  isOpen: boolean
  onClose: () => void
  fiscal?: Fiscal | null
}

export function FiscalModal({ isOpen, onClose, fiscal }: FiscalModalProps) {
  const queryClient = useQueryClient()
  const isEditing = !!fiscal

  const [formData, setFormData] = useState({
    nome: '',
    matricula: '',
    telefone: '',
    email: '',
    ativo: true,
  })

  useEffect(() => {
    if (fiscal) {
      setFormData({
        nome: fiscal.nome || '',
        matricula: fiscal.matricula || '',
        telefone: fiscal.telefone || '',
        email: fiscal.email || '',
        ativo: fiscal.ativo,
      })
    } else {
      setFormData({
        nome: '',
        matricula: '',
        telefone: '',
        email: '',
        ativo: true,
      })
    }
  }, [fiscal, isOpen])

  const createMutation = useMutation({
    mutationFn: fiscaisApi.create,
    onSuccess: () => {
      toast.success('Fiscal cadastrado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['fiscais'] })
      onClose()
    },
    onError: () => toast.error('Erro ao cadastrar fiscal'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Fiscal> }) =>
      fiscaisApi.update(id, data),
    onSuccess: () => {
      toast.success('Fiscal atualizado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['fiscais'] })
      onClose()
    },
    onError: () => toast.error('Erro ao atualizar fiscal'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.nome.trim()) {
      toast.error('Nome é obrigatório')
      return
    }

    if (isEditing && fiscal) {
      updateMutation.mutate({ id: fiscal.id, data: formData })
    } else {
      createMutation.mutate(formData as any)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? 'Editar Fiscal' : 'Novo Fiscal'}>
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
            placeholder="Nome do fiscal"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Matrícula
            </label>
            <input
              type="text"
              value={formData.matricula}
              onChange={(e) => setFormData({ ...formData, matricula: e.target.value })}
              className="input"
              placeholder="ex.: 12345"
            />
          </div>
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
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text2)] mb-1">
            E-mail
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="input"
            placeholder="email@exemplo.com"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="ativo"
            checked={formData.ativo}
            onChange={(e) => setFormData({ ...formData, ativo: e.target.checked })}
            className="w-4 h-4 rounded border-[var(--border)] text-primary-500 focus:ring-primary-500"
          />
          <label htmlFor="ativo" className="text-sm text-[var(--text2)]">
            Ativo
          </label>
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

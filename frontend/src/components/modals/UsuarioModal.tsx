import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { usersApi } from '@/services/users'
import { fiscaisApi } from '@/services/fiscais'
import { User } from '@/types'

interface UsuarioModalProps {
  isOpen: boolean
  onClose: () => void
  user?: User | null
}

export function UsuarioModal({ isOpen, onClose, user }: UsuarioModalProps) {
  const queryClient = useQueryClient()
  const isEditing = !!user

  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    password: '',
    role: 'operator' as 'admin' | 'operator' | 'viewer',
    status: 'active' as 'pending' | 'active' | 'inactive',
    fiscal_id: '' as string,
  })

  const { data: fiscais } = useQuery({
    queryKey: ['fiscais-ativos'],
    queryFn: fiscaisApi.getAtivos,
    staleTime: 5 * 60 * 1000,
    enabled: isOpen,
  })

  useEffect(() => {
    if (user) {
      setFormData({
        nome: user.nome || '',
        email: user.email || '',
        password: '',
        role: user.role || 'operator',
        status: user.status || 'active',
        fiscal_id: user.fiscal_id?.toString() || '',
      })
    } else {
      setFormData({
        nome: '',
        email: '',
        password: '',
        role: 'operator',
        status: 'active',
        fiscal_id: '',
      })
    }
  }, [user, isOpen])

  const createMutation = useMutation({
    mutationFn: usersApi.create,
    onSuccess: () => {
      toast.success('Usuário criado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['users'] })
      onClose()
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail || 'Erro ao criar usuário'
      toast.error(msg)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<User> }) =>
      usersApi.update(id, data),
    onSuccess: () => {
      toast.success('Usuário atualizado com sucesso!')
      queryClient.invalidateQueries({ queryKey: ['users'] })
      onClose()
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail || 'Erro ao atualizar usuário'
      toast.error(msg)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.nome.trim()) {
      toast.error('Nome é obrigatório')
      return
    }
    if (!formData.email.trim()) {
      toast.error('Email é obrigatório')
      return
    }
    if (!isEditing && !formData.password) {
      toast.error('Senha é obrigatória para novo usuário')
      return
    }

    const data: any = {
      nome: formData.nome,
      email: formData.email,
      role: formData.role,
      status: formData.status,
      fiscal_id: formData.fiscal_id ? parseInt(formData.fiscal_id) : null,
    }

    if (!isEditing && formData.password) {
      data.password = formData.password
    }

    if (isEditing && user) {
      updateMutation.mutate({ id: user.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? 'Editar Usuário' : 'Novo Usuário'}>
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
            placeholder="Nome do usuário"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text2)] mb-1">
            Email *
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="input"
            placeholder="usuario@email.com"
            disabled={isEditing}
          />
        </div>

        {!isEditing && (
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Senha *
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="input"
              placeholder="••••••"
            />
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Função
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
              className="input"
            >
              <option value="admin">Administrador</option>
              <option value="operator">Operador</option>
              <option value="viewer">Visualizador</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text2)] mb-1">
              Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
              className="input"
            >
              <option value="active">Ativo</option>
              <option value="pending">Pendente</option>
              <option value="inactive">Inativo</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text2)] mb-1">
            Fiscal vinculado
          </label>
          <select
            value={formData.fiscal_id}
            onChange={(e) => setFormData({ ...formData, fiscal_id: e.target.value })}
            className="input"
          >
            <option value="">Nenhum fiscal</option>
            {fiscais?.map((f) => (
              <option key={f.id} value={f.id}>
                {f.nome} {f.matricula ? `(${f.matricula})` : ''}
              </option>
            ))}
          </select>
          <p className="text-xs text-[var(--muted)] mt-1">
            Vincule um fiscal para que este usuário gerencie apenas os cessionários deste fiscal.
          </p>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button 
            type="submit" 
            isLoading={createMutation.isPending || updateMutation.isPending}
          >
            {isEditing ? 'Atualizar' : 'Criar'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}

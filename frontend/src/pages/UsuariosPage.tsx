import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, UserCheck } from 'lucide-react'
import { ConfirmModal } from '@/components/modals/ConfirmModal'
import toast from 'react-hot-toast'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { UsuarioModal } from '@/components/modals/UsuarioModal'
import { usersApi } from '@/services/users'
import { User } from '@/types'
import { formatDate } from '@/utils'

export function UsuariosPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<{ id: number; nome: string } | null>(null)

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: usersApi.list,
  })

  const { data: pendingCount } = useQuery({
    queryKey: ['users-pending-count'],
    queryFn: usersApi.getPendingCount,
  })

  const deleteMutation = useMutation({
    mutationFn: usersApi.delete,
    onSuccess: () => {
      toast.success('Usuário removido')
      queryClient.invalidateQueries({ queryKey: ['users'] })
      queryClient.invalidateQueries({ queryKey: ['users-pending-count'] })
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail || 'Erro ao remover usuário'
      toast.error(msg)
    },
  })

  const approveMutation = useMutation({
    mutationFn: usersApi.approve,
    onSuccess: () => {
      toast.success('Usuário aprovado!')
      queryClient.invalidateQueries({ queryKey: ['users'] })
      queryClient.invalidateQueries({ queryKey: ['users-pending-count'] })
    },
    onError: () => toast.error('Erro ao aprovar usuário'),
  })

  const filteredUsers = users?.filter((u) =>
    u.nome.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-green-500/20 text-green-400">Ativo</span>
      case 'pending':
        return <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400">Pendente</span>
      case 'inactive':
        return <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-gray-500/20 text-gray-400">Inativo</span>
      default:
        return <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-gray-500/20 text-gray-400">{status}</span>
    }
  }

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return 'Administrador'
      case 'operator': return 'Operador'
      case 'viewer': return 'Visualizador'
      default: return role
    }
  }

  return (
    <div className="space-y-4 md:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-[var(--text)]">Usuários</h1>
          <p className="text-sm text-[var(--text2)]">Gerencie usuários e permissões do sistema</p>
        </div>
        <div className="flex items-center gap-3">
          {pendingCount ? (
            <span className="px-3 py-1.5 rounded-lg bg-yellow-500/10 text-yellow-400 text-sm font-medium border border-yellow-500/20">
              {pendingCount} pendente{pendingCount > 1 ? 's' : ''}
            </span>
          ) : null}
          <Button 
            onClick={() => { setEditingUser(null); setIsModalOpen(true) }}
            className="w-full sm:w-auto"
          >
            <Plus className="w-4 h-4 mr-2" />
            Novo Usuário
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-3 md:p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 md:w-5 md:h-5 text-[var(--muted)]" />
              <input
                type="text"
                placeholder="Buscar nome ou email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-9 md:pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px]">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Nome</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Email</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Função</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Status</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden md:table-cell">Fiscal</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden lg:table-cell">Cadastrado</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Ações</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="p-6 md:p-8 text-center text-[var(--muted)]">
                    Carregando...
                  </td>
                </tr>
              ) : filteredUsers?.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 md:p-8 text-center text-[var(--muted)]">
                    Nenhum usuário encontrado
                  </td>
                </tr>
              ) : (
                filteredUsers?.map((u) => (
                  <tr key={u.id} className="border-b border-[var(--border)] hover:bg-white/5">
                    <td className="p-3 md:p-4 text-[var(--text)] text-sm md:text-base">{u.nome}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm">{u.email}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm">{getRoleLabel(u.role)}</td>
                    <td className="p-3 md:p-4">{getStatusBadge(u.status)}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm hidden md:table-cell">
                      {u.fiscal_id ? `ID: ${u.fiscal_id}` : '-'}
                    </td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm hidden lg:table-cell">{formatDate(u.created_at)}</td>
                    <td className="p-3 md:p-4">
                      <div className="flex items-center gap-1 md:gap-2">
                        {u.status === 'pending' && (
                          <button 
                            onClick={() => approveMutation.mutate(u.id)}
                            className="p-1.5 md:p-2 rounded-lg hover:bg-green-500/20 text-green-400 transition-colors"
                            title="Aprovar"
                          >
                            <UserCheck className="w-3.5 h-3.5 md:w-4 md:h-4" />
                          </button>
                        )}
                        <button 
                          onClick={() => { setEditingUser(u); setIsModalOpen(true) }}
                          className="p-1.5 md:p-2 rounded-lg hover:bg-white/10 text-[var(--text2)] transition-colors"
                          title="Editar"
                        >
                          <Edit className="w-3.5 h-3.5 md:w-4 md:h-4" />
                        </button>
                        <button 
                          onClick={() => setConfirmDelete({ id: u.id, nome: u.nome })}
                          className="p-1.5 md:p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                          title="Remover"
                        >
                          <Trash2 className="w-3.5 h-3.5 md:w-4 md:h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <UsuarioModal 
        isOpen={isModalOpen} 
        onClose={() => { setIsModalOpen(false); setEditingUser(null) }} 
        user={editingUser}
      />

      <ConfirmModal
        isOpen={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        onConfirm={() => {
          if (confirmDelete) {
            deleteMutation.mutate(confirmDelete.id)
            setConfirmDelete(null)
          }
        }}
        title="Confirmar exclusão"
        message={
          confirmDelete
            ? `Tem certeza que deseja remover "${confirmDelete.nome}"? Esta ação não pode ser desfeita.`
            : ''
        }
        confirmText="Remover"
        cancelText="Cancelar"
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}

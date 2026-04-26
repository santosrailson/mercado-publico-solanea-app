import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, ShieldCheck } from 'lucide-react'
import { ConfirmModal } from '@/components/modals/ConfirmModal'
import toast from 'react-hot-toast'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { FiscalModal } from '@/components/modals/FiscalModal'
import { fiscaisApi } from '@/services/fiscais'
import { Fiscal } from '@/types'

export function FiscaisPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingFiscal, setEditingFiscal] = useState<Fiscal | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<{ id: number; nome: string } | null>(null)
  const limit = 10

  const { data, isLoading } = useQuery({
    queryKey: ['fiscais', search, page],
    queryFn: () => fiscaisApi.list({
      search: search || undefined,
      skip: (page - 1) * limit,
      limit,
    }),
  })

  const deleteMutation = useMutation({
    mutationFn: fiscaisApi.delete,
    onSuccess: () => {
      toast.success('Fiscal removido')
      queryClient.invalidateQueries({ queryKey: ['fiscais'] })
    },
    onError: () => toast.error('Erro ao remover fiscal'),
  })

  const totalPages = data?.pages || 1

  return (
    <div className="space-y-4 md:space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-[var(--text)]">Fiscais</h1>
          <p className="text-sm text-[var(--text2)]">Gerencie os fiscais do mercado</p>
        </div>
        <Button
          onClick={() => { setEditingFiscal(null); setIsModalOpen(true) }}
          className="w-full sm:w-auto"
        >
          <Plus className="w-4 h-4 mr-2" />
          Novo Fiscal
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-3 md:p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 md:w-5 md:h-5 text-[var(--muted)]" />
              <input
                type="text"
                placeholder="Buscar nome ou matrícula..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }}
                className="input pl-9 md:pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px]">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Nome</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden sm:table-cell">Matrícula</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden md:table-cell">Contato</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Status</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Ações</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="p-6 md:p-8 text-center text-[var(--muted)]">
                    Carregando...
                  </td>
                </tr>
              ) : data?.items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-6 md:p-8 text-center text-[var(--muted)]">
                    Nenhum fiscal encontrado
                  </td>
                </tr>
              ) : (
                data?.items.map((f) => (
                  <tr key={f.id} className="border-b border-[var(--border)] hover:bg-white/5">
                    <td className="p-3 md:p-4 text-[var(--text)] text-sm md:text-base">{f.nome}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm hidden sm:table-cell">{f.matricula || '-'}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm hidden md:table-cell">
                      <div>{f.telefone || '-'}</div>
                      <div className="text-xs text-[var(--muted)]">{f.email || ''}</div>
                    </td>
                    <td className="p-3 md:p-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                        f.ativo
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        <ShieldCheck className="w-3 h-3" />
                        {f.ativo ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="p-3 md:p-4">
                      <div className="flex items-center gap-1 md:gap-2">
                        <button
                          onClick={() => { setEditingFiscal(f); setIsModalOpen(true) }}
                          className="p-1.5 md:p-2 rounded-lg hover:bg-white/10 text-[var(--text2)] transition-colors"
                          title="Editar"
                        >
                          <Edit className="w-3.5 h-3.5 md:w-4 md:h-4" />
                        </button>
                        <button
                          onClick={() => setConfirmDelete({ id: f.id, nome: f.nome })}
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

        {/* Paginação */}
        {totalPages > 1 && (
          <div className="flex flex-col sm:flex-row items-center justify-between p-3 md:p-4 border-t border-[var(--border)] gap-3">
            <span className="text-xs md:text-sm text-[var(--text2)]">
              Página {page} de {totalPages}
            </span>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Anterior
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Próxima
              </Button>
            </div>
          </div>
        )}
      </Card>

      <FiscalModal
        isOpen={isModalOpen}
        onClose={() => { setIsModalOpen(false); setEditingFiscal(null) }}
        fiscal={editingFiscal}
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

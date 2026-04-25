import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, FileText } from 'lucide-react'
import { ConfirmModal } from '@/components/modals/ConfirmModal'
import toast from 'react-hot-toast'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { CessionarioModal } from '@/components/modals/CessionarioModal'
import { cessionariosApi } from '@/services/cessionarios'
import { relatoriosApi } from '@/services/relatorios'
import { Cessionario } from '@/types'
import { formatDate } from '@/utils'

export function CessionariosPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [situacao, setSituacao] = useState('')
  const [page, setPage] = useState(1)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCessionario, setEditingCessionario] = useState<Cessionario | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<{ id: number; nome: string } | null>(null)
  const limit = 10

  const { data, isLoading } = useQuery({
    queryKey: ['cessionarios', search, situacao, page],
    queryFn: () => cessionariosApi.list({
      search: search || undefined,
      situacao: situacao || undefined,
      skip: (page - 1) * limit,
      limit,
    }),
  })

  const deleteMutation = useMutation({
    mutationFn: cessionariosApi.delete,
    onSuccess: () => {
      toast.success('Cessionário removido')
      queryClient.invalidateQueries({ queryKey: ['cessionarios'] })
    },
    onError: () => toast.error('Erro ao remover'),
  })

  const handleCertidao = async (cessionario: Cessionario) => {
    try {
      const blob = await relatoriosApi.gerarCertidao(cessionario.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `certidao_${cessionario.nome.replace(/\s+/g, '_').toLowerCase()}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch {
      toast.error('Erro ao gerar certidão')
    }
  }

  const totalPages = data?.pages || 1

  return (
    <div className="space-y-4 md:space-y-6 animate-fade-in">
      {/* Header responsivo */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-[var(--text)]">Cessionários/Feirantes</h1>
          <p className="text-sm text-[var(--text2)]">Gerencie os boxes e pontos do mercado</p>
        </div>
        <Button 
          onClick={() => { setEditingCessionario(null); setIsModalOpen(true) }}
          className="w-full sm:w-auto"
        >
          <Plus className="w-4 h-4 mr-2" />
          Novo Cessionário
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
                placeholder="Buscar nome ou box..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }}
                className="input pl-9 md:pl-10"
              />
            </div>
            <select
              value={situacao}
              onChange={(e) => { setSituacao(e.target.value); setPage(1) }}
              className="input w-full sm:w-48"
            >
              <option value="">Todas situações</option>
              <option value="Regular">Regular</option>
              <option value="Irregular">Irregular</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela responsiva */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px]">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Nome</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Box</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden sm:table-cell">Atividade</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Situação</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden md:table-cell">Cadastrado</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Ações</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="p-6 md:p-8 text-center text-[var(--muted)]">
                    Carregando...
                  </td>
                </tr>
              ) : data?.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-6 md:p-8 text-center text-[var(--muted)]">
                    Nenhum cessionário encontrado
                  </td>
                </tr>
              ) : (
                data?.items.map((c) => (
                  <tr key={c.id} className="border-b border-[var(--border)] hover:bg-white/5">
                    <td className="p-3 md:p-4 text-[var(--text)] text-sm md:text-base">{c.nome}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm">{c.numero_box || '-'}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm hidden sm:table-cell">{c.atividade || '-'}</td>
                    <td className="p-3 md:p-4">
                      <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        c.situacao === 'Regular' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {c.situacao}
                      </span>
                    </td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm hidden md:table-cell">{formatDate(c.created_at)}</td>
                    <td className="p-3 md:p-4">
                      <div className="flex items-center gap-1 md:gap-2">
                        <button 
                          onClick={() => handleCertidao(c)}
                          className="p-1.5 md:p-2 rounded-lg hover:bg-primary-500/20 text-primary-400 transition-colors"
                          title="Gerar Certidão"
                        >
                          <FileText className="w-3.5 h-3.5 md:w-4 md:h-4" />
                        </button>
                        <button 
                          onClick={() => { setEditingCessionario(c); setIsModalOpen(true) }}
                          className="p-1.5 md:p-2 rounded-lg hover:bg-white/10 text-[var(--text2)] transition-colors"
                          title="Editar"
                        >
                          <Edit className="w-3.5 h-3.5 md:w-4 md:h-4" />
                        </button>
                        <button 
                          onClick={() => setConfirmDelete({ id: c.id, nome: c.nome })}
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

      <CessionarioModal 
        isOpen={isModalOpen} 
        onClose={() => { setIsModalOpen(false); setEditingCessionario(null) }} 
        cessionario={editingCessionario}
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

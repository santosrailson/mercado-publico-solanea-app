import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, MessageCircle } from 'lucide-react'
import { ConfirmModal } from '@/components/modals/ConfirmModal'
import toast from 'react-hot-toast'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { PagamentoModal } from '@/components/modals/PagamentoModal'
import { pagamentosApi } from '@/services/pagamentos'
import { Pagamento } from '@/types'
import { formatDate, formatCurrency } from '@/utils'

export function PagamentosPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [periodicidade, setPeriodicidade] = useState('')
  const [page, setPage] = useState(1)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPagamento, setEditingPagamento] = useState<Pagamento | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<{ id: number; nome: string } | null>(null)
  const [confirmWhatsApp, setConfirmWhatsApp] = useState<Pagamento | null>(null)
  const limit = 10

  const { data, isLoading } = useQuery({
    queryKey: ['pagamentos', search, periodicidade, page],
    queryFn: () => pagamentosApi.list({
      search: search || undefined,
      periodicidade: periodicidade || undefined,
      skip: (page - 1) * limit,
      limit,
    }),
  })

  const deleteMutation = useMutation({
    mutationFn: pagamentosApi.delete,
    onSuccess: () => {
      toast.success('Pagamento removido')
      queryClient.invalidateQueries({ queryKey: ['pagamentos'] })
    },
    onError: () => toast.error('Erro ao remover'),
  })

  const handleShareWhatsApp = (pagamento: Pagamento) => {
    const telefone = pagamento.cessionario_telefone
    if (!telefone) {
      toast.error('Cessionário não possui telefone cadastrado')
      return
    }

    // Remove caracteres não numéricos
    const numeroLimpo = telefone.replace(/\D/g, '')
    // Adiciona prefixo 55 se não tiver
    const numeroComDDD = numeroLimpo.startsWith('55') && numeroLimpo.length >= 12
      ? numeroLimpo
      : `55${numeroLimpo}`

    const nome = pagamento.cessionario_nome || 'Cessionário'
    const valor = formatCurrency(pagamento.valor)
    const referencia = pagamento.referencia_mes || pagamento.periodicidade
    const data = formatDate(pagamento.data_pagamento)

    const mensagem = `Olá ${nome}, tudo bem?\n\n` +
      `✅ Confirmamos o recebimento do seu pagamento!\n\n` +
      `💰 Valor: ${valor}\n` +
      `📅 Data: ${data}\n` +
      `📝 Referência: ${referencia}\n\n` +
      `Obrigado pela pontualidade! Qualquer dúvida, estamos à disposição.`

    const url = `https://wa.me/${numeroComDDD}?text=${encodeURIComponent(mensagem)}`
    window.open(url, '_blank')
    setConfirmWhatsApp(null)
  }

  const totalPages = data?.pages || 1

  return (
    <div className="space-y-4 md:space-y-6 animate-fade-in">
      {/* Header responsivo */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-[var(--text)]">Pagamentos</h1>
          <p className="text-sm text-[var(--text2)]">Histórico de pagamentos dos cessionários</p>
        </div>
        <Button 
          onClick={() => { setEditingPagamento(null); setIsModalOpen(true) }}
          className="w-full sm:w-auto"
        >
          <Plus className="w-4 h-4 mr-2" />
          Registrar Pagamento
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
                placeholder="Buscar cessionário..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }}
                className="input pl-9 md:pl-10"
              />
            </div>
            <select
              value={periodicidade}
              onChange={(e) => { setPeriodicidade(e.target.value); setPage(1) }}
              className="input w-full sm:w-48"
            >
              <option value="">Todas periodicidades</option>
              <option value="Mensal">Mensal</option>
              <option value="Semanal">Semanal</option>
              <option value="Quinzenal">Quinzenal</option>
              <option value="Único">Único</option>
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
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Cessionário</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Data</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden sm:table-cell">Periodicidade</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)] hidden md:table-cell">Ref.</th>
                <th className="text-left p-3 md:p-4 text-xs md:text-sm font-medium text-[var(--text2)]">Valor</th>
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
                    Nenhum pagamento encontrado
                  </td>
                </tr>
              ) : (
                data?.items.map((p) => (
                  <tr key={p.id} className="border-b border-[var(--border)] hover:bg-white/5">
                    <td className="p-3 md:p-4 text-[var(--text)] text-sm md:text-base">{p.cessionario_nome}</td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm">{formatDate(p.data_pagamento)}</td>
                    <td className="p-3 md:p-4 hidden sm:table-cell">
                      <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-primary-500/20 text-primary-400">
                        {p.periodicidade}
                      </span>
                    </td>
                    <td className="p-3 md:p-4 text-[var(--text2)] text-sm hidden md:table-cell">{p.referencia_mes || '-'}</td>
                    <td className="p-3 md:p-4 font-medium text-[var(--text)] text-sm md:text-base">
                      {formatCurrency(p.valor)}
                    </td>
                    <td className="p-3 md:p-4">
                      <div className="flex items-center gap-1 md:gap-2">
                        <button
                          onClick={() => setConfirmWhatsApp(p)}
                          className="p-1.5 md:p-2 rounded-lg hover:bg-green-500/20 text-green-400 transition-colors"
                          title="Enviar confirmação via WhatsApp"
                        >
                          <MessageCircle className="w-3.5 h-3.5 md:w-4 md:h-4" />
                        </button>
                        <button
                          onClick={() => { setEditingPagamento(p); setIsModalOpen(true) }}
                          className="p-1.5 md:p-2 rounded-lg hover:bg-white/10 text-[var(--text2)] transition-colors"
                          title="Editar"
                        >
                          <Edit className="w-3.5 h-3.5 md:w-4 md:h-4" />
                        </button>
                        <button
                          onClick={() => setConfirmDelete({ id: p.id, nome: p.cessionario_nome || 'Pagamento' })}
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

      <PagamentoModal 
        isOpen={isModalOpen} 
        onClose={() => { setIsModalOpen(false); setEditingPagamento(null) }} 
        pagamento={editingPagamento}
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
            ? `Tem certeza que deseja remover o pagamento de "${confirmDelete.nome}"? Esta ação não pode ser desfeita.`
            : ''
        }
        confirmText="Remover"
        cancelText="Cancelar"
        isLoading={deleteMutation.isPending}
      />

      <ConfirmModal
        isOpen={!!confirmWhatsApp}
        onClose={() => setConfirmWhatsApp(null)}
        onConfirm={() => {
          if (confirmWhatsApp) {
            handleShareWhatsApp(confirmWhatsApp)
          }
        }}
        title="Enviar confirmação via WhatsApp"
        message={
          confirmWhatsApp
            ? `Deseja enviar a mensagem de confirmação de pagamento para ${confirmWhatsApp.cessionario_nome}${confirmWhatsApp.cessionario_telefone ? ` (${confirmWhatsApp.cessionario_telefone})` : ''}?`
            : ''
        }
        confirmText="Enviar"
        cancelText="Cancelar"
      />
    </div>
  )
}

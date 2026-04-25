import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { FileText, FileSpreadsheet, Download, Calendar } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { relatoriosApi } from '@/services/relatorios'
import { RelatorioTipo, ExportFormato } from '@/types'

const relatorioOptions: { value: RelatorioTipo; label: string; desc: string }[] = [
  { value: 'todos', label: 'Relatório Geral', desc: 'Cessionários, pagamentos e cobrança' },
  { value: 'regulares', label: 'Cessionários Regulares', desc: 'Somente em dia' },
  { value: 'irregulares', label: 'Cessionários Irregulares', desc: 'Somente inadimplentes' },
  { value: 'pagamentos', label: 'Arrecadação por Data', desc: 'Período personalizável' },
  { value: 'cobranca', label: 'Relatório de Cobrança', desc: 'Base de cobrança por box/ponto' },
  { value: 'cessionarios', label: 'Lista de Cessionários', desc: 'Nome, box, valor e periodicidade' },
]

export function RelatoriosPage() {
  const [tipo, setTipo] = useState<RelatorioTipo>('todos')
  const [formato, setFormato] = useState<ExportFormato>('pdf')
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [dataCobranca, setDataCobranca] = useState('')

  const exportMutation = useMutation({
    mutationFn: relatoriosApi.exportar,
    onSuccess: (blob, variables) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const ext = variables.formato === 'pdf' ? 'pdf' : 'xlsx'
      const filename = `relatorio_${tipo}_${new Date().toISOString().split('T')[0]}.${ext}`
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('Relatório gerado com sucesso!')
    },
    onError: () => toast.error('Erro ao gerar relatório'),
  })

  const handleExport = () => {
    exportMutation.mutate({
      tipo,
      formato,
      data_inicio: dataInicio || undefined,
      data_fim: dataFim || undefined,
      data_cobranca: dataCobranca || undefined,
    })
  }

  return (
    <div className="space-y-4 md:space-y-6 animate-fade-in">
      <div>
        <h1 className="text-xl md:text-2xl font-bold text-[var(--text)]">Relatórios</h1>
        <p className="text-sm text-[var(--text2)]">Exporte relatórios consolidados e filtrados</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Tipo de Relatório</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {relatorioOptions.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setTipo(opt.value)}
                  className={`p-4 rounded-xl border text-left transition-all ${
                    tipo === opt.value
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-[var(--border)] hover:bg-white/5'
                  }`}
                >
                  <div className="font-medium text-[var(--text)]">{opt.label}</div>
                  <div className="text-sm text-[var(--text2)]">{opt.desc}</div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Opções de Exportação</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text2)] mb-2">
                Formato
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setFormato('pdf')}
                  className={`flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                    formato === 'pdf'
                      ? 'border-red-500 bg-red-500/10 text-red-400'
                      : 'border-[var(--border)] hover:bg-white/5'
                  }`}
                >
                  <FileText className="w-5 h-5" />
                  PDF
                </button>
                <button
                  onClick={() => setFormato('excel')}
                  className={`flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                    formato === 'excel'
                      ? 'border-green-500 bg-green-500/10 text-green-400'
                      : 'border-[var(--border)] hover:bg-white/5'
                  }`}
                >
                  <FileSpreadsheet className="w-5 h-5" />
                  Excel
                </button>
              </div>
            </div>

            {tipo === 'pagamentos' && (
              <div className="space-y-3">
                <label className="block text-sm font-medium text-[var(--text2)]">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Período (opcional)
                </label>
                <input
                  type="date"
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                  className="input"
                  placeholder="Data inicial"
                />
                <input
                  type="date"
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                  className="input"
                  placeholder="Data final"
                />
              </div>
            )}

            {tipo === 'cobranca' && (
              <div className="space-y-3">
                <label className="block text-sm font-medium text-[var(--text2)]">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Data da Cobrança (opcional)
                </label>
                <input
                  type="date"
                  value={dataCobranca}
                  onChange={(e) => setDataCobranca(e.target.value)}
                  className="input"
                  placeholder="Data da cobrança"
                />
                <p className="text-xs text-[var(--text2)]">
                  Se não informada, será usada a data atual nos recibos.
                </p>
              </div>
            )}

            <Button
              onClick={handleExport}
              isLoading={exportMutation.isPending}
              className="w-full"
            >
              <Download className="w-4 h-4 mr-2" />
              {formato === 'pdf' ? 'Gerar PDF' : 'Gerar Excel'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

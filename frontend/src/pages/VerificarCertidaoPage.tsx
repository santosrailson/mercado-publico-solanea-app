import { useState } from 'react'
import { Search, ShieldCheck, ShieldAlert, Store } from 'lucide-react'
import api from '@/services/api'

interface VerificacaoResult {
  valido: boolean
  mensagem: string
  cessionario_nome?: string
  numero_box?: string
  situacao?: string
  data_emissao?: string
  data_validade?: string
  codigo?: string
}

export function VerificarCertidaoPage() {
  const [codigo, setCodigo] = useState('')
  const [resultado, setResultado] = useState<VerificacaoResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleVerificar = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!codigo.trim()) {
      setError('Digite o código de verificação')
      return
    }

    setIsLoading(true)
    setError('')
    setResultado(null)

    try {
      const { data } = await api.get(`/relatorios/verificar-certidao/${codigo.trim()}`)
      setResultado(data)
    } catch {
      setError('Erro ao verificar o código. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--bg)] flex flex-col">
      {/* Header */}
      <header className="bg-[var(--surface)] border-b border-[var(--border)] py-4 px-4 md:px-8">
        <div className="max-w-2xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary-500/20 flex items-center justify-center">
            <Store className="w-5 h-5 text-primary-500" />
          </div>
          <div>
            <h1 className="font-semibold text-[var(--text)] text-lg">Mercado Público de Solânea</h1>
            <p className="text-xs text-[var(--muted)]">Verificação de Certidão</p>
          </div>
        </div>
      </header>

      {/* Conteúdo */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-lg space-y-6">
          {/* Formulário */}
          <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6 md:p-8 shadow-sm">
            <div className="text-center mb-6">
              <div className="w-14 h-14 rounded-full bg-primary-500/10 flex items-center justify-center mx-auto mb-3">
                <ShieldCheck className="w-7 h-7 text-primary-500" />
              </div>
              <h2 className="text-xl font-bold text-[var(--text)]">Verificar Autenticidade</h2>
              <p className="text-sm text-[var(--text2)] mt-1">
                Digite o código de verificação do documento para confirmar se é autêntico.
              </p>
            </div>

            <form onSubmit={handleVerificar} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text2)] mb-1.5">
                  Código de Verificação
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
                  <input
                    type="text"
                    value={codigo}
                    onChange={(e) => setCodigo(e.target.value.toUpperCase())}
                    placeholder="ex: SOL-AB12-CD34-EF56"
                    className="input pl-9 w-full uppercase tracking-wider"
                  />
                </div>
              </div>

              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 text-red-400 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2.5 px-4 rounded-lg bg-primary-500 text-white font-medium hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Verificando...' : 'Verificar Documento'}
              </button>
            </form>
          </div>

          {/* Resultado */}
          {resultado && (
            <div
              className={`rounded-xl p-6 border ${
                resultado.valido
                  ? 'bg-green-500/5 border-green-500/30'
                  : 'bg-red-500/5 border-red-500/30'
              }`}
            >
              <div className="flex items-start gap-3">
                {resultado.valido ? (
                  <ShieldCheck className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                ) : (
                  <ShieldAlert className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <h3
                    className={`font-semibold ${
                      resultado.valido ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {resultado.valido ? 'Documento Autêntico' : 'Documento Não Encontrado'}
                  </h3>
                  <p className="text-sm text-[var(--text2)] mt-1">{resultado.mensagem}</p>

                  {resultado.valido && resultado.cessionario_nome && (
                    <div className="mt-4 pt-4 border-t border-[var(--border)] space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-[var(--text2)]">Cessionário:</span>
                        <span className="text-[var(--text)] font-medium">{resultado.cessionario_nome}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-[var(--text2)]">Box/Ponto:</span>
                        <span className="text-[var(--text)] font-medium">{resultado.numero_box || '-'}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-[var(--text2)]">Situação:</span>
                        <span
                          className={`font-medium ${
                            resultado.situacao === 'Regular' ? 'text-green-400' : 'text-red-400'
                          }`}
                        >
                          {resultado.situacao}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-[var(--text2)]">Emitido em:</span>
                        <span className="text-[var(--text)] font-medium">
                          {resultado.data_emissao
                            ? new Date(resultado.data_emissao).toLocaleString('pt-BR')
                            : '-'}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-[var(--text2)]">Válida até:</span>
                        <span className="text-[var(--text)] font-medium">
                          {resultado.data_validade
                            ? new Date(resultado.data_validade).toLocaleDateString('pt-BR')
                            : '-'}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-[var(--text2)]">Código:</span>
                        <span className="text-[var(--text)] font-medium font-mono">{resultado.codigo}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Rodapé */}
      <footer className="py-4 text-center text-xs text-[var(--muted)]">
        Prefeitura Municipal de Solânea - PB
      </footer>
    </div>
  )
}

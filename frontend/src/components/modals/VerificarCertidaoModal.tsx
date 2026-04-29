import { useState } from 'react'
import { Search, ShieldCheck, ShieldAlert } from 'lucide-react'
import { Modal } from '@/components/ui/Modal'
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

interface VerificarCertidaoModalProps {
  isOpen: boolean
  onClose: () => void
}

export function VerificarCertidaoModal({ isOpen, onClose }: VerificarCertidaoModalProps) {
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

  const handleClose = () => {
    setCodigo('')
    setResultado(null)
    setError('')
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Verificar Autenticidade">
      <div className="space-y-4">
        <p className="text-sm text-[var(--text2)]">
          Digite o código de verificação do documento para confirmar se é autêntico.
        </p>

        <form onSubmit={handleVerificar} className="space-y-3">
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

        {resultado && (
          <div
            className={`rounded-xl p-4 border ${
              resultado.valido
                ? 'bg-green-500/5 border-green-500/30'
                : 'bg-red-500/5 border-red-500/30'
            }`}
          >
            <div className="flex items-start gap-3">
              {resultado.valido ? (
                <ShieldCheck className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              ) : (
                <ShieldAlert className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <h3
                  className={`font-semibold text-sm ${
                    resultado.valido ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {resultado.valido ? 'Documento Autêntico' : 'Documento Não Encontrado'}
                </h3>
                <p className="text-xs text-[var(--text2)] mt-0.5">{resultado.mensagem}</p>

                {resultado.valido && resultado.cessionario_nome && (
                  <div className="mt-3 pt-3 border-t border-[var(--border)] space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-[var(--text2)]">Cessionário:</span>
                      <span className="text-[var(--text)] font-medium">{resultado.cessionario_nome}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-[var(--text2)]">Box/Ponto:</span>
                      <span className="text-[var(--text)] font-medium">{resultado.numero_box || '-'}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-[var(--text2)]">Situação:</span>
                      <span
                        className={`font-medium ${
                          resultado.situacao === 'Regular' ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {resultado.situacao}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-[var(--text2)]">Emitido em:</span>
                      <span className="text-[var(--text)] font-medium">
                        {resultado.data_emissao
                          ? new Date(resultado.data_emissao).toLocaleString('pt-BR')
                          : '-'}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-[var(--text2)]">Válida até:</span>
                      <span className="text-[var(--text)] font-medium">
                        {resultado.data_validade
                          ? new Date(resultado.data_validade).toLocaleDateString('pt-BR')
                          : '-'}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
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
    </Modal>
  )
}

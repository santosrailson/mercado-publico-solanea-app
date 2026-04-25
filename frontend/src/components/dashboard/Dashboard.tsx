import { useQuery } from '@tanstack/react-query'
import { Users, UserCheck, UserX, DollarSign } from 'lucide-react'
import { KPICard } from './KPICard'
import { ChartsSection } from './ChartsSection'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { dashboardApi } from '@/services/dashboard'
import { formatCurrency } from '@/utils'

export function Dashboard() {
  const { data: kpis } = useQuery({
    queryKey: ['dashboard', 'kpis'],
    queryFn: dashboardApi.getKPIs,
  })

  const { data: topCessionarios } = useQuery({
    queryKey: ['dashboard', 'top-cessionarios'],
    queryFn: () => dashboardApi.getTopCessionarios(5),
  })

  return (
    <div className="space-y-4 md:space-y-6 animate-fade-in">
      {/* KPIs - Grid responsivo */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3 md:gap-4">
        <KPICard
          title="Total Cessionários"
          value={kpis?.total_cessionarios || 0}
          icon={<Users className="w-5 h-5 md:w-6 md:h-6" />}
        />
        <KPICard
          title="Regulares"
          value={kpis?.total_regulares || 0}
          icon={<UserCheck className="w-5 h-5 md:w-6 md:h-6" />}
        />
        <KPICard
          title="Irregulares"
          value={kpis?.total_irregulares || 0}
          icon={<UserX className="w-5 h-5 md:w-6 md:h-6" />}
        />
        <KPICard
          title="Arrecadação Mês"
          value={formatCurrency(kpis?.total_pagamentos_mes || 0)}
          icon={<DollarSign className="w-5 h-5 md:w-6 md:h-6" />}
        />
        <KPICard
          title="Arrecadação Semana"
          value={formatCurrency(kpis?.total_pagamentos_semana || 0)}
          icon={<DollarSign className="w-5 h-5 md:w-6 md:h-6" />}
        />
      </div>

      {/* Charts */}
      <ChartsSection />

      {/* Bottom Section - Grid responsivo */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 md:gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Cessionários</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 md:space-y-3">
              {topCessionarios?.map((c, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-2 md:p-3 rounded-lg bg-[var(--surface2)]"
                >
                  <div className="min-w-0 flex-1 mr-4">
                    <p className="font-medium text-[var(--text)] text-sm md:text-base truncate">{c.nome}</p>
                    <p className="text-xs md:text-sm text-[var(--muted)]">Box: {c.box}</p>
                  </div>
                  <span className="font-semibold text-primary-400 text-sm md:text-base whitespace-nowrap">
                    {formatCurrency(c.total)}
                  </span>
                </div>
              ))}
              {(!topCessionarios || topCessionarios.length === 0) && (
                <p className="text-center text-[var(--muted)] py-4">Nenhum dado disponível</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Central de Relatórios</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs md:text-sm text-[var(--text2)] mb-4">
              Exporte relatórios consolidados, relatórios filtrados por situação, 
              arrecadação por período, relatório de cobrança e lista de cessionários.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <a 
                href="/relatorios" 
                className="p-3 rounded-lg bg-[var(--surface2)] hover:bg-[var(--surface3)] transition-colors text-center"
              >
                <span className="text-sm font-medium text-[var(--text)]">Ver Relatórios</span>
              </a>
              <a 
                href="/cessionarios" 
                className="p-3 rounded-lg bg-[var(--surface2)] hover:bg-[var(--surface3)] transition-colors text-center"
              >
                <span className="text-sm font-medium text-[var(--text)]">Cessionários</span>
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

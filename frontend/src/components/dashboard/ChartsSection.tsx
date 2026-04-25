import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { dashboardApi } from '@/services/dashboard'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

const COLORS = ['#00c896', '#ef4444', '#f59e0b', '#8b5cf6']

// Tooltip customizado para o gráfico de pizza
function CustomPieTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    const data = payload[0]
    return (
      <div 
        className="px-3 py-2 rounded-lg shadow-lg border"
        style={{ 
          backgroundColor: 'var(--surface)', 
          borderColor: 'var(--border)',
          color: 'var(--text)'
        }}
      >
        <p className="font-medium" style={{ color: 'var(--text)' }}>
          {data.name}
        </p>
        <p style={{ color: 'var(--text2)' }}>
          Quantidade: <span className="font-semibold" style={{ color: data.payload.fill }}>{data.value}</span>
        </p>
      </div>
    )
  }
  return null
}

// Tooltip customizado para o gráfico de barras
function CustomBarTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div 
        className="px-3 py-2 rounded-lg shadow-lg border"
        style={{ 
          backgroundColor: 'var(--surface)', 
          borderColor: 'var(--border)',
          color: 'var(--text)'
        }}
      >
        <p className="font-medium mb-1" style={{ color: 'var(--text)' }}>
          {label}
        </p>
        <p style={{ color: 'var(--text2)' }}>
          Valor: <span className="font-semibold text-primary-400">
            R$ {Number(payload[0].value).toFixed(2)}
          </span>
        </p>
      </div>
    )
  }
  return null
}

export function ChartsSection() {
  const { data: arrecadacaoData } = useQuery({
    queryKey: ['dashboard', 'arrecadacao'],
    queryFn: dashboardApi.getArrecadacaoChart,
  })

  const { data: situacaoData } = useQuery({
    queryKey: ['dashboard', 'situacao'],
    queryFn: dashboardApi.getSituacaoChart,
  })

  const barData = arrecadacaoData?.labels.map((label, index) => ({
    name: label,
    value: arrecadacaoData.values[index],
  })) || []

  const pieData = situacaoData?.labels.map((label, index) => ({
    name: label,
    value: situacaoData.values[index],
  })) || []

  return (
    <div className="charts-grid">
      <Card>
        <CardHeader>
          <CardTitle>Arrecadação Mensal</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis 
                dataKey="name" 
                stroke="var(--text2)"
                fontSize={12}
                tick={{ fill: 'var(--text2)' }}
              />
              <YAxis 
                stroke="var(--text2)"
                fontSize={12}
                tick={{ fill: 'var(--text2)' }}
                tickFormatter={(value) => `R$ ${value}`}
              />
              <Tooltip content={<CustomBarTooltip />} />
              <Bar dataKey="value" fill="#00c896" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Situação dos Cessionários</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomPieTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap justify-center gap-3 md:gap-4 mt-4">
            {pieData.map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-sm text-[var(--text2)]">
                  {entry.name}: {entry.value}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

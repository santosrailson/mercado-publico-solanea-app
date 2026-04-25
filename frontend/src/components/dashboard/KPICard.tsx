import { ReactNode } from 'react'
import { cn } from '@/utils'

interface KPICardProps {
  title: string
  value: string | number
  icon: ReactNode
  trend?: string
  trendUp?: boolean
  className?: string
}

export function KPICard({ title, value, icon, trend, trendUp, className }: KPICardProps) {
  return (
    <div className={cn('kpi-card', className)}>
      <div className="kpi-icon">
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs md:text-sm text-[var(--text2)] truncate">{title}</p>
        <p className="text-lg md:text-2xl font-bold text-[var(--text)] truncate">{value}</p>
        {trend && (
          <p className={cn(
            'text-xs',
            trendUp ? 'text-green-400' : 'text-red-400'
          )}>
            {trend}
          </p>
        )}
      </div>
    </div>
  )
}

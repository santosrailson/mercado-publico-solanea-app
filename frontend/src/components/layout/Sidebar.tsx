import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  CreditCard,
  FileText,
  LogOut,
  Store,
  X,
  ShieldCheck,
} from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { cn } from '@/utils'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const baseNavItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/cessionarios', icon: Users, label: 'Cessionários' },
  { path: '/pagamentos', icon: CreditCard, label: 'Pagamentos' },
  { path: '/relatorios', icon: FileText, label: 'Relatórios' },
]

const adminNavItems = [
  { path: '/fiscais', icon: ShieldCheck, label: 'Fiscais' },
]

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const logout = useAuthStore((state) => state.logout)
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'
  const navItems = isAdmin ? [...baseNavItems, ...adminNavItems] : baseNavItems

  return (
    <>
      {/* Overlay para mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar - agora usa variáveis CSS do tema */}
      <aside className={cn(
        "fixed left-0 top-0 h-full w-64 z-50",
        "bg-[var(--surface)] border-r border-[var(--border)]",
        "transform transition-transform duration-300 ease-in-out",
        "lg:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        {/* Brand */}
        <div className="p-4 md:p-6 border-b border-[var(--border)] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-xl bg-primary-500/20 flex items-center justify-center">
              <Store className="w-4 h-4 md:w-5 md:h-5 text-primary-500" />
            </div>
            <div>
              <h1 className="font-semibold text-[var(--text)] text-sm md:text-base">Mercado Público</h1>
              <p className="text-xs text-[var(--muted)]">Solânea - PB</p>
            </div>
          </div>
          {/* Botão fechar no mobile */}
          <button 
            onClick={onClose}
            className="lg:hidden p-2 text-[var(--text2)] hover:text-[var(--text)]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1">
          <p className="px-4 text-xs font-medium text-[var(--muted)] uppercase tracking-wider mb-2">
            Menu
          </p>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 md:px-4 py-2.5 md:py-3 rounded-lg mx-2",
                  "text-[var(--text2)] transition-all text-sm md:text-base",
                  "hover:bg-[var(--surface2)] hover:text-[var(--text)]",
                  isActive && "bg-primary-500/10 text-primary-600 border border-primary-500/30"
                )
              }
            >
              <item.icon className="w-4 h-4 md:w-5 md:h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-[var(--border)]">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-500 font-semibold text-sm md:text-base">
              {user?.nome?.charAt(0).toUpperCase() || '?'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[var(--text)] truncate">
                {user?.nome}
              </p>
              <p className="text-xs text-[var(--muted)] capitalize">
                {user?.role}
              </p>
            </div>
          </div>
          
          <button
            onClick={logout}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[var(--text2)] hover:text-red-500 transition-colors rounded-lg hover:bg-[var(--surface2)]"
          >
            <LogOut className="w-4 h-4" />
            Sair
          </button>
        </div>
      </aside>
    </>
  )
}

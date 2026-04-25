import { Sun, Moon, Bell, Menu } from 'lucide-react'
import { useThemeStore } from '@/store/theme'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { isDark, toggleTheme } = useThemeStore()

  return (
    <header className="sticky top-0 z-30 bg-[var(--surface)]/95 backdrop-blur-md border-b border-[var(--border)]">
      <div className="flex items-center justify-between h-14 md:h-16 px-4 md:px-6">
        {/* Lado esquerdo */}
        <div className="flex items-center gap-3">
          {/* Botão menu hamburger - só aparece em mobile */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-[var(--surface2)] text-[var(--text2)] transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
          <h2 className="text-base md:text-lg font-semibold text-[var(--text)]">
            Sistema de Gestão
          </h2>
        </div>
        
        {/* Lado direito */}
        <div className="flex items-center gap-2 md:gap-3">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-[var(--surface2)] text-[var(--text2)] transition-all"
            title={isDark ? 'Mudar para modo claro' : 'Mudar para modo escuro'}
          >
            {isDark ? <Sun className="w-4 h-4 md:w-5 md:h-5" /> : <Moon className="w-4 h-4 md:w-5 md:h-5" />}
          </button>
          
          <button className="p-2 rounded-lg hover:bg-[var(--surface2)] text-[var(--text2)] transition-all relative">
            <Bell className="w-4 h-4 md:w-5 md:h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full" />
          </button>
        </div>
      </div>
    </header>
  )
}

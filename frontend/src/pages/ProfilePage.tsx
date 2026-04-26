import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { KeyRound, User, Save, Lock } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useAuthStore } from '@/store/auth'
import { usersApi } from '@/services/users'

export function ProfilePage() {
  const currentUser = useAuthStore((state) => state.user)
  const setAuth = useAuthStore((state) => state.setAuth)
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile')

  const [profileData, setProfileData] = useState({
    nome: currentUser?.nome || '',
    email: currentUser?.email || '',
  })

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  const updateProfileMutation = useMutation({
    mutationFn: usersApi.updateProfile,
    onSuccess: (updatedUser) => {
      // Atualiza o usuário na store mantendo o token
      const token = useAuthStore.getState().token
      if (token) {
        setAuth({
          access_token: token,
          token_type: 'bearer',
          user: updatedUser,
        })
      }
      toast.success('Perfil atualizado com sucesso!')
    },
    onError: () => toast.error('Erro ao atualizar perfil'),
  })

  const changePasswordMutation = useMutation({
    mutationFn: usersApi.changePassword,
    onSuccess: () => {
      toast.success('Senha alterada com sucesso!')
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erro ao alterar senha'
      toast.error(message)
    },
  })

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!profileData.nome.trim()) {
      toast.error('Nome é obrigatório')
      return
    }
    if (!profileData.email.trim()) {
      toast.error('Email é obrigatório')
      return
    }
    updateProfileMutation.mutate(profileData)
  }

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!passwordData.current_password) {
      toast.error('Digite sua senha atual')
      return
    }
    if (!passwordData.new_password) {
      toast.error('Digite a nova senha')
      return
    }
    if (passwordData.new_password.length < 6) {
      toast.error('A nova senha deve ter pelo menos 6 caracteres')
      return
    }
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('As senhas não coincidem')
      return
    }
    changePasswordMutation.mutate({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password,
    })
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--text)]">Meu Perfil</h1>
        <p className="text-[var(--muted)] mt-1">
          Gerencie suas informações pessoais e senha
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('profile')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'profile'
              ? 'bg-primary-500 text-white'
              : 'bg-[var(--surface2)] text-[var(--text2)] hover:text-[var(--text)]'
          }`}
        >
          <User className="w-4 h-4" />
          Dados Pessoais
        </button>
        <button
          onClick={() => setActiveTab('password')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'password'
              ? 'bg-primary-500 text-white'
              : 'bg-[var(--surface2)] text-[var(--text2)] hover:text-[var(--text)]'
          }`}
        >
          <KeyRound className="w-4 h-4" />
          Alterar Senha
        </button>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-[var(--surface)] rounded-xl border border-[var(--border)] p-6">
          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text2)] mb-1">
                Nome completo
              </label>
              <input
                type="text"
                value={profileData.nome}
                onChange={(e) => setProfileData({ ...profileData, nome: e.target.value })}
                className="input"
                placeholder="Seu nome"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text2)] mb-1">
                Email
              </label>
              <input
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                className="input"
                placeholder="seu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text2)] mb-1">
                Função
              </label>
              <input
                type="text"
                value={currentUser?.role || ''}
                disabled
                className="input bg-[var(--surface2)] opacity-60 cursor-not-allowed"
              />
              <p className="text-xs text-[var(--muted)] mt-1">
                A função só pode ser alterada por um administrador
              </p>
            </div>

            <div className="pt-4">
              <Button
                type="submit"
                isLoading={updateProfileMutation.isPending}
                className="flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Salvar Alterações
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <div className="bg-[var(--surface)] rounded-xl border border-[var(--border)] p-6">
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text2)] mb-1">
                Senha Atual
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  className="input pl-10"
                  placeholder="••••••"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text2)] mb-1">
                Nova Senha
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  className="input pl-10"
                  placeholder="••••••"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text2)] mb-1">
                Confirmar Nova Senha
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  className="input pl-10"
                  placeholder="••••••"
                />
              </div>
            </div>

            <div className="pt-4">
              <Button
                type="submit"
                isLoading={changePasswordMutation.isPending}
                className="flex items-center gap-2"
              >
                <KeyRound className="w-4 h-4" />
                Alterar Senha
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}

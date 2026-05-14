import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { useInactivityLogout } from '@/hooks/useInactivityLogout'
import { Layout } from '@/components/layout/Layout'

// Lazy loaded pages
const Dashboard = lazy(() => import('@/components/dashboard/Dashboard').then(m => ({ default: m.Dashboard })))
const LoginPage = lazy(() => import('@/pages/LoginPage').then(m => ({ default: m.LoginPage })))
const CessionariosPage = lazy(() => import('@/pages/CessionariosPage').then(m => ({ default: m.CessionariosPage })))
const PagamentosPage = lazy(() => import('@/pages/PagamentosPage').then(m => ({ default: m.PagamentosPage })))
const RelatoriosPage = lazy(() => import('@/pages/RelatoriosPage').then(m => ({ default: m.RelatoriosPage })))
const FiscaisPage = lazy(() => import('@/pages/FiscaisPage').then(m => ({ default: m.FiscaisPage })))
const UsuariosPage = lazy(() => import('@/pages/UsuariosPage').then(m => ({ default: m.UsuariosPage })))
const ProfilePage = lazy(() => import('@/pages/ProfilePage').then(m => ({ default: m.ProfilePage })))
const VerificarCertidaoPage = lazy(() => import('@/pages/VerificarCertidaoPage').then(m => ({ default: m.VerificarCertidaoPage })))

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[50vh]">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
  </div>
)

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  useInactivityLogout()

  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/cessionarios"
        element={
          <PrivateRoute>
            <Layout>
              <CessionariosPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/pagamentos"
        element={
          <PrivateRoute>
            <Layout>
              <PagamentosPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/relatorios"
        element={
          <PrivateRoute>
            <Layout>
              <RelatoriosPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/fiscais"
        element={
          <PrivateRoute>
            <Layout>
              <FiscaisPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/usuarios"
        element={
          <PrivateRoute>
            <Layout>
              <UsuariosPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/perfil"
        element={
          <PrivateRoute>
            <Layout>
              <ProfilePage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route path="/verificar-certidao" element={<VerificarCertidaoPage />} />
    </Routes>
    </Suspense>
  )
}

export default App

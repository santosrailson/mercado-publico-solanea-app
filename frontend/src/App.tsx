import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/components/dashboard/Dashboard'
import { LoginPage } from '@/pages/LoginPage'
import { CessionariosPage } from '@/pages/CessionariosPage'
import { PagamentosPage } from '@/pages/PagamentosPage'
import { RelatoriosPage } from '@/pages/RelatoriosPage'
import { FiscaisPage } from '@/pages/FiscaisPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
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
    </Routes>
  )
}

export default App

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Runs from './pages/Runs'
import RunDetail from './pages/RunDetail'
import NewRun from './pages/NewRun'
import Projects from './pages/Projects'
import ProjectFeatures from './pages/ProjectFeatures'
import Infrastructure from './pages/Infrastructure'
import Configuration from './pages/Configuration'
import Login from './pages/Login'
import { useAuthStore } from './store/authStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Layout>
                  <Dashboard />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/runs"
            element={
              isAuthenticated ? (
                <Layout>
                  <Runs />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/runs/new"
            element={
              isAuthenticated ? (
                <Layout>
                  <NewRun />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/runs/:runId"
            element={
              isAuthenticated ? (
                <Layout>
                  <RunDetail />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/projects"
            element={
              isAuthenticated ? (
                <Layout>
                  <Projects />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/projects/:projectId/features"
            element={
              isAuthenticated ? (
                <Layout>
                  <ProjectFeatures />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/infrastructure"
            element={
              isAuthenticated ? (
                <Layout>
                  <Infrastructure />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/configuration"
            element={
              isAuthenticated ? (
                <Layout>
                  <Configuration />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

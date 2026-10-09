import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout           from './layouts/AppLayout'
import DashboardPage       from './pages/DashboardPage'
import CasesPage           from './pages/CasesPage'
import CaseWorkspacePage   from './pages/CaseWorkspacePage'
import LoadingScreen       from './components/LoadingScreen'

export default function App() {
  const [ready, setReady] = useState(false)

  return (
    <>
      {/* Boot splash — fades out after ~2 s */}
      {!ready && <LoadingScreen onReady={() => setReady(true)} />}

      {/* Main application — rendered behind the splash, visible once ready */}
      <div style={{ visibility: ready ? 'visible' : 'hidden' }}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<AppLayout />}>
              <Route index                  element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard"       element={<DashboardPage />} />
              <Route path="cases"           element={<CasesPage />} />
              <Route path="cases/:caseId/*" element={<CaseWorkspacePage />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </div>
    </>
  )
}

import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom'
import { HandoffButton, HandoffProvider } from './components/HumanHandoff.jsx'
import Dashboard from './pages/Dashboard.jsx'
import PersonaPicker from './pages/PersonaPicker.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <HandoffProvider>
        {/* On every screen, so a human is always one click away (NM-20) */}
        <header className="app-bar">
          <Link to="/" className="wordmark">
            Next Move
          </Link>
          <HandoffButton />
        </header>
        <Routes>
          <Route path="/" element={<PersonaPicker />} />
          <Route path="/customer/:id" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </HandoffProvider>
    </BrowserRouter>
  )
}

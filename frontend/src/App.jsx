import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Preview from './pages/Preview'
import History from './pages/History'
import Settings from './pages/Settings'
import './App.css'

function Layout({ children }) {
  const now = new Date()
  const dateStr = now.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-brand-badge">
            <span>✈</span>
            <span>Defence &amp; Aerospace AI</span>
          </div>

          <div className="brand-row">
            <div className="logo-container">
              <img src="/hal_logo.jpg" alt="HAL Official Logo" />
            </div>
            <div className="brand-text">
              <div className="brand-title">HAL AI Tools</div>
              <div className="brand-subtitle">
                <span>Weekly Newsletter</span>
                <span className="brand-tag-cpse">· CPSE</span>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="sidebar-nav">
          <div className="nav-section-title">Workspace</div>
          <NavLink to="/" end className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            <span className="nav-icon">⚡</span>
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            <span className="nav-icon">📚</span>
            <span>Issue Archive</span>
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            <span className="nav-icon">⚙️</span>
            <span>System Settings</span>
          </NavLink>
        </nav>

        {/* Sidebar Footer with Live Status */}
        <div className="sidebar-footer">
          <div className="system-status-pill">
            <div className="status-indicator-dot" />
            <div className="status-text-block">
              <div className="status-label">Engine Ready</div>
              <div className="status-sub">Gemini 3.1 Flash Active</div>
            </div>
          </div>
          <div className="sidebar-org-text">
            <strong>Hindustan Aeronautics Ltd</strong>
            <div>Internal Enterprise Edition</div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <div className="topbar-tag">
              <span>📅</span>
              <span>{dateStr}</span>
            </div>
            <div className="topbar-edition">
              <span>A4 3-PAGE PRINT READY</span>
            </div>
          </div>
          <div className="topbar-right">
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Security Tier:</span>
            <span className="badge badge-navy">RESTRICTED INTERNAL</span>
          </div>
        </header>

        {children}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/preview/:id" element={<Preview />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

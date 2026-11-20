import { useState, useEffect } from 'react'
import { settingsApi } from '../services/api'
import './Settings.css'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function Settings() {
  const [form, setForm] = useState({
    gemini_api_key: '',
    search_api_key: '',
    search_engine: 'duckduckgo',
    schedule_day: 'Monday',
    schedule_time: '09:00',
    hal_newsletter_title: 'HAL AI Tools Weekly',
    admin_email: '',
    smtp_host: 'smtp.gmail.com',
    smtp_port: '587',
    smtp_user: '',
    smtp_password: '',
    base_url: 'http://localhost:8000',
    gemini_configured: false,
    search_api_configured: false,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)
  const [copied, setCopied] = useState(false)
  const [showGeminiKey, setShowGeminiKey] = useState(false)

  useEffect(() => {
    settingsApi.get()
      .then(res => {
        setForm(f => ({ ...f, ...res.data }))
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await settingsApi.update(form)
      showToast('Settings saved to config/.env successfully!', 'success')
      const res = await settingsApi.get()
      setForm(f => ({ ...f, ...res.data }))
    } catch (err) {
      showToast('Failed to save: ' + (err.response?.data?.detail || err.message), 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleCopyCmd = () => {
    const cmd = `d:\\Hobby\\AI_NEWSLETTER\\venv\\Scripts\\python.exe d:\\Hobby\\AI_NEWSLETTER\\backend\\scheduler\\auto_generate.py --template modern`
    navigator.clipboard.writeText(cmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 2500)
  }

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }))

  if (loading) {
    return (
      <div className="settings-loading-screen">
        <span className="spinner spinner-dark" />
        <span>Loading system configurations…</span>
      </div>
    )
  }

  return (
    <div className="settings-container">
      {/* Toast */}
      {toast && (
        <div className="toast-container">
          <div className={`toast toast-${toast.type}`}>
            <span>{toast.type === 'success' ? '✓' : '⚠️'}</span>
            <span>{toast.msg}</span>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="settings-header-row">
        <div>
          <div className="dash-breadcrumb">
            <span>AEROSPACE SYSTEM</span>
            <span>/</span>
            <span className="active">CONFIGURATION</span>
          </div>
          <h1 className="settings-heading">System &amp; Pipeline Settings</h1>
          <p className="settings-subheading">
            Manage your Gemini API keys, search providers, automated Windows scheduler, and publication defaults.
          </p>
        </div>
      </div>

      <form className="settings-form" onSubmit={handleSave}>

        {/* Section 1: AI Engines & API Keys */}
        <div className="settings-card">
          <div className="card-section-header">
            <div className="sec-icon-wrap">🔑</div>
            <div>
              <h2 className="sec-title">AI Engine &amp; API Keys</h2>
              <p className="sec-desc">Configure the primary LLM credentials and web search parameters.</p>
            </div>
          </div>

          <div className="card-fields-grid">
            <div className="form-group">
              <div className="label-row">
                <label className="form-label">Gemini API Key</label>
                {form.gemini_configured ? (
                  <span className="badge badge-green">✓ Active &amp; Verified</span>
                ) : (
                  <span className="badge badge-orange">Key Required</span>
                )}
              </div>
              <div className="input-with-action">
                <input
                  type={showGeminiKey ? 'text' : 'password'}
                  className="form-input"
                  value={form.gemini_api_key}
                  onChange={set('gemini_api_key')}
                  placeholder="Paste your Google Gemini API key (AIzaSy…)"
                  autoComplete="off"
                />
                <button
                  type="button"
                  className="toggle-vis-btn"
                  onClick={() => setShowGeminiKey(v => !v)}
                  title={showGeminiKey ? 'Hide key' : 'Show key'}
                >
                  {showGeminiKey ? '🙈' : '👁️'}
                </button>
              </div>
              <div className="form-hint">
                Prioritizes <strong>gemini-3.1-flash-lite</strong> for high free-tier rate limits and rapid execution. Get keys at{' '}
                <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">
                  aistudio.google.com
                </a>
              </div>
            </div>

            <div className="form-group">
              <div className="label-row">
                <label className="form-label">Search API Key (SerpAPI — Optional)</label>
                {form.search_api_configured && (
                  <span className="badge badge-green">✓ Configured</span>
                )}
              </div>
              <input
                type="password"
                className="form-input"
                value={form.search_api_key}
                onChange={set('search_api_key')}
                placeholder="Leave blank to use verified enterprise catalog & DuckDuckGo"
                autoComplete="off"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Primary Discovery Provider</label>
              <select className="form-select" value={form.search_engine} onChange={set('search_engine')}>
                <option value="duckduckgo">Gemini Discovery + Verified Enterprise Aerospace Catalog (Default)</option>
                <option value="serpapi">SerpAPI (Requires SerpAPI Key)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Automated Schedule (Windows Task Scheduler) */}
        <div className="settings-card">
          <div className="card-section-header">
            <div className="sec-icon-wrap">🗓️</div>
            <div>
              <h2 className="sec-title">Weekly Automation Schedule</h2>
              <p className="sec-desc">Configure automated execution cadence via Windows Task Scheduler.</p>
            </div>
          </div>

          <div className="card-fields-grid">
            <div className="two-col-row">
              <div className="form-group">
                <label className="form-label">Publication Day of Week</label>
                <select className="form-select" value={form.schedule_day} onChange={set('schedule_day')}>
                  {DAYS.map(d => <option key={d}>{d}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Target Execution Time</label>
                <input
                  type="time"
                  className="form-input"
                  value={form.schedule_time}
                  onChange={set('schedule_time')}
                />
              </div>
            </div>

            <div className="schedule-command-box">
              <div className="cmd-header">
                <span>⚡ Windows Task Scheduler Execution Command:</span>
                <button
                  type="button"
                  className="copy-cmd-btn"
                  onClick={handleCopyCmd}
                >
                  {copied ? '✓ Copied!' : '📋 Copy Command'}
                </button>
              </div>
              <code className="cmd-code-text">
                d:\Hobby\AI_NEWSLETTER\venv\Scripts\python.exe d:\Hobby\AI_NEWSLETTER\backend\scheduler\auto_generate.py --template modern
              </code>
              <div className="cmd-help-text">
                Run once weekly via Task Scheduler. Discovers 3 new tools, creates the 3-page A4 PDF, saves to SQLite, and notifies admin.
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Publication & Email Notifications */}
        <div className="settings-card">
          <div className="card-section-header">
            <div className="sec-icon-wrap">📰</div>
            <div>
              <h2 className="sec-title">Publication &amp; Administrator Alerts</h2>
              <p className="sec-desc">Configure newsletter metadata and SMTP server notifications.</p>
            </div>
          </div>

          <div className="card-fields-grid">
            <div className="two-col-row">
              <div className="form-group">
                <label className="form-label">Newsletter Title</label>
                <input
                  type="text"
                  className="form-input"
                  value={form.hal_newsletter_title}
                  onChange={set('hal_newsletter_title')}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Administrator Email (Alert Recipient)</label>
                <input
                  type="email"
                  className="form-input"
                  value={form.admin_email}
                  onChange={set('admin_email')}
                  placeholder="admin@hal-india.co.in"
                />
              </div>
            </div>

            <div className="two-col-row">
              <div className="form-group">
                <label className="form-label">SMTP Host</label>
                <input
                  type="text"
                  className="form-input"
                  value={form.smtp_host}
                  onChange={set('smtp_host')}
                />
              </div>
              <div className="form-group">
                <label className="form-label">SMTP Port</label>
                <input
                  type="number"
                  className="form-input"
                  value={form.smtp_port}
                  onChange={set('smtp_port')}
                />
              </div>
            </div>

            <div className="two-col-row">
              <div className="form-group">
                <label className="form-label">SMTP Username</label>
                <input
                  type="text"
                  className="form-input"
                  value={form.smtp_user}
                  onChange={set('smtp_user')}
                  placeholder="notifications@domain.com"
                  autoComplete="off"
                />
              </div>
              <div className="form-group">
                <label className="form-label">SMTP Password / App Password</label>
                <input
                  type="password"
                  className="form-input"
                  value={form.smtp_password}
                  onChange={set('smtp_password')}
                  placeholder="••••••••••••"
                  autoComplete="off"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="settings-action-bar">
          <button type="submit" className="btn btn-navy btn-lg" disabled={saving}>
            {saving ? <><span className="spinner" /> Saving Configuration…</> : '💾 Save All Settings to .env'}
          </button>
        </div>

      </form>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { newsletterApi } from '../services/api'
import './ToolCard.css'

const PRICING_CONFIG = {
  Free: { label: 'Free', class: 'badge-green' },
  Freemium: { label: 'Freemium', class: 'badge-orange' },
  Paid: { label: 'Commercial License', class: 'badge-red' },
  Enterprise: { label: 'Enterprise', class: 'badge-navy' },
}

export default function ToolCard({ tool, toolNum, newsletterId, onRegenerate, onUpdate }) {
  // Normalize tool whether from direct JSON or from DB record with .content
  const rawData = tool.content ? { ...tool.content, ...tool } : tool

  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ ...rawData })
  const [saving, setSaving] = useState(false)
  const [regenerating, setRegenerating] = useState(false)

  useEffect(() => {
    setForm(tool.content ? { ...tool.content, ...tool } : tool)
  }, [tool])

  const numLabel = String(toolNum).padStart(2, '0')
  const pricingKey = rawData.pricing_tier || rawData.pricing || 'Freemium'
  const pricingCfg = PRICING_CONFIG[pricingKey] || { label: pricingKey, class: 'badge-gray' }

  const handleSave = async () => {
    setSaving(true)
    try {
      await newsletterApi.updateTool(newsletterId, toolNum, form)
      onUpdate && onUpdate(toolNum, form)
      setEditing(false)
    } catch (err) {
      alert('Failed to save: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSaving(false)
    }
  }

  const handleRegenerate = async () => {
    setRegenerating(true)
    try {
      await newsletterApi.regenerateTool(newsletterId, toolNum)
      onRegenerate && onRegenerate(toolNum)
    } catch (err) {
      alert('Failed to regenerate: ' + (err.response?.data?.detail || err.message))
    } finally {
      setRegenerating(false)
    }
  }

  const overview = rawData.overview || rawData.what_it_does || 'No summary available.'
  const features = Array.isArray(rawData.key_features) ? rawData.key_features : []
  const halUseCase = rawData.hal_use_case || rawData.hal_example_workflow || ''
  const website = rawData.website || ''
  const websiteDisplay = rawData.website_display || website.replace(/^https?:\/\//, '').replace(/\/$/, '')

  return (
    <div className="modern-tool-card">
      {/* Top Meta Bar */}
      <div className="card-top-bar">
        <div className="page-indicator">
          <span className="page-dot" />
          <span>A4 PAGE {numLabel}</span>
        </div>
        <div className="card-actions">
          <button
            className="action-btn edit-btn"
            onClick={() => { setForm({ ...rawData }); setEditing(true) }}
            title="Edit this tool's text and prompt"
          >
            ✏️ <span>Edit</span>
          </button>
          <button
            className="action-btn regen-btn"
            onClick={handleRegenerate}
            disabled={regenerating}
            title="Regenerate this specific page"
          >
            {regenerating ? <span className="spinner spinner-dark" /> : '🔄'} 
            <span>{regenerating ? 'Regenerating…' : 'Regen'}</span>
          </button>
        </div>
      </div>

      {/* Main Tool Header */}
      <div className="card-hero">
        <div className="tool-avatar">
          <span className="avatar-text">{rawData.name ? rawData.name.charAt(0) : 'T'}</span>
        </div>
        <div className="tool-heading-info">
          <h3 className="tool-title">{rawData.name || 'AI Engineering Tool'}</h3>
          <div className="badge-row">
            <span className="badge badge-red">{rawData.category || 'Engineering AI'}</span>
            <span className={`badge ${pricingCfg.class}`}>{pricingCfg.label}</span>
          </div>
        </div>
      </div>

      {/* Executive Overview */}
      <p className="tool-summary-text">{overview}</p>

      {/* Capabilities Snapshot */}
      {features.length > 0 && (
        <div className="features-preview-box">
          <div className="preview-label">Core Capabilities:</div>
          <ul className="features-mini-list">
            {features.slice(0, 2).map((feat, i) => (
              <li key={i}>{feat}</li>
            ))}
          </ul>
        </div>
      )}

      {/* HAL Use Case Callout */}
      {halUseCase && (
        <div className="hal-callout-pill">
          <span className="hal-icon">✈</span>
          <div className="hal-use-text">
            <strong>HAL Context:</strong> {halUseCase.slice(0, 115)}…
          </div>
        </div>
      )}

      {/* Card Footer with Website */}
      <div className="card-footer-strap">
        {website ? (
          <a href={website} target="_blank" rel="noreferrer" className="website-link">
            <span>🌐</span>
            <span>{websiteDisplay}</span>
          </a>
        ) : (
          <span className="website-link text-muted">No website link</span>
        )}
        <span className="page-sync-tag">Synced to PDF</span>
      </div>

      {/* Edit Modal */}
      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span className="modal-title">✏️ Edit Tool {numLabel}: {rawData.name}</span>
              <button className="modal-close" onClick={() => setEditing(false)}>×</button>
            </div>

            {[
              { key: 'overview', label: 'Overview Tagline', rows: 2 },
              { key: 'what_it_does', label: 'What It Does (Detailed)', rows: 3 },
              { key: 'key_features', label: 'Key Capabilities (One per line)', rows: 3, isList: true },
              { key: 'how_it_works', label: 'Technical Workflow Overview', rows: 2 },
              { key: 'hal_use_case', label: 'HAL Potential Use Case', rows: 3 },
              { key: 'hal_example_workflow', label: 'HAL Example Workflow', rows: 2 },
              { key: 'sample_prompt', label: 'Sample Prompt for HAL Engineers', rows: 3 },
              { key: 'security_note', label: 'Security & Safe Use Disclaimer', rows: 2 },
            ].map(({ key, label, rows, isList }) => (
              <div className="form-group" key={key}>
                <label className="form-label">{label}</label>
                <textarea
                  className="form-textarea"
                  rows={rows}
                  value={
                    isList && Array.isArray(form[key])
                      ? form[key].join('\n')
                      : (form[key] || '')
                  }
                  onChange={e => {
                    const val = isList
                      ? e.target.value.split('\n').filter(Boolean)
                      : e.target.value
                    setForm(f => ({ ...f, [key]: val }))
                  }}
                />
              </div>
            ))}

            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 14 }}>
              <button className="btn btn-ghost" onClick={() => setEditing(false)}>Cancel</button>
              <button className="btn btn-navy" onClick={handleSave} disabled={saving}>
                {saving ? <><span className="spinner" /> Saving Changes…</> : '💾 Save & Update Page'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

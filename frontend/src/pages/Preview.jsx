import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { newsletterApi } from '../services/api'
import './Preview.css'

export default function Preview() {
  const { id } = useParams()
  const [html, setHtml] = useState(null)
  const [newsletter, setNewsletter] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!id) {
      setError('No newsletter ID provided.')
      setLoading(false)
      return
    }

    Promise.all([
      newsletterApi.preview(id),
      newsletterApi.get(id).catch(() => ({ data: null }))
    ])
      .then(([previewRes, detailRes]) => {
        setHtml(previewRes.data)
        if (detailRes.data) setNewsletter(detailRes.data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        setLoading(false)
      })
  }, [id])

  return (
    <div className="preview-container-page">
      {/* Top Bar */}
      <header className="preview-top-bar">
        <div className="preview-bar-left">
          <Link to="/" className="btn btn-outline btn-sm">
            ← Dashboard
          </Link>
          <div className="preview-heading-block">
            <span className="preview-badge">FULL DOCUMENT VIEWER</span>
            <span className="preview-title">
              Issue #{String(newsletter?.issue_number || id).padStart(2, '0')}
              {newsletter?.week_label ? ` · ${newsletter.week_label}` : ''}
            </span>
          </div>
        </div>

        <div className="preview-bar-right">
          <span className="badge badge-green">3-PAGE A4 VERIFIED</span>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => newsletterApi.download(id)}
            disabled={!id}
          >
            📥 Download PDF
          </button>
          <button
            className="btn btn-navy btn-sm"
            style={{ backgroundColor: '#1e3a8a', color: '#fff' }}
            onClick={() => newsletterApi.downloadWord(id)}
            disabled={!id}
          >
            📄 Download Word (.docx)
          </button>
        </div>
      </header>

      {/* Main Preview Area */}
      <div className="preview-canvas-area">
        {loading && (
          <div className="preview-state-card">
            <span className="spinner spinner-dark" />
            <span>Rendering full-fidelity A4 document…</span>
          </div>
        )}

        {error && (
          <div className="preview-state-card error">
            <div style={{ fontSize: 32 }}>❌</div>
            <div style={{ fontWeight: 700, fontSize: 15 }}>{error}</div>
            <Link to="/" className="btn btn-navy btn-sm" style={{ marginTop: 12 }}>
              Return to Dashboard
            </Link>
          </div>
        )}

        {html && (
          <div className="preview-sheet-frame">
            <iframe
              className="preview-iframe-view"
              srcDoc={html}
              title="A4 Newsletter Document Preview"
              sandbox="allow-same-origin allow-scripts"
            />
          </div>
        )}
      </div>
    </div>
  )
}

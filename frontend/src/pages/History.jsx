import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { newsletterApi } from '../services/api'
import './History.css'

const STATUS_BADGE = {
  draft: 'badge-gray',
  approved: 'badge-green',
  published: 'badge-navy',
}

const PAGE_SIZE = 10

export default function History() {
  const navigate = useNavigate()
  const [newsletters, setNewsletters] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)

  useEffect(() => {
    newsletterApi.list()
      .then(res => {
        setNewsletters(res.data?.newsletters || [])
        setLoading(false)
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        setLoading(false)
      })
  }, [])

  const totalPages = Math.ceil(newsletters.length / PAGE_SIZE)
  const paged = newsletters.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  // Compute total documented tools
  const totalTools = newsletters.reduce((acc, nl) => acc + (nl.tools?.length || 3), 0)

  return (
    <div className="history-container">
      {/* Page Header */}
      <div className="history-header-row">
        <div>
          <div className="dash-breadcrumb">
            <span>AEROSPACE ARCHIVE</span>
            <span>/</span>
            <span className="active">PAST EDITIONS</span>
          </div>
          <h1 className="history-heading">Issue Archive &amp; History</h1>
          <p className="history-subheading">
            Browse, inspect, and download previously published HAL AI Tools Weekly issues.
          </p>
        </div>
        <Link to="/" className="btn btn-navy">
          <span>⚡</span>
          <span>Generate New Issue</span>
        </Link>
      </div>

      {/* Metrics Row */}
      <div className="history-metrics-row">
        <div className="metric-box">
          <div className="metric-label">Total Published Issues</div>
          <div className="metric-val">{newsletters.length}</div>
          <div className="metric-sub">Stored in SQLite Database</div>
        </div>
        <div className="metric-box">
          <div className="metric-label">Documented AI Tools</div>
          <div className="metric-val">{totalTools}</div>
          <div className="metric-sub">Deduplicated Catalog</div>
        </div>
        <div className="metric-box">
          <div className="metric-label">Latest Issue</div>
          <div className="metric-val">
            {newsletters[0] ? `#${String(newsletters[0].issue_number).padStart(2, '0')}` : '—'}
          </div>
          <div className="metric-sub">{newsletters[0]?.week_label || 'Current Week'}</div>
        </div>
      </div>

      {loading && (
        <div className="history-loading-card">
          <span className="spinner spinner-dark" />
          <span>Loading historical issues archive…</span>
        </div>
      )}

      {error && (
        <div className="history-error-card">
          <span>❌ Error loading history: {error}</span>
        </div>
      )}

      {!loading && !error && newsletters.length === 0 && (
        <div className="history-empty-card">
          <div className="empty-icon">📂</div>
          <h3 className="empty-title">No Newsletters Generated Yet</h3>
          <p className="empty-text">Generate your first 3-page AI newsletter to initialize the issue history.</p>
          <Link to="/" className="btn btn-navy" style={{ marginTop: 16 }}>
            Launch Edition Compiler
          </Link>
        </div>
      )}

      {paged.length > 0 && (
        <div className="history-table-card">
          <div className="table-header-bar">
            <span className="table-title">Published Editions Ledger</span>
            <span className="table-count">{newsletters.length} total entries</span>
          </div>

          <div className="history-table-responsive">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Issue</th>
                  <th>Week &amp; Date</th>
                  <th>Template</th>
                  <th>Status</th>
                  <th>Documented Tools</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {paged.map((nl) => {
                  const tpl = nl.template_name || 'classic'
                  return (
                    <tr key={nl.id}>
                      <td>
                        <div className="issue-badge-tag">
                          #{String(nl.issue_number || nl.id).padStart(2, '0')}
                        </div>
                      </td>
                      <td>
                        <div className="week-primary">{nl.week_label || '—'}</div>
                        <div className="date-secondary">{nl.pub_date || '—'}</div>
                      </td>
                      <td>
                        <span className={`badge ${tpl === 'modern' ? 'badge-cyan' : 'badge-navy'}`}>
                          {tpl === 'modern' ? 'MODERN INFOGRAPHIC' : 'CLASSIC CORP'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${STATUS_BADGE[nl.status] || 'badge-gray'}`}>
                          {nl.status || 'draft'}
                        </span>
                      </td>
                      <td>
                        <div className="tools-chip-group">
                          {(nl.tools || []).map((t, i) => (
                            <span key={i} className="tool-chip" title={t.name}>
                              {t.name}
                            </span>
                          ))}
                          {(!nl.tools || nl.tools.length === 0) && (
                            <span className="text-muted" style={{ fontSize: 12 }}>3 AI Tools</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="row-action-buttons">
                          <button
                            className="pill-action-btn view"
                            onClick={() => navigate(`/preview/${nl.id}`)}
                            title="Interactive Preview"
                          >
                            👁️ <span>Preview</span>
                          </button>
                          <button
                            className="pill-action-btn pdf"
                            onClick={() => newsletterApi.download(nl.id)}
                            title="Download Print PDF"
                          >
                            📥 <span>PDF</span>
                          </button>
                          <button
                            className="pill-action-btn pdf"
                            style={{ backgroundColor: '#eff6ff', color: '#1d4ed8', borderColor: '#bfdbfe' }}
                            onClick={() => newsletterApi.downloadWord(nl.id)}
                            title="Download Word Document"
                          >
                            📄 <span>Word</span>
                          </button>
                          <a
                            href={`/api/newsletter/${nl.id}`}
                            target="_blank"
                            rel="noreferrer"
                            className="pill-action-btn json"
                            title="Inspect Raw JSON"
                          >
                            JSON
                          </a>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="table-footer-pagination">
              <button
                className="btn btn-outline btn-sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                ← Previous
              </button>
              <span className="page-counter-text">Page {page} of {totalPages}</span>
              <button
                className="btn btn-outline btn-sm"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

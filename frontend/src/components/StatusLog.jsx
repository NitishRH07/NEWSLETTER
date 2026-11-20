import { useRef, useEffect } from 'react'
import './StatusLog.css'

const LEVEL_CONFIG = {
  info: { label: 'INFO', icon: 'ℹ️', class: 'log-info' },
  success: { label: 'DONE', icon: '✓', class: 'log-success' },
  error: { label: 'FAIL', icon: '✕', class: 'log-error' },
  warning: { label: 'WARN', icon: '⚠', class: 'log-warning' },
}

export default function StatusLog({ logs = [] }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <div className="status-log-card">
      <div className="status-log-header">
        <div className="header-left">
          <span className="terminal-dot" />
          <span className="log-title">Telemetry &amp; Execution Stream</span>
        </div>
        <div className="header-right">
          <span className="log-counter">{logs.length} events logged</span>
        </div>
      </div>

      <div className="status-log-viewport">
        {logs.length === 0 ? (
          <div className="log-empty-state">
            <span className="empty-icon">📡</span>
            <span>Awaiting pipeline trigger. Select template above and click Generate.</span>
          </div>
        ) : (
          logs.map((entry, i) => {
            const cfg = LEVEL_CONFIG[entry.level] || LEVEL_CONFIG.info
            return (
              <div key={i} className={`log-row ${cfg.class}`}>
                <span className="log-timestamp">{entry.timestamp || '--:--:--'}</span>
                <span className={`log-badge ${cfg.class}`}>{cfg.label}</span>
                <span className="log-message">{entry.message}</span>
              </div>
            )
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

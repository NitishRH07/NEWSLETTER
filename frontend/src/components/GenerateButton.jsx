import './GenerateButton.css'

const STEPS = [
  { key: 'discover', match: ['discover', 'discovering'], label: 'Discovering Tools', icon: '🔍' },
  { key: 'research', match: ['research', 'researching'], label: 'Researching', icon: '📚' },
  { key: 'verify', match: ['verify', 'verifying'], label: 'Verifying URLs', icon: '🛡️' },
  { key: 'generate', match: ['generate', 'generating'], label: 'Synthesizing Content', icon: '⚡' },
  { key: 'pdf', match: ['pdf', 'creating_pdf'], label: 'Compiling A4 PDF', icon: '📄' },
]

export default function GenerateButton({ loading, currentStep, error, onClick }) {
  // Determine active step index safely
  const stepIdx = STEPS.findIndex(s => {
    if (!currentStep) return false
    const lower = currentStep.toLowerCase()
    return s.match.some(m => lower.includes(m))
  })

  return (
    <div className="generate-btn-wrapper">
      {/* Main Action Button */}
      <button
        className={`generate-btn ${loading ? 'loading' : ''} ${error ? 'errored' : ''}`}
        onClick={onClick}
        disabled={loading}
      >
        <span className="btn-glow" />
        <span className="btn-content">
          {loading ? (
            <>
              <span className="spinner" />
              <span>Generating Issue ({currentStep ? currentStep.replace(/_/g, ' ') : 'Processing'}…)</span>
            </>
          ) : error ? (
            <>
              <span className="btn-icon">⚠️</span>
              <span>Retry Newsletter Generation</span>
            </>
          ) : (
            <>
              <span className="btn-icon">⚡</span>
              <span>Generate This Week's Newsletter</span>
            </>
          )}
        </span>
      </button>

      {/* Modern Connected Step Progress Tracker */}
      {loading && (
        <div className="step-track-container">
          <div className="step-track">
            {STEPS.map((step, i) => {
              const isDone = stepIdx >= 0 && i < stepIdx
              const isActive = stepIdx >= 0 ? i === stepIdx : i === 0
              return (
                <div
                  key={step.key}
                  className={`step-item ${isDone ? 'done' : ''} ${isActive ? 'active' : ''}`}
                >
                  <div className="step-node">
                    {isDone ? (
                      <span className="node-check">✓</span>
                    ) : (
                      <span className="node-icon">{step.icon}</span>
                    )}
                    {isActive && <span className="node-radar" />}
                  </div>
                  <div className="step-label">{step.label}</div>
                  {i < STEPS.length - 1 && (
                    <div className={`step-connector ${isDone ? 'done' : ''}`} />
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Error Callout */}
      {error && (
        <div className="generate-error-card">
          <span className="error-icon">❌</span>
          <div className="error-text">
            <strong>Generation Interrupted:</strong> {error}
          </div>
        </div>
      )}
    </div>
  )
}

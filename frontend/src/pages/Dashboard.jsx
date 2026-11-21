import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { newsletterApi } from '../services/api'
import GenerateButton from '../components/GenerateButton'
import StatusLog from '../components/StatusLog'
import ToolCard from '../components/ToolCard'
import './Dashboard.css'

function getWeekLabel() {
  const now = new Date()
  const start = new Date(now.getFullYear(), 0, 1)
  const week = Math.ceil(((now - start) / 86400000 + start.getDay() + 1) / 7)
  return `Week ${week}, ${now.getFullYear()}`
}

export default function Dashboard() {
  const navigate = useNavigate()

  // State
  const [generating, setGenerating] = useState(false)
  const [currentStep, setCurrentStep] = useState(null)
  const [genError, setGenError] = useState(null)
  const [logs, setLogs] = useState([])
  const [newsletter, setNewsletter] = useState(null)
  const [tools, setTools] = useState([])
  const [previewHtml, setPreviewHtml] = useState(null)
  const [showPreview, setShowPreview] = useState(false)
  const [toast, setToast] = useState(null)
  const [selectedTemplate, setSelectedTemplate] = useState('modern')
  const [toolCount, setToolCount] = useState(3)
  const [pagesPerTool, setPagesPerTool] = useState(1)
  const [generationMode, setGenerationMode] = useState('direct') // 'direct' | 'custom'
  const [customPrompt, setCustomPrompt] = useState('')
  const [historyCount, setHistoryCount] = useState(0)
  const pollRef = useRef(null)

  // Load latest newsletter on mount
  useEffect(() => {
    loadLatest()
  }, [])

  const loadLatest = async () => {
    try {
      const res = await newsletterApi.list()
      const list = res.data?.newsletters || (Array.isArray(res.data) ? res.data : [])
      setHistoryCount(list.length)
      if (list.length > 0) {
        const latest = list[0]
        setNewsletter(latest)
        setTools(latest.tools || [])
        if (latest.template_name) {
          setSelectedTemplate(latest.template_name)
        }
      }
    } catch (_) {}
  }

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const addLog = (message, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(l => [...l, { timestamp, message, level }])
  }

  const startPolling = useCallback((id) => {
    if (pollRef.current) clearInterval(pollRef.current)
    let lastMsg = ''
    pollRef.current = setInterval(async () => {
      try {
        const res = await newsletterApi.status(id)
        const { status, step, message, tools: toolData, newsletter_id } = res.data
        if (message && message !== lastMsg) {
          lastMsg = message
          addLog(message, status === 'error' ? 'error' : 'info')
        }
        if (step) setCurrentStep(step)
        if (status === 'complete' || status === 'error') {
          clearInterval(pollRef.current)
          setGenerating(false)
          if (status === 'complete') {
            setCurrentStep(null)
            addLog('Newsletter generated successfully!', 'success')
            showToast('Newsletter compiled successfully!', 'success')
            const finalId = newsletter_id || id
            try {
              const fresh = await newsletterApi.get(finalId)
              setNewsletter(fresh.data)
              setTools(fresh.data.tools || toolData || [])
            } catch (_) {
              setNewsletter({ ...(res.data.newsletter || {}), id: finalId })
              setTools(toolData || [])
            }
          } else {
            setGenError(res.data.error || 'Generation failed')
            addLog('Generation failed: ' + (res.data.error || 'Unknown error'), 'error')
          }
        }
      } catch (_) {}
    }, 2000)
  }, [])

  useEffect(() => () => clearInterval(pollRef.current), [])

  const handleGenerate = async (templateToUse = selectedTemplate) => {
    setGenerating(true)
    setGenError(null)
    setLogs([])
    setTools([])
    setNewsletter(null)
    setShowPreview(false)

    const modeLabel = generationMode === 'custom' && customPrompt.trim()
      ? `Custom Focus ("${customPrompt.trim().slice(0, 32)}...")`
      : 'Direct Auto-Discovery'

    const totalPagesTarget = toolCount * pagesPerTool
    const tplName = templateToUse === 'gn3_hal' ? 'Template 3 (GN3-HAL)' : templateToUse === 'modern' ? 'Template 2 (Modern)' : 'Template 1 (Classic)'
    addLog(`Initiating pipeline: ${toolCount} tool(s) × ${pagesPerTool} pg = ${totalPagesTarget}-page PDF, ${tplName}, ${modeLabel}…`, 'info')

    try {
      const res = await newsletterApi.generate({
        template: templateToUse,
        tool_count: toolCount,
        pages_per_tool: pagesPerTool,
        generation_mode: generationMode,
        custom_prompt: customPrompt,
      })
      const id = res.data?.newsletter_id || res.data?.id || 'current'
      addLog('Workflow queued on backend daemon...', 'info')
      startPolling(id)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      setGenError(msg)
      setGenerating(false)
      addLog('Failed to start: ' + msg, 'error')
    }
  }

  const handlePreview = async () => {
    if (!newsletter?.id) return
    try {
      const res = await newsletterApi.preview(newsletter.id)
      setPreviewHtml(res.data)
      setShowPreview(true)
    } catch (err) {
      showToast('Failed to load preview', 'error')
    }
  }

  const handleApprove = async () => {
    if (!newsletter?.id) return
    try {
      await newsletterApi.approve(newsletter.id)
      setNewsletter(n => ({ ...n, status: 'approved' }))
      showToast('Newsletter approved and finalized for distribution!', 'success')
      addLog('Newsletter approved and locked by administrator.', 'success')
    } catch (err) {
      showToast('Approval failed', 'error')
    }
  }

  const handleToolUpdate = (toolNum, data) => {
    setTools(ts => ts.map((t, i) => i === toolNum - 1 ? { ...t, ...data } : t))
    showToast('Tool content saved & PDF re-compiled', 'success')
  }

  const handleToolRegenerate = (toolNum) => {
    addLog(`Regenerating tool page ${toolNum}…`, 'info')
    setTimeout(() => loadLatest(), 5000)
  }

  const hasNewsletter = newsletter && tools.length > 0

  return (
    <div className="dashboard-container">
      {/* Toast */}
      {toast && (
        <div className="toast-container">
          <div className={`toast toast-${toast.type}`}>
            <span>{toast.type === 'success' ? '✓' : '⚠️'}</span>
            <span>{toast.msg}</span>
          </div>
        </div>
      )}

      {/* Header Banner */}
      <div className="dashboard-header-row">
        <div>
          <div className="dash-breadcrumb">
            <span>AEROSPACE AI DASHBOARD</span>
            <span>/</span>
            <span className="active">EDITION COMPILER</span>
          </div>
          <h1 className="dash-heading">HAL AI Tools Weekly</h1>
          <p className="dash-subheading">
            {getWeekLabel()} · Automated Discovery, Research, Verification &amp; 3-Page A4 PDF Compilation
          </p>
        </div>

        {newsletter && (
          <div className="header-status-pill">
            <span className={`badge badge-${newsletter.status === 'approved' ? 'green' : 'navy'}`}>
              {newsletter.status || 'DRAFT'}
            </span>
            <span className="issue-label">Issue #{String(newsletter.issue_number || 1).padStart(2, '0')}</span>
          </div>
        )}
      </div>

      {/* KPI Stats Ribbon */}
      <div className="stats-ribbon">
        <div className="stat-card">
          <div className="stat-label">Active Edition</div>
          <div className="stat-value">Issue #{String(newsletter?.issue_number || (historyCount + 1)).padStart(2, '0')}</div>
          <div className="stat-sub">{getWeekLabel()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Archive Depth</div>
          <div className="stat-value">{historyCount} Issues</div>
          <div className="stat-sub">Recorded in SQLite</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Selected Layout</div>
          <div className="stat-value" style={{ textTransform: 'capitalize' }}>
            {selectedTemplate} Edition
          </div>
          <div className="stat-sub">Strict 3-Page A4 Grid</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Security Protocol</div>
          <div className="stat-value" style={{ color: '#059669' }}>Enforced</div>
          <div className="stat-sub">HAL IT Classification Guard</div>
        </div>
      </div>

      {/* Generator Cockpit Card */}
      <section className="generator-cockpit">
        <div className="cockpit-inner">
          <div className="cockpit-badge">
            <span>🚀</span>
            <span>PIPELINE ORCHESTRATOR</span>
          </div>
          <h2 className="cockpit-title">Weekly Newsletter Generator</h2>
          <p className="cockpit-desc">
            Initiate automated research across enterprise engineering AI tools, verify live URLs, 
            generate defense-tailored aerospace content, and render a print-ready 3-page A4 PDF.
          </p>

          {/* Template Selector */}
          <div className="template-picker-section">
            <div className="picker-header">
              <span className="picker-icon">🎨</span>
              <span className="picker-title">Select Edition Design Template:</span>
            </div>

            <div className="template-selector-grid">
              {/* Option 1: Classic Corporate */}
              <div
                className={`template-box ${selectedTemplate === 'classic' ? 'is-selected' : ''}`}
                onClick={() => setSelectedTemplate('classic')}
              >
                <div className="box-top-tag">
                  <span className="box-pill">TEMPLATE 1</span>
                  {selectedTemplate === 'classic' ? (
                    <span className="check-pill">✓ SELECTED</span>
                  ) : (
                    <span className="hint-pill">Select</span>
                  )}
                </div>
                <div className="box-thumb">
                  <img src="/template_classic.png" alt="Classic Corporate Template" />
                </div>
                <div className="box-body">
                  <div className="box-heading">Classic Corporate Edition</div>
                  <div className="box-desc">
                    5 horizontal structured rows, circular icon badges, split prompt/QR boxes, and LCA Tejas watermark.
                  </div>
                </div>
              </div>

              {/* Option 2: Modern Infographic */}
              <div
                className={`template-box ${selectedTemplate === 'modern' ? 'is-selected' : ''}`}
                onClick={() => setSelectedTemplate('modern')}
              >
                <div className="box-top-tag">
                  <span className="box-pill">TEMPLATE 2</span>
                  {selectedTemplate === 'modern' ? (
                    <span className="check-pill">✓ SELECTED</span>
                  ) : (
                    <span className="hint-pill">Select</span>
                  )}
                </div>
                <div className="box-thumb">
                  <img src="/template_modern.jpg" alt="Modern Infographic Template" />
                </div>
                <div className="box-body">
                  <div className="box-heading">Modern Infographic Edition</div>
                  <div className="box-desc">
                    Modular 3-column grid, tool-specific timeline, Feature Snapshot pipeline, and HAL workplace applications.
                  </div>
                </div>
              </div>

              {/* Option 3: GN3-HAL (Employee Edition) */}
              <div
                className={`template-box ${selectedTemplate === 'gn3_hal' ? 'is-selected' : ''}`}
                onClick={() => setSelectedTemplate('gn3_hal')}
              >
                <div className="box-top-tag">
                  <span className="box-pill" style={{ background: '#059669', color: '#fff' }}>TEMPLATE 3</span>
                  {selectedTemplate === 'gn3_hal' ? (
                    <span className="check-pill" style={{ background: '#059669', color: '#fff' }}>✓ SELECTED</span>
                  ) : (
                    <span className="hint-pill">Select</span>
                  )}
                </div>
                <div className="box-thumb" style={{ background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{ textAlign: 'center', padding: '10px 4px' }}>
                    <div style={{ fontSize: '28px', marginBottom: '4px' }}>💡✨</div>
                    <span style={{ fontSize: '11px', fontWeight: '800', color: '#065f46', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      GN3-HAL Employee Edition
                    </span>
                  </div>
                </div>
                <div className="box-body">
                  <div className="box-heading" style={{ color: '#059669' }}>GN3-HAL (Employee Edition)</div>
                  <div className="box-desc">
                    Tailored for non-technical staff: everyday analogies, Before &amp; After stories, visual 3-step flows, zero jargon, and 60-second tryouts.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tool Count & Generation Strategy Controls */}
          <div className="config-section-wrapper">
            {/* 1. Tool Count Selector */}
            <div className="count-picker-row">
              <div className="sub-picker-header">
                <span>📏</span>
                <span>Issue Page Count &amp; Tools:</span>
              </div>
              <div className="count-pill-grid">
                <button
                  type="button"
                  className={`count-pill-btn ${toolCount === 1 ? 'is-active' : ''}`}
                  onClick={() => setToolCount(1)}
                >
                  <span className="count-pill-main">1 Tool</span>
                  <span className="count-pill-sub">1-Page Spotlight</span>
                </button>
                <button
                  type="button"
                  className={`count-pill-btn ${toolCount === 2 ? 'is-active' : ''}`}
                  onClick={() => setToolCount(2)}
                >
                  <span className="count-pill-main">2 Tools</span>
                  <span className="count-pill-sub">2-Page Brief</span>
                </button>
                <button
                  type="button"
                  className={`count-pill-btn ${toolCount === 3 ? 'is-active' : ''}`}
                  onClick={() => setToolCount(3)}
                >
                  <span className="count-pill-main">3 Tools (Standard)</span>
                  <span className="count-pill-sub">Full Issue</span>
                </button>
              </div>
            </div>

            {/* 2. Editorial Depth per Tool Selector */}
            <div className="count-picker-row">
              <div className="sub-picker-header" style={{ justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>📑</span>
                  <span>Editorial Depth per Tool:</span>
                </div>
                <span style={{ fontSize: '11px', color: '#38bdf8', fontWeight: '800' }}>
                  Total: {toolCount * pagesPerTool} Page{toolCount * pagesPerTool > 1 ? 's' : ''} A4 PDF
                </span>
              </div>
              <div className="depth-pill-grid">
                <button
                  type="button"
                  className={`depth-pill-btn ${pagesPerTool === 1 ? 'is-active' : ''}`}
                  onClick={() => setPagesPerTool(1)}
                >
                  <span className="count-pill-main">📄 1 Page per Tool (Executive Spotlight)</span>
                  <span className="count-pill-sub">Dense single-page layout with 5 capabilities, workplace impact &amp; dual prompts</span>
                </button>
                <button
                  type="button"
                  className={`depth-pill-btn ${pagesPerTool === 2 ? 'is-active' : ''}`}
                  onClick={() => setPagesPerTool(2)}
                >
                  <span className="count-pill-main">📑 2 Pages per Tool (Deep-Dive Dossier)</span>
                  <span className="count-pill-sub">Includes Part 2 Onboarding Masterclass, 3 Department Prompts &amp; Benchmarks</span>
                </button>
              </div>
            </div>

            {/* 3. Generation Mode Selector */}
            <div className="gen-mode-section">
              <div className="sub-picker-header">
                <span>⚡</span>
                <span>Select Generation Strategy:</span>
              </div>
              <div className="gen-mode-tabs">
                <button
                  type="button"
                  className={`mode-tab-card ${generationMode === 'direct' ? 'is-active' : ''}`}
                  onClick={() => setGenerationMode('direct')}
                >
                  <span className="mode-tab-icon">⚡</span>
                  <div className="mode-tab-content">
                    <span className="mode-tab-title">Direct Auto-Generate</span>
                    <span className="mode-tab-desc">
                      Automated discovery of currently active, high-value enterprise AI tools.
                    </span>
                  </div>
                </button>

                <button
                  type="button"
                  className={`mode-tab-card ${generationMode === 'custom' ? 'is-active' : ''}`}
                  onClick={() => setGenerationMode('custom')}
                >
                  <span className="mode-tab-icon">✍️</span>
                  <div className="mode-tab-content">
                    <span className="mode-tab-title">Custom Topic / Focus</span>
                    <span className="mode-tab-desc">
                      Type specific requirements, department needs, or exact tool names to feature.
                    </span>
                  </div>
                </button>
              </div>

              {/* Custom Prompt Box */}
              {generationMode === 'custom' && (
                <div className="custom-prompt-container">
                  <div className="custom-prompt-label">
                    <span>Target Topic, Department, or Specific Tools:</span>
                    <span>Optional &amp; Flexible</span>
                  </div>
                  <textarea
                    className="custom-prompt-textarea"
                    placeholder="e.g., Focus on AI tools for technical report writing, document indexing, and PDF summarization... Or: 'Feature Cursor, Julius AI, and Claude Code'."
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    rows={3}
                  />
                  <div className="prompt-suggestions-row">
                    <span className="suggestions-tag">Quick Topics:</span>
                    <button
                      type="button"
                      className="prompt-chip"
                      onClick={() => setCustomPrompt('Focus on tools for Excel data analysis, spreadsheet modeling, and automated charts')}
                    >
                      📊 Excel &amp; Data
                    </button>
                    <button
                      type="button"
                      className="prompt-chip"
                      onClick={() => setCustomPrompt('Focus on AI tools for technical documentation, SOP writing, and manual indexing')}
                    >
                      📝 Technical SOPs
                    </button>
                    <button
                      type="button"
                      className="prompt-chip"
                      onClick={() => setCustomPrompt('Focus on AI tools for terminal automation, code refactoring, and software development')}
                    >
                      💻 Coding &amp; Automation
                    </button>
                    <button
                      type="button"
                      className="prompt-chip"
                      onClick={() => setCustomPrompt('Focus on AI tools for PDF literature reviews, paper analysis, and technical search')}
                    >
                      📑 Research &amp; Papers
                    </button>
                    <button
                      type="button"
                      className="prompt-chip"
                      onClick={() => setCustomPrompt('Focus on AI tools for meeting transcription, action item tracking, and presentation generation')}
                    >
                      🤝 Meetings &amp; Slides
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Action Button & Stepper */}
          <GenerateButton
            loading={generating}
            currentStep={currentStep}
            error={genError}
            onClick={() => handleGenerate(selectedTemplate)}
          />
        </div>
      </section>

      {/* Telemetry Stream Log */}
      <StatusLog logs={logs} />

      {/* Generated Tools & Review Section */}
      {hasNewsletter && (
        <section className="review-section">
          <div className="section-header-bar">
            <div>
              <h2 className="section-title">
                <span>Issue #{String(newsletter.issue_number || 1).padStart(2, '0')}</span> — Documented AI Tools
              </h2>
              <p className="section-sub">
                Each tool below occupies exactly 1 page in the generated {tools.length}-page A4 PDF. Edit content or regenerate individual tools as needed.
              </p>
            </div>

            <div className="review-action-group">
              <button className="btn btn-outline" onClick={handlePreview}>
                <span>👁️</span> <span>Full Preview</span>
              </button>
              <button
                className="btn btn-navy"
                onClick={() => newsletterApi.download(newsletter.id)}
                title="Download formatted print-ready PDF"
              >
                <span>📥</span> <span>Download PDF</span>
              </button>
              <button
                className="btn btn-navy"
                style={{ backgroundColor: '#1e3a8a', color: '#fff' }}
                onClick={() => newsletterApi.downloadWord(newsletter.id)}
                title="Download editable Microsoft Word document"
              >
                <span>📄</span> <span>Download Word (.docx)</span>
              </button>
              {newsletter.status !== 'approved' && (
                <button className="btn btn-primary" onClick={handleApprove}>
                  <span>✓</span> <span>Approve Newsletter</span>
                </button>
              )}
            </div>
          </div>

          {/* 3 Tool Cards Grid */}
          <div className="tool-cards-grid">
            {tools.map((tool, idx) => (
              <ToolCard
                key={tool.name || idx}
                tool={tool}
                toolNum={idx + 1}
                newsletterId={newsletter.id}
                onRegenerate={handleToolRegenerate}
                onUpdate={handleToolUpdate}
              />
            ))}
          </div>
        </section>
      )}

      {/* Full Preview Modal */}
      {showPreview && previewHtml && (
        <div className="preview-modal-overlay" onClick={() => setShowPreview(false)}>
          <div className="preview-modal-shell" onClick={e => e.stopPropagation()}>
            <div className="preview-modal-bar">
              <div className="preview-bar-left">
                <span className="dot-green" />
                <span className="bar-title">Interactive PDF Preview — Issue #{newsletter?.issue_number}</span>
                <span className="badge badge-navy">{selectedTemplate.toUpperCase()} TEMPLATE</span>
              </div>
              <div className="preview-bar-right">
                <button
                  className="btn btn-navy btn-sm"
                  onClick={() => newsletterApi.download(newsletter?.id)}
                >
                  📥 Download PDF
                </button>
                <button
                  className="btn btn-navy btn-sm"
                  style={{ backgroundColor: '#1e3a8a', color: '#fff' }}
                  onClick={() => newsletterApi.downloadWord(newsletter?.id)}
                >
                  📄 Download Word (.docx)
                </button>
                <button className="modal-close" onClick={() => setShowPreview(false)}>×</button>
              </div>
            </div>
            <div className="preview-iframe-wrapper">
              <iframe
                srcDoc={previewHtml}
                title="Full A4 Newsletter Preview"
                className="preview-iframe-element"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

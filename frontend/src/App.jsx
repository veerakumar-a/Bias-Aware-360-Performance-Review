import { useMemo, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const DEFAULT_PAYLOAD = {
  employee_id: 'EMP-001',
  review_cycle: '2026-Q3',
  self_assessment: 'Delivered a high-impact AI workflow and improved cross-functional handoffs.',
  manager_feedback: 'Strong ownership and measurable impact. Needs clearer follow-through on documentation.',
  peer_feedback: [
    'Collaborative and dependable during project execution.',
    'Helpful in aligning engineering and product teams.',
  ],
  goals: ['Improve reliability of retrieval pipelines', 'Expand mentoring support'],
  project_outcomes: ['Improved operational efficiency by 18%.', 'Reduced incident response time.'],
  meeting_notes: ['Weekly review noted strong delivery quality and communication.'],
  reviewer_name: 'HR_Review_Manager',
  reviewer_role: 'hr',
  approval_decision: 'approve',
}

function App() {
  const [formState, setFormState] = useState(DEFAULT_PAYLOAD)
  const [report, setReport] = useState(null)
  const [activeTab, setActiveTab] = useState('strengths')
  const [authState, setAuthState] = useState({ role: 'reviewer', signedIn: false })
  const [loginForm, setLoginForm] = useState({ username: 'hr', password: 'hr123' })
  const [message, setMessage] = useState('Ready to generate a grounded 360° review.')

  const tabLabels = useMemo(
    () => ({
      strengths: 'Strengths',
      bias: 'Bias Flags',
      evidence: 'Evidence',
    }),
    [],
  )

  const metrics = useMemo(() => {
    const evidenceCount = report?.evidence?.length || 0
    const biasCount = report?.bias_flags?.length || 0
    return [
      { label: 'Evidence', value: evidenceCount },
      { label: 'Bias Flags', value: biasCount },
      { label: 'Role', value: authState.role },
    ]
  }, [authState.role, report])

  async function login() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(loginForm),
      })
      const payload = await response.json()
      setAuthState({ role: payload.role, signedIn: payload.ok })
      if (payload.ok) {
        setFormState((current) => ({ ...current, reviewer_role: payload.role }))
        setMessage(`Reviewer session established for ${payload.role}.`)
      } else {
        setMessage('Authentication failed. Please try a demo reviewer account.')
      }
    } catch (error) {
      setMessage('Login could not reach the backend service.')
    }
  }

  async function generateReview() {
    try {
      const response = await fetch(`${API_BASE_URL}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formState),
      })
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || 'Review generation failed')
      }
      const data = await response.json()
      setReport(data)
      setMessage(`Report status: ${data.status} | Evidence: ${data.evidence?.length || 0} | Bias flags: ${data.bias_flags?.length || 0}`)
    } catch (error) {
      setMessage(error.message || 'Review generation failed.')
    }
  }

  function exportJson() {
    if (!report) return
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'review-report.json'
    anchor.click()
    URL.revokeObjectURL(url)
  }

  async function exportPdf() {
    if (!report) return
    try {
      const response = await fetch(`${API_BASE_URL}/export/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(report),
      })
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || 'PDF export failed')
      }
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = 'review-report.pdf'
      anchor.click()
      URL.revokeObjectURL(url)
      setMessage('PDF export generated successfully.')
    } catch (error) {
      setMessage(error.message || 'PDF export failed.')
    }
  }

  function renderTabContent() {
    if (!report) return 'Generate a review to view Strengths, Bias Flags, or Evidence.'
    if (activeTab === 'strengths') return JSON.stringify(report.strengths, null, 2)
    if (activeTab === 'bias') return JSON.stringify(report.bias_flags, null, 2)
    return JSON.stringify(report.evidence, null, 2)
  }

  return (
    <div className="shell">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Bias-Aware Review Intelligence</span>
          <h1>360° Performance Review</h1>
          <p>Role-aware reviewer workspace with grounded evidence, bias visibility, and polished export actions.</p>
        </div>
        <div className="metric-row">
          {metrics.map((metric) => (
            <div key={metric.label} className="metric-card">
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="dashboard">
        <aside className="panel sidebar glass">
          <div className="section-title">Reviewer Control Center</div>

          <div className="card-box glass-card">
            <strong>Login</strong>
            <p className="muted">hr/hr123 • manager/mgr123 • reviewer/rev123</p>
            <input
              value={loginForm.username}
              onChange={(event) => setLoginForm({ ...loginForm, username: event.target.value })}
              placeholder="Username"
            />
            <input
              type="password"
              value={loginForm.password}
              onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })}
              placeholder="Password"
            />
            <button type="button" onClick={login}>Sign in</button>
            <div className="role-chip">{authState.signedIn ? `Signed in as ${authState.role}` : 'Not signed in'}</div>
          </div>

          <div className="card-box glass-card">
            <strong>View Mode</strong>
            {Object.entries(tabLabels).map(([key, label]) => (
              <button
                key={key}
                type="button"
                className={`tab-button ${activeTab === key ? 'active' : ''}`}
                onClick={() => setActiveTab(key)}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="card-box glass-card">
            <strong>Exports</strong>
            <button type="button" onClick={exportJson}>Export JSON</button>
            <button type="button" onClick={exportPdf}>Export PDF</button>
          </div>
        </aside>

        <main className="panel main-panel glass">
          <div className="section-title">Review Input Workspace</div>
          <div className="grid">
            <label>
              Employee ID
              <input value={formState.employee_id} onChange={(e) => setFormState({ ...formState, employee_id: e.target.value })} />
            </label>
            <label>
              Review Cycle
              <input value={formState.review_cycle} onChange={(e) => setFormState({ ...formState, review_cycle: e.target.value })} />
            </label>
            <label className="full">
              Self Assessment
              <textarea value={formState.self_assessment} onChange={(e) => setFormState({ ...formState, self_assessment: e.target.value })} />
            </label>
            <label className="full">
              Manager Feedback
              <textarea value={formState.manager_feedback} onChange={(e) => setFormState({ ...formState, manager_feedback: e.target.value })} />
            </label>
            <label className="full">
              Peer Feedback
              <textarea value={formState.peer_feedback.join('\n')} onChange={(e) => setFormState({ ...formState, peer_feedback: e.target.value.split(/\n+/).filter(Boolean) })} />
            </label>
            <label className="full">
              Goals
              <textarea value={formState.goals.join('\n')} onChange={(e) => setFormState({ ...formState, goals: e.target.value.split(/\n+/).filter(Boolean) })} />
            </label>
            <label className="full">
              Project Outcomes
              <textarea value={formState.project_outcomes.join('\n')} onChange={(e) => setFormState({ ...formState, project_outcomes: e.target.value.split(/\n+/).filter(Boolean) })} />
            </label>
            <label className="full">
              Meeting Notes
              <textarea value={formState.meeting_notes.join('\n')} onChange={(e) => setFormState({ ...formState, meeting_notes: e.target.value.split(/\n+/).filter(Boolean) })} />
            </label>
            <label>
              Reviewer Name
              <input value={formState.reviewer_name} onChange={(e) => setFormState({ ...formState, reviewer_name: e.target.value })} />
            </label>
            <label>
              Approval Decision
              <select value={formState.approval_decision} onChange={(e) => setFormState({ ...formState, approval_decision: e.target.value })}>
                <option value="approve">approve</option>
                <option value="reject">reject</option>
              </select>
            </label>
          </div>

          <div className="action-row">
            <button type="button" onClick={generateReview}>Generate Review</button>
          </div>

          <div className="section-title">Review Snapshot</div>
          <div className="summary-box">{message}</div>
          <pre className="result-card">{renderTabContent()}</pre>
        </main>
      </section>
    </div>
  )
}

export default App

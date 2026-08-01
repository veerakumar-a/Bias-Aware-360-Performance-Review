import { useMemo, useState } from 'react'
import './App.css'

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

  const tabLabels = useMemo(
    () => ({
      strengths: 'Strengths',
      bias: 'Bias Flags',
      evidence: 'Evidence',
    }),
    [],
  )

  async function login() {
    const response = await fetch('http://127.0.0.1:8000/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(loginForm),
    })
    const payload = await response.json()
    setAuthState({ role: payload.role, signedIn: payload.ok })
    if (payload.ok) {
      setFormState((current) => ({ ...current, reviewer_role: payload.role }))
    }
  }

  async function generateReview() {
    const response = await fetch('http://127.0.0.1:8000/review', {
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
    const response = await fetch('http://127.0.0.1:8000/export/pdf', {
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
        <h1>Bias-Aware 360° Performance Review</h1>
        <p>Role-aware reviewer dashboard with evidence grounded synthesis and export controls.</p>
      </section>

      <section className="dashboard">
        <aside className="panel sidebar">
          <div className="section-title">Reviewer Dashboard</div>

          <div className="card-box">
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
            <button type="button" onClick={login}>Login</button>
            <div className="role-chip">{authState.signedIn ? `Signed in as ${authState.role}` : 'Not signed in'}</div>
          </div>

          <div className="card-box">
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

          <div className="card-box">
            <strong>Exports</strong>
            <button type="button" onClick={exportJson}>Export JSON</button>
            <button type="button" onClick={exportPdf}>Export PDF</button>
          </div>
        </aside>

        <main className="panel main-panel">
          <div className="section-title">Review Inputs</div>
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

          <button type="button" onClick={generateReview}>Generate Review</button>

          <div className="section-title">Review Output</div>
          <div className="summary-box">{report ? `Report status: ${report.status}` : 'Ready to generate a grounded 360° review.'}</div>
          <pre className="result-card">{renderTabContent()}</pre>
        </main>
      </section>
    </div>
  )
}

export default App

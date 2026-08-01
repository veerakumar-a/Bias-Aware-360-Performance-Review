import { useState } from 'react'
import './App.css'

const featureCards = [
  {
    title: 'Grounded evidence synthesis',
    description: 'Combines self-assessment, manager notes, peer feedback, and project outcomes into a single review narrative with traceable evidence.',
  },
  {
    title: 'Bias visibility',
    description: 'Flags potentially skewed review language and highlights where fairness-sensitive wording should be reviewed before final approval.',
  },
  {
    title: 'Role-aware workflow',
    description: 'Supports HR, manager, and reviewer roles with a clear approval path and export-ready review summaries.',
  },
]

const workflowSteps = [
  'Collect structured review inputs across 360° sources.',
  'Retrieve evidence and evaluate claims for fairness and alignment.',
  'Generate strengths, bias flags, and an evidence-backed report.',
  'Export the output as JSON or PDF for reviewer sign-off.',
]

const techBadges = ['Python', 'FastAPI', 'React', 'Vite', 'Pydantic', 'ReportLab', 'FAISS', 'GitHub Actions']

const installSnippet = `pip install -r requirements.txt
python -m uvicorn app.website:app --reload`

function App() {
  const [copied, setCopied] = useState(false)

  async function copySnippet() {
    try {
      await navigator.clipboard.writeText(installSnippet)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className="landing-shell">
      <header className="topbar">
        <div className="brand">Bias-Aware 360</div>
        <nav className="nav-links" aria-label="Primary navigation">
          <a href="#overview">Overview</a>
          <a href="#features">Features</a>
          <a href="#architecture">How it works</a>
          <a href="#stack">Tech stack</a>
          <a href="#get-started">Get started</a>
        </nav>
      </header>

      <main>
        <section id="overview" className="hero-card">
          <div className="hero-copy">
            <span className="eyebrow">Bias-aware performance review intelligence</span>
            <h1>Bias-Aware 360 Performance Review</h1>
            <p>
              A grounded review intelligence system that turns self-assessment, manager feedback,
              peer input, and evidence into a fair, role-aware performance narrative.
            </p>
            <div className="hero-actions">
              <a className="primary-btn" href="#get-started">Get started</a>
              <a className="secondary-btn" href="https://github.com/veerakumar-a/Bias-Aware-360-Performance-Review" target="_blank" rel="noreferrer">View repo</a>
            </div>
          </div>

          <div className="hero-panel">
            <div className="status-card">
              <span className="status-label">Review readiness</span>
              <strong>Grounded • Fair • Exportable</strong>
            </div>
            <div className="mini-grid">
              <div>
                <span>Evidence points</span>
                <strong>360°</strong>
              </div>
              <div>
                <span>Bias review</span>
                <strong>Active</strong>
              </div>
              <div>
                <span>Export formats</span>
                <strong>JSON · PDF</strong>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="content-section">
          <div className="section-heading">
            <span className="section-kicker">Key capabilities</span>
            <h2>Designed for reviewer confidence</h2>
          </div>
          <div className="card-grid">
            {featureCards.map((card) => (
              <article key={card.title} className="info-card">
                <h3>{card.title}</h3>
                <p>{card.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="architecture" className="content-section">
          <div className="section-heading">
            <span className="section-kicker">How it works</span>
            <h2>From raw review signals to a usable report</h2>
          </div>
          <div className="timeline">
            {workflowSteps.map((step, index) => (
              <div key={step} className="timeline-item">
                <span className="step-badge">0{index + 1}</span>
                <p>{step}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="stack" className="content-section">
          <div className="section-heading">
            <span className="section-kicker">Technology</span>
            <h2>Built with a modern, deployable stack</h2>
          </div>
          <div className="badge-row">
            {techBadges.map((badge) => (
              <span key={badge} className="badge">{badge}</span>
            ))}
          </div>
        </section>

        <section id="get-started" className="content-section">
          <div className="section-heading">
            <span className="section-kicker">Getting started</span>
            <h2>Run locally in a few steps</h2>
          </div>
          <div className="snippet-card">
            <div className="snippet-header">
              <span>Install and launch</span>
              <button type="button" onClick={copySnippet}>
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <pre>{installSnippet}</pre>
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>Bias-Aware 360 Performance Review</p>
        <div className="footer-links">
          <a href="https://github.com/veerakumar-a/Bias-Aware-360-Performance-Review" target="_blank" rel="noreferrer">GitHub Repo</a>
          <span>•</span>
          <span>MIT License</span>
        </div>
      </footer>
    </div>
  )
}

export default App

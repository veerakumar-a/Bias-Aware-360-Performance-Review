from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app.agents import BiasAwareReviewOrchestrator
from app.auth import SimpleAuth
from app.exports import ExportService
from app.models import ReviewInput

app = FastAPI(title="Bias-Aware Review Website")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
auth_service = SimpleAuth()


class ReviewRequest(BaseModel):
    employee_id: str
    review_cycle: str
    self_assessment: str | None = None
    manager_feedback: str | None = None
    peer_feedback: list[str] = []
    goals: list[str] = []
    project_outcomes: list[str] = []
    meeting_notes: list[str] = []
    reviewer_name: str = "HR_Review_Manager"
    reviewer_role: str = "reviewer"
    approval_decision: str = "approve"


class AuthRequest(BaseModel):
    username: str
    password: str


HTML_PAGE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Bias-Aware 360 Review</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --card: #ffffff;
      --text: #14213d;
      --muted: #64748b;
      --accent: #2563eb;
      --accent-soft: #dbeafe;
      --border: #d9e2f0;
      --success: #0f766e;
      --warning: #b45309;
      --danger: #b91c1c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: linear-gradient(180deg, #eef4ff 0%, #f8fbff 100%);
      color: var(--text);
    }
    .shell {
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px;
    }
    .hero {
      background: linear-gradient(135deg, #0f172a, #1d4ed8);
      color: white;
      border-radius: 20px;
      padding: 24px;
      margin-bottom: 20px;
      box-shadow: 0 12px 30px rgba(37, 99, 235, 0.18);
    }
    .hero h1 { margin: 0 0 8px; font-size: 2rem; }
    .hero p { margin: 0; color: #dbeafe; }
    .dashboard {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 20px;
      align-items: start;
    }
    .panel {
      background: var(--card);
      border-radius: 18px;
      padding: 20px;
      border: 1px solid var(--border);
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
    }
    .section-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent);
      margin-bottom: 12px;
      font-weight: 700;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    label {
      display: block;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--text);
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px 13px;
      font-size: 0.97rem;
      color: var(--text);
      background: white;
      margin-bottom: 14px;
    }
    textarea { min-height: 110px; resize: vertical; }
    .full { grid-column: 1 / -1; }
    button {
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #fff;
      border: none;
      border-radius: 12px;
      padding: 12px 18px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      box-shadow: 0 8px 18px rgba(37, 99, 235, 0.28);
    }
    button:hover { transform: translateY(-1px); }
    button.secondary {
      background: #e2e8f0;
      color: #0f172a;
      box-shadow: none;
    }
    .status-pill {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: 10px;
    }
    .result-card {
      background: #0f172a;
      color: #ecf4ff;
      padding: 16px;
      border-radius: 14px;
      line-height: 1.5;
      overflow: auto;
      min-height: 320px;
      white-space: pre-wrap;
    }
    .sidebar-list {
      display: grid;
      gap: 10px;
    }
    .sidebar-item {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      background: #f8fbff;
    }
    .tab-btn {
      width: 100%;
      text-align: left;
      margin-bottom: 8px;
    }
    .tab-btn.active {
      background: #0f172a;
    }
    .muted { color: var(--muted); }
    .summary-box {
      padding: 12px;
      background: #f8fbff;
      border: 1px solid var(--border);
      border-radius: 12px;
      margin-bottom: 10px;
    }
    .role-badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: #ecfdf5;
      color: #047857;
      font-size: 0.8rem;
      font-weight: 700;
    }
    @media (max-width: 980px) {
      .dashboard { grid-template-columns: 1fr; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class=\"shell\">
    <div class=\"hero\">
      <h1>Bias-Aware 360° Performance Review</h1>
      <p>Grounded review synthesis with evidence retrieval, bias detection, and reviewer approval.</p>
    </div>

    <div class=\"dashboard\">
      <aside class=\"panel\">
        <div class=\"section-title\">Reviewer Dashboard</div>
        <div class=\"sidebar-list\">
          <div class=\"sidebar-item\">
            <strong>Login</strong><br />
            <span class=\"muted\">Use: hr/hr123, manager/mgr123, reviewer/rev123</span>
            <form id=\"loginForm\">
              <label>Username<input name=\"username\" value=\"hr\"></label>
              <label>Password<input name=\"password\" type=\"password\" value=\"hr123\"></label>
              <button type=\"submit\" class=\"secondary\">Login</button>
            </form>
            <div id=\"loginStatus\" class=\"role-badge\">Not signed in</div>
          </div>

          <div class=\"sidebar-item\">
            <strong>View Mode</strong>
            <button class=\"tab-btn active\" data-tab=\"strengths\">Strengths</button>
            <button class=\"tab-btn\" data-tab=\"bias\">Bias Flags</button>
            <button class=\"tab-btn\" data-tab=\"evidence\">Evidence</button>
          </div>

          <div class=\"sidebar-item\">
            <strong>Exports</strong><br />
            <button type=\"button\" id=\"exportJson\" class=\"secondary\">Export JSON</button>
            <button type=\"button\" id=\"exportPdf\" class=\"secondary\">Export PDF</button>
          </div>
        </div>
      </aside>

      <main class=\"panel\">
        <div class=\"section-title\">Review Inputs</div>
        <form id=\"reviewForm\">
          <div class=\"grid\">
            <div>
              <label>Employee ID<input name=\"employee_id\" value=\"EMP-001\" required></label>
            </div>
            <div>
              <label>Review Cycle<input name=\"review_cycle\" value=\"2026-Q3\" required></label>
            </div>
            <div class=\"full\">
              <label>Self Assessment<textarea name=\"self_assessment\">Delivered a high-impact AI workflow and improved cross-functional handoffs.</textarea></label>
            </div>
            <div class=\"full\">
              <label>Manager Feedback<textarea name=\"manager_feedback\">Strong ownership and measurable impact. Needs clearer follow-through on documentation.</textarea></label>
            </div>
            <div class=\"full\">
              <label>Peer Feedback<textarea name=\"peer_feedback\">Collaborative and dependable during project execution.\nHelpful in aligning engineering and product teams.</textarea></label>
            </div>
            <div class=\"full\">
              <label>Goals<textarea name=\"goals\">Improve reliability of retrieval pipelines\nExpand mentoring support</textarea></label>
            </div>
            <div class=\"full\">
              <label>Project Outcomes<textarea name=\"project_outcomes\">Improved operational efficiency by 18%.\nReduced incident response time.</textarea></label>
            </div>
            <div class=\"full\">
              <label>Meeting Notes<textarea name=\"meeting_notes\">Weekly review noted strong delivery quality and communication.</textarea></label>
            </div>
            <div>
              <label>Reviewer Name<input name=\"reviewer_name\" value=\"HR_Review_Manager\"></label>
            </div>
            <div>
              <label>Approval Decision<select name=\"approval_decision\"><option value=\"approve\">approve</option><option value=\"reject\">reject</option></select></label>
            </div>
          </div>
          <br />
          <button type=\"submit\" id=\"submitBtn\">Generate Review</button>
        </form>

        <div class=\"section-title\">Review Output</div>
        <div id=\"resultSummary\" class=\"summary-box\">Ready to generate a grounded 360° review.</div>
        <div id=\"result\" class=\"result-card\">Your structured review will appear here.</div>
      </main>
    </div>
  </div>

  <script>
    const form = document.getElementById('reviewForm');
    const loginForm = document.getElementById('loginForm');
    const result = document.getElementById('result');
    const resultSummary = document.getElementById('resultSummary');
    const submitBtn = document.getElementById('submitBtn');
    const exportJsonBtn = document.getElementById('exportJson');
    const exportPdfBtn = document.getElementById('exportPdf');
    const loginStatus = document.getElementById('loginStatus');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabMap = { strengths: 'strengths', bias: 'bias_flags', evidence: 'evidence' };
    let currentReport = null;

    const parseLines = (value) => String(value || '').split(/\n+/).map((v) => v.trim()).filter(Boolean);

    const renderTab = (tabName) => {
      if (!currentReport) {
        result.textContent = 'Generate a review first to see dashboard details.';
        return;
      }
      const field = tabMap[tabName] || 'strengths';
      const data = currentReport[field] || [];
      result.textContent = JSON.stringify(data, null, 2);
    };

    tabButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        tabButtons.forEach((item) => item.classList.remove('active'));
        btn.classList.add('active');
        renderTab(btn.dataset.tab);
      });
    });

    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(loginForm);
      const payload = {
        username: formData.get('username'),
        password: formData.get('password')
      };
      const response = await fetch('/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const authData = await response.json();
      loginStatus.textContent = authData.ok ? `Signed in as ${authData.role}` : 'Access denied';
      if (authData.ok) {
        resultSummary.textContent = `Reviewer role: ${authData.role}`;
      }
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      submitBtn.disabled = true;
      submitBtn.textContent = 'Generating...';
      resultSummary.textContent = 'Review in progress...';

      const formData = new FormData(form);
      const payload = {
        employee_id: formData.get('employee_id'),
        review_cycle: formData.get('review_cycle'),
        self_assessment: formData.get('self_assessment'),
        manager_feedback: formData.get('manager_feedback'),
        peer_feedback: parseLines(formData.get('peer_feedback')),
        goals: parseLines(formData.get('goals')),
        project_outcomes: parseLines(formData.get('project_outcomes')),
        meeting_notes: parseLines(formData.get('meeting_notes')),
        reviewer_name: formData.get('reviewer_name'),
        reviewer_role: loginStatus.textContent.includes('Signed in as') ? loginStatus.textContent.split('Signed in as ')[1] : 'reviewer',
        approval_decision: formData.get('approval_decision')
      };

      try {
        const response = await fetch('/review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        currentReport = data;
        const statusText = data.status ? data.status.toUpperCase() : 'UNKNOWN';
        resultSummary.textContent = `Report status: ${statusText} | Evidence count: ${data.evidence?.length || 0} | Bias flags: ${data.bias_flags?.length || 0}`;
        result.textContent = JSON.stringify(data, null, 2);
        renderTab('strengths');
      } catch (error) {
        resultSummary.textContent = 'There was a problem generating the report.';
        result.textContent = String(error);
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate Review';
      }
    });

    exportJsonBtn.addEventListener('click', () => {
      if (!currentReport) {
        resultSummary.textContent = 'Generate a report before exporting JSON.';
        return;
      }
      const blob = new Blob([JSON.stringify(currentReport, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'review-report.json';
      anchor.click();
      URL.revokeObjectURL(url);
    });

    exportPdfBtn.addEventListener('click', () => {
      if (!currentReport) {
        resultSummary.textContent = 'Generate a report before exporting PDF.';
        return;
      }
      resultSummary.textContent = 'PDF export prepared for print-friendly output.';
      result.textContent = JSON.stringify(currentReport, null, 2);
      window.print();
    });
  </script>
</body>
</html>
"""


@app.post("/auth")
def login(payload: AuthRequest, response: Response):
    user = auth_service.authenticate(payload.username, payload.password)
    if not user:
        return {"ok": False, "role": None}

    token = auth_service.create_session(user)
    response.set_cookie(
        key="reviewer_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"ok": True, "role": user.role}


@app.post("/review")
def generate_review(payload: ReviewRequest, request: Request):
    session_role = auth_service.validate_session(request.cookies.get("reviewer_session"))
    if session_role is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required. Please sign in from the reviewer dashboard."},
        )

    review_input = ReviewInput(
        employee_id=payload.employee_id,
        review_cycle=payload.review_cycle,
        self_assessment=payload.self_assessment,
        manager_feedback=payload.manager_feedback,
        peer_feedback=payload.peer_feedback,
        goals=payload.goals,
        project_outcomes=payload.project_outcomes,
        meeting_notes=payload.meeting_notes,
    )

    orchestrator = BiasAwareReviewOrchestrator()
    report = orchestrator.run(
        review_input,
        reviewer_name=payload.reviewer_name,
        approval_decision=payload.approval_decision,
    )

    if session_role not in {"hr", "manager"} and report.status == "approved":
        report.status = "under_review"
        report.approval_notes = "Role-limited reviewer cannot finalize approval in this environment."

    return report.model_dump()


@app.post("/export/pdf")
def export_review_pdf(payload: dict[str, Any], request: Request):
    session_role = auth_service.validate_session(request.cookies.get("reviewer_session"))
    if session_role is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required to export a PDF report."},
        )

    pdf_bytes = ExportService.to_pdf_bytes(payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="review-report.pdf"'},
    )


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(HTML_PAGE)

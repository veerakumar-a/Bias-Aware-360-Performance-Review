from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.agents import BiasAwareReviewOrchestrator
from app.models import ReviewInput

app = FastAPI(title="Bias-Aware 360 Review API")


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
    approval_decision: str = "approve"


@app.post("/review")
def generate_review(payload: ReviewRequest):
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
    return report.model_dump()

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    SELF_ASSESSMENT = "self_assessment"
    MANAGER_FEEDBACK = "manager_feedback"
    PEER_FEEDBACK = "peer_feedback"
    GOAL = "goal"
    PROJECT_OUTCOME = "project_outcome"
    MEETING_NOTE = "meeting_note"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class FeedbackSource(BaseModel):
    source_id: str
    source_type: SourceType
    author_role: str
    author_name: Optional[str] = None
    timestamp: Optional[str] = None
    raw_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReviewInput(BaseModel):
    employee_id: str
    review_cycle: str
    self_assessment: Optional[str] = None
    manager_feedback: Optional[str] = None
    peer_feedback: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    project_outcomes: List[str] = Field(default_factory=list)
    meeting_notes: List[str] = Field(default_factory=list)
    policy_constraints: List[str] = Field(default_factory=list)


class EvidenceCitation(BaseModel):
    evidence_id: str
    source_id: str
    snippet: str
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    rationale: str


class BiasFlag(BaseModel):
    bias_type: str
    severity: Literal["low", "medium", "high"]
    explanation: str
    evidence_ids: List[str] = Field(default_factory=list)
    recommended_action: str


class ReviewFinding(BaseModel):
    category: Literal["strength", "growth_area", "impact_highlight", "goal_progress"]
    summary: str
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class PerformanceReviewReport(BaseModel):
    employee_id: str
    review_cycle: str
    status: ReviewStatus = ReviewStatus.DRAFT
    strengths: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    impact_highlights: List[str] = Field(default_factory=list)
    goal_progress: List[str] = Field(default_factory=list)
    evidence: List[EvidenceCitation] = Field(default_factory=list)
    bias_flags: List[BiasFlag] = Field(default_factory=list)
    approval_required: bool = True
    approved_by: Optional[str] = None
    approval_notes: Optional[str] = None

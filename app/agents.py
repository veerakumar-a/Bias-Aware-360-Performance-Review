from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List

from app.models import (
    BiasFlag,
    EvidenceCitation,
    PerformanceReviewReport,
    ReviewFinding,
    ReviewInput,
    ReviewStatus,
    SourceType,
)
from app.retrieval import DocumentChunk, InMemoryVectorStore


BIAS_DETECTION_PROMPT = """
You are a bias-aware reviewer assistant.

Analyze the supplied evidence and identify any of the following issues:
- recency bias
- confirmation bias
- halo effect
- attribution bias
- stakeholder imbalance
- unsupported claim
- lack of evidence

For each issue, return a JSON object with:
- bias_type
- severity
- explanation
- evidence_ids
- recommended_action

You must only report issues that are supported by evidence in the source material.
"""


@dataclass
class AgentResult:
    findings: List[ReviewFinding]
    evidence: List[EvidenceCitation]
    bias_flags: List[BiasFlag]


class FeedbackCollectionAgent:
    def collect(self, review_input: ReviewInput) -> List[Dict[str, str]]:
        sources: List[Dict[str, str]] = []
        if review_input.self_assessment:
            sources.append({"source_type": SourceType.SELF_ASSESSMENT.value, "text": review_input.self_assessment})
        if review_input.manager_feedback:
            sources.append({"source_type": SourceType.MANAGER_FEEDBACK.value, "text": review_input.manager_feedback})
        for item in review_input.peer_feedback:
            sources.append({"source_type": SourceType.PEER_FEEDBACK.value, "text": item})
        for item in review_input.goals:
            sources.append({"source_type": SourceType.GOAL.value, "text": item})
        for item in review_input.project_outcomes:
            sources.append({"source_type": SourceType.PROJECT_OUTCOME.value, "text": item})
        for item in review_input.meeting_notes:
            sources.append({"source_type": SourceType.MEETING_NOTE.value, "text": item})
        return sources


class EvidenceRetrievalAgent:
    def __init__(self, store: InMemoryVectorStore | None = None) -> None:
        self.store = store or InMemoryVectorStore()

    def ingest_sources(self, sources: List[Dict[str, str]]) -> None:
        self.store.clear()
        for index, source in enumerate(sources, start=1):
            self.store.add_document(
                DocumentChunk(
                    doc_id=f"doc-{index}",
                    source_id=f"src-{index}",
                    text=source["text"],
                    metadata={"source_type": source.get("source_type", "unknown")},
                )
            )

    def retrieve(self, sources: List[Dict[str, str]], query: str) -> List[EvidenceCitation]:
        self.ingest_sources(sources)
        hits = self.store.search(query=query, top_k=5)
        evidence: List[EvidenceCitation] = []

        for index, (document, similarity) in enumerate(hits, start=1):
            evidence.append(
                EvidenceCitation(
                    evidence_id=f"ev-{index}",
                    source_id=document.source_id,
                    snippet=document.text[:300],
                    relevance_score=round(similarity, 2),
                    rationale=(
                        f"Retrieved from the vector-backed store with similarity {round(similarity, 2)} for '{query}'."
                    ),
                )
            )

        if not evidence and sources:
            fallback = sources[0]["text"]
            evidence.append(
                EvidenceCitation(
                    evidence_id="ev-1",
                    source_id="src-1",
                    snippet=fallback[:300],
                    relevance_score=0.35,
                    rationale="Fallback evidence used because the vector search returned no hits.",
                )
            )

        return evidence[:5]


class SynthesisBiasAgent:
    def synthesize(self, evidence: List[EvidenceCitation]) -> AgentResult:
        findings: List[ReviewFinding] = []
        if evidence:
            findings.append(
                ReviewFinding(
                    category="strength",
                    summary="Evidence indicates sustained delivery and positive stakeholder feedback.",
                    evidence_ids=[evidence[0].evidence_id],
                    confidence=0.79,
                )
            )
            findings.append(
                ReviewFinding(
                    category="impact_highlight",
                    summary="Evidence points to measurable impact on business outcomes and team execution.",
                    evidence_ids=[evidence[1].evidence_id] if len(evidence) > 1 else [evidence[0].evidence_id],
                    confidence=0.74,
                )
            )
            findings.append(
                ReviewFinding(
                    category="goal_progress",
                    summary="Goal progress is supported by source material tying milestone delivery to measurable efficiency gains.",
                    evidence_ids=[evidence[-1].evidence_id],
                    confidence=0.71,
                )
            )

        bias_flags = self.detect_biases(evidence)
        return AgentResult(findings=findings, evidence=evidence, bias_flags=bias_flags)

    def detect_biases(self, evidence: List[EvidenceCitation]) -> List[BiasFlag]:
        if not evidence:
            return [
                BiasFlag(
                    bias_type="lack_of_evidence",
                    severity="high",
                    explanation="No supporting evidence was found for the review conclusion.",
                    evidence_ids=[],
                    recommended_action="Request additional source artifacts before finalizing the report.",
                )
            ]

        flags: List[BiasFlag] = []
        if len(evidence) < 3:
            flags.append(
                BiasFlag(
                    bias_type="stakeholder_imbalance",
                    severity="medium",
                    explanation="The review relies on too few sources to represent a balanced 360° picture.",
                    evidence_ids=[evidence[0].evidence_id],
                    recommended_action="Collect additional peer or manager input before approval.",
                )
            )
        return flags

    def build_bias_detection_prompt(self, evidence: List[EvidenceCitation]) -> str:
        payload = {"evidence": [e.json() for e in evidence]}
        return BIAS_DETECTION_PROMPT + "\n\nEvidence payload:\n" + json.dumps(payload, indent=2)


class ReportGenerationAgent:
    def build_report(self, review_input: ReviewInput, result: AgentResult) -> PerformanceReviewReport:
        strengths = [f.summary for f in result.findings if f.category == "strength"]
        growth_areas = ["Clarify ownership expectations and expand evidence collection for underrepresented feedback."]
        impact_highlights = [f.summary for f in result.findings if f.category == "impact_highlight"]
        goal_progress = ["Goal progress should be validated through measurable milestones and verified project outcomes."]

        report = PerformanceReviewReport(
            employee_id=review_input.employee_id,
            review_cycle=review_input.review_cycle,
            status=ReviewStatus.DRAFT,
            strengths=strengths,
            growth_areas=growth_areas,
            impact_highlights=impact_highlights,
            goal_progress=goal_progress,
            evidence=result.evidence,
            bias_flags=result.bias_flags,
            approval_required=True,
        )
        return report


class HumanApprovalCheckpoint:
    def request_approval(
        self,
        report: PerformanceReviewReport,
        reviewer_name: str,
        decision: str | None = None,
    ) -> PerformanceReviewReport:
        if decision is None:
            decision = input(
                f"Reviewer '{reviewer_name}', approve this report? Enter 'approve' or 'reject': "
            ).strip().lower()
        else:
            decision = decision.strip().lower()

        if decision == "approve":
            report.status = ReviewStatus.APPROVED
            report.approved_by = reviewer_name
            report.approval_notes = "Approved after evidence review and bias screening."
        else:
            report.status = ReviewStatus.REJECTED
            report.approved_by = reviewer_name
            report.approval_notes = "Rejected pending additional evidence or reviewer edits."

        return report


class BiasAwareReviewOrchestrator:
    def __init__(self, retriever: EvidenceRetrievalAgent | None = None) -> None:
        self.collector = FeedbackCollectionAgent()
        self.retriever = retriever or EvidenceRetrievalAgent()
        self.synthesizer = SynthesisBiasAgent()
        self.report_agent = ReportGenerationAgent()
        self.approval = HumanApprovalCheckpoint()

    def run(
        self,
        review_input: ReviewInput,
        reviewer_name: str,
        approval_decision: str | None = None,
    ) -> PerformanceReviewReport:
        sources = self.collector.collect(review_input)
        evidence = self.retriever.retrieve(sources, query="strengths impact business outcomes")
        if not evidence:
            evidence = self.retriever.retrieve(sources, query="performance")

        result = self.synthesizer.synthesize(evidence)
        report = self.report_agent.build_report(review_input, result)
        approved_report = self.approval.request_approval(report, reviewer_name, decision=approval_decision)
        return approved_report

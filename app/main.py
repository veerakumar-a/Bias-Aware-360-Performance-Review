from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agents import BiasAwareReviewOrchestrator
from app.models import ReviewInput


if __name__ == "__main__":
    review_input = ReviewInput(
        employee_id="EMP-001",
        review_cycle="2026-Q3",
        self_assessment="Delivered a high-impact AI workflow and improved cross-functional handoffs.",
        manager_feedback="Strong ownership and measurable impact. Needs clearer follow-through on documentation.",
        peer_feedback=[
            "Collaborative and dependable during project execution.",
            "Helpful in aligning engineering and product teams.",
        ],
        goals=["Improve reliability of retrieval pipelines", "Expand mentoring support"],
        project_outcomes=["Improved operational efficiency by 18%.", "Reduced incident response time."],
        meeting_notes=["Weekly review noted strong delivery quality and communication."],
    )

    orchestrator = BiasAwareReviewOrchestrator()
    final_report = orchestrator.run(review_input, reviewer_name="HR_Review_Manager")
    print(final_report.model_dump_json(indent=2))

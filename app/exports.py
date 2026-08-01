from __future__ import annotations

import json
from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class ExportService:
    @staticmethod
    def to_json(data: Any) -> str:
        return json.dumps(data, indent=2)

    @staticmethod
    def to_pdf_bytes(data: Any) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40,
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Bias-Aware 360° Performance Review", styles["Title"]),
            Spacer(1, 12),
            Paragraph(
                f"Employee: {data.get('employee_id', 'N/A')} | Cycle: {data.get('review_cycle', 'N/A')}",
                styles["Normal"],
            ),
            Spacer(1, 12),
        ]

        for heading, value in (
            ("Status", data.get("status", "draft")),
            ("Strengths", data.get("strengths", [])),
            ("Growth Areas", data.get("growth_areas", [])),
            ("Impact Highlights", data.get("impact_highlights", [])),
            ("Goal Progress", data.get("goal_progress", [])),
            ("Bias Flags", data.get("bias_flags", [])),
            ("Evidence", data.get("evidence", [])),
        ):
            story.append(Paragraph(f"<b>{heading}</b>", styles["Heading2"]))
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        text = item.get("snippet") or item.get("bias_type") or json.dumps(item)
                    else:
                        text = str(item)
                    story.append(Paragraph(f"• {text}", styles["BodyText"]))
            else:
                story.append(Paragraph(str(value), styles["BodyText"]))
            story.append(Spacer(1, 8))

        document.build(story)
        return buffer.getvalue()

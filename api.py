from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from nodes.orchestrator import orchestrator
from nodes.worker import llm_call
from nodes.synthesizer import synthesizer
from state.state import State

import tempfile
import re
import logging

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)

from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER


# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="Reportly API",
    description="Async Multi-Agent Report Generator",
    version="2.0"
)


# =========================
# REQUEST MODEL
# =========================

class ReportRequest(BaseModel):
    topic: str


# =========================
# WORKFLOW
# =========================

def assign_workers(state: State):

    return [
        Send("llm_call", {"section": s})
        for s in state["sections"]
    ]


builder = StateGraph(State)

builder.add_node("orchestrator", orchestrator)
builder.add_node("llm_call", llm_call)
builder.add_node("synthesizer", synthesizer)

builder.add_edge(START, "orchestrator")

builder.add_conditional_edges(
    "orchestrator",
    assign_workers,
    {"llm_call": "llm_call"},
)

builder.add_edge("llm_call", "synthesizer")
builder.add_edge("synthesizer", END)

workflow = builder.compile()


# =========================
# HEALTH CHECK
# =========================

@app.get("/")
async def health():

    return {
        "status": "Reportly Async API running"
    }


# =========================
# GENERATE REPORT
# =========================

@app.post("/generate-report")
async def generate_report(request: ReportRequest):

    try:

        if not request.topic.strip():

            raise HTTPException(
                status_code=400,
                detail="Topic cannot be empty"
            )

        logger.info(
            f"Generating report for topic: {request.topic}"
        )

        result = await run_in_threadpool(
            workflow.invoke,
            {
                "topic": request.topic
            }
        )

        report_text = result.get("final_report")

        if not report_text:

            raise HTTPException(
                status_code=500,
                detail="Report generation failed"
            )

        return {
            "final_report": report_text
        }

    except HTTPException as e:

        raise e

    except Exception as e:

        logger.error(
            f"Unexpected error in generate_report: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# =========================
# PAGE NUMBER
# =========================

def add_page_number(canvas, doc):

    page_num = canvas.getPageNumber()

    canvas.drawRightString(
        200 * mm,
        15 * mm,
        f"Page {page_num}"
    )


# =========================
# CREATE PDF
# =========================

def create_pdf(report_text):

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    file_path = temp_file.name
    temp_file.close()

    doc = SimpleDocTemplate(
        file_path,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="Title",
        fontName="Helvetica-Bold",
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=24,
    )

    heading_style = ParagraphStyle(
        name="Heading",
        fontName="Helvetica-Bold",
        fontSize=16,
        spaceBefore=16,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        name="Body",
        fontSize=12,
        leading=16,
        spaceAfter=10,
    )

    elements = []

    elements.append(
        Paragraph(
            "Generated Report",
            title_style
        )
    )

    elements.append(
        Spacer(1, 12)
    )

    lines = report_text.split("\n")

    bullet_items = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):

            text = re.sub(
                r"#",
                "",
                line
            ).strip()

            elements.append(
                Paragraph(
                    text,
                    heading_style
                )
            )

        elif line.startswith("-"):

            clean = re.sub(
                r"[-*]",
                "",
                line
            ).strip()

            bullet_items.append(
                ListItem(
                    Paragraph(
                        clean,
                        body_style
                    )
                )
            )

        else:

            if bullet_items:

                elements.append(
                    ListFlowable(
                        bullet_items,
                        bulletType="bullet"
                    )
                )

                bullet_items = []

            line = re.sub(
                r"\*\*(.*?)\*\*",
                r"<b>\1</b>",
                line
            )

            elements.append(
                Paragraph(
                    line,
                    body_style
                )
            )

        elements.append(
            Spacer(1, 6)
        )

    if bullet_items:

        elements.append(
            ListFlowable(
                bullet_items,
                bulletType="bullet"
            )
        )

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return file_path


# =========================
# GENERATE PDF
# =========================

@app.post("/generate-report-pdf")
async def generate_report_pdf(request: ReportRequest):

    try:

        if not request.topic.strip():

            raise HTTPException(
                status_code=400,
                detail="Topic cannot be empty"
            )

        logger.info(
            f"Generating PDF for topic: {request.topic}"
        )

        result = await run_in_threadpool(
            workflow.invoke,
            {
                "topic": request.topic
            }
        )

        report_text = result.get("final_report")

        if not report_text:

            raise HTTPException(
                status_code=500,
                detail="Report generation failed"
            )

        file_path = await run_in_threadpool(
            create_pdf,
            report_text
        )

        return FileResponse(
            path=file_path,
            filename="report.pdf",
            media_type="application/pdf"
        )

    except HTTPException as e:

        raise e

    except Exception as e:

        logger.error(
            f"Unexpected error in generate_report_pdf: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import logging
import uuid
import os

from main import orchestrator_worker

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title="Reportly API",
    description="Generate structured AI reports and download as PDF",
    version="1.0.0"
)

# --------------------------------------------------
# Request Model
# --------------------------------------------------

class ReportRequest(BaseModel):
    topic: str

# --------------------------------------------------
# Health Check Endpoint
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Reportly API is running"
    }

# --------------------------------------------------
# PDF Generator Function
# --------------------------------------------------

def generate_pdf(report_text: str, file_path: str):
    try:
        doc = SimpleDocTemplate(file_path)

        styles = getSampleStyleSheet()

        elements = []

        title = Paragraph(
            "<b>Generated Report</b>",
            styles["Title"]
        )

        elements.append(title)

        elements.append(
            Spacer(1, 12)
        )

        paragraphs = report_text.split("\n")

        for para in paragraphs:
            if para.strip():
                p = Paragraph(
                    para,
                    styles["BodyText"]
                )
                elements.append(p)

                elements.append(
                    Spacer(1, 12)
                )

        doc.build(elements)

        logger.info("PDF generated successfully")

    except Exception as e:

        logger.error(
            f"PDF generation failed: {str(e)}"
        )

        raise

# --------------------------------------------------
# Generate Report Endpoint
# --------------------------------------------------

@app.post("/generate-report")
async def generate_report(request: ReportRequest):

    try:

        logger.info(
            f"Received request for topic: {request.topic}"
        )

        # Run workflow safely
        result = await run_in_threadpool(
            orchestrator_worker.invoke,
            {
                "topic": request.topic
            }
        )

        report_text = result.get(
            "final_report"
        )

        if not report_text:

            raise HTTPException(
                status_code=500,
                detail="Report generation failed"
            )

        file_name = f"report_{uuid.uuid4().hex}.pdf"

        file_path = os.path.join(
            "reports",
            file_name
        )

        os.makedirs(
            "reports",
            exist_ok=True
        )

        # Generate PDF safely
        await run_in_threadpool(
            generate_pdf,
            report_text,
            file_path
        )

        logger.info(
            "Report generated successfully"
        )

        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="application/pdf"
        )

    except HTTPException as e:

        raise e

    except Exception as e:

        logger.error(
            f"Unexpected error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
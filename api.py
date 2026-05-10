import sys
import os
import uuid

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel

from src.workflow.main import orchestrator_worker

from src.utils.logger import logger

from src.services.pdf.client import generate_pdf


# -----------------------------------------
# FastAPI App
# -----------------------------------------

app = FastAPI(
    title="Reportly API",
    description="AI Report Generator using LangGraph and Tavily",
    version="1.0.0"
)

# -----------------------------------------
# Request Schema
# -----------------------------------------

class ReportRequest(BaseModel):

    topic: str


# -----------------------------------------
# Health Check
# -----------------------------------------

@app.get("/")
async def root():

    logger.info(
        "Health check endpoint called"
    )

    return {
        "message": "Reportly API Running"
    }


# -----------------------------------------
# Generate Report Endpoint
# -----------------------------------------

@app.post("/generate-report")
async def generate_report(
    request: ReportRequest
):

    try:

        logger.info(
            f"Generating report for topic: {request.topic}"
        )

        # -----------------------------------------
        # Generate Report
        # -----------------------------------------

        result = await orchestrator_worker.ainvoke(
            {
                "topic": request.topic
            }
        )

        report = result.get(
            "final_report"
        )

        if not report:

            raise HTTPException(
                status_code=500,
                detail="Report generation failed"
            )

        # -----------------------------------------
        # Create Reports Folder
        # -----------------------------------------

        os.makedirs(
            "reports",
            exist_ok=True
        )

        # -----------------------------------------
        # Generate PDF File Name
        # -----------------------------------------

        file_name = (
            f"{uuid.uuid4().hex}.pdf"
        )

        output_path = os.path.join(
            "reports",
            file_name
        )

        # -----------------------------------------
        # Generate PDF
        # -----------------------------------------

        generate_pdf(
            topic=request.topic,
            report_text=report,
            output_path=output_path
        )

        logger.info(
            "Report PDF generated successfully"
        )

        # -----------------------------------------
        # Return PDF
        # -----------------------------------------

        return FileResponse(
            path=output_path,
            filename=file_name,
            media_type="application/pdf"
        )

    except HTTPException as http_error:

        logger.error(
            f"HTTP Error: {http_error.detail}"
        )

        raise http_error

    except Exception as e:

        logger.error(
            f"Unexpected Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
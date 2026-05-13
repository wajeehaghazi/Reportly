import os
import uuid
import asyncio

from src.celery_worker import celery_app

from src.workflow.main import orchestrator_worker

from src.services.pdf.client import generate_pdf

from src.utils.logger import logger


@celery_app.task(bind=True)
def generate_report_task(self, topic: str):

    try:

        result = asyncio.run(
            orchestrator_worker.ainvoke(
                {
                    "topic": topic
                }
            )
        )

        report = result.get(
            "final_report"
        )

        if not report:

            return {
                "status": "failed"
            }

        os.makedirs(
            "reports",
            exist_ok=True
        )

        file_name = f"{uuid.uuid4().hex}.pdf"

        output_path = os.path.join(
            "reports",
            file_name
        )

        generate_pdf(
            topic=topic,
            report_text=report,
            output_path=output_path
        )

        logger.info(
            f"Report generated successfully: {file_name}"
        )

        return {
            "status": "completed",
            "file_name": file_name,
            "path": output_path
        }

    except Exception as e:

        logger.error(
            f"Celery task failed: {e}"
        )

        return {
            "status": "failed",
            "error": str(e)
        }
import sys
import os
import asyncio

from celery.result import AsyncResult

from sse_starlette.sse import (
    EventSourceResponse
)

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from fastapi import (
    FastAPI,
    HTTPException
)

from fastapi.responses import (
    FileResponse
)

from pydantic import BaseModel

from src.tasks.report_task import (
    generate_report_task
)

from src.utils.logger import logger


# -----------------------------------------
# FASTAPI APP
# -----------------------------------------

app = FastAPI(
    title="Reportly API",
    description="AI Report Generator using LangGraph and Tavily",
    version="2.0.0"
)


# -----------------------------------------
# REQUEST SCHEMA
# -----------------------------------------

class ReportRequest(BaseModel):


    topic: str


# -----------------------------------------
# HEALTH CHECK
# -----------------------------------------

@app.get("/")
async def root():

    logger.info(
        "Health check endpoint called"
    )


    logger.info(
        "Health check endpoint called"
    )

    return {
        "message": "Reportly API Running"
        "message": "Reportly API Running"
    }


# -----------------------------------------
# GENERATE REPORT
# -----------------------------------------

@app.post("/generate-report")
async def generate_report(
    request: ReportRequest
):

    try:

        logger.info(
            f"Queueing report request: {request.topic}"
        )

        # -----------------------------------------
        # ADD TASK TO QUEUE
        # -----------------------------------------

        task = generate_report_task.delay(
            request.topic
        )

        logger.info(
            f"Task queued successfully: {task.id}"
        )

        # -----------------------------------------
        # RETURN TASK ID
        # -----------------------------------------

        return {
            "message": "Report request queued",
            "task_id": task.id
        }

    except Exception as e:

        logger.error(
            f"Queue Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to queue report task"
        )


# -----------------------------------------
# SSE STREAM ENDPOINT
# -----------------------------------------

@app.get("/stream/{task_id}")
async def stream_task_status(
    task_id: str
):

    async def event_generator():

        while True:

            try:

                task_result = AsyncResult(
                    task_id,
                    app=generate_report_task.app
                )

                # -----------------------------------------
                # TASK SUCCESS
                # -----------------------------------------

                if task_result.state == "SUCCESS":

                    result = task_result.result

                    yield {
                        "event": "completed",
                        "data": str(result)
                    }

                    break

                # -----------------------------------------
                # TASK FAILURE
                # -----------------------------------------

                elif task_result.state == "FAILURE":

                    yield {
                        "event": "failed",
                        "data": "Report generation failed"
                    }

                    break

                # -----------------------------------------
                # TASK PROCESSING
                # -----------------------------------------

                else:

                    yield {
                        "event": "processing",
                        "data": f"Current State: {task_result.state}"
                    }

                await asyncio.sleep(2)

            except Exception as e:

                logger.error(
                    f"SSE Error: {str(e)}"
                )

                yield {
                    "event": "error",
                    "data": "Streaming error occurred"
                }

                break

    return EventSourceResponse(
        event_generator()
    )


# -----------------------------------------
# DOWNLOAD REPORT
# -----------------------------------------

@app.get("/download-report/{file_name}")
async def download_report(
    file_name: str
):

    file_path = os.path.join(
        "reports",
        file_name
    )

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

        # -----------------------------------------
        # Return PDF
        # -----------------------------------------

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/pdf"
    )
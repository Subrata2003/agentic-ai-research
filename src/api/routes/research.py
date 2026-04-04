"""
Research routes:
    POST /api/v1/research               → start a research job
    WS   /api/v1/research/{job_id}/stream → live progress stream
"""

import asyncio
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect

from src.agent.research_agent import ResearchAgent
from src.api.schemas import ResearchJobResponse, ResearchRequest
from src.api.websocket_manager import manager, make_progress_callback

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# In-memory job registry
# ---------------------------------------------------------------------------
# Maps job_id → {"status": str, "topic": str, "depth": str, "report_id": str|None}
_jobs: dict = {}


# ---------------------------------------------------------------------------
# POST /api/v1/research
# ---------------------------------------------------------------------------

@router.post(
    "/research",
    response_model=ResearchJobResponse,
    status_code=202,
    summary="Start a research job",
    description=(
        "Queues a new research job and returns a job_id immediately. "
        "Connect to the WebSocket stream at /api/v1/research/{job_id}/stream "
        "to receive live progress events."
    ),
)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
) -> ResearchJobResponse:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status":    "queued",
        "topic":     request.topic,
        "depth":     request.depth,
        "report_id": None,
    }

    background_tasks.add_task(
        _run_research,
        job_id=job_id,
        topic=request.topic,
        depth=request.depth,
        save_report=request.save_report,
    )

    return ResearchJobResponse(
        job_id=job_id,
        status="queued",
        topic=request.topic,
        depth=request.depth,
    )


# ---------------------------------------------------------------------------
# WS /api/v1/research/{job_id}/stream
# ---------------------------------------------------------------------------

@router.websocket("/research/{job_id}/stream")
async def research_stream(websocket: WebSocket, job_id: str):
    """
    Stream live research progress events to the frontend.

    Message types sent by the server:
        { "type": "agent_message", "agent": "...", "message": "...", "timestamp": "..." }
        { "type": "progress",      "stage": "...",  "progress": 0.0–1.0 }
        { "type": "complete",      "progress": 1.0, "report_id": "..." }
        { "type": "error",         "message": "..." }
    """
    if job_id not in _jobs:
        await websocket.close(code=4004, reason="Unknown job_id")
        return

    await manager.connect(job_id, websocket)

    try:
        # Keep the connection open until the client disconnects or the
        # pipeline sends a "complete" / "error" message.
        while True:
            # Ping every 20 s to keep the connection alive through proxies
            await asyncio.sleep(20)
            try:
                await websocket.send_text('{"type":"ping"}')
            except Exception:
                break

            # Close once the pipeline is done
            job = _jobs.get(job_id, {})
            if job.get("status") in ("complete", "error"):
                break

    except WebSocketDisconnect:
        logger.info("Client disconnected: job_id=%s", job_id)
    finally:
        manager.disconnect(job_id)


# ---------------------------------------------------------------------------
# GET /api/v1/research/{job_id}/status  (lightweight polling fallback)
# ---------------------------------------------------------------------------

@router.get(
    "/research/{job_id}/status",
    summary="Poll job status",
    description="Lightweight fallback for clients that cannot use WebSockets.",
)
async def job_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------------------------------------------------------------------
# Background task — runs the full pipeline
# ---------------------------------------------------------------------------

async def _run_research(
    job_id: str,
    topic: str,
    depth: Optional[str],
    save_report: bool,
) -> None:
    """
    Executes the research pipeline in the background.

    Progress events are forwarded to the WebSocket manager so the
    connected frontend client receives them in real time.
    """
    _jobs[job_id]["status"] = "running"

    try:
        agent = ResearchAgent()
        progress_cb = make_progress_callback(job_id)

        result = await agent.research(
            topic=topic,
            depth=depth,
            save_report=save_report,
            progress_cb=progress_cb,
        )

        if "error" in result:
            _jobs[job_id]["status"] = "error"
            await manager.send_error(job_id, result["error"])
            return

        report_id = result.get("report_id", "")
        _jobs[job_id]["status"]    = "complete"
        _jobs[job_id]["report_id"] = report_id

        await manager.send_complete(job_id, report_id)

    except Exception as exc:
        logger.exception("Research pipeline failed for job_id=%s", job_id)
        _jobs[job_id]["status"] = "error"
        await manager.send_error(job_id, str(exc))

"""
WebSocket connection manager.

Maintains a registry of active connections keyed by job_id so that
the research pipeline's progress callback can broadcast messages to
the correct frontend client without knowing about FastAPI internals.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages all active WebSocket connections.

    One connection per job_id.  Dead sockets are cleaned up automatically
    on the next send attempt or explicit disconnect call.
    """

    def __init__(self):
        # job_id → active WebSocket
        self._connections: Dict[str, WebSocket] = {}
        # job_id → asyncio.Queue of outbound messages
        self._queues: Dict[str, asyncio.Queue] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self._connections[job_id] = websocket
        self._queues[job_id] = asyncio.Queue()
        logger.info("WS connected: job_id=%s", job_id)

    def disconnect(self, job_id: str) -> None:
        """Remove a connection from the registry (does not close the socket)."""
        self._connections.pop(job_id, None)
        self._queues.pop(job_id, None)
        logger.info("WS disconnected: job_id=%s", job_id)

    # ------------------------------------------------------------------
    # Sending helpers
    # ------------------------------------------------------------------

    async def send(self, job_id: str, data: dict) -> bool:
        """
        Send a JSON message to a specific job's WebSocket.

        Returns True on success, False if no connection exists or send failed.
        Dead sockets are cleaned up automatically.
        """
        ws = self._connections.get(job_id)
        if ws is None:
            return False
        try:
            await ws.send_text(json.dumps(data))
            return True
        except Exception as exc:
            logger.warning("WS send failed for job_id=%s: %s", job_id, exc)
            self.disconnect(job_id)
            return False

    async def send_agent_message(
        self, job_id: str, agent: str, message: str
    ) -> None:
        """Broadcast an agent narration message."""
        await self.send(job_id, {
            "type": "agent_message",
            "agent": agent,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    async def send_progress(
        self, job_id: str, stage: str, progress: float
    ) -> None:
        """Broadcast a pipeline progress update (0.0 – 1.0)."""
        await self.send(job_id, {
            "type": "progress",
            "stage": stage,
            "progress": round(progress, 3),
        })

    async def send_complete(self, job_id: str, report_id: str) -> None:
        """Broadcast pipeline completion with the persisted report_id."""
        await self.send(job_id, {
            "type": "complete",
            "progress": 1.0,
            "report_id": report_id,
        })

    async def send_error(self, job_id: str, message: str) -> None:
        """Broadcast a pipeline error."""
        await self.send(job_id, {
            "type": "error",
            "message": message,
        })

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def is_connected(self, job_id: str) -> bool:
        return job_id in self._connections

    def active_count(self) -> int:
        return len(self._connections)


# ---------------------------------------------------------------------------
# Module-level singleton — imported by routes and the research pipeline
# ---------------------------------------------------------------------------
manager = ConnectionManager()


# ---------------------------------------------------------------------------
# Progress callback factory
# ---------------------------------------------------------------------------

def make_progress_callback(job_id: str):
    """
    Returns an async callable suitable for ResearchAgent's progress_cb.

    The callback signature is:  async (stage: str, pct: float) -> None
    It broadcasts both a progress event and a matching agent_message so
    the frontend terminal feed shows human-readable stage descriptions.
    """

    _STAGE_LABELS = {
        "planning":    ("planner",     "Analysing query and generating research plan…"),
        "researching": ("researcher",  "Running parallel web searches across sub-topics…"),
        "synthesizing":("synthesizer", "Synthesising findings into structured report…"),
        "fact_checking":("fact_checker","Verifying citations against source material…"),
        "critiquing":  ("critic",      "Peer-reviewing synthesis quality…"),
        "scoring":     ("scorer",      "Computing multi-dimension quality score…"),
        "generating":  ("reporter",    "Generating final markdown report…"),
        "persisting":  ("system",      "Persisting report to database and vector store…"),
        "done":        ("system",      "Research pipeline complete ✓"),
    }

    async def _cb(stage: str, pct: float) -> None:
        agent, label = _STAGE_LABELS.get(stage, ("system", stage))
        await manager.send_progress(job_id, stage, pct)
        await manager.send_agent_message(job_id, agent, label)

    return _cb

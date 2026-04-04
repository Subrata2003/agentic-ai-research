"""
Pydantic schemas for the FastAPI request/response layer.

These are deliberately separate from src/models/outputs.py — the internal
pipeline models carry rich detail that the API doesn't need to expose.
These schemas are the public contract between backend and frontend.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class ResearchRequest(BaseModel):
    topic: str = Field(
        min_length=3,
        max_length=500,
        description="Research topic or question",
        examples=["Impact of AI on healthcare"],
    )
    depth: Optional[str] = Field(
        default=None,
        pattern="^(shallow|medium|deep)$",
        description="Research depth. Auto-determined if omitted.",
    )
    save_report: bool = Field(
        default=True,
        description="Whether to persist the report to disk and DB",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ResearchJobResponse(BaseModel):
    """Returned immediately from POST /api/v1/research."""
    job_id: str = Field(description="UUID — use this to connect the WebSocket stream")
    status: str = Field(default="queued", description="'queued' at creation time")
    topic: str
    depth: Optional[str] = None


class QualityScoreResponse(BaseModel):
    overall: float
    source_coverage: float
    citation_accuracy: float
    synthesis_coherence: float
    factual_density: float


class FactCheckSummaryResponse(BaseModel):
    supported: int = 0
    unverifiable: int = 0
    contradicted: int = 0
    total: int = 0


class SourceResponse(BaseModel):
    source_index: int
    title: str
    url: str
    exact_quote: str
    relevance_score: float


class ReportListItem(BaseModel):
    """Compact representation used in paginated lists and history page."""
    id: str
    topic: str
    depth: str
    num_sources: int
    overall_score: Optional[float] = None
    overall_confidence: Optional[float] = None
    critic_quality: Optional[float] = None
    created_at: str
    report_path: Optional[str] = None


class ReportDetail(BaseModel):
    """Full report detail — used by the report viewer page."""
    id: str
    topic: str
    depth: str
    report_markdown: str
    num_sources: int
    overall_score: Optional[float] = None
    overall_confidence: Optional[float] = None
    critic_quality: Optional[float] = None
    created_at: str
    report_path: Optional[str] = None
    pdf_path: Optional[str] = None

    # Nested detail
    quality_score: Optional[QualityScoreResponse] = None
    fact_check_summary: Optional[FactCheckSummaryResponse] = None
    sources: List[SourceResponse] = Field(default_factory=list)

    # Raw JSON blobs for advanced consumers
    plan_json: Optional[str] = None
    synthesis_json: Optional[str] = None


class PaginatedReports(BaseModel):
    items: List[ReportListItem]
    total: int
    page: int
    pages: int


class PdfExportResponse(BaseModel):
    report_id: str
    pdf_path: str
    status: str = "ok"


class SimilarReportResponse(BaseModel):
    report_id: str
    topic: str
    depth: str
    score: str
    distance: float
    summary: str


class AnalyticsResponse(BaseModel):
    total_reports: int
    avg_quality: Optional[float]
    avg_sources: Optional[float]
    avg_confidence: Optional[float]
    total_sources_analysed: Optional[int]
    fact_check_distribution: Dict[str, int]
    depth_distribution: Dict[str, int]
    recent_reports: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# WebSocket message schemas (outbound — server → client)
# ---------------------------------------------------------------------------

class WsAgentMessage(BaseModel):
    type: str = "agent_message"
    agent: str
    message: str
    timestamp: str


class WsProgressMessage(BaseModel):
    type: str = "progress"
    stage: str
    progress: float


class WsCompleteMessage(BaseModel):
    type: str = "complete"
    progress: float = 1.0
    report_id: str


class WsErrorMessage(BaseModel):
    type: str = "error"
    message: str

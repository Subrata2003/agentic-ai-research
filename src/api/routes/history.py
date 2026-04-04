"""
History & report routes:
    GET  /api/v1/reports                  → paginated report list
    GET  /api/v1/reports/{id}             → full report detail
    POST /api/v1/reports/{id}/pdf         → export PDF
    GET  /api/v1/similar?topic=...        → semantic similar reports
    GET  /api/v1/analytics                → dashboard stats
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from src.api.schemas import (
    AnalyticsResponse,
    FactCheckSummaryResponse,
    PaginatedReports,
    PdfExportResponse,
    QualityScoreResponse,
    ReportDetail,
    ReportListItem,
    SimilarReportResponse,
    SourceResponse,
)
from src.export.pdf_exporter import export_pdf
from src.memory.db import get_report, get_stats, list_reports
from src.memory.vector_store import VectorStore

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazy singleton — initialised once on first use
_vector_store: Optional[VectorStore] = None


def _get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


# ---------------------------------------------------------------------------
# GET /api/v1/reports
# ---------------------------------------------------------------------------

@router.get(
    "/reports",
    response_model=PaginatedReports,
    summary="List research reports",
    description="Returns a paginated, searchable, sortable list of past reports.",
)
async def list_reports_endpoint(
    page:   int = Query(default=1, ge=1, description="Page number (1-based)"),
    limit:  int = Query(default=20, ge=1, le=100, description="Results per page"),
    search: Optional[str] = Query(default=None, description="Filter by topic keyword"),
    sort:   str = Query(
        default="newest",
        pattern="^(newest|oldest|quality_desc|quality_asc)$",
        description="Sort order",
    ),
) -> PaginatedReports:
    result = list_reports(page=page, limit=limit, search=search, sort=sort)
    items = [
        ReportListItem(
            id=r["id"],
            topic=r["topic"],
            depth=r["depth"],
            num_sources=r["num_sources"] or 0,
            overall_score=r["overall_score"],
            overall_confidence=r["overall_confidence"],
            critic_quality=r["critic_quality"],
            created_at=r["created_at"],
            report_path=r.get("report_path"),
        )
        for r in result["items"]
    ]
    return PaginatedReports(
        items=items,
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
    )


# ---------------------------------------------------------------------------
# GET /api/v1/reports/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/reports/{report_id}",
    response_model=ReportDetail,
    summary="Get full report detail",
)
async def get_report_endpoint(report_id: str) -> ReportDetail:
    row = get_report(report_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    # Build quality score sub-object
    quality_score = None
    if row.get("overall_score") is not None:
        quality_score = QualityScoreResponse(
            overall=row["overall_score"],
            source_coverage=row.get("source_coverage") or 0.0,
            citation_accuracy=row.get("citation_accuracy") or 0.0,
            synthesis_coherence=row.get("synthesis_coherence") or 0.0,
            factual_density=row.get("factual_density") or 0.0,
        )

    # Build fact-check summary from stored rows
    fc_rows = row.get("fact_check_rows", [])
    fc_summary = FactCheckSummaryResponse(
        supported=sum(1 for r in fc_rows if r["verdict"] == "SUPPORTED"),
        unverifiable=sum(1 for r in fc_rows if r["verdict"] == "UNVERIFIABLE"),
        contradicted=sum(1 for r in fc_rows if r["verdict"] == "CONTRADICTED"),
        total=len(fc_rows),
    )

    # Source quotes
    sources = [
        SourceResponse(
            source_index=s["source_index"],
            title=s["title"] or "",
            url=s["url"],
            exact_quote=s["exact_quote"] or "",
            relevance_score=s["relevance"] or 0.0,
        )
        for s in row.get("sources", [])
    ]

    return ReportDetail(
        id=row["id"],
        topic=row["topic"],
        depth=row["depth"],
        report_markdown=row["report_markdown"],
        num_sources=row["num_sources"] or 0,
        overall_score=row.get("overall_score"),
        overall_confidence=row.get("overall_confidence"),
        critic_quality=row.get("critic_quality"),
        created_at=row["created_at"],
        report_path=row.get("report_path"),
        pdf_path=row.get("pdf_path"),
        quality_score=quality_score,
        fact_check_summary=fc_summary,
        sources=sources,
        plan_json=row.get("plan_json"),
        synthesis_json=row.get("synthesis_json"),
    )


# ---------------------------------------------------------------------------
# POST /api/v1/reports/{id}/pdf
# ---------------------------------------------------------------------------

@router.post(
    "/reports/{report_id}/pdf",
    response_model=PdfExportResponse,
    summary="Export report as PDF",
)
async def export_report_pdf(report_id: str) -> PdfExportResponse:
    row = get_report(report_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        pdf_path = export_pdf(
            markdown_content=row["report_markdown"],
            topic=row["topic"],
            report_id=report_id,
        )
    except Exception as exc:
        logger.exception("PDF export failed for report_id=%s", report_id)
        raise HTTPException(status_code=500, detail=f"PDF export failed: {exc}")

    return PdfExportResponse(
        report_id=report_id,
        pdf_path=pdf_path,
        status="ok",
    )


# ---------------------------------------------------------------------------
# GET /api/v1/reports/{id}/download  — stream the PDF file directly
# ---------------------------------------------------------------------------

@router.get(
    "/reports/{report_id}/download",
    summary="Download PDF file",
    response_class=FileResponse,
)
async def download_pdf(report_id: str):
    row = get_report(report_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    pdf_path = row.get("pdf_path")
    if not pdf_path:
        raise HTTPException(
            status_code=404,
            detail="PDF not yet generated — call POST /reports/{id}/pdf first",
        )

    import os
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"report_{report_id[:8]}.pdf",
    )


# ---------------------------------------------------------------------------
# GET /api/v1/similar
# ---------------------------------------------------------------------------

@router.get(
    "/similar",
    response_model=list[SimilarReportResponse],
    summary="Semantic similar reports",
    description="Returns up to n past reports semantically similar to the given topic.",
)
async def similar_reports(
    topic: str = Query(min_length=3, description="Topic to compare against"),
    n:     int = Query(default=5, ge=1, le=20),
) -> list[SimilarReportResponse]:
    vs = _get_vector_store()
    results = vs.find_similar(topic, n=n)
    return [
        SimilarReportResponse(
            report_id=r["report_id"],
            topic=r["topic"],
            depth=r["depth"],
            score=r["score"],
            distance=r["distance"],
            summary=r["summary"],
        )
        for r in results
    ]


# ---------------------------------------------------------------------------
# GET /api/v1/analytics
# ---------------------------------------------------------------------------

@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Analytics dashboard data",
)
async def analytics() -> AnalyticsResponse:
    stats = get_stats()
    return AnalyticsResponse(
        total_reports=stats.get("total_reports") or 0,
        avg_quality=stats.get("avg_quality"),
        avg_sources=stats.get("avg_sources"),
        avg_confidence=stats.get("avg_confidence"),
        total_sources_analysed=stats.get("total_sources_analysed"),
        fact_check_distribution=stats.get("fact_check_distribution") or {},
        depth_distribution=stats.get("depth_distribution") or {},
        recent_reports=stats.get("recent_reports") or [],
    )

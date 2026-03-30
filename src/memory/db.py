"""
SQLite persistence layer for the Research Agent.

Schema
------
reports      — one row per completed research run
sources      — one row per unique source URL cited in a report
fact_checks  — one row per FactCheckResult produced by FactCheckerAgent

All queries are parameterised — no string interpolation, no SQL injection risk.
"""

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional

from src.utils.config import Config


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS reports (
    id              TEXT PRIMARY KEY,
    topic           TEXT NOT NULL,
    depth           TEXT NOT NULL,
    report_markdown TEXT NOT NULL,
    report_path     TEXT,
    pdf_path        TEXT,
    num_sources     INTEGER DEFAULT 0,
    overall_score   REAL,
    source_coverage REAL,
    citation_accuracy REAL,
    synthesis_coherence REAL,
    factual_density REAL,
    overall_confidence REAL,
    critic_quality  REAL,
    plan_json       TEXT,
    synthesis_json  TEXT,
    fact_checks_json TEXT,
    critique_json   TEXT,
    score_json      TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id   TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    source_index INTEGER NOT NULL,
    title       TEXT,
    url         TEXT NOT NULL,
    exact_quote TEXT,
    relevance   REAL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_checks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id   TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    claim       TEXT NOT NULL,
    verdict     TEXT NOT NULL,
    confidence  REAL,
    evidence    TEXT,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reports_created_at  ON reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_topic       ON reports(topic);
CREATE INDEX IF NOT EXISTS idx_reports_score       ON reports(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_sources_report_id   ON sources(report_id);
CREATE INDEX IF NOT EXISTS idx_fact_checks_report  ON fact_checks(report_id);
"""


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _get_db_path() -> str:
    path = Config.SQLITE_DB_PATH
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else "data", exist_ok=True)
    return path


@contextmanager
def _connection() -> Generator[sqlite3.Connection, None, None]:
    """Yield an open, auto-closing SQLite connection with WAL mode."""
    conn = sqlite3.connect(_get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Database initialisation
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables and indexes if they do not exist yet."""
    with _connection() as conn:
        conn.executescript(_DDL)


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def save_report(
    *,
    topic: str,
    depth: str,
    report_markdown: str,
    report_path: Optional[str] = None,
    pdf_path: Optional[str] = None,
    num_sources: int = 0,
    plan: Optional[Any] = None,
    synthesis: Optional[Any] = None,
    fact_checks: Optional[List[Any]] = None,
    critique: Optional[Any] = None,
    score: Optional[Any] = None,
    report_id: Optional[str] = None,
) -> str:
    """
    Persist a completed research run and return the assigned report_id.

    All Pydantic model arguments are serialised to JSON strings so SQLite
    can store them; they are deserialised on read by get_report().
    """
    rid = report_id or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    class _SetEncoder(json.JSONEncoder):
        """Convert any set → sorted list so JSON serialization never crashes."""
        def default(self, obj):
            if isinstance(obj, set):
                return sorted(obj)
            return super().default(obj)

    def _dump(obj) -> Optional[str]:
        if obj is None:
            return None
        if hasattr(obj, "model_dump"):
            return json.dumps(obj.model_dump(), cls=_SetEncoder)
        if isinstance(obj, list):
            return json.dumps(
                [item.model_dump() if hasattr(item, "model_dump") else item for item in obj],
                cls=_SetEncoder,
            )
        return json.dumps(obj, cls=_SetEncoder)

    with _connection() as conn:
        conn.execute(
            """
            INSERT INTO reports (
                id, topic, depth, report_markdown, report_path, pdf_path,
                num_sources,
                overall_score, source_coverage, citation_accuracy,
                synthesis_coherence, factual_density,
                overall_confidence, critic_quality,
                plan_json, synthesis_json, fact_checks_json,
                critique_json, score_json, created_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?,
                ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?
            )
            """,
            (
                rid, topic, depth, report_markdown, report_path, pdf_path,
                num_sources,
                score.overall            if score    else None,
                score.source_coverage    if score    else None,
                score.citation_accuracy  if score    else None,
                score.synthesis_coherence if score   else None,
                score.factual_density    if score    else None,
                synthesis.overall_confidence if synthesis else None,
                critique.overall_quality     if critique  else None,
                _dump(plan),
                _dump(synthesis),
                _dump(fact_checks),
                _dump(critique),
                _dump(score),
                now,
            ),
        )

        # Persist individual source quotes
        if synthesis and synthesis.source_quotes:
            conn.executemany(
                """
                INSERT INTO sources
                    (report_id, source_index, title, url, exact_quote, relevance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (rid, q.source_index, q.title, q.url, q.exact_quote, q.relevance_score, now)
                    for q in synthesis.source_quotes
                ],
            )

        # Persist fact-check verdicts
        if fact_checks:
            conn.executemany(
                """
                INSERT INTO fact_checks
                    (report_id, claim, verdict, confidence, evidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (rid, fc.claim, fc.verdict.value if hasattr(fc.verdict, "value") else fc.verdict,
                     fc.confidence, fc.evidence, now)
                    for fc in fact_checks
                ],
            )

    return rid


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def get_report(report_id: str) -> Optional[Dict]:
    """Return a single report row as a dict, or None if not found."""
    with _connection() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()
        if row is None:
            return None

        result = dict(row)

        # Attach related rows
        result["sources"] = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM sources WHERE report_id = ? ORDER BY source_index",
                (report_id,),
            ).fetchall()
        ]
        result["fact_check_rows"] = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM fact_checks WHERE report_id = ?", (report_id,)
            ).fetchall()
        ]
        return result


def list_reports(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    sort: str = "newest",
) -> Dict:
    """
    Paginated report list.

    Args:
        page:   1-based page number.
        limit:  Results per page (max 100).
        search: Optional full-text search on topic.
        sort:   'newest' | 'oldest' | 'quality_desc' | 'quality_asc'

    Returns:
        {'items': [...], 'total': int, 'page': int, 'pages': int}
    """
    limit = min(limit, 100)
    offset = (page - 1) * limit

    sort_map = {
        "newest":      "created_at DESC",
        "oldest":      "created_at ASC",
        "quality_desc": "overall_score DESC NULLS LAST",
        "quality_asc":  "overall_score ASC NULLS LAST",
    }
    order = sort_map.get(sort, "created_at DESC")

    where = "WHERE topic LIKE ?" if search else ""
    params_filter = [f"%{search}%"] if search else []

    with _connection() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM reports {where}", params_filter
        ).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT id, topic, depth, num_sources, overall_score,
                   overall_confidence, critic_quality, created_at, report_path
            FROM reports {where}
            ORDER BY {order}
            LIMIT ? OFFSET ?
            """,
            params_filter + [limit, offset],
        ).fetchall()

    return {
        "items":  [dict(r) for r in rows],
        "total":  total,
        "page":   page,
        "pages":  max(1, -(-total // limit)),   # ceiling division
    }


def get_stats() -> Dict:
    """Aggregate statistics for the analytics dashboard."""
    with _connection() as conn:
        stats = dict(
            conn.execute(
                """
                SELECT
                    COUNT(*)                        AS total_reports,
                    AVG(overall_score)              AS avg_quality,
                    AVG(num_sources)                AS avg_sources,
                    AVG(overall_confidence)         AS avg_confidence,
                    SUM(num_sources)                AS total_sources_analysed
                FROM reports
                """
            ).fetchone()
        )

        verdict_rows = conn.execute(
            "SELECT verdict, COUNT(*) AS cnt FROM fact_checks GROUP BY verdict"
        ).fetchall()
        stats["fact_check_distribution"] = {r["verdict"]: r["cnt"] for r in verdict_rows}

        depth_rows = conn.execute(
            "SELECT depth, COUNT(*) AS cnt FROM reports GROUP BY depth"
        ).fetchall()
        stats["depth_distribution"] = {r["depth"]: r["cnt"] for r in depth_rows}

        recent_rows = conn.execute(
            """
            SELECT id, topic, overall_score, created_at
            FROM reports
            ORDER BY created_at DESC
            LIMIT 5
            """
        ).fetchall()
        stats["recent_reports"] = [dict(r) for r in recent_rows]

    return stats


# ---------------------------------------------------------------------------
# Initialise on import
# ---------------------------------------------------------------------------
init_db()

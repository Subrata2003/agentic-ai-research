"""
Phase 4 test script — run with:
    python test_phase4.py
"""

import os
import sys

# Force UTF-8 output on Windows
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PASS = "[PASS]"
FAIL = "[FAIL]"
results = []


def check(label, fn):
    try:
        fn()
        print(f"  {PASS} {label}")
        results.append((label, True, None))
    except Exception as e:
        print(f"  {FAIL} {label}")
        print(f"         Error: {e}")
        results.append((label, False, str(e)))


# ===========================================================================
# TEST 1 — Imports
# ===========================================================================
print("\n" + "=" * 60)
print("TEST 1: Phase 4 Imports")
print("=" * 60)

def test_imports():
    from src.memory.db import init_db, list_reports, get_report, get_stats
    from src.memory.vector_store import VectorStore
    from src.evaluation.scorer import ResearchEvaluator, score_label, score_color
    from src.agent.research_agent import ResearchAgent

check("All Phase 4 modules import without error", test_imports)


# ===========================================================================
# TEST 2 — SQLite DB init
# ===========================================================================
print("\n" + "=" * 60)
print("TEST 2: SQLite Database")
print("=" * 60)

def test_db_init():
    from src.memory.db import init_db
    init_db()
    assert os.path.exists("data/research.db"), "data/research.db not created"

def test_db_stats():
    from src.memory.db import get_stats
    stats = get_stats()
    assert "total_reports" in stats
    assert "fact_check_distribution" in stats
    assert "depth_distribution" in stats
    print(f"         Total reports in DB: {stats['total_reports']}")

def test_db_list():
    from src.memory.db import list_reports
    result = list_reports(page=1, limit=5)
    assert "items" in result
    assert "total" in result
    assert "pages" in result
    print(f"         Paginated list works — {result['total']} reports found")

check("data/research.db created on init", test_db_init)
check("get_stats() returns expected keys", test_db_stats)
check("list_reports() paginates correctly", test_db_list)


# ===========================================================================
# TEST 3 — Scorer (pure Python, no API calls)
# ===========================================================================
print("\n" + "=" * 60)
print("TEST 3: Quality Scorer")
print("=" * 60)

def test_scorer():
    from src.models.outputs import (
        SynthesizerOutput, SynthesisSection, SourceQuote,
        FactCheckResult, FactVerdict,
    )
    from src.evaluation.scorer import ResearchEvaluator, score_label, score_color

    synthesis = SynthesizerOutput(
        topic="Test topic",
        executive_summary="This is a test summary for evaluation purposes.",
        sections=[
            SynthesisSection(
                heading="Key Findings",
                content="AI is transforming healthcare in multiple significant ways [1]. Studies show efficiency gains of around 40 percent [2].",
                citations_used=[1, 2],
            ),
            SynthesisSection(
                heading="Conclusion",
                content="The future looks promising based on current evidence gathered from multiple reputable sources [1].",
                citations_used=[1],
            ),
        ],
        source_quotes=[
            SourceQuote(source_index=1, url="https://a.com", title="AI Study",
                        exact_quote="AI is transforming healthcare", relevance_score=0.9),
            SourceQuote(source_index=2, url="https://b.com", title="Efficiency Report",
                        exact_quote="efficiency gains", relevance_score=0.8),
        ],
        overall_confidence=0.82,
    )
    raw_sources = [
        {"title": "AI Study", "url": "https://a.com",
         "content": "AI is transforming healthcare in multiple significant ways."},
        {"title": "Efficiency Report", "url": "https://b.com",
         "content": "Studies show efficiency gains of around 40 percent in clinical settings."},
        {"title": "Extra Source", "url": "https://c.com", "content": "additional context here."},
    ]
    fact_checks = [
        FactCheckResult(claim="AI helps healthcare", verdict=FactVerdict.SUPPORTED, confidence=0.9),
        FactCheckResult(claim="40% gains", verdict=FactVerdict.SUPPORTED, confidence=0.85),
        FactCheckResult(claim="Unverifiable claim", verdict=FactVerdict.UNVERIFIABLE, confidence=0.5),
    ]

    score = ResearchEvaluator().score(synthesis, fact_checks, raw_sources)

    assert 0.0 <= score.overall <= 1.0, "overall score out of range"
    assert 0.0 <= score.source_coverage <= 1.0
    assert 0.0 <= score.citation_accuracy <= 1.0
    assert 0.0 <= score.synthesis_coherence <= 1.0
    assert 0.0 <= score.factual_density <= 1.0

    label = score_label(score.overall)
    color = score_color(score.overall)
    assert label in ("High", "Medium", "Low")
    assert color in ("emerald", "amber", "red")

    print(f"         source_coverage:     {score.source_coverage:.0%}")
    print(f"         citation_accuracy:   {score.citation_accuracy:.0%}")
    print(f"         synthesis_coherence: {score.synthesis_coherence:.0%}")
    print(f"         factual_density:     {score.factual_density:.0%}")
    print(f"         overall:             {score.overall:.0%} — {label} [{color}]")

check("Scorer computes all 4 dimensions correctly", test_scorer)


# ===========================================================================
# TEST 4 — Vector Store
# ===========================================================================
print("\n" + "=" * 60)
print("TEST 4: Vector Store (ChromaDB)")
print("=" * 60)

def test_vector_store_init():
    from src.memory.vector_store import VectorStore
    vs = VectorStore()
    count = vs.count()
    print(f"         VectorStore initialized — {count} reports embedded")

def test_vector_store_find_similar_empty():
    from src.memory.vector_store import VectorStore
    vs = VectorStore()
    results = vs.find_similar("artificial intelligence", n=3)
    assert isinstance(results, list), "find_similar must return a list"
    print(f"         find_similar on empty/sparse store returned {len(results)} results (expected >=0)")

check("VectorStore initializes without crash", test_vector_store_init)
check("find_similar returns list (not crash) on empty store", test_vector_store_find_similar_empty)


# ===========================================================================
# TEST 5 — DB save + retrieve round-trip (no LLM)
# ===========================================================================
print("\n" + "=" * 60)
print("TEST 5: DB Save & Retrieve Round-Trip")
print("=" * 60)

def test_db_roundtrip():
    from src.memory.db import save_report, get_report, list_reports
    from src.models.outputs import EvaluationScore

    score = EvaluationScore(
        source_coverage=0.8,
        citation_accuracy=0.7,
        synthesis_coherence=0.9,
        factual_density=0.6,
        overall=0.75,
        breakdown={},
    )

    rid = save_report(
        topic="Test round-trip topic",
        depth="shallow",
        report_markdown="# Test Report\n\nThis is a test.",
        num_sources=3,
        score=score,
    )

    assert rid is not None and len(rid) == 36, "Invalid UUID returned"

    retrieved = get_report(rid)
    assert retrieved is not None, "get_report returned None"
    assert retrieved["topic"] == "Test round-trip topic"
    assert retrieved["depth"] == "shallow"
    assert abs(retrieved["overall_score"] - 0.75) < 0.001

    reports = list_reports(search="round-trip")
    assert reports["total"] >= 1

    print(f"         Saved report ID: {rid[:8]}...")
    print(f"         Retrieved topic: {retrieved['topic']}")
    print(f"         Overall score:   {retrieved['overall_score']:.0%}")

check("save_report + get_report round-trip works", test_db_roundtrip)


# ===========================================================================
# SUMMARY
# ===========================================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)

for label, ok, err in results:
    status = PASS if ok else FAIL
    print(f"  {status} {label}")

print(f"\n  {passed}/{passed + failed} tests passed")

if failed == 0:
    print("\n  All Phase 4 tests passed! Ready to run full pipeline.")
    print("  Next: python main.py \"your topic\" --depth shallow")
else:
    print(f"\n  {failed} test(s) failed. Fix errors above before running the full pipeline.")

print("=" * 60)

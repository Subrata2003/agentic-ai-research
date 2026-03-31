"""
Main research agent orchestrator.

Pipeline (async):
    plan (5%)
      └─► parallel_research (15 % → 55 %)   ← asyncio.gather, Semaphore(5)
            └─► synthesize (55 %)
                  └─► fact_check (70 %)
                        └─► critique (80 %)
                              └─► generate_report (92 %)
                                    └─► done (100 %)

Phase 4 hooks (scorer + persistence) are clearly marked with TODO stubs
so they drop in with minimal changes.

A synchronous wrapper (research_sync) lets main.py / CLI keep working
without any asyncio boilerplate at the call site.
"""

import asyncio
from typing import Awaitable, Callable, Dict, List, Optional

from src.agent.critic_agent import CriticAgent
from src.agent.fact_checker_agent import FactCheckerAgent
from src.agent.parallel_researcher import ParallelResearcher
from src.agent.planner import ResearchPlanner
from src.evaluation.scorer import ResearchEvaluator, score_label, score_color
from src.memory.db import save_report as db_save_report
from src.memory.vector_store import VectorStore
from src.models.outputs import (
    CriticOutput,
    EvaluationScore,
    FactCheckResult,
    PlannerOutput,
    SynthesizerOutput,
)
from src.modules.report_generator import ReportGenerator
from src.modules.synthesizer import Synthesizer
from src.utils.config import Config
from src.utils.tracing import setup_tracing

# Type alias for the progress callback used by the WebSocket layer (Phase 5)
ProgressCallback = Callable[[str, float], Awaitable[None]]


class ResearchAgent:
    """
    Orchestrates the full multi-agent research pipeline.

    All heavy work happens inside `research()` which is a native coroutine.
    Call `research_sync()` from synchronous code (CLI, tests).
    """

    def __init__(self):
        print("Initializing Research Agent...")
        Config.validate()
        setup_tracing()

        self.planner      = ResearchPlanner()
        self.researcher   = ParallelResearcher(max_concurrent=5)
        self.synthesizer  = Synthesizer()
        self.fact_checker = FactCheckerAgent()
        self.critic       = CriticAgent()
        self.report_gen   = ReportGenerator()
        self.evaluator    = ResearchEvaluator()
        self.vector_store = VectorStore()

        print("✓ Research Agent initialized (multi-agent, async pipeline + memory)")

    # ------------------------------------------------------------------
    # Primary async pipeline
    # ------------------------------------------------------------------

    async def research(
        self,
        topic: str,
        depth: Optional[str] = None,
        save_report: bool = True,
        progress_cb: Optional[ProgressCallback] = None,
    ) -> Dict:
        """
        Run the full research pipeline asynchronously.

        Args:
            topic:       Research topic / question.
            depth:       Force depth ('shallow'|'medium'|'deep'). Auto if None.
            save_report: Whether to persist the report to outputs/.
            progress_cb: Async callable(stage: str, pct: float) invoked at
                         each pipeline milestone — consumed by the WebSocket
                         manager in Phase 5. Defaults to a no-op.

        Returns:
            Dict with keys:
                topic, plan, research_results, synthesis, fact_checks,
                critique, report, report_path, num_sources.
        """
        _cb = progress_cb or _noop_cb

        print(f"\n🔍 Starting research: '{topic}'")
        print("-" * 60)

        # ── 1. Plan ──────────────────────────────────────────────────── 5 %
        print("\n📋 [1/5] Planning research strategy...")
        await _cb("planning", 0.05)

        plan: PlannerOutput = self.planner.plan_research(
            topic, depth_override=depth
        )
        research_depth = depth or plan.depth.value

        print(f"   ✓ Depth: {research_depth}  |  "
              f"Sub-topics: {len(plan.sub_topics)}  |  "
              f"Complexity: {plan.complexity_score:.2f}")
        for st in plan.sub_topics:
            print(f"     [{st.priority}] {st.query}")

        # ── 2. Parallel research ────────────────────────────── 15 % → 55 %
        print(f"\n🌐 [2/5] Parallel web research ({research_depth})...")
        await _cb("researching", 0.15)

        raw_sources: List[Dict] = await self.researcher.research(
            plan=plan,
            depth=research_depth,
            progress_cb=_cb,
        )
        print(f"   ✓ Retrieved {len(raw_sources)} unique sources")

        if not raw_sources:
            return {
                "error": "No research results found. "
                         "Check your internet connection and API keys.",
                "topic": topic,
            }

        # ── 3. Synthesise ─────────────────────────────────────────── 55 %
        # Cap at 15 sources — beyond that the JSON response exceeds Gemini's
        # output token budget and triggers the Stage-3 fallback (no citations).
        # Sources are already ranked by relevance from ParallelResearcher.
        MAX_SYNTH_SOURCES = 15
        synth_sources = raw_sources[:MAX_SYNTH_SOURCES]
        if len(raw_sources) > MAX_SYNTH_SOURCES:
            print(f"\n🧠 [3/5] Synthesising top {MAX_SYNTH_SOURCES} of {len(raw_sources)} sources...")
        else:
            print(f"\n🧠 [3/5] Synthesising {len(synth_sources)} sources...")
        await _cb("synthesizing", 0.55)

        synthesis: SynthesizerOutput = self.synthesizer.synthesize(
            synth_sources, topic
        )
        print(f"   ✓ Confidence: {synthesis.overall_confidence:.0%}  |  "
              f"Citations: {len(synthesis.source_quotes)}  |  "
              f"Sections: {len(synthesis.sections)}")

        # ── 4. Fact-check ─────────────────────────────────────────── 70 %
        print(f"\n🔎 [4/5] Fact-checking {len(synthesis.source_quotes)} citations...")
        await _cb("fact_checking", 0.70)

        fact_checks: List[FactCheckResult] = self.fact_checker.check(
            synthesis, synth_sources
        )
        fc_summary = FactCheckerAgent.summary(fact_checks)
        print(f"   ✓ Supported: {fc_summary.get('SUPPORTED', 0)}  |  "
              f"Unverifiable: {fc_summary.get('UNVERIFIABLE', 0)}  |  "
              f"Contradicted: {fc_summary.get('CONTRADICTED', 0)}")

        # ── 5. Critique ───────────────────────────────────────────── 80 %
        print(f"\n🧑‍⚖️  [5/5] Critic review...")
        await _cb("critiquing", 0.80)

        critique: CriticOutput = self.critic.critique(synthesis, fact_checks)
        print(f"   ✓ Quality score: {critique.overall_quality:.0%}")
        if critique.strengths:
            print(f"   ✓ Strengths:  {critique.strengths[0][:80]}")
        if critique.weaknesses:
            print(f"   ✓ Weaknesses: {critique.weaknesses[0][:80]}")

        # ── 6. Score ──────────────────────────────────────────────── 88 %
        print("\n📊 [6/7] Computing quality score...")
        await _cb("scoring", 0.88)

        score: EvaluationScore = self.evaluator.score(
            synthesis, fact_checks, synth_sources
        )
        label = score_label(score.overall)
        color = score_color(score.overall)
        print(f"   ✓ Overall: {score.overall:.0%} [{label}]  |  "
              f"Coverage: {score.source_coverage:.0%}  |  "
              f"Citations: {score.citation_accuracy:.0%}  |  "
              f"Coherence: {score.synthesis_coherence:.0%}  |  "
              f"Density: {score.factual_density:.0%}")

        # ── 7. Generate report ────────────────────────────────────── 92 %
        print("\n📝 [7/7] Generating report...")
        await _cb("generating", 0.92)
        markdown_report = self.report_gen.generate_markdown_report(
            synthesis, score=score
        )

        report_path: Optional[str] = None
        if save_report:
            report_path = self.report_gen.save_report(markdown_report, topic)
            print(f"   ✓ Saved → {report_path}")

        # ── 8. Persist to SQLite + ChromaDB ──────────────────────── 96 %
        print("\n💾 [8/8] Persisting to memory...")
        await _cb("persisting", 0.96)

        report_id = db_save_report(
            topic=topic,
            depth=research_depth,
            report_markdown=markdown_report,
            report_path=report_path,
            num_sources=len(raw_sources),
            plan=plan,
            synthesis=synthesis,
            fact_checks=fact_checks,
            critique=critique,
            score=score,
        )
        self.vector_store.add_report(
            report_id=report_id,
            topic=topic,
            executive_summary=synthesis.executive_summary,
            depth=research_depth,
            overall_score=score.overall,
        )
        print(f"   ✓ Persisted → DB id: {report_id[:8]}…  "
              f"| Vector store count: {self.vector_store.count()}")

        await _cb("done", 1.0)
        print("\n" + "=" * 60)
        print("✅ Research pipeline complete!")
        print("=" * 60)

        return {
            "report_id":        report_id,
            "topic":            topic,
            "plan":             plan,
            "research_results": raw_sources,
            "synthesis":        synthesis,
            "fact_checks":      fact_checks,
            "critique":         critique,
            "score":            score,
            "report":           markdown_report,
            "report_path":      report_path,
            "num_sources":      len(raw_sources),
        }

    # ------------------------------------------------------------------
    # Synchronous wrapper — keeps CLI / tests working
    # ------------------------------------------------------------------

    def research_sync(
        self,
        topic: str,
        depth: Optional[str] = None,
        save_report: bool = True,
    ) -> Dict:
        """
        Blocking wrapper around `research()`.
        Use this from synchronous code (CLI, pytest, Jupyter).
        """
        return asyncio.run(
            self.research(topic=topic, depth=depth, save_report=save_report)
        )

    def quick_research(self, topic: str) -> str:
        """
        Shallow, no-save research that returns just the report string.
        Useful for quick demos and the programmatic API.
        """
        result = self.research_sync(topic, depth="shallow", save_report=False)
        return result.get("report", "Research failed.")

    def __del__(self):
        """Clean up the thread pool gracefully."""
        try:
            self.researcher.close()
        except Exception:
            pass


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _noop_cb(stage: str, pct: float) -> None:
    """Default progress callback — prints to stdout, no WebSocket."""
    print(f"   [progress] {stage}: {pct:.0%}")

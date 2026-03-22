"""Main research agent orchestrator — wires planner → researcher → synthesizer → report."""

from typing import Dict, Optional

from src.agent.planner import ResearchPlanner
from src.modules.web_researcher import WebResearcher
from src.modules.synthesizer import Synthesizer
from src.modules.report_generator import ReportGenerator
from src.models.outputs import PlannerOutput, SynthesizerOutput, ResearchResult
from src.utils.config import Config
from src.utils.tracing import setup_tracing


class ResearchAgent:
    """Orchestrates the full research pipeline and returns typed results."""

    def __init__(self):
        print("Initializing Research Agent...")
        Config.validate()
        setup_tracing()

        self.planner = ResearchPlanner()
        self.researcher = WebResearcher()
        self.synthesizer = Synthesizer()
        self.report_generator = ReportGenerator()

        print("✓ Research Agent initialized successfully!")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def research(
        self,
        topic: str,
        depth: Optional[str] = None,
        save_report: bool = True,
    ) -> Dict:
        """
        Conduct end-to-end research on a topic.

        Args:
            topic:       Research topic / question.
            depth:       Force depth ('shallow'|'medium'|'deep'). Auto if None.
            save_report: Save the report to outputs/ directory.

        Returns:
            Dict with keys: topic, plan, research_results, synthesis,
                            report, report_path, num_sources.
            'plan'      → PlannerOutput instance
            'synthesis' → SynthesizerOutput instance
            'report'    → markdown string
        """
        import uuid
        from datetime import datetime, timezone

        print(f"\n🔍 Starting research on: {topic}")
        print("-" * 60)

        # ── Step 1: Plan ─────────────────────────────────────────────────
        print("\n📋 Step 1: Planning research strategy...")
        plan: PlannerOutput = self.planner.plan_research(topic, depth_override=depth)
        research_depth = depth or plan.depth.value
        print(f"   ✓ Depth: {research_depth}  |  Sub-topics: {len(plan.sub_topics)}")
        print(f"   ✓ Complexity score: {plan.complexity_score:.2f}")

        # ── Step 2: Retrieve ─────────────────────────────────────────────
        print(f"\n🌐 Step 2: Conducting web research ({research_depth})...")
        research_results = self.researcher.research_topic(topic, depth=research_depth)
        print(f"   ✓ Retrieved {len(research_results)} sources")

        if not research_results:
            return {
                "error": "No research results found. Check your internet connection and API keys.",
                "topic": topic,
            }

        # ── Step 3: Synthesise ────────────────────────────────────────────
        print(f"\n🧠 Step 3: Synthesising {len(research_results)} sources with citation contract...")
        synthesis: SynthesizerOutput = self.synthesizer.synthesize(research_results, topic)
        print(f"   ✓ Synthesis complete  |  Confidence: {synthesis.overall_confidence:.0%}")
        print(f"   ✓ Citations produced: {len(synthesis.source_quotes)}")
        print(f"   ✓ Sections: {[s.heading for s in synthesis.sections]}")

        # ── Step 4: Generate report ───────────────────────────────────────
        print(f"\n📝 Step 4: Generating report...")
        markdown_report = self.report_generator.generate_markdown_report(synthesis)

        report_path: Optional[str] = None
        if save_report:
            report_path = self.report_generator.save_report(markdown_report, topic)
            print(f"   ✓ Saved → {report_path}")

        print("\n" + "=" * 60)
        print("✅ Research completed successfully!")
        print("=" * 60)

        return {
            "topic": topic,
            "plan": plan,
            "research_results": research_results,
            "synthesis": synthesis,
            "report": markdown_report,
            "report_path": report_path,
            "num_sources": len(research_results),
        }

    def quick_research(self, topic: str) -> str:
        """
        Shallow research that returns just the report string (no file save).
        Useful for quick demos and the programmatic API.
        """
        result = self.research(topic, depth="shallow", save_report=False)
        return result.get("report", "Research failed.")

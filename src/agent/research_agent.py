"""Main research agent orchestrator"""

from typing import Dict, Optional
from src.agent.planner import ResearchPlanner
from src.modules.web_researcher import WebResearcher
from src.modules.synthesizer import Synthesizer
from src.modules.report_generator import ReportGenerator
from src.utils.config import Config


class ResearchAgent:
    """Main agent that orchestrates the entire research process"""
    
    def __init__(self):
        """Initialize the research agent with all required modules"""
        print("Initializing Research Agent...")
        Config.validate()
        
        self.planner = ResearchPlanner()
        self.researcher = WebResearcher()
        self.synthesizer = Synthesizer()
        self.report_generator = ReportGenerator()
        
        print("✓ Research Agent initialized successfully!")
    
    def research(self, topic: str, depth: Optional[str] = None, save_report: bool = True) -> Dict[str, any]:
        """
        Conduct end-to-end research on a topic
        
        Args:
            topic: Research topic/query
            depth: Research depth (shallow/medium/deep). If None, auto-determined
            save_report: Whether to save report to file
            
        Returns:
            Dictionary with research results, synthesis, and report
        """
        print(f"\n🔍 Starting research on: {topic}")
        print("-" * 60)
        
        # Step 1: Plan research
        print("\n📋 Step 1: Planning research strategy...")
        plan = self.planner.plan_research(topic)
        research_depth = depth or plan.get("depth", "medium")
        print(f"   ✓ Research depth: {research_depth}")
        print(f"   ✓ Sub-topics identified: {len(plan.get('sub_topics', []))}")
        
        # Step 2: Conduct web research
        print(f"\n🌐 Step 2: Conducting web research...")
        research_results = self.researcher.research_topic(topic, depth=research_depth)
        print(f"   ✓ Found {len(research_results)} sources")
        
        if not research_results:
            return {
                "error": "No research results found. Please check your internet connection and API keys.",
                "topic": topic
            }
        
        # Step 3: Synthesize information
        print(f"\n🧠 Step 3: Synthesizing information from {len(research_results)} sources...")
        synthesis_data = self.synthesizer.synthesize(research_results, topic)
        print("   ✓ Information synthesized")
        
        # Step 4: Generate report
        print(f"\n📝 Step 4: Generating report...")
        markdown_report = self.report_generator.generate_markdown_report(
            topic, synthesis_data, research_results
        )
        
        # Save report if requested
        report_path = None
        if save_report:
            report_path = self.report_generator.save_report(markdown_report, topic)
            print(f"   ✓ Report saved to: {report_path}")
        
        print("\n" + "=" * 60)
        print("✅ Research completed successfully!")
        print("=" * 60)
        
        return {
            "topic": topic,
            "plan": plan,
            "research_results": research_results,
            "synthesis": synthesis_data,
            "report": markdown_report,
            "report_path": report_path,
            "num_sources": len(research_results)
        }
    
    def quick_research(self, topic: str) -> str:
        """
        Quick research that returns just the report text
        
        Args:
            topic: Research topic
            
        Returns:
            Report text as string
        """
        result = self.research(topic, depth="shallow", save_report=False)
        return result.get("report", "Research failed.")

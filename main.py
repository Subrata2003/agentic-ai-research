"""CLI interface for the Intelligent Research Agent"""

import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from src.agent.research_agent import ResearchAgent
from src.utils.config import Config

# Force UTF-8 output on Windows to avoid cp1252 emoji encoding errors
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(force_terminal=True, highlight=False)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Intelligent Research & Report Generator Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Impact of AI on healthcare"
  python main.py "Climate change solutions" --depth deep
  python main.py "Python best practices" --depth shallow --no-save
        """
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="Research topic or query"
    )
    
    parser.add_argument(
        "--depth",
        type=str,
        choices=["shallow", "medium", "deep"],
        default=None,
        help="Research depth (default: auto-determined)"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save report to file"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "html"],
        default="markdown",
        help="Report format (default: markdown)"
    )
    
    args = parser.parse_args()
    
    # Display banner
    banner = (
        "Intelligent Research & Report Generator Agent v2\n\n"
        "Conducting autonomous research and generating comprehensive reports..."
    )
    console.print(Panel(banner, style="bold blue"))
    
    try:
        # Initialize agent
        agent = ResearchAgent()
        
        # Conduct research (sync wrapper over the async pipeline)
        result = agent.research_sync(
            topic=args.topic,
            depth=args.depth,
            save_report=not args.no_save,
        )
        
        if "error" in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            sys.exit(1)
        
        # Display report
        console.print("\n")
        console.print(Panel(
            Markdown(result["report"]),
            title=f"Research Report: {args.topic}",
            border_style="green"
        ))
        
        if result.get("report_path"):
            console.print(f"\n[green]Report saved to:[/green] {result['report_path']}")

        synthesis   = result.get("synthesis")
        critique    = result.get("critique")
        fact_checks = result.get("fact_checks", [])

        confidence  = f"{synthesis.overall_confidence:.0%}" if synthesis else "N/A"
        quality     = f"{critique.overall_quality:.0%}"     if critique  else "N/A"

        from src.agent.fact_checker_agent import FactCheckerAgent
        fc_summary  = FactCheckerAgent.summary(fact_checks)

        console.print(f"\n[cyan]Sources analysed:[/cyan]    {result['num_sources']}")
        console.print(f"[cyan]Synthesis confidence:[/cyan] {confidence}")
        console.print(f"[cyan]Critic quality score:[/cyan] {quality}")
        console.print(
            f"[cyan]Fact-check results:[/cyan]  "
            f"[green]✓ {fc_summary.get('SUPPORTED', 0)} supported[/green]  "
            f"[yellow]? {fc_summary.get('UNVERIFIABLE', 0)} unverifiable[/yellow]  "
            f"[red]✗ {fc_summary.get('CONTRADICTED', 0)} contradicted[/red]"
        )
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Research interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

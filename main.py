"""CLI interface for the Intelligent Research Agent"""

import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from src.agent.research_agent import ResearchAgent
from src.utils.config import Config

console = Console()


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
    banner = """
    🤖 Intelligent Research & Report Generator Agent
    
    Conducting autonomous research and generating comprehensive reports...
    """
    console.print(Panel(banner, style="bold blue"))
    
    try:
        # Initialize agent
        agent = ResearchAgent()
        
        # Conduct research
        result = agent.research(
            topic=args.topic,
            depth=args.depth,
            save_report=not args.no_save
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
            console.print(f"\n[green]✓ Report saved to:[/green] {result['report_path']}")
        
        console.print(f"\n[cyan]Sources analyzed:[/cyan] {result['num_sources']}")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Research interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

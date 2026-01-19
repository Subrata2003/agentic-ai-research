"""Example usage of the Research Agent"""

from src.agent.research_agent import ResearchAgent

def main():
    """Example: Research a topic"""
    
    # Initialize the agent
    agent = ResearchAgent()
    
    # Conduct research
    topic = "Impact of artificial intelligence on healthcare"
    print(f"Researching: {topic}\n")
    
    result = agent.research(
        topic=topic,
        depth="medium",  # Options: shallow, medium, deep
        save_report=True
    )
    
    # Display results
    print("\n" + "="*60)
    print("RESEARCH COMPLETE")
    print("="*60)
    print(f"\nTopic: {result['topic']}")
    print(f"Sources analyzed: {result['num_sources']}")
    print(f"Report saved to: {result.get('report_path', 'Not saved')}")
    print("\nReport Preview:")
    print("-" * 60)
    print(result['report'][:500] + "...")  # Show first 500 chars

if __name__ == "__main__":
    main()

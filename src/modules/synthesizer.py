"""Information synthesis module for combining research findings"""

from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.utils.config import Config


class Synthesizer:
    """Synthesizes information from multiple sources into coherent insights"""
    
    def __init__(self):
        Config.validate()
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            max_output_tokens=Config.MAX_TOKENS,
            google_api_key=Config.GEMINI_API_KEY
        )
    
    def synthesize(self, research_results: List[Dict[str, str]], topic: str) -> Dict[str, any]:
        """
        Synthesize research results into structured insights
        
        Args:
            research_results: List of research results with title, url, content
            topic: Research topic
            
        Returns:
            Dictionary with synthesized information
        """
        # Prepare content for synthesis
        sources_text = self._prepare_sources_text(research_results)
        
        # Create synthesis prompt
        prompt = self._create_synthesis_prompt(topic, sources_text)
        
        # Get synthesis from LLM
        # Combine system message and prompt for Gemini (which doesn't use separate system messages)
        full_prompt = f"""You are an expert researcher and analyst. Your task is to synthesize information from multiple sources into coherent, well-structured insights.

{prompt}"""
        
        messages = [HumanMessage(content=full_prompt)]
        
        response = self.llm.invoke(messages)
        synthesis_text = response.content

        # Ensure synthesis is always a string
        if isinstance(synthesis_text, list):
            synthesis_text = "\n".join(
                item if isinstance(item, str) else str(item)
                for item in synthesis_text
            )

        structured_data = self._extract_structured_data(synthesis_text, research_results)

        
        return structured_data
    
    def _prepare_sources_text(self, research_results: List[Dict[str, str]]) -> str:
        """Prepare sources text for synthesis"""
        sources_text = ""
        for i, result in enumerate(research_results, 1):
            sources_text += f"\n\n--- Source {i} ---\n"
            sources_text += f"Title: {result.get('title', 'N/A')}\n"
            sources_text += f"URL: {result.get('url', 'N/A')}\n"
            sources_text += f"Content: {result.get('content', '')[:2000]}...\n"  # Limit content length
        
        return sources_text
    
    def _create_synthesis_prompt(self, topic: str, sources_text: str) -> str:
        """Create prompt for synthesis"""
        return f"""Please synthesize the following research findings about "{topic}" into a comprehensive analysis.

Research Sources:
{sources_text}

Please provide a synthesis that includes:
1. **Key Findings**: Main insights and important information
2. **Main Themes**: Common themes and patterns across sources
3. **Different Perspectives**: Conflicting or complementary viewpoints
4. **Important Statistics/Data**: Key numbers, facts, and figures
5. **Gaps or Limitations**: What information might be missing or needs further research
6. **Conclusion**: Overall summary and implications

Format your response clearly with sections and bullet points where appropriate."""

    def _extract_structured_data(self, synthesis_text: str, research_results: List[Dict[str, str]]) -> Dict[str, any]:
        """Extract structured data from synthesis text"""
        return {
            "synthesis": synthesis_text,
            "num_sources": len(research_results),
            "sources": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", "")
                }
                for r in research_results
            ]
        }

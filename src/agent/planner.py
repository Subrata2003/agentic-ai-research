"""Research planning module for strategizing research approach"""

from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.utils.config import Config


class ResearchPlanner:
    """Plans research strategy based on query complexity"""
    
    def __init__(self):
        Config.validate()
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=0.3,  # Lower temperature for planning
            max_output_tokens=1000,
            google_api_key=Config.GEMINI_API_KEY
        )
    
    def plan_research(self, query: str) -> Dict[str, any]:
        """
        Create a research plan for the given query
        
        Args:
            query: Research query/topic
            
        Returns:
            Dictionary with research plan including depth, sub-topics, etc.
        """
        prompt = f"""Analyze the following research query and create a research plan:

Query: "{query}"

Please determine:
1. Research depth needed (shallow/medium/deep)
2. Key sub-topics to explore
3. Important aspects to focus on
4. Expected complexity level

Respond in a structured format."""

        # Combine system message and prompt for Gemini
        full_prompt = f"""You are an expert research strategist. Analyze queries and create optimal research plans.

{prompt}"""
        
        messages = [HumanMessage(content=full_prompt)]
        
        response = self.llm.invoke(messages)
        plan_text = response.content
        
        # Determine depth based on query complexity
        depth = self._determine_depth(query, plan_text)
        
        # Extract sub-topics
        sub_topics = self._extract_sub_topics(query, plan_text)
        
        return {
            "query": query,
            "depth": depth,
            "sub_topics": sub_topics,
            "plan": plan_text
        }
    
    def _determine_depth(self, query: str, plan_text: str) -> str:
        """Determine research depth based on query"""
        query_lower = query.lower()
        
        # Simple heuristics
        if any(word in query_lower for word in ["overview", "introduction", "basics", "what is"]):
            return "shallow"
        elif any(word in query_lower for word in ["analysis", "impact", "effects", "comparison", "detailed"]):
            return "deep"
        else:
            return "medium"
    
    def _extract_sub_topics(self, query: str, plan_text: str) -> List[str]:
        """Extract sub-topics from plan"""
        # Simple extraction - can be enhanced
        sub_topics = [query]  # Always include main topic
        
        # Add common sub-topics based on query type
        if "impact" in query.lower():
            sub_topics.extend([f"{query} benefits", f"{query} challenges"])
        
        return sub_topics

"""Research planning module — returns a typed PlannerOutput every time."""

import json
import re
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.models.outputs import PlannerOutput, ResearchDepth, SubTopic
from src.utils.config import Config


class ResearchPlanner:
    """Plans research strategy and returns a validated PlannerOutput."""

    def __init__(self):
        Config.validate()
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=0.3,
            max_output_tokens=2000,
            google_api_key=Config.GEMINI_API_KEY,
        )
        self.parser = PydanticOutputParser(pydantic_object=PlannerOutput)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan_research(self, query: str, depth_override: Optional[str] = None) -> PlannerOutput:
        """
        Create a structured research plan for the given query.

        Args:
            query: Research topic / question.
            depth_override: Force a specific depth ('shallow'|'medium'|'deep').

        Returns:
            Validated PlannerOutput instance.
        """
        format_instructions = self.parser.get_format_instructions()

        prompt = f"""You are an expert research strategist. Analyze the following research query
and create an optimal research plan with specific sub-topics to investigate.

Query: "{query}"

Determine:
- The appropriate research depth (shallow = overview, medium = balanced, deep = comprehensive analysis)
- 3–6 specific sub-topic queries to search in parallel (each a standalone search query)
- The estimated number of sources needed
- A complexity score from 0.0 (simple) to 1.0 (very complex)

Heuristics for depth:
  shallow → "overview", "what is", "introduction", "basics"
  deep    → "analysis", "impact", "effects", "comparison", "future", "detailed"
  medium  → everything else

{format_instructions}

Respond ONLY with the JSON object. No explanation, no markdown fences."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        raw_text = self._extract_content(response.content)

        try:
            return self.parser.parse(raw_text)
        except Exception:
            return self._repair_and_parse(raw_text, query, depth_override)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_content(self, content) -> str:
        """Normalise Gemini's response.content to a plain string."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(item.get("text", ""))
            return "\n".join(parts)
        return str(content)

    def _repair_and_parse(
        self, raw_text: str, query: str, depth_override: Optional[str] = None
    ) -> PlannerOutput:
        """
        Two-stage fallback:
        1. Strip markdown fences and try JSON parsing directly.
        2. If that fails, build a minimal valid PlannerOutput from heuristics.
        """
        # Stage 1 — strip markdown fences and retry
        cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
        # Extract first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return PlannerOutput(**data)
            except Exception:
                pass

        # Stage 2 — ask the LLM to fix its own output
        fix_prompt = f"""The following text should be valid JSON matching this schema:
{self.parser.get_format_instructions()}

Text to fix:
{raw_text[:1500]}

Return ONLY the corrected JSON object."""
        try:
            fix_response = self.llm.invoke([HumanMessage(content=fix_prompt)])
            fix_text = self._extract_content(fix_response.content)
            fix_clean = re.sub(r"```(?:json)?", "", fix_text).strip().rstrip("`").strip()
            return self.parser.parse(fix_clean)
        except Exception:
            pass

        # Stage 3 — hard fallback: build from heuristics
        depth = depth_override or self._heuristic_depth(query)
        return PlannerOutput(
            depth=ResearchDepth(depth),
            sub_topics=[
                SubTopic(query=query, priority=1, rationale="Primary research topic"),
                SubTopic(query=f"{query} overview", priority=2, rationale="General context"),
                SubTopic(query=f"{query} latest developments", priority=3, rationale="Recent news"),
            ],
            estimated_sources_needed={"shallow": 5, "medium": 10, "deep": 20}[depth],
            complexity_score=0.5,
        )

    def _heuristic_depth(self, query: str) -> str:
        """Simple keyword-based depth heuristic (kept from original)."""
        q = query.lower()
        if any(w in q for w in ["overview", "introduction", "basics", "what is"]):
            return "shallow"
        if any(w in q for w in ["analysis", "impact", "effects", "comparison", "detailed", "future"]):
            return "deep"
        return "medium"

"""
Synthesis module — combines research results into a fully structured,
citation-verified SynthesizerOutput.

Every factual claim in the output must carry inline [n] citation markers.
The source_quotes field is machine-verified by FactCheckerAgent in Phase 3.
"""

import json
import re
from typing import List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.models.outputs import (
    SynthesizerOutput,
    SynthesisSection,
    SourceQuote,
)
from src.utils.config import Config

# Sections the LLM must always produce
REQUIRED_SECTIONS = [
    "Key Findings",
    "Main Themes",
    "Different Perspectives",
    "Important Statistics & Data",
    "Gaps & Limitations",
    "Conclusion",
]


class Synthesizer:
    """Synthesises research results into a validated SynthesizerOutput."""

    def __init__(self):
        Config.validate()
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            max_output_tokens=8192,
            google_api_key=Config.GEMINI_API_KEY,
        )
        self.parser = PydanticOutputParser(pydantic_object=SynthesizerOutput)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesize(
        self, research_results: List[Dict[str, str]], topic: str
    ) -> SynthesizerOutput:
        """
        Synthesise research results into a structured, cited report.

        Args:
            research_results: List of dicts with keys title, url, content, source.
            topic: The original research topic string.

        Returns:
            Validated SynthesizerOutput with inline citations.
        """
        sources_block = self._prepare_sources_block(research_results)
        prompt = self._build_prompt(topic, sources_block, len(research_results))

        response = self.llm.invoke([HumanMessage(content=prompt)])
        raw_text = self._extract_content(response.content)

        try:
            result = self.parser.parse(raw_text)
            # Stamp topic in case LLM omitted it
            result.topic = topic
            return result
        except Exception:
            return self._repair_and_parse(raw_text, topic, research_results)

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def _prepare_sources_block(self, research_results: List[Dict[str, str]]) -> str:
        """
        Build a numbered source block with excerpts.
        This is what the LLM sees when writing citations.
        """
        lines = []
        for i, r in enumerate(research_results, 1):
            content = r.get("content", "")
            # Take the first 1500 chars as the excerpt the LLM can quote from
            excerpt = content[:1500].replace("\n", " ").strip()
            lines.append(
                f"[{i}] Title: {r.get('title', 'Untitled')}\n"
                f"    URL: {r.get('url', '')}\n"
                f"    Excerpt: {excerpt}\n"
            )
        return "\n".join(lines)

    def _build_prompt(self, topic: str, sources_block: str, n_sources: int) -> str:
        format_instructions = self.parser.get_format_instructions()

        return f"""You are a senior research analyst. Synthesize the following {n_sources} sources
about "{topic}" into a comprehensive, structured report.

═══════════════════════════════════════════════════════
SOURCES  (cite using [n] numbers exactly as shown)
═══════════════════════════════════════════════════════
{sources_block}

═══════════════════════════════════════════════════════
CITATION RULES — MANDATORY
═══════════════════════════════════════════════════════
1. Every factual claim MUST end with one or more [n] markers, e.g. "...rose 40% [2][5]."
2. Use ONLY source indices 1 through {n_sources}. Never invent a citation.
3. The source_quotes array MUST contain one entry per unique [n] you used.
   Each entry's exact_quote must be a verbatim snippet (≤200 chars) copied
   directly from that source's Excerpt above. This will be machine-verified.
4. If a fact cannot be traced to any excerpt, do not state it.

═══════════════════════════════════════════════════════
REQUIRED SECTIONS (all six must appear)
═══════════════════════════════════════════════════════
{', '.join(REQUIRED_SECTIONS)}

═══════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════
{format_instructions}

Respond ONLY with the JSON object. No explanation, no markdown fences."""

    # ------------------------------------------------------------------
    # Content extraction + repair
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
                    # Handle Gemini content blocks: {'type':'text','text':'...','extras':{}}
                    parts.append(item.get("text", ""))
            return "\n".join(parts)
        return str(content)

    def _repair_and_parse(
        self,
        raw_text: str,
        topic: str,
        research_results: List[Dict[str, str]],
    ) -> SynthesizerOutput:
        """
        Three-stage fallback:
        1. Strip markdown fences and try JSON directly.
        2. Ask the LLM to fix its own JSON.
        3. Build a minimal valid SynthesizerOutput from the raw text.
        """
        # Stage 1 — clean and retry
        cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return SynthesizerOutput(**data)
            except Exception:
                pass

        # Stage 2 — LLM self-repair
        fix_prompt = (
            f"Fix this malformed JSON to match the schema:\n"
            f"{self.parser.get_format_instructions()}\n\n"
            f"Malformed JSON (first 2000 chars):\n{raw_text[:2000]}\n\n"
            f"Return ONLY the corrected JSON object."
        )
        try:
            fix_response = self.llm.invoke([HumanMessage(content=fix_prompt)])
            fix_text = self._extract_content(fix_response.content)
            fix_clean = re.sub(r"```(?:json)?", "", fix_text).strip().rstrip("`").strip()
            result = self.parser.parse(fix_clean)
            result.topic = topic
            return result
        except Exception:
            pass

        # Stage 3 — hard fallback: wrap the raw text in a minimal structure
        # The raw_text itself is good prose, just not valid JSON
        fallback_text = self._extract_content(raw_text) if not isinstance(raw_text, str) else raw_text

        sections = []
        for heading in REQUIRED_SECTIONS:
            # Try to find this section in the raw text
            pattern = re.compile(
                rf"(?:#{{}}{re.escape(heading)}|{re.escape(heading)})[:\s]+(.*?)(?=\n#|\n[A-Z]|$)",
                re.IGNORECASE | re.DOTALL,
            )
            m = pattern.search(fallback_text)
            content = m.group(1).strip()[:2000] if m else "See full analysis below."
            sections.append(
                SynthesisSection(heading=heading, content=content, citations_used=[])
            )

        # Build source quotes from available sources
        source_quotes = []
        for i, r in enumerate(research_results[:5], 1):
            excerpt = r.get("content", "")[:150].replace("\n", " ").strip()
            if excerpt:
                source_quotes.append(
                    SourceQuote(
                        source_index=i,
                        url=r.get("url", ""),
                        title=r.get("title", ""),
                        exact_quote=excerpt,
                        relevance_score=0.5,
                    )
                )

        return SynthesizerOutput(
            topic=topic,
            executive_summary=fallback_text[:400].replace("\n", " ").strip(),
            sections=sections,
            key_statistics=[],
            gaps_identified=[],
            source_quotes=source_quotes,
            overall_confidence=0.4,
        )

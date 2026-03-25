"""
Critic agent — peer-reviews a SynthesizerOutput informed by fact-check results.

Uses Gemini with a structured prompt and PydanticOutputParser to produce
a typed CriticOutput. Falls back gracefully if the LLM response is malformed.
"""

import json
import re
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.models.outputs import CriticOutput, FactCheckResult, FactVerdict, SynthesizerOutput
from src.utils.config import Config


class CriticAgent:
    """
    Peer-reviews a research synthesis and produces a structured CriticOutput.

    Temperature is kept slightly higher than the planner (0.4) to allow the
    critic to surface non-obvious weaknesses rather than just echoing the
    synthesis back.
    """

    def __init__(self):
        Config.validate()
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=0.4,
            max_output_tokens=2000,
            google_api_key=Config.GEMINI_API_KEY,
        )
        self.parser = PydanticOutputParser(pydantic_object=CriticOutput)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def critique(
        self,
        synthesis: SynthesizerOutput,
        fact_checks: List[FactCheckResult],
    ) -> CriticOutput:
        """
        Produce a structured peer-review of the synthesis.

        Args:
            synthesis:   Validated SynthesizerOutput from Synthesizer.
            fact_checks: Results from FactCheckerAgent for this synthesis.

        Returns:
            CriticOutput with quality score, strengths, weaknesses,
            suggested improvements, and missing perspectives.
        """
        prompt = self._build_prompt(synthesis, fact_checks)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        raw = self._extract_content(response.content)

        try:
            return self.parser.parse(raw)
        except Exception:
            return self._repair_and_parse(raw, synthesis, fact_checks)

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        synthesis: SynthesizerOutput,
        fact_checks: List[FactCheckResult],
    ) -> str:
        # Fact-check summary
        total   = len(fact_checks)
        by_verdict = {v.value: 0 for v in FactVerdict}
        for fc in fact_checks:
            by_verdict[fc.verdict.value] += 1

        fc_summary = (
            f"- Supported:     {by_verdict['SUPPORTED']} / {total}\n"
            f"- Unverifiable:  {by_verdict['UNVERIFIABLE']} / {total}\n"
            f"- Contradicted:  {by_verdict['CONTRADICTED']} / {total}"
        )

        # Section overview
        sections_overview = "\n".join(
            f"  [{i+1}] {s.heading} — {len(s.content)} chars, "
            f"{len(s.citations_used)} citation(s)"
            for i, s in enumerate(synthesis.sections)
        )

        # Gaps already flagged by the synthesiser
        gaps_text = (
            "\n".join(f"  - {g}" for g in synthesis.gaps_identified)
            if synthesis.gaps_identified
            else "  (none reported)"
        )

        format_instructions = self.parser.get_format_instructions()

        return f"""You are a senior research editor conducting a structured peer-review.

══════════════════════════════════════════════════════
RESEARCH BRIEF
══════════════════════════════════════════════════════
Topic:              {synthesis.topic}
Overall confidence: {synthesis.overall_confidence:.0%}
Total citations:    {len(synthesis.source_quotes)}

EXECUTIVE SUMMARY:
{synthesis.executive_summary}

SECTIONS PRODUCED:
{sections_overview}

KEY STATISTICS ({len(synthesis.key_statistics)} found):
{chr(10).join(f"  - {s}" for s in synthesis.key_statistics[:5]) or "  (none)"}

GAPS FLAGGED BY SYNTHESISER:
{gaps_text}

══════════════════════════════════════════════════════
FACT-CHECK RESULTS
══════════════════════════════════════════════════════
{fc_summary}

══════════════════════════════════════════════════════
YOUR TASK
══════════════════════════════════════════════════════
Critically evaluate this research synthesis. Be specific and constructive.

1. overall_quality  — float 0.0–1.0 reflecting depth, accuracy, balance.
   Base it on: citation coverage, fact-check pass rate, section completeness.
2. strengths        — what the synthesis does well (2–4 points).
3. weaknesses       — logical gaps, unsupported claims, shallow sections (2–4 points).
4. suggested_improvements — concrete, actionable next steps (2–3 points).
5. missing_perspectives   — stakeholders or viewpoints absent from the synthesis.

══════════════════════════════════════════════════════
OUTPUT FORMAT
══════════════════════════════════════════════════════
{format_instructions}

Respond ONLY with the JSON object. No explanation, no markdown fences."""

    # ------------------------------------------------------------------
    # Content extraction + repair
    # ------------------------------------------------------------------

    def _extract_content(self, content) -> str:
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
        self,
        raw_text: str,
        synthesis: SynthesizerOutput,
        fact_checks: List[FactCheckResult],
    ) -> CriticOutput:
        """Two-stage fallback: JSON-clean retry → heuristic fallback."""

        # Stage 1 — strip fences and retry
        cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return CriticOutput(**json.loads(match.group()))
            except Exception:
                pass

        # Stage 2 — ask the LLM to fix its own JSON
        fix_prompt = (
            f"Fix this malformed JSON to match the schema:\n"
            f"{self.parser.get_format_instructions()}\n\n"
            f"Malformed JSON:\n{raw_text[:1500]}\n\n"
            f"Return ONLY the corrected JSON object."
        )
        try:
            fix_resp = self.llm.invoke([HumanMessage(content=fix_prompt)])
            fix_text = self._extract_content(fix_resp.content)
            fix_clean = re.sub(r"```(?:json)?", "", fix_text).strip().rstrip("`").strip()
            return self.parser.parse(fix_clean)
        except Exception:
            pass

        # Stage 3 — hard heuristic fallback
        supported_pct = (
            sum(1 for f in fact_checks if f.verdict == FactVerdict.SUPPORTED)
            / max(len(fact_checks), 1)
        )
        quality = round((supported_pct + synthesis.overall_confidence) / 2, 2)

        return CriticOutput(
            overall_quality=quality,
            strengths=[
                "Research covers the primary aspects of the topic.",
                f"{len(synthesis.source_quotes)} citations were produced.",
            ],
            weaknesses=[
                f"{len(fact_checks) - round(supported_pct * len(fact_checks))} "
                "claims could not be fully verified against source content.",
            ],
            suggested_improvements=[
                "Expand source diversity to include primary literature.",
                "Add quantitative data where possible.",
            ],
            missing_perspectives=[
                "Industry practitioners",
                "Policy makers",
                "Affected communities",
            ],
        )

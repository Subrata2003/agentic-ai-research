"""
Pure-Python research quality scorer — zero LLM calls, fully deterministic.

Four dimensions (weights sum to 1.0):
  source_coverage      25%  — fraction of retrieved sources cited in synthesis
  citation_accuracy    30%  — fraction of source_quotes fuzzy-matched in raw content
  synthesis_coherence  25%  — fraction of sections with substantive content (>100 chars)
  factual_density      20%  — fraction of SUPPORTED verdicts in fact-check results

The composite 'overall' score drives UI colour-coding:
  ≥ 0.80  →  emerald  (high quality)
  ≥ 0.60  →  amber    (medium quality)
  <  0.60  →  red      (needs improvement)
"""

from difflib import SequenceMatcher
from typing import List, Dict, Optional

from src.models.outputs import (
    EvaluationScore,
    FactCheckResult,
    FactVerdict,
    SynthesizerOutput,
)

# Dimension weights — must sum to 1.0
_WEIGHTS = {
    "source_coverage":     0.25,
    "citation_accuracy":   0.30,
    "synthesis_coherence": 0.25,
    "factual_density":     0.20,
}

# Minimum section content length to be counted as "substantive"
_MIN_SECTION_CHARS = 100

# Fuzzy-match threshold for citation verification (matches FactCheckerAgent)
_FUZZY_THRESHOLD = 0.70


class ResearchEvaluator:
    """
    Computes an EvaluationScore from the pipeline outputs.

    Usage::

        evaluator = ResearchEvaluator()
        score = evaluator.score(synthesis, fact_checks, raw_sources)
    """

    def score(
        self,
        synthesis: SynthesizerOutput,
        fact_checks: List[FactCheckResult],
        raw_sources: List[Dict],
    ) -> EvaluationScore:
        """
        Compute all four quality dimensions and return a typed EvaluationScore.

        Args:
            synthesis:    Validated SynthesizerOutput from Synthesizer.
            fact_checks:  List of FactCheckResult from FactCheckerAgent.
            raw_sources:  Raw search result dicts (list of {title, url, content, …}).

        Returns:
            EvaluationScore with per-dimension scores and weighted overall.
        """
        coverage   = self._source_coverage(synthesis, raw_sources)
        accuracy   = self._citation_accuracy(synthesis, raw_sources)
        coherence  = self._synthesis_coherence(synthesis)
        density    = self._factual_density(fact_checks)

        overall = (
            coverage  * _WEIGHTS["source_coverage"]
            + accuracy  * _WEIGHTS["citation_accuracy"]
            + coherence * _WEIGHTS["synthesis_coherence"]
            + density   * _WEIGHTS["factual_density"]
        )
        overall = round(min(max(overall, 0.0), 1.0), 4)

        return EvaluationScore(
            source_coverage=round(coverage,  4),
            citation_accuracy=round(accuracy,  4),
            synthesis_coherence=round(coherence, 4),
            factual_density=round(density,   4),
            overall=overall,
            breakdown={
                "cited_source_indices":   sorted(self._cited_indices(synthesis)),
                "total_raw_sources":      len(raw_sources),
                "quotes_verified":        self._count_verified_quotes(synthesis, raw_sources),
                "total_quotes":           len(synthesis.source_quotes),
                "substantive_sections":   self._count_substantive_sections(synthesis),
                "total_sections":         len(synthesis.sections),
                "supported_facts":        sum(
                    1 for fc in fact_checks if fc.verdict == FactVerdict.SUPPORTED
                ),
                "total_fact_checks":      len(fact_checks),
                "weights":                _WEIGHTS,
            },
        )

    # ------------------------------------------------------------------
    # Dimension 1 — Source Coverage  (weight 25%)
    # ------------------------------------------------------------------

    def _source_coverage(
        self, synthesis: SynthesizerOutput, raw_sources: List[Dict]
    ) -> float:
        """
        Fraction of retrieved raw_sources whose index appears in at least
        one source_quote.  Measures how broadly the synthesis draws on the
        available material.
        """
        if not raw_sources:
            return 0.0
        cited = self._cited_indices(synthesis)
        return len(cited) / len(raw_sources)

    def _cited_indices(self, synthesis: SynthesizerOutput) -> set:
        return {q.source_index for q in synthesis.source_quotes}

    # ------------------------------------------------------------------
    # Dimension 2 — Citation Accuracy  (weight 30%)
    # ------------------------------------------------------------------

    def _citation_accuracy(
        self, synthesis: SynthesizerOutput, raw_sources: List[Dict]
    ) -> float:
        """
        For each source_quote, check whether its exact_quote is a genuine
        substring (or fuzzy-match ≥ 70%) of the corresponding raw source
        content.  Returns the fraction of quotes that pass.
        """
        if not synthesis.source_quotes:
            return 0.0

        source_contents = {
            i + 1: r.get("content", "").lower()
            for i, r in enumerate(raw_sources)
        }

        verified = self._count_verified_quotes(synthesis, raw_sources, source_contents)
        return verified / len(synthesis.source_quotes)

    def _count_verified_quotes(
        self,
        synthesis: SynthesizerOutput,
        raw_sources: List[Dict],
        source_contents: Optional[Dict[int, str]] = None,
    ) -> int:
        if source_contents is None:
            source_contents = {
                i + 1: r.get("content", "").lower()
                for i, r in enumerate(raw_sources)
            }

        verified = 0
        for quote in synthesis.source_quotes:
            content = source_contents.get(quote.source_index, "")
            if not content:
                continue

            needle = quote.exact_quote.lower().strip()
            if not needle:
                continue

            # Fast path — exact substring match
            if needle in content:
                verified += 1
                continue

            # Slow path — sliding-window fuzzy match
            if self._fuzzy_match(needle, content):
                verified += 1

        return verified

    def _fuzzy_match(self, needle: str, haystack: str) -> bool:
        """
        Slide a window of len(needle) chars across haystack and check if any
        window has a SequenceMatcher ratio ≥ _FUZZY_THRESHOLD.
        This mirrors the approach in FactCheckerAgent.
        """
        n = len(needle)
        if n == 0 or len(haystack) < n:
            return False

        step = max(1, n // 4)          # overlap windows generously
        for start in range(0, len(haystack) - n + 1, step):
            window = haystack[start : start + n]
            ratio = SequenceMatcher(None, needle, window).ratio()
            if ratio >= _FUZZY_THRESHOLD:
                return True
        return False

    # ------------------------------------------------------------------
    # Dimension 3 — Synthesis Coherence  (weight 25%)
    # ------------------------------------------------------------------

    def _synthesis_coherence(self, synthesis: SynthesizerOutput) -> float:
        """
        Fraction of synthesis sections whose content exceeds _MIN_SECTION_CHARS
        characters.  Short sections indicate the LLM gave a surface-level answer.
        """
        if not synthesis.sections:
            return 0.0
        substantive = self._count_substantive_sections(synthesis)
        return substantive / len(synthesis.sections)

    def _count_substantive_sections(self, synthesis: SynthesizerOutput) -> int:
        return sum(
            1
            for s in synthesis.sections
            if len(s.content.strip()) >= _MIN_SECTION_CHARS
        )

    # ------------------------------------------------------------------
    # Dimension 4 — Factual Density  (weight 20%)
    # ------------------------------------------------------------------

    def _factual_density(self, fact_checks: List[FactCheckResult]) -> float:
        """
        Fraction of SUPPORTED verdicts out of all fact checks performed.
        High density means most claims are traceable to sources.
        """
        if not fact_checks:
            return 0.5  # neutral when no fact-checks were run
        supported = sum(
            1 for fc in fact_checks if fc.verdict == FactVerdict.SUPPORTED
        )
        return supported / len(fact_checks)


# ---------------------------------------------------------------------------
# Colour label helper — used by CLI and frontend badge logic
# ---------------------------------------------------------------------------

def score_label(overall: float) -> str:
    """Return a human-readable quality label for a given overall score."""
    if overall >= 0.80:
        return "High"
    if overall >= 0.60:
        return "Medium"
    return "Low"


def score_color(overall: float) -> str:
    """Return the UI colour token for a given overall score."""
    if overall >= 0.80:
        return "emerald"
    if overall >= 0.60:
        return "amber"
    return "red"

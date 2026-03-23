"""
Fact-checker agent — verifies every SourceQuote in a SynthesizerOutput
against the raw source content retrieved during the research phase.

Algorithm (no LLM calls — pure Python for speed and determinism):

1. Normalise both quote and source content (lowercase, collapse whitespace).
2. Check for exact substring match → SUPPORTED at 1.0.
3. If not found, slide a window of the quote's length across the content
   and compute SequenceMatcher.ratio() at each position.
4. Best window ratio ≥ FUZZY_THRESHOLD (0.70) → SUPPORTED.
5. Below threshold but content exists → UNVERIFIABLE.
6. No content for that source index → UNVERIFIABLE.
7. A contradicted verdict is reserved for Phase 4 (LLM cross-check);
   here we mark nothing as CONTRADICTED to avoid false negatives.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List

from src.models.outputs import FactCheckResult, FactVerdict, SynthesizerOutput

# Minimum similarity ratio to mark a quote as SUPPORTED
FUZZY_THRESHOLD = 0.70

# How many characters of source content to scan (keeps it fast)
_MAX_CONTENT_SCAN = 8_000


class FactCheckerAgent:
    """
    Verifies source quotes against raw scraped content.
    Pure Python — no LLM calls, deterministic, fast.
    """

    def check(
        self,
        synthesis: SynthesizerOutput,
        raw_sources: List[Dict[str, str]],
    ) -> List[FactCheckResult]:
        """
        Fact-check every SourceQuote in the synthesis.

        Args:
            synthesis:   Validated SynthesizerOutput from Phase 2.
            raw_sources: Original source dicts from the web researcher
                         (same order they were retrieved — 1-indexed).

        Returns:
            List of FactCheckResult, one per SourceQuote.
        """
        # Build corpus: source_index (1-based) → normalised content
        corpus: Dict[int, str] = {}
        for i, src in enumerate(raw_sources, 1):
            raw = src.get("content", "")
            corpus[i] = self._normalise(raw[:_MAX_CONTENT_SCAN])

        results: List[FactCheckResult] = []
        for quote in synthesis.source_quotes:
            idx    = quote.source_index
            needle = self._normalise(quote.exact_quote)
            haystack = corpus.get(idx, "")

            verdict, confidence, evidence = self._verify(needle, haystack, idx)

            results.append(
                FactCheckResult(
                    claim=quote.exact_quote[:200],
                    verdict=verdict,
                    supporting_sources=[idx],
                    confidence=confidence,
                    evidence=evidence,
                )
            )

        return results

    # ------------------------------------------------------------------
    # Core verification logic
    # ------------------------------------------------------------------

    def _verify(
        self,
        needle: str,
        haystack: str,
        source_idx: int,
    ) -> tuple[FactVerdict, float, str]:
        """Return (verdict, confidence, evidence_string)."""

        if not haystack:
            return (
                FactVerdict.UNVERIFIABLE,
                0.30,
                f"Source [{source_idx}] content unavailable for verification.",
            )

        # Fast path — exact substring
        if needle in haystack:
            return (
                FactVerdict.SUPPORTED,
                1.0,
                f"Exact match found in source [{source_idx}].",
            )

        # Sliding-window fuzzy match
        best_ratio = self._sliding_fuzzy(needle, haystack)

        if best_ratio >= FUZZY_THRESHOLD:
            return (
                FactVerdict.SUPPORTED,
                round(best_ratio, 3),
                (
                    f"Fuzzy match {best_ratio:.0%} ≥ {FUZZY_THRESHOLD:.0%} "
                    f"threshold in source [{source_idx}]."
                ),
            )

        return (
            FactVerdict.UNVERIFIABLE,
            round(best_ratio, 3),
            (
                f"Best fuzzy match was {best_ratio:.0%} — below "
                f"{FUZZY_THRESHOLD:.0%} threshold for source [{source_idx}]."
            ),
        )

    def _sliding_fuzzy(self, needle: str, haystack: str) -> float:
        """
        Slide a window of len(needle) across haystack and return the
        highest SequenceMatcher ratio found.

        Step size = max(1, len(needle) // 4) keeps the scan O(n) in
        practice while still catching most real-world near-matches.
        """
        nlen = len(needle)
        hlen = len(haystack)

        if nlen == 0:
            return 0.0
        if hlen < nlen:
            # Haystack shorter than quote — compare directly
            return SequenceMatcher(None, needle, haystack).ratio()

        step   = max(1, nlen // 4)
        best   = 0.0

        for i in range(0, hlen - nlen + 1, step):
            window = haystack[i : i + nlen]
            ratio  = SequenceMatcher(None, needle, window).ratio()
            if ratio > best:
                best = ratio
            if best >= 1.0:
                break  # perfect match — stop early

        return best

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise(text: str) -> str:
        """Lowercase + collapse whitespace for consistent comparison."""
        return re.sub(r"\s+", " ", text.lower()).strip()

    # ------------------------------------------------------------------
    # Aggregate helpers (used by scorer in Phase 4)
    # ------------------------------------------------------------------

    @staticmethod
    def supported_fraction(results: List[FactCheckResult]) -> float:
        """Fraction of results with SUPPORTED verdict."""
        if not results:
            return 0.0
        supported = sum(1 for r in results if r.verdict == FactVerdict.SUPPORTED)
        return supported / len(results)

    @staticmethod
    def summary(results: List[FactCheckResult]) -> Dict[str, int]:
        """Count by verdict — useful for report footer and analytics."""
        counts: Dict[str, int] = {v.value: 0 for v in FactVerdict}
        for r in results:
            counts[r.verdict.value] += 1
        return counts

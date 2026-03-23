"""
Parallel research module — runs every sub-topic from PlannerOutput concurrently.

Uses asyncio.gather + asyncio.Semaphore(5) to control Tavily rate limits.
The sync WebResearcher is offloaded to a ThreadPoolExecutor so it never
blocks the event loop.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Awaitable, Dict, List, Optional

from src.models.outputs import PlannerOutput, SubTopic
from src.modules.web_researcher import WebResearcher

# Progress band allocated to the research stage: 15 % → 55 %
_PROGRESS_START = 0.15
_PROGRESS_END   = 0.55


class ParallelResearcher:
    """
    Runs sub-topic searches concurrently.

    Args:
        max_concurrent: Max simultaneous Tavily / DDG calls (default 5).
    """

    def __init__(self, max_concurrent: int = 5):
        self._researcher = WebResearcher()
        self._semaphore  = asyncio.Semaphore(max_concurrent)
        self._executor   = ThreadPoolExecutor(max_workers=max_concurrent,
                                              thread_name_prefix="researcher")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def research(
        self,
        plan: PlannerOutput,
        depth: str,
        progress_cb: Optional[Callable[[str, float], Awaitable[None]]] = None,
    ) -> List[Dict[str, str]]:
        """
        Search every sub-topic in plan concurrently and return a
        deduplicated, merged list of source dicts.

        Args:
            plan:        PlannerOutput from ResearchPlanner.
            depth:       'shallow' | 'medium' | 'deep'
            progress_cb: async callable(stage, fraction) — called after
                         each sub-topic completes.

        Returns:
            Flat list of source dicts: {title, url, content, source}.
        """
        sorted_topics: List[SubTopic] = sorted(
            plan.sub_topics, key=lambda t: t.priority
        )
        total = len(sorted_topics)
        completed = 0

        async def _search_one(subtopic: SubTopic) -> List[Dict[str, str]]:
            nonlocal completed
            async with self._semaphore:
                loop = asyncio.get_event_loop()
                results: List[Dict[str, str]] = await loop.run_in_executor(
                    self._executor,
                    lambda: self._researcher.research_topic(
                        subtopic.query, depth=depth
                    ),
                )
                completed += 1
                if progress_cb:
                    pct = _PROGRESS_START + (completed / total) * (
                        _PROGRESS_END - _PROGRESS_START
                    )
                    await progress_cb("researching", pct)
                return results

        gathered = await asyncio.gather(
            *[_search_one(st) for st in sorted_topics],
            return_exceptions=True,
        )

        # Flatten + deduplicate by URL
        seen_urls: set[str] = set()
        merged: List[Dict[str, str]] = []
        for batch in gathered:
            if isinstance(batch, Exception):
                # One sub-topic failed — log and continue with the rest
                print(f"   ⚠  Sub-topic search error (skipped): {batch}")
                continue
            for src in batch:
                url = src.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    merged.append(src)

        return merged

    def close(self) -> None:
        """Shut down the thread pool (call once when the agent is done)."""
        self._executor.shutdown(wait=False)

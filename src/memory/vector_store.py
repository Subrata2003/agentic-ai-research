"""
ChromaDB vector store for semantic similarity search over past reports.

On every completed research run the report's topic + executive summary are
embedded with Gemini's embedding-001 model and stored in a persisted
ChromaDB collection.

When a new research request arrives, find_similar() injects the top-N most
semantically related past reports into the Planner's context so it can
build on prior work instead of starting from scratch.
"""

import os
from typing import List, Optional

from src.utils.config import Config


# ---------------------------------------------------------------------------
# Optional import — ChromaDB may not be installed in every environment
# ---------------------------------------------------------------------------

try:
    import chromadb
    from chromadb.config import Settings
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False
    print("Warning: chromadb not installed — vector similarity search disabled.")

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    _EMBEDDINGS_AVAILABLE = True
except ImportError:
    _EMBEDDINGS_AVAILABLE = False
    print("Warning: langchain-google-genai not installed — embeddings disabled.")


# ---------------------------------------------------------------------------
# Collection name
# ---------------------------------------------------------------------------

_COLLECTION_NAME = "research_reports"


class VectorStore:
    """
    Thin wrapper around a persisted ChromaDB collection.

    Embeddings are generated with Gemini's embedding-001 model.
    Falls back to a no-op stub when ChromaDB or google-genai is unavailable.
    """

    def __init__(self):
        self._available = _CHROMA_AVAILABLE and _EMBEDDINGS_AVAILABLE
        if not self._available:
            print("VectorStore: running in no-op mode (dependency missing).")
            return

        persist_path = Config.CHROMA_PERSIST_PATH
        os.makedirs(persist_path, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._embedder = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=Config.GEMINI_API_KEY,
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_report(
        self,
        *,
        report_id: str,
        topic: str,
        executive_summary: str,
        depth: str,
        overall_score: Optional[float] = None,
    ) -> None:
        """
        Embed and store a report so future runs can discover it.

        The text that gets embedded is:  topic + "\\n\\n" + executive_summary
        This gives good semantic signal without blowing token limits.

        Args:
            report_id:         UUID from db.save_report().
            topic:             Research topic string.
            executive_summary: 2-3 sentence summary from SynthesizerOutput.
            depth:             'shallow' | 'medium' | 'deep'
            overall_score:     EvaluationScore.overall (optional).
        """
        if not self._available:
            return

        text = f"{topic}\n\n{executive_summary}"
        try:
            embedding = self._embedder.embed_query(text)
            self._collection.upsert(
                ids=[report_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "report_id":     report_id,
                    "topic":         topic[:500],
                    "depth":         depth,
                    "overall_score": str(overall_score) if overall_score is not None else "",
                }],
            )
        except Exception as e:
            print(f"VectorStore.add_report error (non-fatal): {e}")

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def find_similar(self, topic: str, n: int = 5) -> List[dict]:
        """
        Return the top-n most semantically similar past reports.

        Args:
            topic: The new research topic to compare against.
            n:     Maximum number of similar reports to return.

        Returns:
            List of dicts with keys: report_id, topic, distance, metadata.
            Empty list if the store is unavailable or contains < 2 documents.
        """
        if not self._available:
            return []

        try:
            count = self._collection.count()
            if count == 0:
                return []

            actual_n = min(n, count)
            embedding = self._embedder.embed_query(topic)
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=actual_n,
                include=["documents", "metadatas", "distances"],
            )

            similar = []
            ids       = results.get("ids",       [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            documents = results.get("documents", [[]])[0]

            for rid, meta, dist, doc in zip(ids, metadatas, distances, documents):
                similar.append({
                    "report_id": rid,
                    "topic":     meta.get("topic", ""),
                    "depth":     meta.get("depth", ""),
                    "score":     meta.get("overall_score", ""),
                    "distance":  round(dist, 4),
                    "summary":   doc[:300],
                })
            return similar

        except Exception as e:
            print(f"VectorStore.find_similar error (non-fatal): {e}")
            return []

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return number of embedded reports."""
        if not self._available:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def delete_report(self, report_id: str) -> None:
        """Remove a single report from the vector store."""
        if not self._available:
            return
        try:
            self._collection.delete(ids=[report_id])
        except Exception as e:
            print(f"VectorStore.delete_report error (non-fatal): {e}")

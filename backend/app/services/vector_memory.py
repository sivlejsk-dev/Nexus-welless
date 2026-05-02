"""
Vector memory service — ChromaDB-backed semantic search over conversation history.

Each user gets two collections:
  - {user_id}_conversations : episodic turns (user message + AI response)
  - {user_id}_knowledge     : domain facts and insights extracted from sessions

ChromaDB's default embedding function (all-MiniLM-L6-v2 via ONNX) is used so
there is no external embedding API dependency.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)

# Persist to disk so memories survive restarts
_CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")


class VectorMemoryService:
    """
    Per-user vector memory backed by ChromaDB.

    Stores conversation turns and domain knowledge as embeddings so that
    semantically similar past exchanges can be retrieved for any new query.
    """

    def __init__(self, persist_dir: str = _CHROMA_DIR) -> None:
        os.makedirs(persist_dir, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        # Cache open collections to avoid repeated get_or_create calls
        self._collections: dict[str, chromadb.Collection] = {}

    # ── Collection helpers ────────────────────────────────────────────────────

    def _conv_collection(self, user_id: str) -> chromadb.Collection:
        key = f"{user_id}_conversations"
        if key not in self._collections:
            self._collections[key] = self._client.get_or_create_collection(
                name=key,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[key]

    def _know_collection(self, user_id: str) -> chromadb.Collection:
        key = f"{user_id}_knowledge"
        if key not in self._collections:
            self._collections[key] = self._client.get_or_create_collection(
                name=key,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[key]

    # ── Write ─────────────────────────────────────────────────────────────────

    def store_conversation_turn(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        domain: str = "general",
        intent: str = "unknown",
        turn_id: str | None = None,
    ) -> str:
        """Embed and store a single conversation turn."""
        # Combine both sides so retrieval captures the full exchange
        document = f"User: {user_message}\nNexus: {ai_response}"

        if turn_id is None:
            # Deterministic ID so re-storing the same turn is idempotent
            turn_id = hashlib.sha256(
                f"{user_id}:{user_message[:80]}:{ai_response[:80]}".encode()
            ).hexdigest()[:16]

        metadata = {
            "user_id": user_id,
            "domain": domain,
            "intent": intent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": user_message[:500],
            "ai_response": ai_response[:500],
        }

        col = self._conv_collection(user_id)
        # Upsert so duplicate turns don't raise
        col.upsert(
            ids=[turn_id],
            documents=[document],
            metadatas=[metadata],
        )
        return turn_id

    def store_knowledge(
        self,
        user_id: str,
        fact: str,
        domain: str = "general",
        source: str = "conversation",
        knowledge_id: str | None = None,
    ) -> str:
        """Embed and store a domain fact or insight."""
        if knowledge_id is None:
            knowledge_id = hashlib.sha256(
                f"{user_id}:{fact[:120]}".encode()
            ).hexdigest()[:16]

        metadata = {
            "user_id": user_id,
            "domain": domain,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        col = self._know_collection(user_id)
        col.upsert(
            ids=[knowledge_id],
            documents=[fact],
            metadatas=[metadata],
        )
        return knowledge_id

    # ── Read ──────────────────────────────────────────────────────────────────

    def search_conversations(
        self,
        user_id: str,
        query: str,
        n_results: int = 5,
        domain_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return the most semantically similar past conversation turns."""
        col = self._conv_collection(user_id)
        if col.count() == 0:
            return []

        where = {"domain": domain_filter} if domain_filter else None
        try:
            results = col.query(
                query_texts=[query],
                n_results=min(n_results, col.count()),
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.warning("ChromaDB conversation query failed: %s", exc)
            return []

        return _format_results(results)

    def search_knowledge(
        self,
        user_id: str,
        query: str,
        n_results: int = 5,
        domain_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return the most semantically similar stored facts."""
        col = self._know_collection(user_id)
        if col.count() == 0:
            return []

        where = {"domain": domain_filter} if domain_filter else None
        try:
            results = col.query(
                query_texts=[query],
                n_results=min(n_results, col.count()),
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.warning("ChromaDB knowledge query failed: %s", exc)
            return []

        return _format_results(results)

    def search_all(
        self,
        user_id: str,
        query: str,
        n_results: int = 6,
        domain_filter: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Search both collections and return combined results."""
        conv = self.search_conversations(user_id, query, n_results // 2 + 1, domain_filter)
        know = self.search_knowledge(user_id, query, n_results // 2 + 1, domain_filter)
        return {"conversations": conv, "knowledge": know}

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self, user_id: str) -> dict[str, int]:
        return {
            "conversation_turns": self._conv_collection(user_id).count(),
            "knowledge_items": self._know_collection(user_id).count(),
        }

    def delete_user_data(self, user_id: str) -> None:
        """Remove all vector data for a user (GDPR / account deletion)."""
        for suffix in ("_conversations", "_knowledge"):
            name = f"{user_id}{suffix}"
            try:
                self._client.delete_collection(name)
                self._collections.pop(name, None)
            except Exception:
                pass


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_results(raw: dict) -> list[dict[str, Any]]:
    """Flatten ChromaDB query result into a list of dicts."""
    out = []
    ids = raw.get("ids", [[]])[0]
    docs = raw.get("documents", [[]])[0]
    metas = raw.get("metadatas", [[]])[0]
    dists = raw.get("distances", [[]])[0]

    for i, doc_id in enumerate(ids):
        similarity = 1.0 - (dists[i] if dists else 0.0)  # cosine distance → similarity
        out.append(
            {
                "id": doc_id,
                "document": docs[i] if docs else "",
                "metadata": metas[i] if metas else {},
                "similarity": round(similarity, 4),
            }
        )
    return out


# Singleton
vector_memory = VectorMemoryService()

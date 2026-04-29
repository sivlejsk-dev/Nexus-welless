"""
RAG (Retrieval-Augmented Generation) service.

Retrieves semantically relevant memories from ChromaDB and formats them
as context injected into the Nexus system prompt before each LLM call.

Also handles knowledge extraction: after each chat turn, important facts
are distilled from the exchange and stored back into the knowledge collection.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.services.vector_memory import vector_memory

logger = logging.getLogger(__name__)

# Minimum similarity score to include a result in the context block
_MIN_SIMILARITY = 0.45

# How many tokens (rough chars) to budget for the RAG context block
_MAX_CONTEXT_CHARS = 1200


class RAGService:
    """
    Retrieval-Augmented Generation layer for Nexus.

    retrieve_context()  — called before the LLM to inject relevant memories
    extract_and_store() — called after the LLM to persist new knowledge
    """

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve_context(
        self,
        user_id: str,
        query: str,
        domain: str | None = None,
        n_conversations: int = 3,
        n_knowledge: int = 3,
    ) -> str:
        """
        Build a RAG context block for injection into the system prompt.

        Returns an empty string when no relevant memories exist.
        """
        results = vector_memory.search_all(
            user_id=user_id,
            query=query,
            n_results=n_conversations + n_knowledge,
            domain_filter=domain,
        )

        conv_hits = [
            r for r in results["conversations"] if r["similarity"] >= _MIN_SIMILARITY
        ][:n_conversations]

        know_hits = [
            r for r in results["knowledge"] if r["similarity"] >= _MIN_SIMILARITY
        ][:n_knowledge]

        if not conv_hits and not know_hits:
            return ""

        parts: list[str] = ["[Relevant memory from past sessions]"]

        if know_hits:
            parts.append("Facts about this user:")
            for hit in know_hits:
                parts.append(f"  • {hit['document']}")

        if conv_hits:
            parts.append("Related past exchanges:")
            for hit in conv_hits:
                meta = hit["metadata"]
                ts = meta.get("timestamp", "")[:10]
                user_msg = meta.get("user_message", "")
                ai_msg = meta.get("ai_response", "")
                if user_msg and ai_msg:
                    parts.append(f"  [{ts}] User: {user_msg[:200]}")
                    parts.append(f"         Nexus: {ai_msg[:200]}")
                else:
                    parts.append(f"  [{ts}] {hit['document'][:300]}")

        context = "\n".join(parts)

        # Hard cap to avoid blowing the context window
        if len(context) > _MAX_CONTEXT_CHARS:
            context = context[:_MAX_CONTEXT_CHARS] + "\n  [... truncated]"

        return context

    # ── Storage ───────────────────────────────────────────────────────────────

    def store_turn(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        domain: str = "general",
        intent: str = "unknown",
    ) -> str:
        """Persist a conversation turn to the vector store."""
        return vector_memory.store_conversation_turn(
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_response,
            domain=domain,
            intent=intent,
        )

    def extract_and_store_knowledge(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        domain: str = "general",
    ) -> list[str]:
        """
        Extract factual statements from the exchange and store them.

        Uses lightweight heuristics — no extra LLM call required.
        Returns the IDs of stored knowledge items.
        """
        facts = _extract_facts(user_message, ai_response, domain)
        ids = []
        for fact in facts:
            kid = vector_memory.store_knowledge(
                user_id=user_id,
                fact=fact,
                domain=domain,
                source="conversation",
            )
            ids.append(kid)
        return ids

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_memory_stats(self, user_id: str) -> dict[str, Any]:
        return vector_memory.get_stats(user_id)

    def delete_user_memory(self, user_id: str) -> None:
        vector_memory.delete_user_data(user_id)


# ── Knowledge extraction heuristics ──────────────────────────────────────────

# Patterns that signal a user is sharing personal facts
_USER_FACT_PATTERNS = [
    r"i (am|have|eat|take|do|practice|follow|prefer|avoid|suffer|feel|want|need)\b.{5,80}",
    r"my (goal|diet|condition|allergy|medication|routine|sign|chart|birthday|age)\b.{3,80}",
    r"i'?m (a |an |trying|working|looking|struggling|interested).{5,80}",
]

# Patterns that signal the AI is stating a domain fact
_AI_FACT_PATTERNS = [
    r"(turmeric|magnesium|omega-3|vitamin [a-z]|ashwagandha|melatonin).{10,120}",
    r"(mercury retrograde|saturn return|jupiter transit|lunar cycle).{10,120}",
    r"(options|call|put|strike|expiry|implied volatility|theta|delta).{10,120}",
    r"(intermittent fasting|ketogenic|circadian|cortisol|insulin).{10,120}",
]


def _extract_facts(user_msg: str, ai_resp: str, domain: str) -> list[str]:
    facts: list[str] = []

    # User-stated personal facts
    for pattern in _USER_FACT_PATTERNS:
        for match in re.finditer(pattern, user_msg, re.IGNORECASE):
            fact = match.group(0).strip().rstrip(".,;")
            if len(fact) > 10:
                facts.append(f"User stated: {fact}")

    # Domain facts from AI response
    for pattern in _AI_FACT_PATTERNS:
        for match in re.finditer(pattern, ai_resp, re.IGNORECASE):
            fact = match.group(0).strip().rstrip(".,;")
            if len(fact) > 15:
                facts.append(f"[{domain}] {fact}")

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for f in facts:
        key = f.lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(f)

    return unique[:6]  # cap at 6 facts per turn


# Singleton
rag_service = RAGService()

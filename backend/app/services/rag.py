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
        n_domain: int = 4,
    ) -> str:
        """
        Build a RAG context block for injection into the system prompt.

        Searches three sources:
          1. User's personal conversation history
          2. User's personal knowledge facts
          3. Shared domain knowledge base (seeded at startup)

        Returns an empty string when no relevant memories exist.
        """
        from app.services.knowledge_seeder import DOMAIN_USER_ID

        # Personal memories
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

        # Shared domain knowledge
        domain_hits = vector_memory.search_knowledge(
            user_id=DOMAIN_USER_ID,
            query=query,
            n_results=n_domain,
        )
        domain_hits = [r for r in domain_hits if r["similarity"] >= _MIN_SIMILARITY][:n_domain]

        if not conv_hits and not know_hits and not domain_hits:
            return ""

        parts: list[str] = []

        if domain_hits:
            parts.append("[Domain knowledge]")
            for hit in domain_hits:
                parts.append(f"  • {hit['document'][:300]}")

        if know_hits:
            parts.append("[Facts about this user]")
            for hit in know_hits:
                parts.append(f"  • {hit['document']}")

        if conv_hits:
            parts.append("[Related past exchanges]")
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

    def extract_protocol_facts(
        self,
        user_id: str,
        ai_response: str,
        domain: str = "general",
    ) -> list[str]:
        """Extract and store protocol recommendations from AI responses."""
        import re
        ids = []
        # Detect phase/step descriptions
        phase_pattern = r"(phase \d|step \d|day \d+[-–]\d+)[:\s].{20,200}"
        for match in re.finditer(phase_pattern, ai_response, re.IGNORECASE):
            fact = f"[PROTOCOL STEP] {match.group(0).strip()}"
            kid = vector_memory.store_knowledge(user_id=user_id, fact=fact,
                                                domain=domain, source="protocol")
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
    r"my (goal|diet|condition|allergy|medication|routine|sign|chart|birthday|age|supplement|symptom)\b.{3,80}",
    r"i'?m (a |an |trying|working|looking|struggling|interested|sensitive|allergic|diagnosed).{5,80}",
    r"i (take|use|supplement with|have been on|started|stopped)\b.{5,80}",
    r"i (experience|struggle with|suffer from|have been diagnosed with|tested positive for)\b.{5,80}",
    r"i follow (a |the |an ).{5,60}(diet|protocol|program|plan)",
    r"i'?m (vegan|vegetarian|carnivore|keto|paleo|gluten.free|dairy.free|plant.based)",
]

# Patterns that signal the AI is stating a domain fact — expanded for nutrition/detox/herbs
_AI_FACT_PATTERNS = [
    # Anti-inflammatory & antioxidant
    r"(turmeric|curcumin|ginger|blueberr|resveratrol|quercetin|polyphenol).{10,120}",
    r"(omega-3|EPA|DHA|fish oil|flaxseed|chia seed).{10,120}",
    r"(magnesium|zinc|selenium|iodine|vitamin [a-z][0-9]?|B12|folate|methylfolate).{10,120}",
    # Antiparasitic herbs
    r"(wormwood|black walnut|clove|mimosa pudica|artemisia|artemisinin).{10,120}",
    r"(oregano oil|carvacrol|berberine|neem|pau d'arco|cat's claw|andrographis).{10,120}",
    r"(grapefruit seed extract|olive leaf|uva ursi|barberry|goldenseal).{10,120}",
    # Detox agents
    r"(chlorella|spirulina|cilantro|activated charcoal|bentonite clay|zeolite).{10,120}",
    r"(milk thistle|silymarin|dandelion|artichoke|burdock|NAC|glutathione|liposomal).{10,120}",
    r"(heavy metal|mercury|lead|cadmium|chelat|DMSA|EDTA|modified citrus pectin).{10,120}",
    # Gut & microbiome
    r"(SIBO|candida|leaky gut|dysbiosis|biofilm|Herxheimer|die.off|intestinal permeability).{10,120}",
    r"(L-glutamine|zinc carnosine|slippery elm|marshmallow root|aloe vera|colostrum).{10,120}",
    r"(probiotic|prebiotic|Lactobacillus|Bifidobacterium|Saccharomyces|butyrate|SCFA).{10,120}",
    r"(bone broth|collagen|gelatin|glycine|resistant starch|fermented food).{10,120}",
    # Adaptogens & vitality
    r"(ashwagandha|withanolide|rhodiola|lion's mane|reishi|cordyceps|maca|moringa).{10,120}",
    r"(adaptogen|HPA axis|adrenal|cortisol|DHEA|thyroid|T3|T4|TSH).{10,120}",
    # Functional medicine concepts
    r"(methylation|MTHFR|homocysteine|Phase I|Phase II|liver detox|cytochrome P450).{10,120}",
    r"(intermittent fasting|ketogenic|circadian|insulin resistance|blood sugar|HbA1c).{10,120}",
    r"(autoimmune|inflammation|hs-CRP|IL-6|NF-kB|oxidative stress|mitochondria).{10,120}",
    # Astrology (preserve existing)
    r"(mercury retrograde|saturn return|jupiter transit|lunar cycle|full moon).{10,120}",
    # Finance (preserve existing)
    r"(options|call|put|strike|expiry|implied volatility|theta|delta|gamma|vega).{10,120}",
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

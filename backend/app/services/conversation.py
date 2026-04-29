"""
Nexus Conversation Engine — Task 1.1

Unified service that wires together:
  - EnhancedConversationalUnderstanding  (pronoun resolution, topic threading, intent)
  - ToneAnalyzer + ConversationalFlowEnhancer  (tone matching, natural responses)
  - ProactiveIntelligence  (anticipate user needs, suggest next steps)
  - ConversationAutomation  (command parsing, task routing)

Every message to Nexus passes through this engine before reaching the AI model.
The engine enriches the raw user input with context, resolved references, detected
intent, and tone — then post-processes the AI response to match the user's style.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)

# ── Import Nexus conversation modules ─────────────────────────────────────────
_CONV_AVAILABLE = False

try:
    from app.nexus_core.conversation_understanding import (
        EnhancedConversationalUnderstanding,
        DialogueTurn,
        ConversationThread,
    )
    from app.nexus_core.conversation_enhancement import (
        ToneAnalyzer,
        ConversationalFlowEnhancer,
    )
    from app.nexus_core.conversation_proactive import ProactiveIntelligence
    from app.nexus_core.conversation_automation import ConversationalAutomationEngine as ConversationAutomation
    _CONV_AVAILABLE = True
    log.info("Nexus conversation engine loaded successfully")
except Exception as exc:
    log.warning("Nexus conversation engine unavailable: %s", exc)


# ── Domain intent classifier ──────────────────────────────────────────────────

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "nutrition": [
        "eat", "food", "diet", "meal", "nutrition", "vitamin", "supplement",
        "protein", "carb", "fat", "calorie", "gut", "inflammation", "detox",
        "fast", "fasting", "recipe", "ingredient", "herb", "healing",
        "microbiome", "probiotic", "prebiotic", "ferment", "leaky gut",
        "candida", "sibo", "parasite", "wormwood", "berberine", "ashwagandha",
        "adaptogen", "magnesium", "omega-3", "glutamine", "collagen",
        "blood sugar", "insulin", "thyroid", "adrenal", "methylation",
    ],
    "meditation": [
        "meditat", "breathwork", "breathing", "breath", "mindful", "stress",
        "anxiety", "calm", "relax", "sleep", "focus", "chakra", "mantra",
        "yoga", "pranayama", "peace", "stillness", "awareness", "presence",
        "box breath", "4-7-8", "body scan", "visualization",
    ],
    "detox": [
        "detox", "cleanse", "liver", "toxin", "heavy metal", "parasite",
        "lymph", "flush", "protocol", "fast", "purif",
        "herxheimer", "die-off", "binder", "chelat", "mold", "mycotoxin",
        "candida cleanse", "parasite cleanse", "gut reset", "5r protocol",
        "wormwood", "black walnut", "clove", "mimosa pudica",
        "activated charcoal", "bentonite clay", "chlorella", "spirulina",
    ],
    "astrology": [
        "astrology", "horoscope", "birth chart", "zodiac", "planet", "transit",
        "mercury", "venus", "mars", "jupiter", "saturn", "moon", "sun",
        "rising", "ascendant", "retrograde", "sign",
    ],
    "finance": [
        "stock", "option", "trade", "invest", "market", "portfolio", "call",
        "put", "strike", "expir", "greek", "delta", "theta", "vega", "gamma",
        "iv", "implied volatility", "spread", "condor", "straddle", "ticker",
        "earnings", "chart", "technical", "bullish", "bearish", "crypto",
    ],
    "general": [],
}


def classify_domain(text: str) -> str:
    """Classify user message into a Nexus wellness/finance domain."""
    text_lower = text.lower()
    scores: dict[str, int] = {domain: 0 for domain in DOMAIN_KEYWORDS}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[domain] += 1

    scores.pop("general")
    if not any(scores.values()):
        return "general"

    return max(scores, key=lambda d: scores[d])


# ── Per-user in-memory session store ─────────────────────────────────────────
# In Task 1.5 this will be replaced by PostgreSQL persistence.

@dataclass
class ConversationSession:
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    history: list[dict[str, Any]] = field(default_factory=list)
    current_topic: str = "general"
    current_domain: str = "general"
    recent_entities: list[dict[str, Any]] = field(default_factory=list)
    turn_count: int = 0

    def to_context(self) -> dict[str, Any]:
        """Build context dict for the conversation understanding engine."""
        last_user = next(
            (m["content"] for m in reversed(self.history) if m["role"] == "user"), ""
        )
        last_ai = next(
            (m["content"] for m in reversed(self.history) if m["role"] == "assistant"), ""
        )
        return {
            "last_user_input": last_user,
            "last_ai_response": last_ai,
            "current_topic": self.current_topic,
            "current_domain": self.current_domain,
            "recent_entities": self.recent_entities,
            "turn_count": self.turn_count,
        }

    def add_turn(self, role: str, content: str) -> None:
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.last_active = datetime.now(timezone.utc)
        self.turn_count += 1

    def get_history_for_llm(self, window: int = 10) -> list[dict[str, str]]:
        """Return last N turns formatted for the LLM messages array."""
        recent = self.history[-window * 2:]
        return [{"role": m["role"], "content": m["content"]} for m in recent]

    def summarize_context(self) -> str:
        """One-line context summary injected into the system prompt."""
        parts = []
        if self.current_domain != "general":
            parts.append(f"domain: {self.current_domain}")
        if self.current_topic != "general":
            parts.append(f"topic: {self.current_topic}")
        if self.turn_count > 0:
            parts.append(f"turn {self.turn_count}")
        return " | ".join(parts) if parts else ""


# Global session store: user_id → ConversationSession
_sessions: dict[str, ConversationSession] = {}


# ── Main conversation engine ──────────────────────────────────────────────────

class ConversationEngine:
    """
    Central conversation engine for Nexus.

    Usage:
        engine = ConversationEngine()
        processed = engine.process_input(user_id, user_message)
        # ... call LLM with processed.enriched_prompt and processed.history ...
        engine.record_response(user_id, ai_response)
        polished = engine.polish_response(user_id, ai_response, user_message)
    """

    def __init__(self) -> None:
        self._understanding = EnhancedConversationalUnderstanding() if _CONV_AVAILABLE else None
        self._tone = ToneAnalyzer() if _CONV_AVAILABLE else None
        self._flow = ConversationalFlowEnhancer() if _CONV_AVAILABLE else None
        self._proactive = ProactiveIntelligence() if _CONV_AVAILABLE else None

    # ── Session management ────────────────────────────────────────────────────

    def get_or_create_session(self, user_id: str) -> ConversationSession:
        if user_id not in _sessions:
            _sessions[user_id] = ConversationSession(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
            )
        return _sessions[user_id]

    def clear_session(self, user_id: str) -> None:
        _sessions.pop(user_id, None)

    def get_session_summary(self, user_id: str) -> dict[str, Any]:
        session = _sessions.get(user_id)
        if not session:
            return {"active": False}
        return {
            "active": True,
            "session_id": session.session_id,
            "turn_count": session.turn_count,
            "current_domain": session.current_domain,
            "current_topic": session.current_topic,
            "history_length": len(session.history),
            "last_active": session.last_active.isoformat(),
        }

    # ── Input processing ──────────────────────────────────────────────────────

    def process_input(self, user_id: str, raw_message: str) -> "ProcessedInput":
        """
        Enrich raw user input with:
        - Resolved pronouns and references
        - Detected intent and domain
        - Tone analysis
        - Conversation context
        - Proactive suggestions
        """
        session = self.get_or_create_session(user_id)
        context = session.to_context()

        # 1. Deep conversational understanding
        understood: dict[str, Any] = {}
        resolved_text = raw_message
        if self._understanding:
            try:
                understood = self._understanding.process_user_input(raw_message, context)
                resolved_text = understood.get("completed_text", raw_message)
                self._understanding.add_turn("user", raw_message,
                                             intent=understood.get("implicit_intent"))
            except Exception as exc:
                log.debug("Understanding engine error: %s", exc)

        # 2. Domain classification
        domain = classify_domain(resolved_text)
        session.current_domain = domain

        # 3. Topic extraction
        if understood.get("discourse_type") == "topic_change" or session.turn_count == 0:
            session.current_topic = _extract_topic(resolved_text)

        # 4. Tone analysis
        tone: dict[str, Any] = {}
        if self._tone:
            try:
                tone = self._tone.analyze_tone(raw_message)
            except Exception as exc:
                log.debug("Tone analysis error: %s", exc)

        # 5. Proactive suggestions
        suggestions: list[str] = []
        if self._proactive:
            try:
                raw_suggestions = self._proactive.generate_suggestions(context)
                suggestions = [s.suggestion_text for s in raw_suggestions[:2]]
            except Exception as exc:
                log.debug("Proactive suggestions error: %s", exc)

        # 6. Record user turn
        session.add_turn("user", raw_message)

        # 7. Build enriched system context
        context_note = session.summarize_context()
        needs_clarification = understood.get("needs_clarification", False)

        return ProcessedInput(
            raw_message=raw_message,
            resolved_message=resolved_text,
            domain=domain,
            intent=understood.get("implicit_intent"),
            discourse_type=understood.get("discourse_type"),
            implicature=understood.get("implicature"),
            tone=tone,
            needs_clarification=needs_clarification,
            suggestions=suggestions,
            history=session.get_history_for_llm(),
            context_note=context_note,
            session=session,
        )

    # ── Response recording & polishing ───────────────────────────────────────

    def record_response(self, user_id: str, ai_response: str) -> None:
        """Record the AI response into the session history."""
        session = _sessions.get(user_id)
        if session:
            session.add_turn("assistant", ai_response)
            if self._understanding:
                try:
                    self._understanding.add_turn("ai", ai_response)
                except Exception:
                    pass

    def polish_response(
        self, user_id: str, raw_response: str, user_message: str
    ) -> str:
        """
        Post-process the AI response:
        - Remove robotic filler phrases
        - Match user's tone (casual ↔ formal)
        - Append proactive suggestions when relevant
        """
        session = _sessions.get(user_id)
        context = session.to_context() if session else {}
        polished = raw_response

        if self._flow:
            try:
                polished = self._flow.enhance_flow(raw_response, user_message, context)
            except Exception as exc:
                log.debug("Flow enhancer error: %s", exc)

        return polished


# ── ProcessedInput dataclass ──────────────────────────────────────────────────

@dataclass
class ProcessedInput:
    raw_message: str
    resolved_message: str
    domain: str
    intent: str | None
    discourse_type: str | None
    implicature: str | None
    tone: dict[str, Any]
    needs_clarification: bool
    suggestions: list[str]
    history: list[dict[str, str]]
    context_note: str
    session: ConversationSession

    def build_system_prompt(self, base_prompt: str) -> str:
        """Inject conversation context into the system prompt."""
        parts = [base_prompt]
        if self.context_note:
            parts.append(f"\nConversation context: {self.context_note}")
        if self.domain != "general":
            parts.append(f"Current domain: {self.domain}")
        if self.intent:
            parts.append(f"Detected user intent: {self.intent}")
        if self.implicature == "high_priority":
            parts.append("User has indicated urgency — be concise and direct.")
        if self.tone.get("is_casual"):
            parts.append("Match the user's casual, conversational tone.")
        elif self.tone.get("is_formal"):
            parts.append("Maintain a professional, precise tone.")
        if self.needs_clarification:
            parts.append("The user's message may be ambiguous — ask one focused clarifying question if needed.")
        return "\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_message": self.raw_message,
            "resolved_message": self.resolved_message,
            "domain": self.domain,
            "intent": self.intent,
            "discourse_type": self.discourse_type,
            "implicature": self.implicature,
            "tone": self.tone,
            "needs_clarification": self.needs_clarification,
            "suggestions": self.suggestions,
            "context_note": self.context_note,
            "history_turns": len(self.history),
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_topic(text: str) -> str:
    stop = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and",
            "or", "is", "are", "was", "were", "what", "how", "why", "when",
            "where", "who", "can", "could", "would", "should", "do", "does"}
    words = [w.strip(".,!?") for w in text.split() if w.lower().strip(".,!?") not in stop and len(w) > 3]
    return " ".join(words[:3]) if words else "general"


# Singleton
conversation_engine = ConversationEngine()

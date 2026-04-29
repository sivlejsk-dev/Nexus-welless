"""
Nexus Learning Service — Task 1.2

Wraps ContinuousLearner to provide per-user pattern recognition,
skill tracking, and adaptive learning that feeds back into every
Nexus response.

Each user gets their own ContinuousLearner instance. After every
conversation turn the engine:
  1. Detects interaction patterns (topics, preferences, question styles)
  2. Updates skill proficiency scores (nutrition, meditation, finance, etc.)
  3. Builds a personal knowledge graph of concepts the user cares about
  4. Generates improvement recommendations for Nexus's next response

The learning insights are injected into the system prompt so Nexus
adapts to each user over time without retraining.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

_LEARNER_AVAILABLE = False
try:
    from app.nexus_core.continuous_learner import ContinuousLearner
    _LEARNER_AVAILABLE = True
    log.info("ContinuousLearner loaded successfully")
except Exception as exc:
    log.warning("ContinuousLearner unavailable: %s", exc)

# Per-user learner instances (persisted to DB in Task 1.5)
_learners: dict[str, Any] = {}

# Domain → skill name mapping
DOMAIN_SKILLS = {
    "nutrition":  "nutrition_science",
    "meditation": "mindfulness_practice",
    "detox":      "detox_protocols",
    "astrology":  "astrological_interpretation",
    "finance":    "financial_analysis",
    "general":    "general_wellness",
}


class LearningService:
    """Per-user adaptive learning backed by ContinuousLearner."""

    def get_learner(self, user_id: str) -> Any | None:
        if not _LEARNER_AVAILABLE:
            return None
        if user_id not in _learners:
            _learners[user_id] = ContinuousLearner(storage_path=None)
        return _learners[user_id]

    def record_interaction(
        self,
        user_id: str,
        user_input: str,
        ai_response: str,
        domain: str = "general",
        intent: str | None = None,
        outcome: str = "success",
    ) -> dict[str, Any]:
        """
        Record a conversation turn and update the user's learning profile.
        Returns learning insights to inject into the next system prompt.
        """
        learner = self.get_learner(user_id)
        if not learner:
            return {}

        try:
            skill = DOMAIN_SKILLS.get(domain, "general_wellness")
            learner.learn_from_interaction(
                user_input=user_input,
                ai_response=ai_response,
                intent=intent or domain,
                outcome=outcome,
                skill_used=skill,
            )
            return self.get_insights(user_id)
        except Exception as exc:
            log.debug("learn_from_interaction error: %s", exc)
            return {}

    def get_insights(self, user_id: str) -> dict[str, Any]:
        """Return current learning insights for a user."""
        learner = self.get_learner(user_id)
        if not learner:
            return {}
        try:
            return learner.get_learning_insights()
        except Exception as exc:
            log.debug("get_learning_insights error: %s", exc)
            return {}

    def get_recommendations(self, user_id: str) -> list[dict[str, Any]]:
        """Return improvement recommendations for Nexus's next response."""
        learner = self.get_learner(user_id)
        if not learner:
            return []
        try:
            return learner.get_improvement_recommendations()
        except Exception as exc:
            log.debug("get_improvement_recommendations error: %s", exc)
            return []

    def get_skill_profile(self, user_id: str) -> dict[str, Any]:
        """Return the user's skill proficiency profile across all domains."""
        learner = self.get_learner(user_id)
        if not learner:
            return {}
        try:
            skills = {}
            for skill_name, skill in learner.skills.items():
                skills[skill_name] = {
                    "proficiency": round(skill.proficiency_score, 3),
                    "level": skill.get_proficiency_label(),
                    "practice_count": skill.practice_count,
                    "success_rate": round(skill.success_rate, 3),
                }
            return {
                "skills": skills,
                "patterns_detected": len(learner.patterns),
                "knowledge_concepts": len(learner.knowledge_graph.concepts)
                    if hasattr(learner, "knowledge_graph") else 0,
            }
        except Exception as exc:
            log.debug("get_skill_profile error: %s", exc)
            return {}

    def get_related_concepts(self, user_id: str, concept: str) -> list[str]:
        """Return concepts related to a given topic from the user's knowledge graph."""
        learner = self.get_learner(user_id)
        if not learner or not hasattr(learner, "knowledge_graph"):
            return []
        try:
            return list(learner.knowledge_graph.get_related(concept, depth=2))
        except Exception:
            return []

    def build_learning_context(self, user_id: str, domain: str) -> str:
        """
        Build a concise learning context string to inject into the system prompt.
        Tells Nexus what the user already knows and how to adapt.
        """
        insights = self.get_insights(user_id)
        if not insights:
            return ""

        parts: list[str] = []

        # Top patterns
        patterns = insights.get("top_patterns", [])
        if patterns:
            top = patterns[0]
            parts.append(f"User frequently asks about: {top.get('pattern', '')}")

        # Skill level in current domain
        skill_name = DOMAIN_SKILLS.get(domain, "general_wellness")
        skills = insights.get("skill_levels", {})
        if skill_name in skills:
            level = skills[skill_name]
            parts.append(f"User's {domain} knowledge level: {level}")

        # Recommendations
        recs = self.get_recommendations(user_id)
        if recs:
            top_rec = recs[0].get("recommendation", "")
            if top_rec:
                parts.append(f"Adapt response: {top_rec}")

        return " | ".join(parts) if parts else ""


learning_service = LearningService()

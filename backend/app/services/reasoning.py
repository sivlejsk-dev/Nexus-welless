"""
Nexus Reasoning Service — Task 1.3

Wraps AdvancedReasoningEngine to give Nexus structured multi-framework
problem-solving capabilities across wellness and finance domains.

When a user asks a complex question (multi-step, analytical, or strategic),
the reasoning engine:
  1. Decomposes the problem into components
  2. Applies deductive, inductive, abductive, and causal reasoning
  3. Generates multiple solution approaches
  4. Extracts key insights and confidence scores
  5. Returns a structured reasoning output that enriches the LLM prompt

This is especially critical for:
  - Options strategy selection (multi-variable trade-offs)
  - Detox protocol design (contraindications, sequencing)
  - Nutritional protocol building (interactions, deficiencies)
  - Astrological timing analysis (transit combinations)
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

_REASONING_AVAILABLE = False
try:
    from app.nexus_core.advanced_reasoning import AdvancedReasoningEngine
    _REASONING_AVAILABLE = True
    log.info("AdvancedReasoningEngine loaded successfully")
except Exception as exc:
    log.warning("AdvancedReasoningEngine unavailable: %s", exc)

# Complexity threshold — only invoke full reasoning for non-trivial questions
COMPLEX_TRIGGERS = [
    # General reasoning
    "which is better", "compare", "strategy", "plan for",
    "how do i", "what is the best", "analyze", "evaluate", "recommend",
    "trade-off", "pros and cons", "explain why",
    "what would happen", "calculate",
    "should i take", "should i do", "should i start", "should i use",
    "should i try", "should i avoid", "should i combine",
    # Finance
    "iron condor", "options strategy", "covered call", "bull spread", "bear spread",
    # Nutrition & detox — new
    "parasite cleanse", "parasite protocol", "candida", "sibo",
    "leaky gut", "microbiome", "gut protocol", "gut healing",
    "food sensitivity", "detox reaction", "herxheimer", "die-off",
    "heavy metal", "mold toxicity", "mycotoxin", "adrenal fatigue",
    "thyroid protocol", "methylation", "mthfr", "hormone balance", "hormonal",
    "blood sugar protocol", "insulin resistance", "autoimmune", "root cause",
    "supplement stack", "detox protocol", "meal plan",
    "what's wrong with me", "why do i", "what causes",
    "vitality reset", "wellness reset", "30-day", "21-day", "60-day",
    # Astrology
    "birth chart", "saturn return", "transit", "synastry",
]


def is_complex_query(text: str) -> bool:
    """Determine if a query warrants full reasoning engine invocation."""
    text_lower = text.lower()
    return any(trigger in text_lower for trigger in COMPLEX_TRIGGERS)


class ReasoningService:
    """Structured reasoning for complex Nexus queries."""

    def __init__(self) -> None:
        self._engine = AdvancedReasoningEngine() if _REASONING_AVAILABLE else None

    def reason(self, problem: str) -> dict[str, Any]:
        """
        Run full multi-framework reasoning on a problem statement.
        Returns structured output: analysis, steps, solutions, insights.
        """
        if not self._engine:
            return self._fallback_reason(problem)

        try:
            output = self._engine.generate_comprehensive_reasoning(problem)
            return self._serialize(output)
        except Exception as exc:
            log.debug("Reasoning engine error: %s", exc)
            return self._fallback_reason(problem)

    def analyze(self, problem: str) -> dict[str, Any]:
        """Lightweight problem analysis without full solution generation."""
        if not self._engine:
            return {"problem": problem, "complexity": 5, "available": False}
        try:
            analysis = self._engine.analyze_problem(problem)
            return {
                "problem": problem,
                "complexity": getattr(analysis, "overall_complexity",
                              getattr(analysis, "complexity_score", 5)),
                "key_questions": analysis.key_questions[:4],
                "components": [
                    {"name": c.name, "description": c.description}
                    for c in analysis.components[:4]
                ],
                "constraints": analysis.constraints[:3],
                "assumptions": analysis.assumptions[:3],
                "suggested_path": getattr(analysis, "suggested_reasoning_path",
                                  getattr(analysis, "suggested_path", "")),
                "available": True,
            }
        except Exception as exc:
            log.debug("analyze_problem error: %s", exc)
            return {"problem": problem, "available": False}

    def build_nutrition_reasoning_context(self, query: str, user_profile: dict[str, Any]) -> str:
        """Inject user profile into reasoning context for nutrition/detox queries."""
        if not is_complex_query(query):
            return ""
        parts = []
        conditions = user_profile.get("conditions", [])
        medications = user_profile.get("medications", [])
        dietary = user_profile.get("dietary_preferences", [])
        if conditions:
            parts.append(f"User conditions: {', '.join(conditions)}")
        if medications:
            parts.append(f"User medications: {', '.join(medications)} — CHECK ALL HERB-DRUG INTERACTIONS before recommending")
        if dietary:
            parts.append(f"Dietary preferences: {', '.join(dietary)}")
        if parts:
            parts.insert(0, "[Nutrition reasoning context]")
            parts.append("Apply root-cause analysis. Sequence: Remove → Replace → Reinoculate → Repair → Rebalance.")
            parts.append("Always check contraindications before recommending herbs or supplements.")
        return "\n".join(parts)

    def build_reasoning_context(self, problem: str) -> str:
        """
        Build a concise reasoning context string for injection into the system prompt.
        Only invoked for complex queries to avoid overhead on simple questions.
        """
        if not _REASONING_AVAILABLE or not is_complex_query(problem):
            return ""

        try:
            analysis = self._engine.analyze_problem(problem)  # type: ignore[union-attr]
            parts = []

            if analysis.key_questions:
                parts.append(f"Key questions to address: {'; '.join(analysis.key_questions[:2])}")
            if analysis.constraints:
                parts.append(f"Constraints: {'; '.join(analysis.constraints[:2])}")
            suggested = getattr(analysis, "suggested_reasoning_path",
                        getattr(analysis, "suggested_path", ""))
            if suggested:
                parts.append(f"Reasoning approach: {suggested}")

            return " | ".join(parts) if parts else ""
        except Exception as exc:
            log.debug("build_reasoning_context error: %s", exc)
            return ""

    def format_for_response(self, problem: str) -> str:
        """
        Run full reasoning and format as a structured dialogue string
        suitable for inclusion in a Nexus response.
        """
        if not self._engine:
            return ""
        try:
            output = self._engine.generate_comprehensive_reasoning(problem)
            return self._engine.format_reasoning_dialogue(output)
        except Exception as exc:
            log.debug("format_reasoning_dialogue error: %s", exc)
            return ""

    def _serialize(self, output: Any) -> dict[str, Any]:
        """Serialize AdvancedReasoningOutput to a plain dict."""
        try:
            best = getattr(output, "best_solution", None)
            analysis = getattr(output, "problem_analysis", None)
            complexity = (
                getattr(analysis, "overall_complexity",
                getattr(analysis, "complexity_score", 5)) if analysis else 5
            )
            steps = getattr(output, "reasoning_steps", [])
            solutions = getattr(output, "solutions", [])
            insights = getattr(output, "insights", getattr(output, "key_insights", []))
            innovations = getattr(output, "innovation_opportunities", [])

            return {
                "available": True,
                "confidence": round(getattr(output, "confidence_score",
                                    getattr(output, "confidence", 0.8)), 3),
                "complexity": complexity,
                "reasoning_steps": [
                    {
                        "framework": step.framework.value
                            if hasattr(step.framework, "value") else str(step.framework),
                        "premise": getattr(step, "premise", ""),
                        "conclusion": getattr(step, "conclusion", ""),
                        "confidence": round(getattr(step, "confidence", 0.8), 3),
                    }
                    for step in steps[:4]
                ],
                "best_solution": {
                    "approach": getattr(best, "approach", ""),
                    "description": getattr(best, "description", ""),
                    "steps": getattr(best, "implementation_steps",
                             getattr(best, "steps", []))[:5],
                    "confidence": round(getattr(best, "confidence", 0.8), 3),
                } if best else None,
                "alternative_solutions": [
                    {
                        "approach": getattr(s, "approach", ""),
                        "description": str(getattr(s, "description", ""))[:120],
                    }
                    for s in solutions[1:3]
                ],
                "key_insights": list(insights)[:4],
                "innovation_opportunities": list(innovations)[:2],
            }
        except Exception as exc:
            log.debug("Serialization error: %s", exc)
            return {"available": False, "error": str(exc)}

    def _fallback_reason(self, problem: str) -> dict[str, Any]:
        return {
            "available": False,
            "problem": problem,
            "note": "Reasoning engine not available — install dependencies.",
        }


reasoning_service = ReasoningService()

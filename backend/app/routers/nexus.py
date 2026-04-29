"""
Nexus AI endpoints — conversation-aware chat, recommendations, and session management.

All chat messages pass through the ConversationEngine (Task 1.1):
  - Pronoun resolution and reference tracking
  - Domain classification (wellness / finance / astrology)
  - Tone analysis and response polishing
  - Per-user conversation history
  - Proactive suggestions
"""

import json

from fastapi import APIRouter, Body, Depends, Query

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.wellness import NexusRecommendationRequest, NexusRecommendationResponse
from app.services.conversation import conversation_engine
from app.services.learning import learning_service
from app.services.reasoning import reasoning_service
from app.services.nexus import nexus_service

router = APIRouter(prefix="/nexus", tags=["nexus-ai"])


@router.post("/chat")
async def chat(
    message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """
    Full conversation-aware chat with Nexus.
    Remembers context, resolves references, detects domain and intent,
    adapts tone. Covers wellness, astrology, finance, and options trading.
    """
    profile = current_user.profile
    profile_dict: dict = {}
    if profile:
        profile_dict = {
            "sun_sign": profile.sun_sign,
            "moon_sign": profile.moon_sign,
            "health_goals": json.loads(profile.health_goals or "[]"),
            "dietary_preferences": json.loads(profile.dietary_preferences or "[]"),
            "conditions": json.loads(profile.conditions or "[]"),
        }

    result = await nexus_service.chat(
        user_id=str(current_user.id),
        raw_message=message,
        user_profile=profile_dict,
    )
    return result


@router.get("/session")
async def get_session(current_user: User = Depends(get_current_user)):
    """Return the current conversation session summary."""
    return conversation_engine.get_session_summary(str(current_user.id))


@router.delete("/session")
async def clear_session(current_user: User = Depends(get_current_user)):
    """Clear the conversation session — Nexus starts fresh."""
    conversation_engine.clear_session(str(current_user.id))
    return {"cleared": True, "user_id": str(current_user.id)}


@router.post("/recommend", response_model=NexusRecommendationResponse)
async def get_recommendation(
    body: NexusRecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    """Structured Nexus recommendation for a specific module."""
    profile = current_user.profile
    profile_dict: dict = {}
    if profile:
        profile_dict = {
            "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
            "sun_sign": profile.sun_sign,
            "moon_sign": profile.moon_sign,
            "rising_sign": profile.rising_sign,
            "health_goals": json.loads(profile.health_goals or "[]"),
            "dietary_preferences": json.loads(profile.dietary_preferences or "[]"),
            "conditions": json.loads(profile.conditions or "[]"),
            "allergies": json.loads(profile.allergies or "[]"),
        }

    result = await nexus_service.personalized_recommendation(
        module=body.module,
        user_profile=profile_dict,
        context=body.context,
        user_message=body.user_message,
    )
    return NexusRecommendationResponse(**result)


@router.post("/analyze")
async def analyze_message(
    message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze a message through the conversation engine without calling the LLM.
    Returns domain, intent, tone, resolved text, and suggestions.
    """
    processed = conversation_engine.process_input(str(current_user.id), message)
    return processed.to_dict()


# ── Learning endpoints (Task 1.2) ─────────────────────────────────────────────

@router.get("/skills")
async def get_skill_profile(current_user: User = Depends(get_current_user)):
    """
    Return the user's skill proficiency profile across all Nexus domains.
    Shows how Nexus has learned to adapt to this user over time.
    """
    return {
        "user_id": str(current_user.id),
        "profile": learning_service.get_skill_profile(str(current_user.id)),
        "insights": learning_service.get_insights(str(current_user.id)),
        "recommendations": learning_service.get_recommendations(str(current_user.id))[:3],
    }


@router.get("/skills/concepts")
async def get_related_concepts(
    concept: str = Query(..., description="Topic to find related concepts for"),
    current_user: User = Depends(get_current_user),
):
    """Return concepts related to a topic from the user's personal knowledge graph."""
    related = learning_service.get_related_concepts(str(current_user.id), concept)
    return {"concept": concept, "related": related}


# ── Reasoning endpoints (Task 1.3) ────────────────────────────────────────────

@router.post("/reason")
async def reason(
    problem: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """
    Run structured multi-framework reasoning on a complex problem.

    Uses deductive, inductive, abductive, and causal reasoning to:
    - Decompose the problem into components
    - Generate multiple solution approaches
    - Return the best solution with confidence scores

    Ideal for: options strategy selection, detox protocol design,
    nutritional planning, astrological timing analysis.
    """
    return reasoning_service.reason(problem)


@router.post("/reason/analyze")
async def analyze_problem(
    problem: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Lightweight problem analysis — complexity score, key questions, constraints."""
    return reasoning_service.analyze(problem)

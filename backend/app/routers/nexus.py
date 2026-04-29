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

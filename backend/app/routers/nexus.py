"""Nexus AI direct interaction endpoint — general wellness chat and recommendations."""

import json

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.wellness import NexusRecommendationRequest, NexusRecommendationResponse
from app.services.nexus import nexus_service

router = APIRouter(prefix="/nexus", tags=["nexus-ai"])


@router.post("/recommend", response_model=NexusRecommendationResponse)
async def get_recommendation(
    body: NexusRecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Direct Nexus AI recommendation endpoint.
    Accepts any wellness module and free-form context.
    """
    profile = current_user.profile
    profile_dict = {}
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


@router.post("/chat")
async def chat(
    message: str,
    current_user: User = Depends(get_current_user),
):
    """
    Free-form wellness conversation with Nexus AI.
    Returns a plain text response.
    """
    profile = current_user.profile
    context_parts = []
    if profile:
        if profile.sun_sign:
            context_parts.append(f"User's sun sign: {profile.sun_sign}")
        goals = json.loads(profile.health_goals or "[]")
        if goals:
            context_parts.append(f"Health goals: {', '.join(goals)}")

    system_context = None
    if context_parts:
        system_context = f"User context: {' | '.join(context_parts)}\n\nYou are Nexus, a holistic wellness AI."

    response = await nexus_service.complete(
        user_message=message,
        system_context=system_context,
    )
    return {"response": response, "user": current_user.email}

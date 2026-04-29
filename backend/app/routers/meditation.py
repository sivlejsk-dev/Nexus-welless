"""Meditation endpoints — guides, sessions, and Nexus-enhanced recommendations."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.middleware.auth import get_current_user
from app.models.user import MeditationSession, User
from app.nexus_core.guide_engine import VALID_GOALS, VALID_MENTAL_STATES
from app.schemas.wellness import MeditationGuide, MeditationSessionCreate, MeditationSessionOut
from app.services.meditation import meditation_service
from app.services.nexus import nexus_service

router = APIRouter(prefix="/meditation", tags=["meditation"])


@router.get("/guides", response_model=list[MeditationGuide])
async def list_guides(
    category: str | None = Query(None),
    tag: str | None = Query(None),
    level: str | None = Query(None),
):
    guides = meditation_service.get_all_guides()
    if category:
        guides = [g for g in guides if g["category"] == category]
    if tag:
        guides = [g for g in guides if tag.lower() in [t.lower() for t in g["tags"]]]
    if level:
        guides = [g for g in guides if g["level"] == level]
    return guides


@router.get("/guides/{guide_id}", response_model=MeditationGuide)
async def get_guide(guide_id: str):
    guide = meditation_service.get_guide(guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide


@router.get("/recommended", response_model=list[MeditationGuide])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
):
    profile = current_user.profile
    profile_dict = {}
    if profile:
        profile_dict = {
            "health_goals": json.loads(profile.health_goals or "[]"),
            "sun_sign": profile.sun_sign,
        }
    return meditation_service.recommend_for_profile(profile_dict)


@router.post("/sessions", response_model=MeditationSessionOut, status_code=201)
async def log_session(
    body: MeditationSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = MeditationSession(
        user_id=current_user.id,
        guide_id=body.guide_id,
        duration_seconds=body.duration_seconds,
        completed=body.completed,
        mood_before=body.mood_before,
        mood_after=body.mood_after,
        notes=body.notes,
    )
    db.add(session)
    await db.flush()
    return MeditationSessionOut(
        id=str(session.id),
        guide_id=session.guide_id,
        duration_seconds=session.duration_seconds,
        completed=session.completed,
        mood_before=session.mood_before,
        mood_after=session.mood_after,
        notes=session.notes,
        started_at=session.started_at.isoformat(),
    )


@router.get("/nexus-insight")
async def nexus_meditation_insight(
    current_user: User = Depends(get_current_user),
):
    """Ask Nexus AI for a personalized meditation recommendation."""
    profile = current_user.profile
    profile_dict = {}
    if profile:
        profile_dict = {
            "health_goals": json.loads(profile.health_goals or "[]"),
            "sun_sign": profile.sun_sign,
            "moon_sign": profile.moon_sign,
        }

    result = await nexus_service.personalized_recommendation(
        module="meditation",
        user_profile=profile_dict,
        context={"available_guides": [g["id"] for g in meditation_service.get_all_guides()]},
    )
    return result


@router.get("/daily-guide")
async def get_daily_guide(
    mental_state: str = Query("neutral", description=f"One of: {', '.join(VALID_MENTAL_STATES)}"),
    goal: str = Query("balance", description=f"One of: {', '.join(VALID_GOALS)}"),
    preferred_style: str | None = Query(None, description="mindfulness | mantra | body_scan"),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a full personalized daily guide using the Nexus guide_engine.

    Returns meditation style, breathing exercise, and meal suggestions
    tailored to the user's mental state and daily goal.
    """
    guide = meditation_service.get_nexus_daily_guide(
        mental_state=mental_state,
        goal=goal,
        preferred_style=preferred_style,
    )
    return {
        **guide,
        "valid_mental_states": VALID_MENTAL_STATES,
        "valid_goals": VALID_GOALS,
    }


@router.get("/guide-options")
async def guide_options():
    """Return valid mental states and goals for the daily guide."""
    return {
        "mental_states": VALID_MENTAL_STATES,
        "goals": VALID_GOALS,
        "meditation_styles": ["mindfulness", "mantra", "body_scan"],
    }

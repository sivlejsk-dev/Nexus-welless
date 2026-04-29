"""Astrology endpoints — birth charts, horoscopes, and Nexus wellness interpretations."""

import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.wellness import BirthChart, BirthChartRequest, DailyHoroscope
from app.services.astrology import ZODIAC_SIGNS, astrology_service
from app.services.nexus import nexus_service

router = APIRouter(prefix="/astrology", tags=["astrology"])


@router.get("/engine-status")
async def engine_status():
    """Report which astrology engine is active."""
    from app.services.astrology import _NEXUS_AVAILABLE
    return {
        "engine": "nexus-celestal-eye" if _NEXUS_AVAILABLE else "fallback",
        "nexus_available": _NEXUS_AVAILABLE,
        "modules": ["BirthChartGenerator", "DailyAstrologer", "AstrologyInterpreter"]
        if _NEXUS_AVAILABLE else [],
    }


@router.post("/birth-chart")
async def calculate_birth_chart(body: BirthChartRequest):
    """Calculate a full natal birth chart using the Nexus BirthChartGenerator."""
    chart = astrology_service.get_birth_chart(
        dob=body.date_of_birth,
        birth_time=body.birth_time,
        lat=body.birth_lat,
        lon=body.birth_lon,
        timezone_str=body.timezone,
    )
    return chart


@router.get("/my-chart", response_model=BirthChart)
async def get_my_chart(
    current_user: User = Depends(get_current_user),
):
    """Calculate birth chart from the user's saved wellness profile."""
    profile = current_user.profile
    if not profile or not profile.date_of_birth:
        raise HTTPException(
            status_code=422,
            detail="Birth date required. Update your wellness profile first.",
        )

    chart = astrology_service.get_birth_chart(
        dob=profile.date_of_birth,
        birth_time=profile.birth_time or "12:00",
        lat=profile.birth_lat or 0.0,
        lon=profile.birth_lon or 0.0,
        timezone_str=profile.timezone or "UTC",
    )

    # Enrich with Nexus interpretation
    profile_dict = {
        "sun_sign": chart["sun"]["sign"],
        "moon_sign": chart["moon"]["sign"],
        "rising_sign": chart["rising"]["sign"],
        "health_goals": json.loads(profile.health_goals or "[]"),
    }
    nexus_result = await nexus_service.personalized_recommendation(
        module="astrology",
        user_profile=profile_dict,
        context={"chart_summary": f"Sun in {chart['sun']['sign']}, Moon in {chart['moon']['sign']}, Rising {chart['rising']['sign']}"},
    )
    chart["nexus_interpretation"] = nexus_result.get("recommendation")
    return chart


@router.get("/horoscope/{sign}", response_model=DailyHoroscope)
async def get_horoscope(
    sign: str,
    target_date: date | None = Query(None, description="ISO date, defaults to today"),
):
    """Daily horoscope for any zodiac sign."""
    sign = sign.capitalize()
    if sign not in ZODIAC_SIGNS:
        raise HTTPException(status_code=400, detail=f"Invalid sign. Choose from: {', '.join(ZODIAC_SIGNS)}")

    horoscope = astrology_service.get_daily_horoscope(sign, target_date)
    return horoscope


@router.get("/horoscope/me/today", response_model=DailyHoroscope)
async def get_my_horoscope(
    current_user: User = Depends(get_current_user),
):
    """Personalized daily horoscope based on the user's sun sign."""
    profile = current_user.profile
    if not profile or not profile.sun_sign:
        # Derive from DOB if available
        if profile and profile.date_of_birth:
            sign = astrology_service.get_sun_sign(profile.date_of_birth)
        else:
            raise HTTPException(status_code=422, detail="Sun sign not set. Update your wellness profile.")
    else:
        sign = profile.sun_sign

    horoscope = astrology_service.get_daily_horoscope(sign)

    # Nexus wellness insight
    nexus_result = await nexus_service.personalized_recommendation(
        module="astrology",
        user_profile={"sun_sign": sign, "moon_sign": profile.moon_sign if profile else None},
        context={"horoscope_theme": horoscope["general"]},
    )
    horoscope["nexus_insight"] = nexus_result.get("recommendation")
    return horoscope


@router.get("/signs")
async def list_signs():
    """All zodiac signs with wellness profiles."""
    return [
        {"sign": sign, **astrology_service.get_sign_wellness_profile(sign)}
        for sign in ZODIAC_SIGNS
    ]

"""User profile endpoints."""

import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, WellnessProfile
from app.schemas.auth import UserOut
from app.schemas.wellness import WellnessProfileOut, WellnessProfileUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm_user(current_user)


@router.get("/me/profile", response_model=WellnessProfileOut)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = current_user.profile
    if not profile:
        return WellnessProfileOut()
    return _profile_to_out(profile)


@router.put("/me/profile", response_model=WellnessProfileOut)
async def update_profile(
    body: WellnessProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = current_user.profile
    if not profile:
        profile = WellnessProfile(user_id=current_user.id)
        db.add(profile)

    data = body.model_dump(exclude_none=True)
    for field in ("dietary_preferences", "health_goals", "allergies", "conditions"):
        if field in data:
            data[field] = json.dumps(data[field])

    for key, value in data.items():
        setattr(profile, key, value)

    await db.flush()
    return _profile_to_out(profile)


def _profile_to_out(profile: WellnessProfile) -> WellnessProfileOut:
    def _parse(val: str | None) -> list[str] | None:
        if val is None:
            return None
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return [val]

    return WellnessProfileOut(
        date_of_birth=profile.date_of_birth,
        birth_time=profile.birth_time,
        birth_location=profile.birth_location,
        birth_lat=profile.birth_lat,
        birth_lon=profile.birth_lon,
        timezone=profile.timezone,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        dietary_preferences=_parse(profile.dietary_preferences),
        health_goals=_parse(profile.health_goals),
        allergies=_parse(profile.allergies),
        conditions=_parse(profile.conditions),
        sun_sign=profile.sun_sign,
        moon_sign=profile.moon_sign,
        rising_sign=profile.rising_sign,
    )

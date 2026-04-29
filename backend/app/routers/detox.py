"""Detox protocol endpoints — protocols, daily guidance, logging, and Nexus recommendations."""

import json

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.middleware.auth import get_current_user
from app.models.user import DetoxLog, User
from app.schemas.wellness import DetoxLogCreate, DetoxLogOut, DetoxProtocol
from app.services.detox import detox_service
from app.services.nexus import nexus_service

router = APIRouter(prefix="/detox", tags=["detox"])


@router.get("/protocols", response_model=list[DetoxProtocol])
async def list_protocols(
    intensity: str | None = Query(None, description="gentle | moderate | intensive"),
):
    protocols = detox_service.get_all_protocols()
    if intensity:
        protocols = [p for p in protocols if p["intensity"] == intensity]
    return protocols


@router.get("/protocols/{protocol_id}", response_model=DetoxProtocol)
async def get_protocol(protocol_id: str):
    protocol = detox_service.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol


@router.get("/protocols/{protocol_id}/day/{day}")
async def get_day_guidance(
    protocol_id: str,
    day: int = Path(ge=1),
):
    """Detailed guidance for a specific day of a detox protocol."""
    guidance = detox_service.get_day_guidance(protocol_id, day)
    if not guidance:
        raise HTTPException(status_code=404, detail="Day not found in protocol")
    return guidance


@router.get("/recommended")
async def get_recommended_protocol(
    current_user: User = Depends(get_current_user),
):
    """Recommend a detox protocol based on the user's wellness profile."""
    profile = current_user.profile
    profile_dict = {}
    if profile:
        profile_dict = {
            "health_goals": json.loads(profile.health_goals or "[]"),
            "conditions": json.loads(profile.conditions or "[]"),
        }
    return detox_service.recommend_protocol(profile_dict)


@router.post("/logs", response_model=DetoxLogOut, status_code=201)
async def log_detox_day(
    body: DetoxLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = DetoxLog(
        user_id=current_user.id,
        protocol_id=body.protocol_id,
        day_number=body.day_number,
        symptoms=json.dumps(body.symptoms),
        energy_level=body.energy_level,
        notes=body.notes,
    )
    db.add(log)
    await db.flush()
    return DetoxLogOut(
        id=str(log.id),
        protocol_id=log.protocol_id,
        day_number=log.day_number,
        symptoms=body.symptoms,
        energy_level=log.energy_level,
        notes=log.notes,
        logged_at=log.logged_at.isoformat(),
    )


@router.get("/nexus-guidance")
async def nexus_detox_guidance(
    protocol_id: str = Query(...),
    day: int = Query(1, ge=1),
    current_user: User = Depends(get_current_user),
):
    """Nexus AI guidance for a specific detox day."""
    guidance = detox_service.get_day_guidance(protocol_id, day)
    profile = current_user.profile
    profile_dict = {}
    if profile:
        profile_dict = {
            "health_goals": json.loads(profile.health_goals or "[]"),
            "conditions": json.loads(profile.conditions or "[]"),
            "sun_sign": profile.sun_sign,
        }

    result = await nexus_service.personalized_recommendation(
        module="detox",
        user_profile=profile_dict,
        context={"protocol_id": protocol_id, "day": day, "guidance": guidance},
    )
    return {**result, "day_guidance": guidance}

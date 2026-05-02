"""FastAPI dependency for extracting and validating the current user from JWT."""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.base import get_db
from app.models.user import User, WellnessProfile

bearer_scheme = HTTPBearer(auto_error=False)

GUEST_EMAIL = "guest@nexus.local"


async def _load_profile(db: AsyncSession, user: User) -> User:
    """Attach profile via separate query — avoids SQLite UUID join issues."""
    result = await db.execute(
        select(WellnessProfile).where(WellnessProfile.user_id == user.id)
    )
    user.__dict__["profile"] = result.scalar_one_or_none()
    return user


async def _get_or_create_guest(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == GUEST_EMAIL))
    guest = result.scalar_one_or_none()
    if not guest:
        guest = User(
            email=GUEST_EMAIL,
            hashed_password="",
            full_name="Guest",
            is_active=True,
            is_verified=True,
        )
        db.add(guest)
        await db.commit()
        await db.refresh(guest)
    guest.__dict__["profile"] = None
    return guest


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # No token — use guest so all endpoints work without login
    if credentials is None:
        return await _get_or_create_guest(db)

    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: str = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return await _load_profile(db, user)

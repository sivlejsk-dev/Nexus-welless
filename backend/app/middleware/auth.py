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

# Kept for backward-compat imports elsewhere; no longer used as a shared account.
GUEST_EMAIL = "guest@nexus.local"


async def _load_profile(db: AsyncSession, user: User) -> User:
    """Attach profile via separate query — avoids SQLite UUID join issues."""
    result = await db.execute(
        select(WellnessProfile).where(WellnessProfile.user_id == user.id)
    )
    user.__dict__["profile"] = result.scalar_one_or_none()
    return user


async def _get_or_create_guest(db: AsyncSession, guest_id: uuid.UUID | None = None) -> User:
    """
    Return a guest User for the given UUID, creating it if needed.

    Each guest session gets its own UUID (issued by POST /auth/guest), so
    guests never share conversation history or vector memory with each other.
    When no UUID is provided (unauthenticated request with no token at all),
    a fresh UUID is generated — the caller won't be able to resume that
    session, but they also won't pollute anyone else's data.
    """
    if guest_id is None:
        guest_id = uuid.uuid4()

    # Unique email per guest UUID keeps the unique constraint happy.
    guest_email = f"guest-{guest_id}@nexus.local"

    result = await db.execute(select(User).where(User.id == guest_id))
    guest = result.scalar_one_or_none()

    if not guest:
        guest = User(
            id=guest_id,
            email=guest_email,
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
    # No token — create a one-off anonymous guest (no persistent session).
    if credentials is None:
        return await _get_or_create_guest(db)

    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: str = payload["sub"]
        is_guest: bool = payload.get("guest", False)
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    uid = uuid.UUID(user_id)

    # Guest tokens resolve to their own isolated guest user row.
    if is_guest:
        return await _get_or_create_guest(db, guest_id=uid)

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return await _load_profile(db, user)

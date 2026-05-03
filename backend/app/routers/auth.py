"""Authentication endpoints — register, login, refresh, guest."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.base import get_db
from app.middleware.auth import _get_or_create_guest
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


async def _get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute;10/hour")
async def register(request: Request, body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await _get_user_by_email(body.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.flush()

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute;20/hour")
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await _get_user_by_email(body.email, db)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/guest", response_model=TokenResponse)
@limiter.limit("10/minute")
async def guest_login(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Issue a JWT for a new isolated guest session.

    Each call creates a unique guest user with its own conversation history
    and vector memory — guests never share data with each other.
    """
    guest_id = uuid.uuid4()
    guest = await _get_or_create_guest(db, guest_id=guest_id)
    guest_extra = {"guest": True}
    return TokenResponse(
        access_token=create_access_token(str(guest.id), extra=guest_extra),
        refresh_token=create_refresh_token(str(guest.id), extra=guest_extra),
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh(request: Request, body: RefreshRequest):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id: str = payload["sub"]
        is_guest: bool = payload.get("guest", False)
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    extra = {"guest": True} if is_guest else None
    return TokenResponse(
        access_token=create_access_token(user_id, extra=extra),
        refresh_token=create_refresh_token(user_id, extra=extra),
    )

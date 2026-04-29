"""User account and wellness profile ORM models."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    profile: Mapped["WellnessProfile | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    meditation_sessions: Mapped[list["MeditationSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    detox_logs: Mapped[list["DetoxLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class WellnessProfile(Base):
    """Extended wellness data used by Nexus AI for personalization."""

    __tablename__ = "wellness_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Demographics
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    birth_time: Mapped[str | None] = mapped_column(String(10))   # "HH:MM"
    birth_location: Mapped[str | None] = mapped_column(String(255))
    birth_lat: Mapped[float | None] = mapped_column(Float)
    birth_lon: Mapped[float | None] = mapped_column(Float)
    timezone: Mapped[str | None] = mapped_column(String(64))

    # Health
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    dietary_preferences: Mapped[str | None] = mapped_column(Text)   # JSON array
    health_goals: Mapped[str | None] = mapped_column(Text)          # JSON array
    allergies: Mapped[str | None] = mapped_column(Text)             # JSON array
    conditions: Mapped[str | None] = mapped_column(Text)            # JSON array

    # Astrology cache
    sun_sign: Mapped[str | None] = mapped_column(String(32))
    moon_sign: Mapped[str | None] = mapped_column(String(32))
    rising_sign: Mapped[str | None] = mapped_column(String(32))

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="profile")


class MeditationSession(Base):
    __tablename__ = "meditation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    guide_id: Mapped[str] = mapped_column(String(128))
    duration_seconds: Mapped[int] = mapped_column(default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    mood_before: Mapped[int | None] = mapped_column()   # 1-10
    mood_after: Mapped[int | None] = mapped_column()    # 1-10
    notes: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="meditation_sessions")


class DetoxLog(Base):
    __tablename__ = "detox_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    protocol_id: Mapped[str] = mapped_column(String(128))
    day_number: Mapped[int] = mapped_column(default=1)
    symptoms: Mapped[str | None] = mapped_column(Text)   # JSON array
    energy_level: Mapped[int | None] = mapped_column()   # 1-10
    notes: Mapped[str | None] = mapped_column(Text)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="detox_logs")

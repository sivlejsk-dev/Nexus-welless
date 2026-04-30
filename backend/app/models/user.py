"""User account and wellness profile ORM models."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import CHAR, TypeDecorator

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PortableUUID(TypeDecorator):
    """UUID stored as CHAR(36) on SQLite, native UUID on PostgreSQL."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return str(value) if isinstance(value, uuid.UUID) else str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PortableUUID, primary_key=True, default=uuid.uuid4)
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
    __tablename__ = "wellness_profiles"

    id: Mapped[uuid.UUID] = mapped_column(PortableUUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    date_of_birth: Mapped[date | None] = mapped_column(Date)
    birth_time: Mapped[str | None] = mapped_column(String(10))
    birth_location: Mapped[str | None] = mapped_column(String(255))
    birth_lat: Mapped[float | None] = mapped_column(Float)
    birth_lon: Mapped[float | None] = mapped_column(Float)
    timezone: Mapped[str | None] = mapped_column(String(64))

    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    dietary_preferences: Mapped[str | None] = mapped_column(Text)
    health_goals: Mapped[str | None] = mapped_column(Text)
    allergies: Mapped[str | None] = mapped_column(Text)
    conditions: Mapped[str | None] = mapped_column(Text)

    sun_sign: Mapped[str | None] = mapped_column(String(32))
    moon_sign: Mapped[str | None] = mapped_column(String(32))
    rising_sign: Mapped[str | None] = mapped_column(String(32))

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="profile")


class MeditationSession(Base):
    __tablename__ = "meditation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(PortableUUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"))
    guide_id: Mapped[str] = mapped_column(String(128))
    duration_seconds: Mapped[int] = mapped_column(default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    mood_before: Mapped[int | None] = mapped_column()
    mood_after: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="meditation_sessions")


class DetoxLog(Base):
    __tablename__ = "detox_logs"

    id: Mapped[uuid.UUID] = mapped_column(PortableUUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PortableUUID, ForeignKey("users.id", ondelete="CASCADE"))
    protocol_id: Mapped[str] = mapped_column(String(128))
    day_number: Mapped[int] = mapped_column(default=1)
    symptoms: Mapped[str | None] = mapped_column(Text)
    energy_level: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(Text)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="detox_logs")

"""ORM models for persistent conversation sessions (Task 1.5)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, CHAR
import sqlalchemy as sa

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── UUID portability shim ─────────────────────────────────────────────────────
# PostgreSQL has a native UUID type; SQLite stores it as CHAR(36).

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


# ── Models ────────────────────────────────────────────────────────────────────

class ChatSession(Base):
    """
    A persistent conversation session between a user and Nexus.

    Stores metadata and a rolling compressed summary so long sessions
    don't blow the LLM context window.
    """

    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        PortableUUID, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PortableUUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Rolling summary of turns that have been compressed out of the live window
    summary: Mapped[str | None] = mapped_column(Text)
    # Domain that dominated this session
    primary_domain: Mapped[str] = mapped_column(String(64), default="general")
    # Total turns ever recorded (including compressed ones)
    total_turns: Mapped[int] = mapped_column(Integer, default=0)
    # Turns currently in the live window (not yet compressed)
    active_turns: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    turns: Mapped[list["ChatTurn"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatTurn.turn_index",
    )


class ChatTurn(Base):
    """
    A single message turn within a ChatSession.

    Only the live window (most recent N turns) is kept as individual rows.
    Older turns are compressed into ChatSession.summary and deleted.
    """

    __tablename__ = "chat_turns"

    id: Mapped[uuid.UUID] = mapped_column(
        PortableUUID, primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        PortableUUID,
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)   # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(64), default="general")
    intent: Mapped[str | None] = mapped_column(String(128))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    session: Mapped["ChatSession"] = relationship(back_populates="turns")

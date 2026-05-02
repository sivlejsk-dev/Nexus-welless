"""
Persistent conversation session service (Task 1.5).

Replaces the in-memory `_sessions` dict in conversation.py with a
SQLAlchemy-backed store. Sessions survive server restarts and can be
queried, listed, and deleted via the API.

Summary compression
-------------------
When a session accumulates more than LIVE_WINDOW_SIZE turns, the oldest
turns are compressed into a plain-text summary appended to ChatSession.summary,
then deleted from chat_turns. This keeps the DB row count bounded while
preserving long-term context in a compact form.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import ChatSession, ChatTurn

logger = logging.getLogger(__name__)

# Turns kept in the live window before compression kicks in
LIVE_WINDOW_SIZE = 20
# Turns to compress per compression pass (must be < LIVE_WINDOW_SIZE)
COMPRESS_BATCH = 10


class SessionStore:
    """
    Async CRUD layer for ChatSession / ChatTurn.

    All methods accept an `AsyncSession` injected by FastAPI's `get_db`
    dependency, so they participate in the request transaction.
    """

    # ── Session lifecycle ─────────────────────────────────────────────────────

    async def get_or_create(
        self, db: AsyncSession, user_id: str | uuid.UUID
    ) -> ChatSession:
        """Return the user's active session, creating one if none exists."""
        uid = uuid.UUID(str(user_id))
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == uid)
            .order_by(ChatSession.last_active.desc())
            .limit(1)
            .options(selectinload(ChatSession.turns))
        )
        session = result.scalar_one_or_none()
        if session is None:
            session = ChatSession(user_id=uid)
            db.add(session)
            await db.flush()
        return session

    async def get_session(
        self, db: AsyncSession, session_id: str | uuid.UUID
    ) -> ChatSession | None:
        sid = uuid.UUID(str(session_id))
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.id == sid)
            .options(selectinload(ChatSession.turns))
        )
        return result.scalar_one_or_none()

    async def list_sessions(
        self, db: AsyncSession, user_id: str | uuid.UUID, limit: int = 20
    ) -> list[ChatSession]:
        uid = uuid.UUID(str(user_id))
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == uid)
            .order_by(ChatSession.last_active.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_session(
        self, db: AsyncSession, session_id: str | uuid.UUID
    ) -> bool:
        sid = uuid.UUID(str(session_id))
        result = await db.execute(
            delete(ChatSession).where(ChatSession.id == sid)
        )
        return result.rowcount > 0

    async def delete_all_sessions(
        self, db: AsyncSession, user_id: str | uuid.UUID
    ) -> int:
        uid = uuid.UUID(str(user_id))
        result = await db.execute(
            delete(ChatSession).where(ChatSession.user_id == uid)
        )
        return result.rowcount

    # ── Turn management ───────────────────────────────────────────────────────

    async def add_turn(
        self,
        db: AsyncSession,
        session: ChatSession,
        role: str,
        content: str,
        domain: str = "general",
        intent: str | None = None,
    ) -> ChatTurn:
        """Append a turn and trigger compression if the window is full."""
        turn = ChatTurn(
            session_id=session.id,
            turn_index=session.total_turns,
            role=role,
            content=content,
            domain=domain,
            intent=intent,
        )
        db.add(turn)

        session.total_turns += 1
        session.active_turns += 1
        session.last_active = datetime.now(timezone.utc)
        if domain != "general":
            session.primary_domain = domain

        await db.flush()

        # Compress if live window is full
        if session.active_turns >= LIVE_WINDOW_SIZE:
            await self._compress(db, session)

        return turn

    async def get_live_turns(
        self, db: AsyncSession, session_id: uuid.UUID
    ) -> list[ChatTurn]:
        """Return the current live-window turns in chronological order."""
        result = await db.execute(
            select(ChatTurn)
            .where(ChatTurn.session_id == session_id)
            .order_by(ChatTurn.turn_index)
        )
        return list(result.scalars().all())

    def build_history_for_llm(
        self, turns: list[ChatTurn], window: int = 10
    ) -> list[dict[str, str]]:
        """Format the most recent N turns for the LLM messages array."""
        recent = turns[-(window * 2):]
        return [{"role": t.role, "content": t.content} for t in recent]

    def build_context_with_summary(self, session: ChatSession) -> str:
        """
        Build a context string that includes the compressed summary (if any)
        followed by a note about the current session state.
        """
        parts: list[str] = []
        if session.summary:
            parts.append(f"[Earlier conversation summary]\n{session.summary}")
        parts.append(
            f"Session: {session.total_turns} total turns | "
            f"domain: {session.primary_domain}"
        )
        return "\n\n".join(parts)

    # ── Summary compression ───────────────────────────────────────────────────

    async def _compress(self, db: AsyncSession, session: ChatSession) -> None:
        """
        Compress the oldest COMPRESS_BATCH turns into session.summary and delete them.

        The summary is plain text — no LLM call required. It captures the
        key user statements and AI responses in a compact form.
        """
        result = await db.execute(
            select(ChatTurn)
            .where(ChatTurn.session_id == session.id)
            .order_by(ChatTurn.turn_index)
            .limit(COMPRESS_BATCH)
        )
        old_turns = list(result.scalars().all())
        if not old_turns:
            return

        compressed = _summarize_turns(old_turns)

        # Append to existing summary
        if session.summary:
            session.summary = session.summary + "\n\n" + compressed
        else:
            session.summary = compressed

        # Delete compressed turns
        turn_ids = [t.id for t in old_turns]
        await db.execute(
            delete(ChatTurn).where(ChatTurn.id.in_(turn_ids))
        )
        session.active_turns = max(0, session.active_turns - len(old_turns))

        logger.debug(
            "Compressed %d turns for session %s (active=%d)",
            len(old_turns), session.id, session.active_turns,
        )

    # ── Serialization ─────────────────────────────────────────────────────────

    def session_to_dict(self, session: ChatSession) -> dict[str, Any]:
        return {
            "session_id": str(session.id),
            "user_id": str(session.user_id),
            "primary_domain": session.primary_domain,
            "total_turns": session.total_turns,
            "active_turns": session.active_turns,
            "has_summary": bool(session.summary),
            "summary_preview": (session.summary or "")[:200] or None,
            "created_at": session.created_at.isoformat(),
            "last_active": session.last_active.isoformat(),
        }


# ── Compression helper ────────────────────────────────────────────────────────

def _summarize_turns(turns: list[ChatTurn]) -> str:
    """
    Produce a compact plain-text summary of a batch of turns.

    Format:
        [Turn N] User: <first 150 chars>
                 Nexus: <first 150 chars>
    """
    lines: list[str] = [f"[Turns {turns[0].turn_index}–{turns[-1].turn_index}]"]
    i = 0
    while i < len(turns):
        turn = turns[i]
        if turn.role == "user":
            user_text = turn.content[:150].replace("\n", " ")
            ai_text = ""
            if i + 1 < len(turns) and turns[i + 1].role == "assistant":
                ai_text = turns[i + 1].content[:150].replace("\n", " ")
                i += 1
            lines.append(f"  User: {user_text}")
            if ai_text:
                lines.append(f"  Nexus: {ai_text}")
        i += 1
    return "\n".join(lines)


# Singleton
session_store = SessionStore()

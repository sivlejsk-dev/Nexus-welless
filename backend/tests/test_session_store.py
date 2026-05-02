"""
Tests for persistent conversation sessions (Task 1.5).

Uses an in-process SQLite database so no external DB is required.
"""

import asyncio
import uuid
import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.db.base import Base
from app.models.session import ChatSession, ChatTurn  # registers models with Base
from app.models.user import User, WellnessProfile, MeditationSession, DetoxLog  # full schema
from app.services.session_store import (
    SessionStore,
    LIVE_WINDOW_SIZE,
    COMPRESS_BATCH,
    _summarize_turns,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture()
async def db_session():
    """Provide a fresh in-memory SQLite async session for each test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        # Create a dummy user row so FK constraints pass
        user_id = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO users (id, email, hashed_password, is_active, is_verified, created_at, updated_at) "
                "VALUES (:id, :email, :pw, 1, 1, datetime('now'), datetime('now'))"
            ),
            {"id": str(user_id), "email": "test@nexus.ai", "pw": "hashed"},
        )
        await session.commit()
        yield session, user_id

    await engine.dispose()


@pytest.fixture()
def store():
    return SessionStore()


# ── Session lifecycle ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_or_create_new_session(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)
    assert sess is not None
    assert sess.user_id == user_id
    assert sess.total_turns == 0


@pytest.mark.asyncio
async def test_get_or_create_returns_existing(db_session, store):
    db, user_id = db_session
    s1 = await store.get_or_create(db, user_id)
    await db.commit()
    s2 = await store.get_or_create(db, user_id)
    assert s1.id == s2.id


@pytest.mark.asyncio
async def test_list_sessions_empty(db_session, store):
    db, user_id = db_session
    sessions = await store.list_sessions(db, user_id)
    assert sessions == []


@pytest.mark.asyncio
async def test_list_sessions_after_create(db_session, store):
    db, user_id = db_session
    await store.get_or_create(db, user_id)
    await db.commit()
    sessions = await store.list_sessions(db, user_id)
    assert len(sessions) == 1


@pytest.mark.asyncio
async def test_delete_session(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)
    await db.commit()
    deleted = await store.delete_session(db, sess.id)
    assert deleted is True
    sessions = await store.list_sessions(db, user_id)
    assert sessions == []


@pytest.mark.asyncio
async def test_delete_all_sessions(db_session, store):
    db, user_id = db_session
    await store.get_or_create(db, user_id)
    await db.commit()
    count = await store.delete_all_sessions(db, user_id)
    assert count == 1
    assert await store.list_sessions(db, user_id) == []


# ── Turn management ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_turn_increments_counters(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)

    await store.add_turn(db, sess, "user", "Hello Nexus", domain="general")
    await store.add_turn(db, sess, "assistant", "Hello! How can I help?", domain="general")
    await db.commit()

    assert sess.total_turns == 2
    assert sess.active_turns == 2


@pytest.mark.asyncio
async def test_get_live_turns(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)

    await store.add_turn(db, sess, "user", "What is turmeric?", domain="nutrition")
    await store.add_turn(db, sess, "assistant", "Turmeric is an anti-inflammatory spice.", domain="nutrition")
    await db.commit()

    turns = await store.get_live_turns(db, sess.id)
    assert len(turns) == 2
    assert turns[0].role == "user"
    assert turns[1].role == "assistant"


@pytest.mark.asyncio
async def test_domain_tracking(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)

    await store.add_turn(db, sess, "user", "Tell me about Saturn return", domain="astrology")
    await db.commit()

    assert sess.primary_domain == "astrology"


@pytest.mark.asyncio
async def test_build_history_for_llm(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)

    await store.add_turn(db, sess, "user", "Message 1", domain="general")
    await store.add_turn(db, sess, "assistant", "Response 1", domain="general")
    await db.commit()

    turns = await store.get_live_turns(db, sess.id)
    history = store.build_history_for_llm(turns, window=5)
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "Message 1"}
    assert history[1] == {"role": "assistant", "content": "Response 1"}


# ── Summary compression ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_compression_triggers_at_window_size(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)

    # Add enough turns to trigger compression
    for i in range(LIVE_WINDOW_SIZE):
        role = "user" if i % 2 == 0 else "assistant"
        await store.add_turn(db, sess, role, f"Turn {i} content", domain="nutrition")

    await db.commit()

    # After compression, active_turns should be reduced
    assert sess.active_turns < LIVE_WINDOW_SIZE
    # Summary should have been written
    assert sess.summary is not None
    assert "Turn" in sess.summary


@pytest.mark.asyncio
async def test_compression_preserves_total_turns(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)

    n = LIVE_WINDOW_SIZE + 4
    for i in range(n):
        role = "user" if i % 2 == 0 else "assistant"
        await store.add_turn(db, sess, role, f"Content {i}", domain="general")

    await db.commit()

    assert sess.total_turns == n


@pytest.mark.asyncio
async def test_build_context_with_summary(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)
    sess.summary = "User asked about nutrition. Nexus recommended turmeric."
    sess.primary_domain = "nutrition"
    sess.total_turns = 5

    ctx = store.build_context_with_summary(sess)
    assert "Earlier conversation summary" in ctx
    assert "turmeric" in ctx
    assert "nutrition" in ctx


# ── _summarize_turns helper ───────────────────────────────────────────────────

def test_summarize_turns_format():
    turns = [
        ChatTurn(turn_index=0, role="user", content="What foods reduce inflammation?"),
        ChatTurn(turn_index=1, role="assistant", content="Turmeric and ginger are excellent."),
        ChatTurn(turn_index=2, role="user", content="How much turmeric per day?"),
        ChatTurn(turn_index=3, role="assistant", content="1-3 grams of curcumin daily is effective."),
    ]
    summary = _summarize_turns(turns)
    assert "Turns 0" in summary
    assert "User:" in summary
    assert "Nexus:" in summary
    assert "turmeric" in summary.lower()


def test_summarize_turns_truncates_long_content():
    long_content = "x" * 300
    turns = [
        ChatTurn(turn_index=0, role="user", content=long_content),
        ChatTurn(turn_index=1, role="assistant", content=long_content),
    ]
    summary = _summarize_turns(turns)
    # Each side is capped at 150 chars
    assert len(summary) < 600


# ── Serialization ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_session_to_dict(db_session, store):
    db, user_id = db_session
    sess = await store.get_or_create(db, user_id)
    d = store.session_to_dict(sess)

    assert "session_id" in d
    assert "user_id" in d
    assert d["total_turns"] == 0
    assert d["has_summary"] is False

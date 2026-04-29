"""
Nexus AI endpoints — conversation-aware chat, recommendations, and session management.

All chat messages pass through the ConversationEngine (Task 1.1):
  - Pronoun resolution and reference tracking
  - Domain classification (wellness / finance / astrology)
  - Tone analysis and response polishing
  - Per-user conversation history
  - Proactive suggestions
"""

import json

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from app.db.base import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.wellness import NexusRecommendationRequest, NexusRecommendationResponse
from app.services.conversation import conversation_engine
from app.services.learning import learning_service
from app.services.reasoning import reasoning_service
from app.services.rag import rag_service
from app.services.session_store import session_store
from app.services.nexus import nexus_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/nexus", tags=["nexus-ai"])


@router.post("/chat")
async def chat(
    message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full conversation-aware chat with Nexus.
    Remembers context, resolves references, detects domain and intent,
    adapts tone. Covers wellness, astrology, finance, and options trading.
    Turns are persisted to the DB and retrievable via /nexus/sessions.
    """
    profile = current_user.profile
    profile_dict: dict = {}
    if profile:
        profile_dict = {
            "sun_sign": profile.sun_sign,
            "moon_sign": profile.moon_sign,
            "health_goals": json.loads(profile.health_goals or "[]"),
            "dietary_preferences": json.loads(profile.dietary_preferences or "[]"),
            "conditions": json.loads(profile.conditions or "[]"),
        }

    result = await nexus_service.chat(
        user_id=str(current_user.id),
        raw_message=message,
        user_profile=profile_dict,
        db=db,
    )
    return result


@router.get("/session")
async def get_session(current_user: User = Depends(get_current_user)):
    """Return the current conversation session summary."""
    return conversation_engine.get_session_summary(str(current_user.id))


@router.delete("/session")
async def clear_session(current_user: User = Depends(get_current_user)):
    """Clear the conversation session — Nexus starts fresh."""
    conversation_engine.clear_session(str(current_user.id))
    return {"cleared": True, "user_id": str(current_user.id)}


@router.post("/recommend", response_model=NexusRecommendationResponse)
async def get_recommendation(
    body: NexusRecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    """Structured Nexus recommendation for a specific module."""
    profile = current_user.profile
    profile_dict: dict = {}
    if profile:
        profile_dict = {
            "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
            "sun_sign": profile.sun_sign,
            "moon_sign": profile.moon_sign,
            "rising_sign": profile.rising_sign,
            "health_goals": json.loads(profile.health_goals or "[]"),
            "dietary_preferences": json.loads(profile.dietary_preferences or "[]"),
            "conditions": json.loads(profile.conditions or "[]"),
            "allergies": json.loads(profile.allergies or "[]"),
        }

    result = await nexus_service.personalized_recommendation(
        module=body.module,
        user_profile=profile_dict,
        context=body.context,
        user_message=body.user_message,
    )
    return NexusRecommendationResponse(**result)


@router.post("/analyze")
async def analyze_message(
    message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze a message through the conversation engine without calling the LLM.
    Returns domain, intent, tone, resolved text, and suggestions.
    """
    processed = conversation_engine.process_input(str(current_user.id), message)
    return processed.to_dict()


# ── Learning endpoints (Task 1.2) ─────────────────────────────────────────────

@router.get("/skills")
async def get_skill_profile(current_user: User = Depends(get_current_user)):
    """
    Return the user's skill proficiency profile across all Nexus domains.
    Shows how Nexus has learned to adapt to this user over time.
    """
    return {
        "user_id": str(current_user.id),
        "profile": learning_service.get_skill_profile(str(current_user.id)),
        "insights": learning_service.get_insights(str(current_user.id)),
        "recommendations": learning_service.get_recommendations(str(current_user.id))[:3],
    }


@router.get("/skills/concepts")
async def get_related_concepts(
    concept: str = Query(..., description="Topic to find related concepts for"),
    current_user: User = Depends(get_current_user),
):
    """Return concepts related to a topic from the user's personal knowledge graph."""
    related = learning_service.get_related_concepts(str(current_user.id), concept)
    return {"concept": concept, "related": related}


# ── Reasoning endpoints (Task 1.3) ────────────────────────────────────────────

@router.post("/reason")
async def reason(
    problem: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """
    Run structured multi-framework reasoning on a complex problem.

    Uses deductive, inductive, abductive, and causal reasoning to:
    - Decompose the problem into components
    - Generate multiple solution approaches
    - Return the best solution with confidence scores

    Ideal for: options strategy selection, detox protocol design,
    nutritional planning, astrological timing analysis.
    """
    return reasoning_service.reason(problem)


@router.post("/reason/analyze")
async def analyze_problem(
    problem: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Lightweight problem analysis — complexity score, key questions, constraints."""
    return reasoning_service.analyze(problem)


# ── Vector memory / RAG endpoints (Task 1.4) ──────────────────────────────────

@router.get("/memory/stats")
async def get_memory_stats(current_user: User = Depends(get_current_user)):
    """Return vector memory usage stats for the current user."""
    return {
        "user_id": str(current_user.id),
        **rag_service.get_memory_stats(str(current_user.id)),
    }


@router.post("/memory/search")
async def search_memory(
    query: str = Body(..., embed=True),
    domain: str | None = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
):
    """
    Semantic search over the user's stored conversation history and knowledge.

    Returns the most relevant past exchanges and facts for a given query.
    Useful for surfacing forgotten context or auditing what Nexus remembers.
    """
    from app.services.vector_memory import vector_memory

    results = vector_memory.search_all(
        user_id=str(current_user.id),
        query=query,
        n_results=8,
        domain_filter=domain,
    )
    return {
        "query": query,
        "domain_filter": domain,
        "conversations": results["conversations"],
        "knowledge": results["knowledge"],
    }


@router.post("/memory/store")
async def store_knowledge(
    fact: str = Body(..., embed=True),
    domain: str = Body("general", embed=True),
    current_user: User = Depends(get_current_user),
):
    """
    Manually store a fact or insight into the user's knowledge base.

    Nexus will retrieve this during future conversations when relevant.
    """
    from app.services.vector_memory import vector_memory

    kid = vector_memory.store_knowledge(
        user_id=str(current_user.id),
        fact=fact,
        domain=domain,
        source="manual",
    )
    return {"stored": True, "knowledge_id": kid, "fact": fact, "domain": domain}


@router.delete("/memory")
async def clear_vector_memory(current_user: User = Depends(get_current_user)):
    """
    Delete all vector memory for the current user.

    Removes both conversation history and knowledge from ChromaDB.
    This cannot be undone.
    """
    rag_service.delete_user_memory(str(current_user.id))
    return {"cleared": True, "user_id": str(current_user.id)}


# ── Persistent session endpoints (Task 1.5) ───────────────────────────────────

@router.get("/sessions")
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the user's conversation sessions, most recent first."""
    sessions = await session_store.list_sessions(db, current_user.id, limit=limit)
    return {
        "user_id": str(current_user.id),
        "sessions": [session_store.session_to_dict(s) for s in sessions],
        "count": len(sessions),
    }


@router.get("/sessions/{session_id}")
async def get_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return full detail for a specific session including live turns."""
    sess = await session_store.get_session(db, session_id)
    if sess is None or str(sess.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Session not found")

    turns = await session_store.get_live_turns(db, sess.id)
    return {
        **session_store.session_to_dict(sess),
        "summary": sess.summary,
        "turns": [
            {
                "turn_index": t.turn_index,
                "role": t.role,
                "content": t.content,
                "domain": t.domain,
                "intent": t.intent,
                "created_at": t.created_at.isoformat(),
            }
            for t in turns
        ],
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific conversation session and all its turns."""
    sess = await session_store.get_session(db, session_id)
    if sess is None or str(sess.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Session not found")
    await session_store.delete_session(db, session_id)
    return {"deleted": True, "session_id": session_id}


@router.delete("/sessions")
async def delete_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete all conversation sessions for the current user."""
    count = await session_store.delete_all_sessions(db, current_user.id)
    return {"deleted": count, "user_id": str(current_user.id)}

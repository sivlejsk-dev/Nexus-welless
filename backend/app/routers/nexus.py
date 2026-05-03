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
import re

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
from app.services.media import media_service
from sqlalchemy.ext.asyncio import AsyncSession

# ── Media intent detection ────────────────────────────────────────────────────

_IMAGE_PATTERNS = re.compile(
    r"\b(generate|create|make|draw|render|show|paint|design|produce|give me)"
    r".{0,30}(image|picture|photo|illustration|visual|artwork|graphic|poster|banner)\b"
    r"|\b(image|picture|photo|illustration|artwork|graphic) of\b"
    r"|\bvisuali[sz]e\b|\bdraw me\b|\bshow me a\b",
    re.IGNORECASE,
)

_VIDEO_PATTERNS = re.compile(
    r"\b(generate|create|make|render|produce|show|give me)"
    r".{0,30}(video|animation|clip|reel|film|motion)\b"
    r"|\b(video|animation|clip) of\b",
    re.IGNORECASE,
)

_GUIDE_PATTERNS = re.compile(
    r"\b(visual guide|step.by.step guide|show me how|walk me through|guide me through)\b",
    re.IGNORECASE,
)


def _detect_media_intent(message: str) -> str | None:
    """Return 'image', 'video', 'guide', or None."""
    if _VIDEO_PATTERNS.search(message):
        return "video"
    if _GUIDE_PATTERNS.search(message):
        return "guide"
    if _IMAGE_PATTERNS.search(message):
        return "image"
    return None


def _extract_topic(message: str) -> str:
    """Best-effort topic extraction for image/video prompts."""
    # Strip the action verb prefix and return the rest as the prompt
    cleaned = re.sub(
        r"^(please\s+)?(generate|create|make|draw|render|show|paint|design|produce|give me|visualize|visualise)\s+(me\s+)?(a\s+|an\s+)?(image|picture|photo|illustration|visual|artwork|graphic|video|animation|clip|poster|banner)?\s*(of\s+)?",
        "",
        message.strip(),
        flags=re.IGNORECASE,
    ).strip(" .,?!")
    return cleaned or message

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

    # ── Media intent interception ─────────────────────────────────────────
    media_intent = _detect_media_intent(message)
    if media_intent:
        prompt = _extract_topic(message)

        if media_intent == "video":
            # Start video generation job and return immediately with job id
            media_result = await media_service.start_video_generation(
                prompt=prompt, size="1280x720", seconds="8"
            )
            # Also get a text response from Nexus to accompany the media
            text_result = await nexus_service.chat(
                user_id=str(current_user.id),
                raw_message=message,
                user_profile=profile_dict,
                db=db,
            )
            return {
                **text_result,
                "media": {"type": "video", **media_result},
            }

        if media_intent == "guide":
            # Match to a visual guide or fall back to image
            media_result = await media_service.query_to_media(
                query=prompt, media_type="guide"
            )
            text_result = await nexus_service.chat(
                user_id=str(current_user.id),
                raw_message=message,
                user_profile=profile_dict,
                db=db,
            )
            return {
                **text_result,
                "media": {"type": "guide", **media_result},
            }

        # Default: image
        media_result = await media_service.generate_image(
            prompt=prompt,
            topic=_classify_topic(prompt),
        )
        text_result = await nexus_service.chat(
            user_id=str(current_user.id),
            raw_message=message,
            user_profile=profile_dict,
            db=db,
        )
        return {
            **text_result,
            "media": {"type": "image", **media_result},
        }

    # ── Standard text chat ────────────────────────────────────────────────
    result = await nexus_service.chat(
        user_id=str(current_user.id),
        raw_message=message,
        user_profile=profile_dict,
        db=db,
    )
    return result


def _classify_topic(prompt: str) -> str:
    """Map a free-text prompt to a FALLBACK_IMAGES topic key."""
    p = prompt.lower()
    if any(w in p for w in ("food", "eat", "nutrition", "meal", "diet", "fruit", "vegetable", "recipe")):
        return "nutrition"
    if any(w in p for w in ("meditat", "breath", "mindful", "calm", "peace", "zen")):
        return "meditation"
    if any(w in p for w in ("detox", "cleanse", "juice", "fast")):
        return "detox"
    if any(w in p for w in ("herb", "plant", "flower", "nature", "garden", "leaf")):
        return "herbs"
    if any(w in p for w in ("cook", "kitchen", "chef", "bake", "recipe")):
        return "cooking"
    if any(w in p for w in ("fitness", "workout", "exercise", "gym", "yoga", "stretch")):
        return "fitness"
    if any(w in p for w in ("sleep", "rest", "night", "dream", "insomnia")):
        return "sleep"
    return "general"


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


# ── Nutrition knowledge endpoints (Stage 10) ──────────────────────────────────

@router.get("/nutrition/foods/{condition}")
async def get_foods_for_condition(
    condition: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return healing foods and herbs for a specific health condition.

    Supports synonym resolution (e.g. 'ibs' → gut-health, 'arthritis' → joint-pain).
    Results are ranked by evidence tier (RCT > meta-analysis > observational > traditional).
    """
    from app.services.nutrition import nutrition_service
    results = nutrition_service.get_healing_foods(condition)
    return {
        "condition": condition,
        "count": len(results),
        "foods": results,
    }


@router.get("/nutrition/herb/{name}")
async def get_herb_monograph(
    name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return the full monograph for a food or herb.

    Includes active compounds, dosing, bioavailability notes,
    drug interactions, contraindications, and evidence tier.
    """
    from app.services.nutrition import nutrition_service
    mono = nutrition_service.get_food_monograph(name)
    if not mono:
        raise HTTPException(status_code=404, detail=f"No monograph found for '{name}'")
    return mono


@router.get("/nutrition/assess")
async def assess_symptoms(
    symptoms: str,
    current_user: User = Depends(get_current_user),
):
    """
    Assess a comma-separated list of symptoms and return likely root causes,
    possible nutrient deficiencies, and recommended labs.

    Example: ?symptoms=fatigue,brain+fog,bloating,sugar+cravings
    """
    from app.nexus_core.nutrition_expertise import nutrition_expertise
    symptom_list = [s.strip() for s in symptoms.split(",") if s.strip()]
    if not symptom_list:
        raise HTTPException(status_code=400, detail="Provide at least one symptom")
    return nutrition_expertise.assess_symptoms(symptom_list)


@router.get("/detox/protocols")
async def list_detox_protocols(
    current_user: User = Depends(get_current_user),
):
    """List all available detox protocols with metadata (no phase detail)."""
    from app.services.detox import detox_service
    protocols = detox_service.get_all_protocols()
    return {
        "count": len(protocols),
        "protocols": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "duration_days": p["duration_days"],
                "intensity": p["intensity"],
                "phases": len(p["phases"]),
                "contraindications": p["contraindications"],
            }
            for p in protocols
        ],
    }


@router.get("/detox/protocols/{protocol_id}")
async def get_detox_protocol(
    protocol_id: str,
    current_user: User = Depends(get_current_user),
):
    """Return full detail for a specific detox protocol including all phases."""
    from app.services.detox import detox_service
    protocol = detox_service.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Protocol '{protocol_id}' not found")
    return protocol


@router.get("/detox/protocols/{protocol_id}/day/{day}")
async def get_protocol_day_guidance(
    protocol_id: str,
    day: int,
    current_user: User = Depends(get_current_user),
):
    """Return specific day guidance for a detox protocol."""
    from app.services.detox import detox_service
    guidance = detox_service.get_day_guidance(protocol_id, day)
    if not guidance:
        raise HTTPException(
            status_code=404,
            detail=f"No guidance for protocol '{protocol_id}' day {day}"
        )
    return guidance


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

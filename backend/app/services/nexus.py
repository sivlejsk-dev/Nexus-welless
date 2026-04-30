"""
Nexus AI service — wraps the Nexus model via OpenAI-compatible API spec.

All messages are routed through the ConversationEngine (Task 1.1) which:
  - Resolves pronouns and references across turns
  - Tracks topic threads and domain context
  - Analyzes tone and adjusts response style
  - Maintains per-user conversation history
  - Generates proactive suggestions
"""

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


def _make_client(base_url: str, api_key: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=base_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=60.0,
    )


SYSTEM_PROMPT = """You are Nexus — a deeply knowledgeable, adaptive wellness intelligence. You speak like a trusted friend who happens to have the knowledge of a functional medicine doctor, a master herbalist, a nutritionist, a financial strategist, and a life coach. You are warm, direct, and never robotic. You meet people where they are.

═══════════════════════════════════════════
CORE DOMAINS
═══════════════════════════════════════════

1. FOOD AS MEDICINE & FUNCTIONAL NUTRITION
You understand that food is the most powerful drug on the planet. Every recommendation you make includes:
- The active compound and its mechanism (e.g., "curcumin inhibits NF-κB, the master switch of inflammation")
- Therapeutic dose ranges (not just "eat turmeric" — "500mg curcumin with 20mg piperine, 3x/day with fat")
- Bioavailability factors (what enhances or blocks absorption)
- Evidence tier (RCT, meta-analysis, traditional use)
- Contraindications and drug interactions

Key food-as-medicine principles you embody:
- Sulforaphane (broccoli sprouts) activates Nrf2 — the master antioxidant pathway. 3-day-old sprouts have 50x more than mature broccoli.
- Quercetin (onions, capers) is a natural antihistamine and mast cell stabilizer — 500mg twice daily rivals pharmaceutical antihistamines.
- Berberine (barberry, goldenseal) activates AMPK — same pathway as metformin. 500mg 3x/day rivals metformin for blood sugar without side effects.
- Omega-3 EPA/DHA reduce IL-6, TNF-alpha, and CRP. Minimum therapeutic dose: 2g EPA+DHA/day. Fish oil oxidizes easily — store in fridge, buy with antioxidants.
- Magnesium deficiency affects 80% of people. Glycinate for sleep/anxiety, malate for energy/fibromyalgia, threonate for brain/cognition, citrate for constipation.
- Vitamin D3 is a hormone, not a vitamin. Optimal range: 60-80 ng/mL. Most people need 5,000-10,000 IU/day with K2 (MK-7) to direct calcium to bones, not arteries.
- Zinc is the gatekeeper of 300+ enzymatic reactions. Deficiency = poor immunity, low testosterone, hair loss, slow wound healing. Picolinate or bisglycinate forms are best absorbed.

2. DETOX PHYSIOLOGY
- Phase I liver detox (cytochrome P450): oxidation, reduction, hydrolysis. Requires B2, B3, B6, B12, folate, glutathione, antioxidants. Cruciferous vegetables are essential.
- Phase II (conjugation): glucuronidation, sulfation, methylation, glutathione conjugation, acetylation. Requires sulfur amino acids (NAC, methionine, cysteine), glycine, glutamine.
- CRITICAL SEQUENCE: Open drainage pathways FIRST (bowels moving 2x/day, kidneys filtering, lymph moving) BEFORE mobilizing toxins. Mobilizing without open drainage = recirculation = feeling worse.
- Binders (activated charcoal, bentonite clay, chlorella, modified citrus pectin) must be used during any die-off or detox to prevent reabsorption. Take away from food and supplements.
- Herxheimer reactions (die-off): fatigue, headache, skin breakouts, brain fog, joint pain. This is expected. Manage with binders, extra hydration (3L/day), Epsom salt baths, rest. Never mistake Herxheimer for protocol failure.

3. PARASITE & PATHOGEN PROTOCOLS
- Antiparasitic trinity: wormwood (kills adults) + black walnut hull (kills larvae) + clove (kills eggs). All three required simultaneously.
- Moon-phase timing: parasites reproduce around the full moon. Intensify protocols 3 days before and 3 days after the full moon.
- Biofilm disruption precedes antiparasitic treatment: serrapeptase, nattokinase, or NAC 600mg on empty stomach breaks biofilm shields.
- Candida protocol sequence: antifungal phase (caprylic acid, oregano oil, berberine) → binder phase → microbiome restoration (S. boulardii first, then Lactobacillus/Bifidobacterium).
- SIBO: elemental diet or herbal antibiotics (rifaximin equivalent: berberine + oregano oil + allicin). Address root cause: low stomach acid, motility issues, structural problems.

4. GUT-BRAIN-IMMUNE AXIS
- 70% of the immune system lives in the gut-associated lymphoid tissue (GALT).
- 90% of serotonin is produced in the gut. Gut dysbiosis = depression, anxiety, brain fog.
- Leaky gut (intestinal permeability): tight junction proteins (claudin, occludin, zonulin) break down from gluten, NSAIDs, alcohol, stress, antibiotics. Repair with L-glutamine 5g/day, zinc carnosine 75mg, collagen, bone broth.
- The 5R protocol: Remove (pathogens, allergens, irritants) → Replace (enzymes, HCl) → Reinoculate (probiotics, prebiotics) → Repair (gut lining) → Rebalance (lifestyle, stress, sleep).

5. PLANT-BASED MEAT SUBSTITUTES
You are an expert in making plant foods satisfy meat cravings through texture and flavor science:
- Jackfruit: fibrous texture = pulled pork. High heat + caramelization is essential.
- Seitan (vital wheat gluten): 25g protein/100g. Closest to chicken/beef texture. Simmer, don't boil.
- Tempeh: fermented, 19g protein. Steam first, marinate deeply, sear for crust.
- Walnuts pulsed in food processor = ground beef texture. Pair with lentils for complete protein.
- Banana blossom + nori + kelp = fish texture and flavor.
- Maillard reaction (280°F+) creates the same flavor compounds in plants as in seared meat.
- Umami layering: tamari + miso + nutritional yeast + tomato paste = meat-like depth.
- Liquid smoke contains the same phenolic compounds as actual wood smoking.

6. ADAPTIVE REASONING
You do NOT give rigid, one-size-fits-all responses. You reason adaptively:
- If someone says they're tired: you ask about sleep, iron, thyroid, adrenals, B12, and mitochondrial function — not just "sleep more."
- If someone has a symptom: you trace it to root causes (gut, liver, hormones, nervous system, nutrient deficiency, toxin load, emotional stress).
- If someone is on medication: you check herb-drug interactions before recommending anything.
- If someone is overwhelmed: you simplify to 1-3 actionable steps, not a 20-point protocol.
- You build on previous conversation turns — you remember what was said and connect the dots.
- You ask clarifying questions when needed: "How long has this been happening?" "What have you already tried?" "Are you under significant stress?"

7. FINANCIAL WELLNESS
You understand that financial stress is a root cause of physical illness (cortisol, inflammation, sleep disruption). You help with:
- Mindset shifts: scarcity vs abundance thinking, money as energy
- Practical budgeting: envelope method, zero-based budgeting, automating savings
- Investing basics: index funds, dollar-cost averaging, compound interest
- Options trading: covered calls, protective puts, the wheel strategy — explained simply
- Income diversification: side income, skills monetization, passive income streams
- The health-wealth connection: investing in your health NOW reduces healthcare costs later

8. ASTROLOGY & COSMIC WELLNESS
- Birth chart interpretation: Sun (identity), Moon (emotions/needs), Rising (how others see you), Venus (love/values), Mars (drive/anger), Saturn (lessons/discipline)
- Transits: how current planetary movements affect your chart
- Wellness timing: Mercury retrograde (review, don't launch), Full Moon (release, complete), New Moon (set intentions, begin)
- Elemental balance: Fire (action), Earth (grounding), Air (communication), Water (emotion)

═══════════════════════════════════════════
COMMUNICATION STYLE
═══════════════════════════════════════════

- Speak like a knowledgeable friend, not a textbook. Warm, direct, never condescending.
- Match the user's energy: if they're casual, be casual. If they want depth, go deep.
- Lead with the most important insight, then support it.
- Use analogies to make complex concepts accessible.
- When giving protocols, number the steps clearly.
- Always end with an invitation to go deeper: "Want me to build out a full protocol for this?" or "Should I explain the mechanism behind that?"
- Never say "I'm just an AI" — you are Nexus, a wellness intelligence. Own it.
- If you don't know something, say so honestly and suggest where to find the answer.

You remember everything said in this conversation and build on it. You are not a search engine — you are a thinking partner."""


class NexusService:
    """
    Client for the Nexus AI model.

    Every chat message is routed through the ConversationEngine which
    enriches it with resolved context, history, tone, and domain before
    sending to the LLM.
    """

    def __init__(self) -> None:
        # Primary: Groq (fast, free) — used for all chat
        self._groq = _make_client(settings.groq_api_base_url, settings.groq_api_key) if settings.groq_api_key else None
        # Secondary: OpenAI — used for voice STT/TTS and as Groq fallback
        self._openai = _make_client(settings.nexus_api_base_url, settings.nexus_api_key) if settings.nexus_api_key else None

    async def _call(
        self,
        client: httpx.AsyncClient,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        response = await client.post("/chat/completions", json=payload)
        if response.status_code == 429:
            raise RuntimeError("rate_limited")
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def complete(
        self,
        user_message: str,
        system_context: str | None = None,
        history: list[dict[str, str]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        prefer_openai: bool = False,
    ) -> str:
        """Route to Groq first (fast/free), fall back to OpenAI, then local."""
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_context or SYSTEM_PROMPT}
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        # Try Groq first unless caller explicitly wants OpenAI (e.g. complex reasoning)
        if self._groq and not prefer_openai:
            try:
                return await self._call(self._groq, settings.groq_model, messages, temperature, max_tokens)
            except Exception:
                pass  # fall through to OpenAI

        # Try OpenAI
        if self._openai:
            try:
                return await self._call(self._openai, settings.nexus_model, messages, temperature, max_tokens)
            except Exception:
                pass

        # Both failed — local fallback
        return _local_fallback(user_message, system_context)

    async def chat(
        self,
        user_id: str,
        raw_message: str,
        user_profile: dict[str, Any] | None = None,
        temperature: float = 0.7,
        db: Any | None = None,
    ) -> dict[str, Any]:
        """
        Full conversation-aware chat with Nexus.

        Pipeline:
        1. Conversation engine  — resolve references, detect domain/intent/tone
        2. RAG retrieval        — inject semantically relevant past memories
        3. Persistent session   — load DB session context + summary
        4. Learning context     — adapt to user's skill level and preferences
        5. Reasoning context    — structured guidance for complex queries
        6. LLM call             — full context-aware completion
        7. Response polishing   — match user's tone
        8. Persist              — save turns to DB, update vector memory + learner
        """
        from app.services.conversation import conversation_engine
        from app.services.learning import learning_service
        from app.services.reasoning import reasoning_service
        from app.services.rag import rag_service
        from app.services.session_store import session_store
        from app.nexus_core.nutrition_expertise import nutrition_expertise

        # 1. Conversation processing — resolve references, detect domain/intent/tone
        processed = conversation_engine.process_input(user_id, raw_message)

        # 2. Build base system prompt with user profile
        profile_note = _format_profile(user_profile or {})
        base_system = SYSTEM_PROMPT
        if profile_note:
            base_system += f"\n\nUser profile: {profile_note}"

        # 3. RAG — retrieve semantically relevant past exchanges and facts
        rag_ctx = rag_service.retrieve_context(
            user_id=user_id,
            query=processed.resolved_message,
            domain=processed.domain,
        )
        if rag_ctx:
            base_system += f"\n\n{rag_ctx}"

        # 4. Persistent session context — compressed summary of earlier turns
        db_session = None
        db_session_id: str | None = None
        if db is not None:
            try:
                db_session = await session_store.get_or_create(db, user_id)
                db_session_id = str(db_session.id)
                session_ctx = session_store.build_context_with_summary(db_session)
                if session_ctx:
                    base_system += f"\n\n{session_ctx}"
            except Exception:
                pass  # DB errors must not break chat

        # 5. NutritionExpertise — inject domain knowledge for nutrition/detox/parasite queries
        _nutrition_domains = {"nutrition", "detox", "parasite", "microbiome", "gut-health"}
        if processed.domain in _nutrition_domains or any(
            kw in processed.resolved_message.lower()
            for kw in ("parasite", "candida", "sibo", "leaky gut", "detox", "herb",
                       "supplement", "gut", "microbiome", "cleanse", "protocol")
        ):
            nutrition_ctx = nutrition_expertise.get_domain_context(
                processed.resolved_message, user_profile or {}
            )
            if nutrition_ctx:
                base_system += f"\n\n[Nutrition expertise]\n{nutrition_ctx}"

            # Nutrition-specific reasoning context (includes user conditions + medications)
            nutrition_reasoning = reasoning_service.build_nutrition_reasoning_context(
                processed.resolved_message, user_profile or {}
            )
            if nutrition_reasoning:
                base_system += f"\n\n{nutrition_reasoning}"

        # 6. Inject learning context — what this user knows and prefers
        learning_ctx = learning_service.build_learning_context(user_id, processed.domain)
        if learning_ctx:
            base_system += f"\n\nLearning context: {learning_ctx}"

        # 7. Inject reasoning context for complex multi-step queries
        reasoning_ctx = reasoning_service.build_reasoning_context(processed.resolved_message)
        if reasoning_ctx:
            base_system += f"\n\nReasoning guidance: {reasoning_ctx}"

        # 8. Build full context-aware system prompt
        system_prompt = processed.build_system_prompt(base_system)

        # 9. LLM call with full conversation history
        try:
            raw_response = await self.complete(
                user_message=processed.resolved_message,
                system_context=system_prompt,
                history=processed.history[:-1],
                temperature=temperature,
            )
        except Exception:
            raw_response = _local_fallback(processed.resolved_message, system_prompt)

        # 9. Polish response to match user's tone
        polished = conversation_engine.polish_response(user_id, raw_response, raw_message)

        # 10. Record in in-memory session and update learner
        conversation_engine.record_response(user_id, polished)
        learning_service.record_interaction(
            user_id=user_id,
            user_input=raw_message,
            ai_response=polished,
            domain=processed.domain,
            intent=processed.intent,
        )

        # 11. Persist turns to DB session (non-blocking on error)
        if db is not None and db_session is not None:
            try:
                await session_store.add_turn(
                    db, db_session, "user", raw_message,
                    domain=processed.domain, intent=processed.intent,
                )
                await session_store.add_turn(
                    db, db_session, "assistant", polished,
                    domain=processed.domain,
                )
            except Exception:
                pass

        # 12. Persist turn + extract knowledge into vector memory (non-blocking)
        try:
            rag_service.store_turn(
                user_id=user_id,
                user_message=raw_message,
                ai_response=polished,
                domain=processed.domain,
                intent=processed.intent,
            )
            rag_service.extract_and_store_knowledge(
                user_id=user_id,
                user_message=raw_message,
                ai_response=polished,
                domain=processed.domain,
            )
        except Exception:
            pass  # vector store errors must never break the chat response

        return {
            "response": polished,
            "domain": processed.domain,
            "intent": processed.intent,
            "discourse_type": processed.discourse_type,
            "needs_clarification": processed.needs_clarification,
            "suggestions": processed.suggestions,
            "context": processed.to_dict(),
            "session_id": db_session_id,
            "engine": "nexus-conversation-v1.5",
        }

    async def personalized_recommendation(
        self,
        module: str,
        user_profile: dict[str, Any],
        context: dict[str, Any],
        user_message: str | None = None,
    ) -> dict[str, Any]:
        """Generate a structured wellness recommendation for a given module."""
        profile_summary = _format_profile(user_profile)
        prompt = _build_module_prompt(module, profile_summary, context, user_message)
        try:
            raw = await self.complete(prompt, temperature=0.6)
        except Exception:
            raw = _local_fallback(prompt, None)
        return {
            "module": module,
            "recommendation": raw,
            "action_items": _extract_action_items(raw),
            "references": [],
            "confidence": 0.85,
        }

    async def close(self) -> None:
        if self._groq:
            await self._groq.aclose()
        if self._openai:
            await self._openai.aclose()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_profile(profile: dict[str, Any]) -> str:
    parts = []
    if profile.get("date_of_birth"):
        parts.append(f"DOB: {profile['date_of_birth']}")
    if profile.get("sun_sign"):
        parts.append(f"Sun: {profile['sun_sign']}, Moon: {profile.get('moon_sign', 'unknown')}, Rising: {profile.get('rising_sign', 'unknown')}")
    if profile.get("health_goals"):
        parts.append(f"Goals: {', '.join(profile['health_goals'])}")
    if profile.get("dietary_preferences"):
        parts.append(f"Diet: {', '.join(profile['dietary_preferences'])}")
    if profile.get("conditions"):
        parts.append(f"Conditions: {', '.join(profile['conditions'])}")
    return " | ".join(parts) if parts else "No profile data available"


def _build_module_prompt(
    module: str,
    profile: str,
    context: dict[str, Any],
    user_message: str | None,
) -> str:
    base = f"User profile: {profile}\n\n"

    prompts = {
        "nutrition": (
            base
            + "Provide a food-as-medicine recommendation. Include specific foods, their healing properties, "
            "preparation methods, and a sample meal idea. Context: " + str(context)
        ),
        "meditation": (
            base
            + "Recommend a personalized meditation practice. Include technique, duration, timing, "
            "and the specific benefit for this user. Context: " + str(context)
        ),
        "detox": (
            base
            + "Suggest a detox protocol phase. Include what to eat, what to avoid, supportive practices, "
            "and what symptoms to expect. Context: " + str(context)
        ),
        "astrology": (
            base
            + "Provide a wellness-focused astrological insight. Connect current planetary transits to "
            "health, energy, and spiritual growth. Context: " + str(context)
        ),
        "general": base + (user_message or "Provide a holistic wellness check-in."),
    }

    prompt = prompts.get(module, prompts["general"])
    if user_message and module != "general":
        prompt += f"\n\nUser question: {user_message}"
    return prompt


def _extract_action_items(text: str) -> list[str]:
    """Pull bullet-point action items from Nexus response text."""
    lines = text.split("\n")
    items = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("- ", "• ", "* ", "→ ")):
            items.append(stripped[2:].strip())
        elif len(stripped) > 3 and stripped[0].isdigit() and stripped[1] in ".):":
            items.append(stripped[2:].strip())
    return items[:8]   # cap at 8 action items


def _local_fallback(user_message: str, system_context: str | None) -> str:
    """Return a structured local response when no Nexus API key is configured."""
    msg_lower = user_message.lower()
    if "nutrition" in msg_lower or "food" in msg_lower or "eat" in msg_lower:
        return (
            "Focus on whole, unprocessed foods. Prioritize leafy greens, healthy fats "
            "(avocado, olive oil, wild fish), and anti-inflammatory spices like turmeric and ginger. "
            "Eliminate refined sugar, seed oils, and ultra-processed foods. "
            "Eat in alignment with your circadian rhythm — largest meal midday."
        )
    if "meditation" in msg_lower or "breath" in msg_lower or "mindful" in msg_lower:
        return (
            "Begin with 10 minutes of box breathing (4-4-4-4) each morning before checking your phone. "
            "This activates the parasympathetic nervous system and sets a calm tone for the day. "
            "Progress to a 20-minute body scan before sleep for deep restoration."
        )
    if "detox" in msg_lower or "cleanse" in msg_lower:
        return (
            "Start your detox with a 3-day elimination phase: remove caffeine, alcohol, gluten, and dairy. "
            "Support your liver with beets, dandelion tea, and milk thistle. "
            "Hydrate with 3L of filtered water daily and incorporate dry brushing each morning."
        )
    if "astrology" in msg_lower or "chart" in msg_lower or "sign" in msg_lower or "planet" in msg_lower:
        return (
            "Your astrological blueprint reveals your soul's evolutionary path. "
            "Your Sun sign shows your core identity, your Moon sign your emotional needs, "
            "and your Rising sign how you engage with the world. "
            "Work with your chart's strengths and consciously evolve beyond its challenges."
        )
    return (
        "True wellness integrates mind, body, and spirit. Begin with your foundation: "
        "quality sleep (7-9 hours), whole foods, daily movement, and 10 minutes of stillness. "
        "From this base, layer in targeted practices for your specific goals. "
        "Set your NEXUS_API_KEY to unlock fully personalized AI-driven recommendations."
    )


# Singleton
nexus_service = NexusService()

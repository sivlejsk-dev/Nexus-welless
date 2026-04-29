"""Nexus AI service — wraps the Nexus model via OpenAI-compatible API spec."""

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


SYSTEM_PROMPT = """You are Nexus, an advanced wellness intelligence engine. You provide deeply 
personalized guidance across nutrition science, meditation, detox protocols, and astrology. 
Your recommendations are grounded in evidence-based wellness practices, integrative medicine, 
and holistic health principles. Always tailor advice to the user's unique profile, health goals, 
and astrological blueprint. Be warm, precise, and actionable."""


class NexusService:
    """Client for the Nexus AI model."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.nexus_api_base_url,
            headers={
                "Authorization": f"Bearer {settings.nexus_api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def complete(
        self,
        user_message: str,
        system_context: str | None = None,
        history: list[dict[str, str]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Send a completion request to Nexus and return the response text.

        Returns a local placeholder when NEXUS_API_KEY is not configured,
        so all endpoints remain functional without an external API key.
        """
        if not settings.nexus_api_key:
            return _local_fallback(user_message, system_context)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_context or SYSTEM_PROMPT}
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": settings.nexus_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

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

        raw = await self.complete(prompt, temperature=0.6)

        return {
            "module": module,
            "recommendation": raw,
            "action_items": _extract_action_items(raw),
            "references": [],
            "confidence": 0.85,
        }

    async def close(self) -> None:
        await self._client.aclose()


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

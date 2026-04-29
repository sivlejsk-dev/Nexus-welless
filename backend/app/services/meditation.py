"""Meditation guide library and session management."""

from typing import Any

# ── Guide library (seed data — expandable via DB or CMS) ─────────────────────
MEDITATION_GUIDES: list[dict[str, Any]] = [
    {
        "id": "breath-478",
        "title": "4-7-8 Breathing",
        "description": "Activates the parasympathetic nervous system. Inhale 4s, hold 7s, exhale 8s.",
        "duration_minutes": 10,
        "category": "breathwork",
        "level": "beginner",
        "tags": ["anxiety", "sleep", "stress-relief"],
        "audio_url": None,
        "thumbnail_url": "/images/meditation/breath-478.jpg",
        "script": [
            "Find a comfortable seated position and close your eyes.",
            "Place the tip of your tongue against the ridge behind your upper front teeth.",
            "Exhale completely through your mouth, making a whoosh sound.",
            "Close your mouth and inhale quietly through your nose for 4 counts.",
            "Hold your breath for 7 counts.",
            "Exhale completely through your mouth for 8 counts.",
            "Repeat this cycle 4 times.",
        ],
    },
    {
        "id": "body-scan-sleep",
        "title": "Deep Sleep Body Scan",
        "description": "Progressive relaxation from crown to feet for deep, restorative sleep.",
        "duration_minutes": 20,
        "category": "body-scan",
        "level": "beginner",
        "tags": ["sleep", "relaxation", "stress-relief"],
        "audio_url": None,
        "thumbnail_url": "/images/meditation/body-scan.jpg",
        "script": [
            "Lie down in a comfortable position. Close your eyes.",
            "Take three deep breaths, releasing tension with each exhale.",
            "Bring awareness to the top of your head. Notice any sensations without judgment.",
            "Slowly move your attention down through your face, jaw, neck, and shoulders.",
            "Continue scanning down through your chest, abdomen, hips, legs, and feet.",
            "With each area, consciously release any held tension.",
            "Rest in full body awareness for several minutes before drifting to sleep.",
        ],
    },
    {
        "id": "morning-intention",
        "title": "Morning Intention Setting",
        "description": "Start your day with clarity and purpose through visualization and affirmation.",
        "duration_minutes": 15,
        "category": "visualization",
        "level": "beginner",
        "tags": ["morning", "focus", "manifestation", "energy"],
        "audio_url": None,
        "thumbnail_url": "/images/meditation/morning.jpg",
        "script": [
            "Sit upright, spine tall. Take five deep, energizing breaths.",
            "Visualize your ideal day unfolding — see it clearly, feel it fully.",
            "Set one clear intention: What quality do you want to embody today?",
            "Repeat your intention three times silently.",
            "Open your eyes and carry this energy into your day.",
        ],
    },
    {
        "id": "loving-kindness",
        "title": "Loving-Kindness (Metta)",
        "description": "Cultivate compassion for self and others through traditional Metta practice.",
        "duration_minutes": 20,
        "category": "mantra",
        "level": "intermediate",
        "tags": ["compassion", "emotional-healing", "relationships", "heart-chakra"],
        "audio_url": None,
        "thumbnail_url": "/images/meditation/metta.jpg",
        "script": [
            "Sit comfortably. Bring your attention to your heart center.",
            "Begin with yourself: 'May I be happy. May I be healthy. May I be at peace.'",
            "Expand to someone you love. Send them the same wishes.",
            "Expand to a neutral person, then to someone difficult.",
            "Finally, expand to all beings everywhere.",
            "Rest in the warmth of open-hearted awareness.",
        ],
    },
    {
        "id": "chakra-activation",
        "title": "7 Chakra Activation",
        "description": "Balance and energize all seven energy centers through visualization and sound.",
        "duration_minutes": 30,
        "category": "visualization",
        "level": "intermediate",
        "tags": ["chakras", "energy", "spiritual", "healing"],
        "audio_url": None,
        "thumbnail_url": "/images/meditation/chakra.jpg",
        "script": [
            "Sit in lotus or easy pose. Ground your energy into the earth.",
            "Root Chakra (red): Feel stability and safety at the base of your spine.",
            "Sacral Chakra (orange): Awaken creativity and flow in your lower abdomen.",
            "Solar Plexus (yellow): Ignite your personal power and confidence.",
            "Heart Chakra (green): Open to love, compassion, and connection.",
            "Throat Chakra (blue): Speak your truth with clarity and grace.",
            "Third Eye (indigo): Trust your intuition and inner wisdom.",
            "Crown Chakra (violet/white): Connect to universal consciousness.",
            "Rest in integrated wholeness for several minutes.",
        ],
    },
    {
        "id": "detox-breath",
        "title": "Detox Breathwork (Kapalabhati)",
        "description": "Cleansing breath technique that stimulates digestion and expels toxins.",
        "duration_minutes": 15,
        "category": "breathwork",
        "level": "intermediate",
        "tags": ["detox", "energy", "digestion", "cleansing"],
        "audio_url": None,
        "thumbnail_url": "/images/meditation/detox-breath.jpg",
        "script": [
            "Sit tall. Take a deep inhale to prepare.",
            "Begin short, sharp exhales through the nose — one per second.",
            "The inhale is passive; focus on the forceful exhale.",
            "Complete 30 pumps, then take a full inhale and hold for 10 seconds.",
            "Exhale slowly. This completes one round.",
            "Repeat for 3-5 rounds. Rest and observe the energy shift.",
        ],
    },
    {
        "id": "sleep-yoga-nidra",
        "title": "Yoga Nidra (Yogic Sleep)",
        "description": "45-minute guided journey into the hypnagogic state — 1 hour of deep rest.",
        "duration_minutes": 45,
        "category": "body-scan",
        "level": "advanced",
        "tags": ["sleep", "deep-rest", "subconscious", "healing"],
        "audio_url": None,
        "thumbnail_url": "/images/meditation/yoga-nidra.jpg",
        "script": [
            "Lie in Savasana. You will remain awake while your body sleeps.",
            "Set your Sankalpa — a short, positive resolve.",
            "Rotate awareness through 61 body points in sequence.",
            "Experience pairs of opposites: heat/cold, heaviness/lightness.",
            "Visualize rapid images as they arise without attachment.",
            "Return to your Sankalpa. Slowly return to waking awareness.",
        ],
    },
]

CATEGORY_MAP: dict[str, list[str]] = {
    "breathwork": ["breath-478", "detox-breath"],
    "body-scan": ["body-scan-sleep", "sleep-yoga-nidra"],
    "visualization": ["morning-intention", "chakra-activation"],
    "mantra": ["loving-kindness"],
    "sleep": ["body-scan-sleep", "sleep-yoga-nidra"],
}


class MeditationService:
    def get_all_guides(self) -> list[dict[str, Any]]:
        return MEDITATION_GUIDES

    def get_guide(self, guide_id: str) -> dict[str, Any] | None:
        return next((g for g in MEDITATION_GUIDES if g["id"] == guide_id), None)

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        ids = CATEGORY_MAP.get(category, [])
        return [g for g in MEDITATION_GUIDES if g["id"] in ids or g["category"] == category]

    def get_by_tag(self, tag: str) -> list[dict[str, Any]]:
        return [g for g in MEDITATION_GUIDES if tag.lower() in [t.lower() for t in g["tags"]]]

    def recommend_for_profile(self, profile: dict[str, Any]) -> list[dict[str, Any]]:
        """Rule-based recommendation enriched by Nexus guide_engine mental-state mapping."""
        goals = profile.get("health_goals", [])
        mental_state = profile.get("mental_state", "neutral")
        recommended_ids: set[str] = set()

        # Use Nexus guide_engine to map mental state → meditation style
        try:
            from app.nexus_core.guide_engine import select_meditation_style
            nexus_style = select_meditation_style(mental_state)
            style_to_ids = {
                "mindfulness": {"breath-478", "morning-intention"},
                "mantra": {"loving-kindness"},
                "body_scan": {"body-scan-sleep"},
            }
            recommended_ids.update(style_to_ids.get(nexus_style, set()))
        except Exception:
            pass

        for goal in goals:
            goal_lower = goal.lower()
            if "sleep" in goal_lower:
                recommended_ids.update(["body-scan-sleep", "sleep-yoga-nidra"])
            if "stress" in goal_lower or "anxiety" in goal_lower:
                recommended_ids.update(["breath-478", "loving-kindness"])
            if "energy" in goal_lower or "morning" in goal_lower:
                recommended_ids.add("morning-intention")
            if "detox" in goal_lower or "cleanse" in goal_lower:
                recommended_ids.add("detox-breath")
            if "spiritual" in goal_lower or "chakra" in goal_lower:
                recommended_ids.add("chakra-activation")

        if not recommended_ids:
            recommended_ids = {"breath-478", "morning-intention", "loving-kindness"}

        return [g for g in MEDITATION_GUIDES if g["id"] in recommended_ids]

    def get_nexus_daily_guide(self, mental_state: str, goal: str,
                               preferred_style: str | None = None) -> dict[str, Any]:
        """Generate a full Nexus daily guide (meditation + breathing + meals)."""
        try:
            from app.nexus_core.guide_engine import generate_guide
            return generate_guide(mental_state=mental_state, goal=goal,
                                  preferred_meditation_style=preferred_style)
        except Exception as exc:
            return {"error": str(exc), "meditation_style": "mindfulness"}


meditation_service = MeditationService()

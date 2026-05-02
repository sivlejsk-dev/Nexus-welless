"""guide_engine.py – Decision logic for generating personalized daily guides.

Given a user's mental state and daily goal this module selects:
  • A meditation style  (mindfulness, mantra, or body scan)
  • A breathing exercise linked to the selected style
  • Meal suggestions    aligned with the user's objective

All logic is pure and stateless – call ``generate_guide`` with the relevant
profile values.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ── Meditation style mapping ──────────────────────────────────────────────────

_MENTAL_STATE_TO_STYLE: Dict[str, str] = {
    "stressed": "mindfulness",
    "anxious": "mindfulness",
    "overwhelmed": "mindfulness",
    "tired": "mantra",
    "low_energy": "mantra",
    "sluggish": "mantra",
    "neutral": "body_scan",
    "balanced": "body_scan",
    "calm": "body_scan",
    "focused": "mindfulness",
    "energized": "mindfulness",
    "motivated": "mindfulness",
}

_DEFAULT_STYLE = "mindfulness"

_STYLE_INFO: Dict[str, Dict[str, str]] = {
    "mindfulness": {
        "description": (
            "Mindfulness meditation cultivates non-judgmental awareness of the present "
            "moment. Sit comfortably, focus on your breath, and gently return attention "
            "whenever the mind wanders. Ideal for reducing stress and building clarity."
        ),
    },
    "mantra": {
        "description": (
            "Mantra meditation uses a repeated word or phrase (e.g. 'so-hum' or "
            "'peace') to anchor the mind and restore energy. Silently repeat your "
            "mantra for 15-20 minutes to uplift mood and concentration."
        ),
    },
    "body_scan": {
        "description": (
            "Body scan meditation brings gentle attention to each part of the body in "
            "turn, releasing tension and deepening body awareness. Lie down, close your "
            "eyes, and slowly scan from head to toe for 20-30 minutes."
        ),
    },
}

# ── Breathing exercise mapping ────────────────────────────────────────────────

_STYLE_TO_BREATHING: Dict[str, Dict[str, str]] = {
    "mindfulness": {
        "exercise": "box_breathing",
        "display_name": "Box Breathing",
        "instructions": (
            "Inhale slowly for 4 counts -> hold for 4 counts -> exhale for 4 counts -> "
            "hold for 4 counts. Repeat 4-6 cycles. This technique activates the "
            "parasympathetic nervous system, reducing anxiety and improving focus."
        ),
    },
    "mantra": {
        "exercise": "alternate_nostril_breathing",
        "display_name": "Alternate Nostril Breathing (Nadi Shodhana)",
        "instructions": (
            "Using your right hand, close the right nostril with your thumb and inhale "
            "through the left for 4 counts. Close both nostrils and hold for 2 counts. "
            "Release the right nostril and exhale for 4 counts. Reverse sides and "
            "repeat for 5-10 cycles. Balances energy and clears the mind."
        ),
    },
    "body_scan": {
        "exercise": "4_7_8_breathing",
        "display_name": "4-7-8 Breathing",
        "instructions": (
            "Inhale quietly through the nose for 4 counts -> hold the breath for 7 "
            "counts -> exhale completely through the mouth for 8 counts. Repeat 4 "
            "cycles. This slows the heart rate and promotes deep relaxation."
        ),
    },
}

# ── Meal suggestion mapping ───────────────────────────────────────────────────

_GOAL_TO_MEALS: Dict[str, List[str]] = {
    "relaxation": [
        "Warm chamomile or lavender tea",
        "Oatmeal with honey and banana",
        "Light vegetable soup with whole-grain bread",
        "Warm almond milk with a pinch of turmeric",
        "Steamed fish with rice and green vegetables",
    ],
    "focus": [
        "Blueberry and walnut oatmeal",
        "Avocado toast on whole-grain bread",
        "Green tea with lemon",
        "Dark chocolate (70%+) with mixed nuts",
        "Grilled salmon with leafy greens and quinoa",
    ],
    "energy": [
        "Banana-spinach smoothie with almond butter",
        "Greek yoghurt with granola and berries",
        "Brown rice with grilled chicken and steamed broccoli",
        "Handful of almonds and dried apricots",
        "Whole-grain pasta with tomato sauce and lentils",
    ],
    "sleep": [
        "Warm milk with honey",
        "Tart cherry juice",
        "Kiwi fruit (2-3 pieces)",
        "Small bowl of oatmeal with sliced almonds",
        "Turkey and cheese sandwich on whole-grain bread",
    ],
    "balance": [
        "Mixed-grain porridge with seeds and fresh fruit",
        "Colourful salad with chickpeas, cucumber, and olive oil",
        "Stir-fried tofu with mixed vegetables and brown rice",
        "Fresh seasonal fruit with natural yogurt",
        "Lentil soup with a side of whole-grain crackers",
    ],
}

_DEFAULT_MEALS = _GOAL_TO_MEALS["balance"]

# ── Public constants ──────────────────────────────────────────────────────────

VALID_MENTAL_STATES: List[str] = sorted(_MENTAL_STATE_TO_STYLE.keys())
VALID_GOALS: List[str] = sorted(_GOAL_TO_MEALS.keys())
VALID_MEDITATION_STYLES: List[str] = sorted(_STYLE_INFO.keys())

# ── Public helper functions ───────────────────────────────────────────────────


def select_meditation_style(mental_state: str) -> str:
    """Return a meditation style key for *mental_state*.

    Falls back to ``_DEFAULT_STYLE`` when the state is unrecognised.
    """
    return _MENTAL_STATE_TO_STYLE.get(mental_state.lower().strip(), _DEFAULT_STYLE)


def get_breathing_exercise(meditation_style: str) -> Dict[str, str]:
    """Return a copy of the breathing exercise dict for *meditation_style*."""
    return dict(
        _STYLE_TO_BREATHING.get(
            meditation_style.lower().strip(),
            _STYLE_TO_BREATHING[_DEFAULT_STYLE],
        )
    )


def get_meal_suggestions(goal: str) -> List[str]:
    """Return a list of meal suggestions for *goal*."""
    return list(_GOAL_TO_MEALS.get(goal.lower().strip(), _DEFAULT_MEALS))


# ── Core guide generator ──────────────────────────────────────────────────────


def generate_guide(
    mental_state: str,
    goal: str,
    *,
    preferred_meditation_style: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a personalized daily guide.

    Parameters
    ----------
    mental_state:
        How the user is feeling right now (e.g. ``"stressed"``, ``"tired"``).
    goal:
        The user's primary objective for the day (e.g. ``"relaxation"``,
        ``"focus"``).
    preferred_meditation_style:
        When provided and valid, overrides the auto-selected meditation style.

    Returns
    -------
    dict with keys:
        ``meditation_style``, ``meditation_description``,
        ``breathing_exercise``, ``breathing_display_name``,
        ``breathing_instructions``, ``meal_suggestions``, ``generated_at``.
    """
    # Determine meditation style – honour explicit preference when valid.
    if (
        preferred_meditation_style
        and preferred_meditation_style.lower().strip() in _STYLE_INFO
    ):
        style = preferred_meditation_style.lower().strip()
    else:
        style = select_meditation_style(mental_state)

    style_info = _STYLE_INFO[style]
    breathing = get_breathing_exercise(style)
    meals = get_meal_suggestions(goal)

    return {
        "meditation_style": style,
        "meditation_description": style_info["description"],
        "breathing_exercise": breathing["exercise"],
        "breathing_display_name": breathing["display_name"],
        "breathing_instructions": breathing["instructions"],
        "meal_suggestions": meals,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

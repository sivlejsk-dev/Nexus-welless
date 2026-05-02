"""
Astrology service — backed by the real Nexus/Celestal-Eye engine.

Uses BirthChartGenerator, DailyAstrologer, and AstrologyInterpreter
from app.nexus_core (the Celestal-Eye source modules).
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any

log = logging.getLogger(__name__)

# ── Nexus core imports ────────────────────────────────────────────────────────
_NEXUS_AVAILABLE = False
_BirthChartGenerator = None
_DailyAstrologer = None
_AstrologyInterpreter = None

try:
    from app.nexus_core.birth_chart import BirthChartGenerator as _BCG
    from app.nexus_core.daily_tips import DailyAstrologer as _DA
    from app.nexus_core.interpretations import AstrologyInterpreter as _AI
    _BirthChartGenerator = _BCG
    _DailyAstrologer = _DA
    _AstrologyInterpreter = _AI
    _NEXUS_AVAILABLE = True
    log.info("Nexus astrology engine loaded successfully")
except Exception as exc:
    log.warning("Nexus astrology engine unavailable, using fallback: %s", exc)

ZODIAC_SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

SUN_SIGN_DATES: list[tuple[int, int, str]] = [
    (3,21,"Aries"),(4,20,"Taurus"),(5,21,"Gemini"),
    (6,21,"Cancer"),(7,23,"Leo"),(8,23,"Virgo"),
    (9,23,"Libra"),(10,23,"Scorpio"),(11,22,"Sagittarius"),
    (12,22,"Capricorn"),(1,20,"Aquarius"),(2,19,"Pisces"),
]

SIGN_WELLNESS: dict[str, dict[str, str]] = {
    "Aries":{"element":"Fire","modality":"Cardinal","body_area":"Head, brain, adrenals","healing_focus":"Cooling foods, stress management, iron-rich diet","meditation":"Dynamic movement meditation, martial arts mindfulness"},
    "Taurus":{"element":"Earth","modality":"Fixed","body_area":"Throat, neck, thyroid","healing_focus":"Grounding foods, iodine support, vocal exercises","meditation":"Nature immersion, sound healing, body scan"},
    "Gemini":{"element":"Air","modality":"Mutable","body_area":"Lungs, nervous system, hands","healing_focus":"Breathwork, adaptogens, omega-3s for neural health","meditation":"Pranayama, journaling meditation, bilateral stimulation"},
    "Cancer":{"element":"Water","modality":"Cardinal","body_area":"Stomach, breasts, lymphatic system","healing_focus":"Gut-healing foods, emotional processing, hydration","meditation":"Water visualization, womb healing, loving-kindness"},
    "Leo":{"element":"Fire","modality":"Fixed","body_area":"Heart, spine, circulation","healing_focus":"Heart-healthy fats, CoQ10, spinal alignment","meditation":"Heart-centered meditation, solar visualization"},
    "Virgo":{"element":"Earth","modality":"Mutable","body_area":"Digestive system, intestines, microbiome","healing_focus":"Fermented foods, digestive enzymes, fiber-rich diet","meditation":"Mindful eating, analytical breathwork, body awareness"},
    "Libra":{"element":"Air","modality":"Cardinal","body_area":"Kidneys, lower back, skin","healing_focus":"Kidney-supportive herbs, alkaline diet, skin nutrition","meditation":"Balance meditation, partner breathing, harmony visualization"},
    "Scorpio":{"element":"Water","modality":"Fixed","body_area":"Reproductive system, colon, detox organs","healing_focus":"Deep detox protocols, liver support, shadow work","meditation":"Transformational breathwork, death-rebirth visualization"},
    "Sagittarius":{"element":"Fire","modality":"Mutable","body_area":"Hips, thighs, liver, sciatic nerve","healing_focus":"Liver-cleansing foods, hip mobility, anti-inflammatory diet","meditation":"Walking meditation, expansive visualization, mantra"},
    "Capricorn":{"element":"Earth","modality":"Cardinal","body_area":"Bones, joints, skin, teeth","healing_focus":"Calcium, magnesium, collagen, joint-supportive foods","meditation":"Mountain meditation, grounding, ancestral healing"},
    "Aquarius":{"element":"Air","modality":"Fixed","body_area":"Ankles, calves, circulatory system","healing_focus":"Circulation support, antioxidants, electromagnetic detox","meditation":"Collective consciousness meditation, future-self visualization"},
    "Pisces":{"element":"Water","modality":"Mutable","body_area":"Feet, lymphatic system, immune system","healing_focus":"Immune-boosting foods, foot reflexology, boundary practices","meditation":"Ocean visualization, dream journaling, dissolution meditation"},
}

DAILY_THEMES = [
    "renewal and fresh starts","grounding and stability","communication and connection",
    "emotional depth and intuition","creativity and self-expression","service and refinement",
    "balance and relationships","transformation and release","expansion and wisdom",
    "discipline and achievement","innovation and community","surrender and spirituality",
]


class AstrologyService:
    def __init__(self) -> None:
        self._chart_gen = _BirthChartGenerator() if _NEXUS_AVAILABLE else None
        self._daily = _DailyAstrologer() if _NEXUS_AVAILABLE else None
        self._interp = _AstrologyInterpreter() if _NEXUS_AVAILABLE else None

    def get_sun_sign(self, dob: date) -> str:
        month, day = dob.month, dob.day
        for m, d, sign in SUN_SIGN_DATES:
            if (month == m and day >= d) or (month == m - 1 and day < d):
                return sign
        if month == 12 and day >= 22:
            return "Capricorn"
        return "Capricorn"

    def get_birth_chart(self, dob: date, birth_time: str, lat: float, lon: float, timezone_str: str) -> dict[str, Any]:
        if _NEXUS_AVAILABLE and self._chart_gen:
            return self._nexus_birth_chart(dob, birth_time, lat, lon)
        return self._fallback_birth_chart(dob)

    def _nexus_birth_chart(self, dob: date, birth_time: str, lat: float, lon: float) -> dict[str, Any]:
        try:
            hour, minute = map(int, birth_time.split(":"))
            birth_dt = datetime(dob.year, dob.month, dob.day, hour, minute, tzinfo=timezone.utc)
            chart = self._chart_gen.generate_chart(birth_date=birth_dt, latitude=lat, longitude=lon, location_name="")

            planets_out = []
            for planet, pos in chart.planets.items():
                planets_out.append({
                    "planet": planet.name.capitalize(),
                    "sign": pos.sign.name.capitalize(),
                    "degree": round(pos.degree, 2),
                    "house": pos.house,
                    "retrograde": pos.retrograde,
                    "dignity": pos.dignity,
                })

            aspects_out = [
                {"planet1": a.planet1.name.capitalize(), "planet2": a.planet2.name.capitalize(),
                 "aspect": a.aspect_type, "orb": round(a.orb, 2)}
                for a in chart.aspects
            ]

            sun_sign = chart.get_sun_sign()
            moon_sign = chart.get_moon_sign()
            rising_sign = chart.get_rising_sign()

            interpretation = ""
            if self._interp:
                try:
                    interpretation = self._interp.generate_full_interpretation(chart)
                except Exception as exc:
                    log.debug("Nexus interpretation failed: %s", exc)

            # Find sun/moon planet positions
            sun_pos = next((p for p in planets_out if p["planet"] == "Sun"), {"degree": 0.0, "house": 1})
            moon_pos = next((p for p in planets_out if p["planet"] == "Moon"), {"degree": 0.0, "house": 4})

            return {
                "sun": {"planet": "Sun", "sign": sun_sign.name.capitalize(), "degree": sun_pos["degree"], "house": sun_pos["house"], "retrograde": False},
                "moon": {"planet": "Moon", "sign": moon_sign.name.capitalize(), "degree": moon_pos["degree"], "house": moon_pos["house"], "retrograde": False},
                "rising": {"planet": "Ascendant", "sign": rising_sign.name.capitalize() if rising_sign else "Unknown", "degree": 0.0, "house": 1, "retrograde": False},
                "planets": planets_out,
                "houses": [],
                "aspects": aspects_out,
                "nexus_interpretation": interpretation[:2000] if interpretation else None,
                "engine": "nexus-celestal-eye",
            }
        except Exception as exc:
            log.error("Nexus birth chart failed, using fallback: %s", exc)
            return self._fallback_birth_chart(dob)

    def _fallback_birth_chart(self, dob: date) -> dict[str, Any]:
        sun_sign = self.get_sun_sign(dob)
        sign_idx = ZODIAC_SIGNS.index(sun_sign)
        moon_sign = ZODIAC_SIGNS[(sign_idx + 4) % 12]
        rising_sign = ZODIAC_SIGNS[(sign_idx + 8) % 12]
        return {
            "sun": {"planet": "Sun", "sign": sun_sign, "degree": 15.0, "house": 1, "retrograde": False},
            "moon": {"planet": "Moon", "sign": moon_sign, "degree": 22.5, "house": 4, "retrograde": False},
            "rising": {"planet": "Ascendant", "sign": rising_sign, "degree": 5.0, "house": 1, "retrograde": False},
            "planets": [
                {"planet": "Mercury", "sign": sun_sign, "degree": 8.0, "house": 1, "retrograde": False},
                {"planet": "Venus", "sign": ZODIAC_SIGNS[(sign_idx+2)%12], "degree": 19.0, "house": 3, "retrograde": False},
                {"planet": "Mars", "sign": ZODIAC_SIGNS[(sign_idx+6)%12], "degree": 11.0, "house": 7, "retrograde": False},
                {"planet": "Jupiter", "sign": ZODIAC_SIGNS[(sign_idx+3)%12], "degree": 27.0, "house": 4, "retrograde": False},
                {"planet": "Saturn", "sign": ZODIAC_SIGNS[(sign_idx+9)%12], "degree": 3.0, "house": 10, "retrograde": True},
            ],
            "houses": [{"house": i+1, "degree": (sign_idx*30+i*30)%360, "sign": ZODIAC_SIGNS[(sign_idx+i)%12]} for i in range(12)],
            "aspects": [
                {"planet1": "Sun", "planet2": "Moon", "aspect": "Trine", "orb": 2.5},
                {"planet1": "Sun", "planet2": "Jupiter", "aspect": "Sextile", "orb": 1.8},
            ],
            "engine": "fallback",
            "note": "Provide birth time and location for precise Nexus calculations.",
        }

    def get_daily_horoscope(self, sign: str, target_date: date | None = None) -> dict[str, Any]:
        if target_date is None:
            target_date = date.today()
        sign_idx = ZODIAC_SIGNS.index(sign) if sign in ZODIAC_SIGNS else 0
        day_seed = target_date.toordinal() + sign_idx
        theme = DAILY_THEMES[day_seed % len(DAILY_THEMES)]
        wellness = SIGN_WELLNESS.get(sign, {})

        # Map sign to a reliable birth date where the sun is in that sign
        _SIGN_SAMPLE_DATES = {
            "Aries": (3, 25), "Taurus": (4, 25), "Gemini": (5, 25),
            "Cancer": (6, 25), "Leo": (7, 25), "Virgo": (8, 25),
            "Libra": (9, 25), "Scorpio": (10, 25), "Sagittarius": (11, 25),
            "Capricorn": (12, 25), "Aquarius": (1, 25), "Pisces": (2, 25),
        }
        nexus_daily_text: str | None = None
        if _NEXUS_AVAILABLE and self._daily and self._chart_gen:
            try:
                month, day = _SIGN_SAMPLE_DATES.get(sign, (6, 21))
                sample_dt = datetime(2000, month, day, 12, 0, tzinfo=timezone.utc)
                chart = self._chart_gen.generate_chart(birth_date=sample_dt, latitude=0.0, longitude=0.0, location_name=sign)
                nexus_daily_text = self._daily.generate_daily_guidance(chart, target_date)
            except Exception as exc:
                log.debug("Nexus daily guidance failed: %s", exc)

        return {
            "sign": sign,
            "date": target_date.isoformat(),
            "general": f"Today carries the energy of {theme}. As a {sign}, your {wellness.get('element','elemental')} nature is activated — lean into your natural strengths while remaining open to unexpected insights.",
            "love": f"Venus highlights {theme} in your relationships. Authentic expression deepens bonds today.",
            "career": f"Your {wellness.get('modality','cardinal')} energy drives purposeful action. Focus on one meaningful task.",
            "health": f"Body focus: {wellness.get('body_area','whole body')}. {wellness.get('healing_focus','Nourish with whole foods and rest.')}",
            "meditation": wellness.get("meditation", "Mindful breathing for 10 minutes"),
            "lucky_number": (day_seed % 9) + 1,
            "lucky_color": ["Gold","Silver","Emerald","Crimson","Violet","Amber","Sapphire"][day_seed % 7],
            "nexus_daily_guidance": nexus_daily_text,
            "engine": "nexus-celestal-eye" if nexus_daily_text else "fallback",
        }

    def get_daily_guide(self, mental_state: str, goal: str, preferred_style: str | None = None) -> dict[str, Any]:
        try:
            from app.nexus_core.guide_engine import generate_guide
            return generate_guide(mental_state=mental_state, goal=goal, preferred_meditation_style=preferred_style)
        except Exception as exc:
            log.error("guide_engine failed: %s", exc)
            return {
                "meditation_style": "mindfulness",
                "meditation_description": "Focus on your breath for 10 minutes.",
                "breathing_exercise": "box_breathing",
                "breathing_display_name": "Box Breathing",
                "breathing_instructions": "Inhale 4s -> hold 4s -> exhale 4s -> hold 4s. Repeat.",
                "meal_suggestions": ["Warm herbal tea", "Oatmeal with berries", "Leafy green salad"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

    def get_sign_wellness_profile(self, sign: str) -> dict[str, Any]:
        return SIGN_WELLNESS.get(sign, {})


astrology_service = AstrologyService()

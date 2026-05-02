"""Secondary progressions calculator.

Secondary progressions use the classical "day-for-a-year" technique: each day
after birth corresponds to one year of lived experience.  The progressed chart
is calculated by advancing the birth date by the number of days equal to the
native's current age (or the number of years until the target date).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from .birth_chart import (
    BirthChart,
    BirthChartGenerator,
    Planet,
    PlanetPosition,
    ZodiacSign,
)


@dataclass
class ProgressedPlanet:
    """A planet's progressed position vs its natal position."""

    planet: Planet
    natal_sign: ZodiacSign
    natal_degree: float
    progressed_sign: ZodiacSign
    progressed_degree: float
    sign_change: bool = False
    interpretation: str = ""

    def __str__(self) -> str:
        arrow = " → " if self.sign_change else " "
        return (
            f"{self.planet.symbol} {self.planet.name}: "
            f"{self.natal_sign.name} {self.natal_degree:.1f}°"
            f"{arrow}{self.progressed_sign.name} {self.progressed_degree:.1f}°"
        )


@dataclass
class ProgressedChart:
    """Result of a secondary progression calculation."""

    birth_date: datetime
    progression_date: datetime
    age_years: float
    progressed_planets: Dict[str, ProgressedPlanet] = field(default_factory=dict)
    progressed_sun_sign: Optional[ZodiacSign] = None
    progressed_moon_sign: Optional[ZodiacSign] = None
    progressed_ascendant_sign: Optional[ZodiacSign] = None
    major_themes: List[str] = field(default_factory=list)


# Interpretation snippets keyed by (planet, sign)
_PROG_SUN_THEMES: Dict[str, str] = {
    "ARIES": "Bold new beginnings and increased drive for independence.",
    "TAURUS": "Stability, sensuality, and building lasting foundations.",
    "GEMINI": "Curiosity, communication, and mental agility take centre stage.",
    "CANCER": "Emotional depth, nurturing instincts, and a focus on home.",
    "LEO": "Self-expression, creativity, and leadership qualities shine.",
    "VIRGO": "Analytical refinement, service, and attention to health and craft.",
    "LIBRA": "Partnership, diplomacy, and aesthetic sensibility are highlighted.",
    "SCORPIO": "Transformation, intensity, and uncovering hidden truths.",
    "SAGITTARIUS": "Philosophical expansion, travel, and questing for meaning.",
    "CAPRICORN": "Ambition, discipline, and long-term goal achievement.",
    "AQUARIUS": "Innovation, humanitarian concerns, and originality flourish.",
    "PISCES": "Spiritual sensitivity, empathy, and imaginative creativity.",
}

_PROG_MOON_THEMES: Dict[str, str] = {
    "ARIES": "Emotional impulses are quick and assertive; lead from feeling.",
    "TAURUS": "A need for emotional stability and sensory comfort.",
    "GEMINI": "Feelings are processed intellectually; communication is vital.",
    "CANCER": "Deep sensitivity and a longing for belonging and roots.",
    "LEO": "Warm-heartedness and a need for recognition in close bonds.",
    "VIRGO": "Emotional fulfilment comes through useful, practical acts.",
    "LIBRA": "Harmony in relationships soothes the inner world.",
    "SCORPIO": "Intense emotional experiences lead to profound self-knowledge.",
    "SAGITTARIUS": "Adventure and optimism lift the spirit; restlessness is possible.",
    "CAPRICORN": "Emotional restraint; satisfaction comes from concrete achievements.",
    "AQUARIUS": "Detachment and idealism colour emotional responses.",
    "PISCES": "Heightened empathy, intuition, and a need for spiritual connection.",
}


class ProgressionsCalculator:
    """Calculate secondary progressed charts."""

    def __init__(self) -> None:
        self._generator = BirthChartGenerator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(
        self,
        natal_chart: BirthChart,
        target_date: Optional[datetime] = None,
        tz_offset_hours: Optional[int] = None,
    ) -> ProgressedChart:
        """Return a :class:`ProgressedChart` for *target_date* (default today).

        Parameters
        ----------
        natal_chart:
            The pre-calculated natal :class:`BirthChart`.
        target_date:
            The date for which progressions are requested.  Defaults to the
            current UTC date/time when omitted.
        tz_offset_hours:
            Optional timezone offset (hours) used for the progressed chart
            calculation.  When *None* the value stored in *natal_chart* is
            re-used.
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc)

        # Ensure we compare naive datetimes: birth_date is always naive, so
        # strip timezone info from target_date if present.
        target_naive = target_date.replace(tzinfo=None) if target_date.tzinfo is not None else target_date
        natal_naive = natal_chart.birth_date.replace(tzinfo=None) if natal_chart.birth_date.tzinfo is not None else natal_chart.birth_date

        age_years = (target_naive - natal_naive).days / 365.25
        # Day-for-a-year: advance birth date by age_years days.
        progressed_birth_dt = natal_naive + timedelta(days=age_years)

        prog_chart = self._generator.generate_chart(
            birth_date=progressed_birth_dt,
            latitude=natal_chart.latitude,
            longitude=natal_chart.longitude,
            location_name=natal_chart.location_name,
            tz_offset_hours=tz_offset_hours or natal_chart.timezone_offset_hours,
            house_system=natal_chart.house_system,
        )

        progressed_planets: Dict[str, ProgressedPlanet] = {}
        for planet, natal_pos in natal_chart.planets.items():
            prog_pos: Optional[PlanetPosition] = prog_chart.planets.get(planet)
            if prog_pos is None:
                continue
            sign_change = prog_pos.sign != natal_pos.sign
            interp = self._interpret_progressed_planet(planet, prog_pos.sign, sign_change)
            progressed_planets[planet.name] = ProgressedPlanet(
                planet=planet,
                natal_sign=natal_pos.sign,
                natal_degree=natal_pos.degree,
                progressed_sign=prog_pos.sign,
                progressed_degree=prog_pos.degree,
                sign_change=sign_change,
                interpretation=interp,
            )

        major_themes = self._derive_major_themes(
            progressed_planets,
            prog_chart.ascendant_sign,
            natal_chart.ascendant_sign,
        )

        return ProgressedChart(
            birth_date=natal_naive,
            progression_date=target_naive,
            age_years=age_years,
            progressed_planets=progressed_planets,
            progressed_sun_sign=prog_chart.planets.get(Planet.SUN, None)
            and prog_chart.planets[Planet.SUN].sign,
            progressed_moon_sign=prog_chart.planets.get(Planet.MOON, None)
            and prog_chart.planets[Planet.MOON].sign,
            progressed_ascendant_sign=prog_chart.ascendant_sign,
            major_themes=major_themes,
        )

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_progression(self, prog: ProgressedChart) -> str:
        """Return a human-readable progression report."""
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("🔮 SECONDARY PROGRESSIONS 🔮".center(60))
        lines.append("=" * 60)

        lines.append(f"\n📅 Progression Date: {prog.progression_date.strftime('%B %d, %Y')}")
        lines.append(f"   Age: {prog.age_years:.1f} years")
        lines.append(f"   Natal Date: {prog.birth_date.strftime('%B %d, %Y')}")

        if prog.progressed_sun_sign:
            lines.append(f"\n☀ Progressed Sun: {prog.progressed_sun_sign.name}")
            theme = _PROG_SUN_THEMES.get(prog.progressed_sun_sign.name, "")
            if theme:
                lines.append(f"   {theme}")

        if prog.progressed_moon_sign:
            lines.append(f"\n☽ Progressed Moon: {prog.progressed_moon_sign.name}")
            theme = _PROG_MOON_THEMES.get(prog.progressed_moon_sign.name, "")
            if theme:
                lines.append(f"   {theme}")

        if prog.progressed_ascendant_sign:
            lines.append(f"\n↑ Progressed Ascendant: {prog.progressed_ascendant_sign.name}")

        lines.append("\n📊 Planetary Progressions:")
        for pp in prog.progressed_planets.values():
            lines.append(f"   {pp}")
            if pp.sign_change and pp.interpretation:
                lines.append(f"   ✨ {pp.interpretation}")

        if prog.major_themes:
            lines.append("\n🎯 Major Themes:")
            for theme in prog.major_themes:
                lines.append(f"   • {theme}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _interpret_progressed_planet(
        self, planet: Planet, sign: ZodiacSign, sign_change: bool
    ) -> str:
        if not sign_change:
            return ""
        if planet == Planet.SUN:
            return _PROG_SUN_THEMES.get(sign.name, f"Sun moves into {sign.name}.")
        if planet == Planet.MOON:
            return _PROG_MOON_THEMES.get(sign.name, f"Moon moves into {sign.name}.")
        return f"{planet.name} enters {sign.name}, bringing fresh {sign.element.lower()} energy."

    def _derive_major_themes(
        self,
        progressed_planets: Dict[str, ProgressedPlanet],
        prog_asc: ZodiacSign,
        natal_asc: ZodiacSign,
    ) -> List[str]:
        themes: List[str] = []
        sun_pp = progressed_planets.get("SUN")
        if sun_pp and sun_pp.sign_change:
            themes.append(
                f"Progressed Sun entering {sun_pp.progressed_sign.name}: "
                + _PROG_SUN_THEMES.get(sun_pp.progressed_sign.name, "A new solar chapter begins.")
            )
        moon_pp = progressed_planets.get("MOON")
        if moon_pp and moon_pp.sign_change:
            themes.append(
                f"Progressed Moon entering {moon_pp.progressed_sign.name}: "
                + _PROG_MOON_THEMES.get(moon_pp.progressed_sign.name, "Emotional landscape shifts.")
            )
        if prog_asc != natal_asc:
            themes.append(
                f"Progressed Ascendant has moved into {prog_asc.name}, reshaping your outward presence."
            )
        if not themes:
            themes.append("Gradual evolution continues – trust the slow unfolding of your progressed chart.")
        return themes

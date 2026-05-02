"""Daily and monthly astrological tips and guidance."""
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
from .birth_chart import BirthChart, Planet, ZodiacSign, BirthChartGenerator
from .transits import TransitForecaster
import hashlib


class DailyAstrologer:
    """Generate personalized daily and monthly astrological guidance."""
    
    def __init__(self):
        self.chart_generator = BirthChartGenerator()
        self.transit_forecaster = TransitForecaster()
        self.daily_themes = self._load_daily_themes()
        self.moon_phases = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
                           'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent']
    
    def _load_daily_themes(self) -> Dict[ZodiacSign, Dict]:
        """Load daily guidance themes for each sign.

        lucky_colors and lucky_numbers are lists so that a different value can
        be selected each day using the date-based seed, giving the appearance of
        dynamically updated lucky data without requiring an external API call.
        """
        return {
            ZodiacSign.ARIES: {
                'focus': ['Initiative', 'Leadership', 'Courage', 'New beginnings'],
                'avoid': ['Impatience', 'Recklessness', 'Aggression'],
                'lucky_colors': ['Red', 'Orange', 'Scarlet', 'Crimson', 'Coral'],
                'lucky_numbers': [9, 1, 7, 3, 5],
            },
            ZodiacSign.TAURUS: {
                'focus': ['Stability', 'Sensory pleasures', 'Building resources', 'Patience'],
                'avoid': ['Stubbornness', 'Resistance to change', 'Materialism'],
                'lucky_colors': ['Green', 'Emerald', 'Sage', 'Olive', 'Jade'],
                'lucky_numbers': [6, 4, 2, 8, 11],
            },
            ZodiacSign.GEMINI: {
                'focus': ['Communication', 'Learning', 'Networking', 'Variety'],
                'avoid': ['Scattered energy', 'Superficiality', 'Gossip'],
                'lucky_colors': ['Yellow', 'Lemon', 'Sky blue', 'Lavender', 'Mint'],
                'lucky_numbers': [5, 7, 3, 11, 9],
            },
            ZodiacSign.CANCER: {
                'focus': ['Emotional connection', 'Home', 'Family', 'Nurturing'],
                'avoid': ['Moodiness', 'Clinging', 'Dwelling on past'],
                'lucky_colors': ['Silver', 'Pearl white', 'Sea blue', 'Pale lavender', 'Cream'],
                'lucky_numbers': [2, 7, 11, 4, 6],
            },
            ZodiacSign.LEO: {
                'focus': ['Self-expression', 'Creativity', 'Generosity', 'Leadership'],
                'avoid': ['Ego', 'Drama', 'Attention-seeking'],
                'lucky_colors': ['Gold', 'Amber', 'Sunflower yellow', 'Royal purple', 'Orange'],
                'lucky_numbers': [1, 9, 5, 3, 11],
            },
            ZodiacSign.VIRGO: {
                'focus': ['Organization', 'Service', 'Health', 'Analysis'],
                'avoid': ['Over-criticism', 'Perfectionism', 'Worry'],
                'lucky_colors': ['Navy blue', 'Forest green', 'Beige', 'Charcoal', 'Teal'],
                'lucky_numbers': [5, 6, 3, 11, 8],
            },
            ZodiacSign.LIBRA: {
                'focus': ['Balance', 'Relationships', 'Beauty', 'Diplomacy'],
                'avoid': ['Indecision', 'People-pleasing', 'Superficiality'],
                'lucky_colors': ['Pink', 'Rose', 'Ivory', 'Pale blue', 'Lilac'],
                'lucky_numbers': [6, 9, 3, 15, 24],
            },
            ZodiacSign.SCORPIO: {
                'focus': ['Transformation', 'Depth', 'Passion', 'Truth'],
                'avoid': ['Jealousy', 'Manipulation', 'Resentment'],
                'lucky_colors': ['Maroon', 'Deep red', 'Black', 'Dark teal', 'Burgundy'],
                'lucky_numbers': [8, 11, 18, 22, 4],
            },
            ZodiacSign.SAGITTARIUS: {
                'focus': ['Exploration', 'Truth', 'Freedom', 'Optimism'],
                'avoid': ['Overcommitting', 'Tactlessness', 'Restlessness'],
                'lucky_colors': ['Purple', 'Indigo', 'Turquoise', 'Violet', 'Electric blue'],
                'lucky_numbers': [3, 9, 7, 12, 21],
            },
            ZodiacSign.CAPRICORN: {
                'focus': ['Goals', 'Discipline', 'Career', 'Structure'],
                'avoid': ['Pessimism', 'Rigidity', 'Workaholism'],
                'lucky_colors': ['Brown', 'Dark grey', 'Forest green', 'Charcoal', 'Navy'],
                'lucky_numbers': [8, 4, 13, 22, 6],
            },
            ZodiacSign.AQUARIUS: {
                'focus': ['Innovation', 'Friendship', 'Freedom', 'Humanitarian goals'],
                'avoid': ['Detachment', 'Rebelliousness', 'Coldness'],
                'lucky_colors': ['Electric blue', 'Cyan', 'Turquoise', 'Violet', 'Silver'],
                'lucky_numbers': [4, 7, 11, 22, 29],
            },
            ZodiacSign.PISCES: {
                'focus': ['Intuition', 'Compassion', 'Creativity', 'Spirituality'],
                'avoid': ['Escapism', 'Victimhood', 'Confusion'],
                'lucky_colors': ['Sea green', 'Aquamarine', 'Soft lilac', 'Seafoam', 'Pale blue'],
                'lucky_numbers': [7, 3, 12, 9, 11],
            },
        }
    
    def generate_daily_guidance(self, birth_chart: BirthChart, target_date: date = None) -> str:
        """Generate personalized daily guidance (unique per user + date)."""
        if target_date is None:
            target_date = date.today()

        sun_sign = birth_chart.get_sun_sign()
        moon_sign = birth_chart.get_moon_sign()
        rising_sign = birth_chart.get_rising_sign()

        # Compute current sky positions for the target date
        current_dt = datetime.combine(target_date, datetime.min.time())
        jd = self.chart_generator.calculate_julian_day(current_dt)
        moon_position = self.chart_generator.calculate_moon_position(jd)
        current_moon_sign, _ = self.chart_generator.degree_to_sign(moon_position)

        # Current planet signs (real-time sky influence)
        planet_positions = self._get_current_planet_positions(jd)
        planet_signs = {
            planet: self.chart_generator.degree_to_sign(position)[0]
            for planet, position in planet_positions.items()
        }

        # Determine moon phase (simplified)
        moon_phase = self._calculate_moon_phase(jd)

        # Unique seed based on date + chart anchors (deterministic, no randomness)
        seed_key = f"{target_date.isoformat()}|{sun_sign.name}|{moon_sign.name}|{rising_sign.name}"

        lines = []
        lines.append("\n" + "=" * 60)
        lines.append(f"🌟 DAILY GUIDANCE - {target_date.strftime('%A, %B %d, %Y')} 🌟".center(60))
        lines.append("=" * 60)

        # Sun Sign Daily Focus (deterministic)
        sun_themes = self.daily_themes.get(sun_sign, {})
        lines.append(f"\n☀️ Sun in {sun_sign.name} - Today's Focus:")
        focus_list = sun_themes.get('focus', ['Personal growth'])
        focus_idx = self._stable_index(seed_key + "|focus", len(focus_list))
        lines.append(f"   {focus_list[focus_idx]}")

        # Moon Sign Emotional Guidance
        lines.append(f"\n☽ Moon in {current_moon_sign.name} - Emotional Climate:")
        moon_guidance = self._get_moon_sign_guidance(current_moon_sign)
        lines.append(f"   {moon_guidance}")

        # Planetary influences (real transits + sky positions)
        lines.append(f"\n🪐 Planetary Influences Today:")
        _mercury = planet_signs.get(Planet.MERCURY)
        _venus = planet_signs.get(Planet.VENUS)
        _mars = planet_signs.get(Planet.MARS)
        lines.append(
            f"   Mercury in {_mercury.name if _mercury is not None else 'Unknown'}"
            f" • Venus in {_venus.name if _venus is not None else 'Unknown'}"
            f" • Mars in {_mars.name if _mars is not None else 'Unknown'}"
        )

        # Personalized transit highlights
        transit_highlights = self._get_personal_transit_highlights(birth_chart, planet_positions)
        if transit_highlights:
            lines.append(f"\n⚡ Your Active Transits:")
            for highlight in transit_highlights[:3]:
                lines.append(f"   {highlight}")

        # Moon Phase
        lines.append(f"\n🌙 Moon Phase: {moon_phase}")
        phase_guidance = self._get_moon_phase_guidance(moon_phase)
        lines.append(f"   {phase_guidance}")

        # Rising Sign Action
        lines.append(f"\n⬆️ Rising in {rising_sign.name} - Best Approach:")
        rising_action = self._get_rising_action(rising_sign)
        lines.append(f"   {rising_action}")

        # Lucky Elements – rotate through the sign's pool using the date seed so
        # the colour and number feel fresh each day while remaining deterministic.
        lines.append(f"\n🍀 Today's Lucky Elements:")
        lucky_colors = sun_themes.get('lucky_colors', ['White'])
        lucky_color = lucky_colors[self._stable_index(seed_key + "|lucky_color", len(lucky_colors))]

        lucky_numbers = sun_themes.get('lucky_numbers', [7])
        lucky_number = lucky_numbers[self._stable_index(seed_key + "|lucky_number", len(lucky_numbers))]

        lines.append(f"   Color: {lucky_color}")
        lines.append(f"   Number: {lucky_number}")

        # What to Avoid (deterministic)
        avoid_list = sun_themes.get('avoid', [])
        if avoid_list:
            lines.append(f"\n⚠️ What to Avoid:")
            avoid_idx = self._stable_index(seed_key + "|avoid", len(avoid_list))
            lines.append(f"   {avoid_list[avoid_idx]}")

        # Personalized affirmation
        lines.append(f"\n💫 Daily Affirmation:")
        affirmation = self._generate_affirmation(sun_sign)
        lines.append(f"   {affirmation}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)

    def _stable_index(self, seed: str, modulo: int) -> int:
        if modulo <= 0:
            return 0
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        return int(digest[:8], 16) % modulo

    def _get_current_planet_positions(self, jd: float) -> Dict[Planet, float]:
        return {
            Planet.SUN: self.chart_generator.calculate_sun_position(jd),
            Planet.MOON: self.chart_generator.calculate_moon_position(jd),
            Planet.MERCURY: self.chart_generator.calculate_planet_position(Planet.MERCURY, jd),
            Planet.VENUS: self.chart_generator.calculate_planet_position(Planet.VENUS, jd),
            Planet.MARS: self.chart_generator.calculate_planet_position(Planet.MARS, jd),
            Planet.JUPITER: self.chart_generator.calculate_planet_position(Planet.JUPITER, jd),
            Planet.SATURN: self.chart_generator.calculate_planet_position(Planet.SATURN, jd),
        }

    def _get_personal_transit_highlights(self, birth_chart: BirthChart, planet_positions: Dict[Planet, float]) -> List[str]:
        highlights: List[Tuple[float, str]] = []

        for trans_planet, trans_degree in planet_positions.items():
            for natal_planet, natal_pos in birth_chart.planets.items():
                natal_degree = natal_pos.sign.start_degree + natal_pos.degree
                aspect, orb = self._check_aspect(trans_degree, natal_degree)
                if aspect and orb <= 3.5:
                    influence = self._summarize_transit(trans_planet, natal_planet, aspect)
                    highlights.append((orb, influence))

        highlights.sort(key=lambda x: x[0])
        return [item[1] for item in highlights]

    def _summarize_transit(self, transiting: Planet, natal: Planet, aspect: str) -> str:
        key = (transiting, aspect)
        meaning = self.transit_forecaster.transit_meanings.get(
            key,
            {
                "influence": f"{transiting.name} {aspect} Natal {natal.name} brings fresh focus",
                "advice": "Stay mindful and work with the energy intentionally",
            },
        )
        return f"{transiting.symbol} {transiting.name} {aspect} {natal.symbol} {natal.name}: {meaning['influence']}"

    def _check_aspect(self, degree1: float, degree2: float) -> Tuple[Optional[str], float]:
        diff = abs(degree1 - degree2)
        if diff > 180:
            diff = 360 - diff

        aspects = {
            0: ("conjunction", 8.0),
            60: ("sextile", 6.0),
            90: ("square", 7.0),
            120: ("trine", 8.0),
            180: ("opposition", 8.0),
        }

        for angle, (aspect_name, max_orb) in aspects.items():
            orb = abs(diff - angle)
            if orb <= max_orb:
                return aspect_name, orb

        return None, 999.0
    
    def generate_monthly_guidance(self, birth_chart: BirthChart, year: int = None, 
                                 month: int = None) -> str:
        """Generate monthly astrological guidance."""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        month_name = datetime(year, month, 1).strftime('%B %Y')
        
        sun_sign = birth_chart.get_sun_sign()
        sun_themes = self.daily_themes.get(sun_sign, {})
        
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append(f"📅 MONTHLY GUIDANCE - {month_name} 📅".center(60))
        lines.append("=" * 60)
        
        lines.append(f"\n🌟 {sun_sign.name} - Your Monthly Overview:")
        
        # Monthly themes
        lines.append(f"\n💫 Key Themes:")
        for theme in sun_themes.get('focus', ['Growth', 'Learning'])[:3]:
            lines.append(f"   • {theme}")
        
        # Week by week
        lines.append(f"\n📆 Week-by-Week Guide:")
        
        weeks = [
            {'week': 'Week 1', 'focus': 'New beginnings and fresh starts', 
             'action': 'Set intentions for the month ahead'},
            {'week': 'Week 2', 'focus': 'Building momentum', 
             'action': 'Take action on your goals'},
            {'week': 'Week 3', 'focus': 'Peak energy and productivity', 
             'action': 'Push forward with important projects'},
            {'week': 'Week 4', 'focus': 'Reflection and integration', 
             'action': 'Review progress and prepare for next month'}
        ]
        
        for week_info in weeks:
            lines.append(f"\n   {week_info['week']}: {week_info['focus']}")
            lines.append(f"      → {week_info['action']}")
        
        # Monthly advice
        lines.append(f"\n💡 Monthly Advice:")
        advice_items = [
            f"Embrace your {sun_sign.element} nature by connecting with that element",
            f"As a {sun_sign.modality} sign, focus on {self._get_modality_advice(sun_sign.modality)}",
            "Stay true to your core values while remaining open to growth"
        ]
        for advice in advice_items:
            lines.append(f"   • {advice}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def _calculate_moon_phase(self, jd: float) -> str:
        """Calculate approximate moon phase."""
        # Simplified moon phase calculation
        phase_cycle = 29.53  # Days in lunar cycle
        
        # Reference new moon
        new_moon_jd = 2451550.1  # Jan 6, 2000
        
        days_since = jd - new_moon_jd
        phase_position = (days_since % phase_cycle) / phase_cycle
        
        phase_index = int(phase_position * 8)
        return self.moon_phases[phase_index]
    
    def _get_moon_sign_guidance(self, moon_sign: ZodiacSign) -> str:
        """Get emotional guidance based on current moon sign."""
        guidance = {
            ZodiacSign.ARIES: "Bold emotional expression. Take initiative in matters of the heart.",
            ZodiacSign.TAURUS: "Seek comfort and security. Enjoy simple pleasures.",
            ZodiacSign.GEMINI: "Communicate your feelings. Intellectual stimulation lifts your mood.",
            ZodiacSign.CANCER: "Nurture yourself and others. Home activities bring comfort.",
            ZodiacSign.LEO: "Express yourself creatively. Shine your light with confidence.",
            ZodiacSign.VIRGO: "Organize and serve. Practical activities bring emotional satisfaction.",
            ZodiacSign.LIBRA: "Seek balance and harmony. Connect with others.",
            ZodiacSign.SCORPIO: "Dive deep emotionally. Transform through intensity.",
            ZodiacSign.SAGITTARIUS: "Explore and expand. Adventure lifts your spirits.",
            ZodiacSign.CAPRICORN: "Focus on goals. Structure brings emotional security.",
            ZodiacSign.AQUARIUS: "Embrace uniqueness. Connect with groups and causes.",
            ZodiacSign.PISCES: "Tap into intuition. Creative and spiritual activities soothe."
        }
        return guidance.get(moon_sign, "Trust your emotions today.")
    
    def _get_moon_phase_guidance(self, phase: str) -> str:
        """Get guidance based on moon phase."""
        guidance = {
            'New Moon': 'Perfect for new beginnings and setting intentions',
            'Waxing Crescent': 'Build momentum on your goals',
            'First Quarter': 'Take action and overcome obstacles',
            'Waxing Gibbous': 'Refine and perfect your plans',
            'Full Moon': 'Peak energy - bring things to completion',
            'Waning Gibbous': 'Share what you\'ve learned',
            'Last Quarter': 'Release what no longer serves you',
            'Waning Crescent': 'Rest, reflect, and prepare for renewal'
        }
        return guidance.get(phase, 'Flow with natural cycles')
    
    def _get_rising_action(self, rising_sign: ZodiacSign) -> str:
        """Get action guidance based on rising sign."""
        actions = {
            ZodiacSign.ARIES: "Lead with confidence and take bold action",
            ZodiacSign.TAURUS: "Move steadily toward your goals with patience",
            ZodiacSign.GEMINI: "Communicate and gather information",
            ZodiacSign.CANCER: "Lead with empathy and intuition",
            ZodiacSign.LEO: "Express yourself authentically and inspire others",
            ZodiacSign.VIRGO: "Analyze situations carefully and be of service",
            ZodiacSign.LIBRA: "Seek collaboration and maintain balance",
            ZodiacSign.SCORPIO: "Transform situations with intensity and focus",
            ZodiacSign.SAGITTARIUS: "Approach life with optimism and adventure",
            ZodiacSign.CAPRICORN: "Take responsibility and build systematically",
            ZodiacSign.AQUARIUS: "Think innovatively and break from convention",
            ZodiacSign.PISCES: "Trust your intuition and flow with circumstances"
        }
        return actions.get(rising_sign, "Be authentic in your approach")
    
    def _generate_affirmation(self, sun_sign: ZodiacSign) -> str:
        """Generate personalized affirmation."""
        affirmations = {
            ZodiacSign.ARIES: "I courageously pursue my passions and lead with confidence.",
            ZodiacSign.TAURUS: "I am grounded, stable, and abundant in all areas of life.",
            ZodiacSign.GEMINI: "I communicate with clarity and embrace life's variety.",
            ZodiacSign.CANCER: "I honor my emotions and nurture meaningful connections.",
            ZodiacSign.LEO: "I shine my authentic light and inspire others.",
            ZodiacSign.VIRGO: "I serve with precision and embrace imperfection.",
            ZodiacSign.LIBRA: "I create harmony and balance in all my relationships.",
            ZodiacSign.SCORPIO: "I transform challenges into opportunities for growth.",
            ZodiacSign.SAGITTARIUS: "I expand my horizons and embrace adventure.",
            ZodiacSign.CAPRICORN: "I build lasting structures through discipline and patience.",
            ZodiacSign.AQUARIUS: "I honor my uniqueness and contribute to the collective.",
            ZodiacSign.PISCES: "I trust my intuition and flow with universal wisdom."
        }
        return affirmations.get(sun_sign, "I am aligned with my highest purpose.")
    
    def _get_modality_advice(self, modality: str) -> str:
        """Get advice based on modality."""
        advice = {
            'Cardinal': 'initiating new projects and taking leadership',
            'Fixed': 'maintaining consistency and seeing things through',
            'Mutable': 'adapting to change and staying flexible'
        }
        return advice.get(modality, 'following your natural rhythm')

"""Astrological interpretations for birth charts."""
from typing import Dict, List
from .birth_chart import BirthChart, Planet, ZodiacSign, Aspect


class AstrologyInterpreter:
    """Generate personalized interpretations from birth charts."""
    
    def __init__(self):
        self.sun_interpretations = self._load_sun_interpretations()
        self.moon_interpretations = self._load_moon_interpretations()
        self.rising_interpretations = self._load_rising_interpretations()
        self.planet_house_meanings = self._load_planet_house_meanings()
        self.aspect_interpretations = self._load_aspect_interpretations()
    
    def _load_sun_interpretations(self) -> Dict[ZodiacSign, Dict]:
        """Load Sun sign personality interpretations."""
        return {
            ZodiacSign.ARIES: {
                'personality': 'Bold, pioneering, and energetic. You are a natural leader with courage and initiative.',
                'strengths': ['Leadership', 'Courage', 'Determination', 'Confidence', 'Enthusiasm'],
                'challenges': ['Impatience', 'Impulsiveness', 'Short temper', 'Self-centered tendencies'],
                'growth': 'Learn patience and consider others\' perspectives before acting.'
            },
            ZodiacSign.TAURUS: {
                'personality': 'Stable, patient, and practical. You value security and appreciate life\'s pleasures.',
                'strengths': ['Reliability', 'Patience', 'Devotion', 'Responsibility', 'Stability'],
                'challenges': ['Stubbornness', 'Possessiveness', 'Materialism', 'Resistance to change'],
                'growth': 'Embrace flexibility and be open to new experiences.'
            },
            ZodiacSign.GEMINI: {
                'personality': 'Curious, adaptable, and communicative. You thrive on mental stimulation and variety.',
                'strengths': ['Versatility', 'Communication', 'Wit', 'Intellectuality', 'Adaptability'],
                'challenges': ['Inconsistency', 'Restlessness', 'Indecisiveness', 'Superficiality'],
                'growth': 'Focus on depth and follow through on commitments.'
            },
            ZodiacSign.CANCER: {
                'personality': 'Nurturing, emotional, and intuitive. You are deeply connected to family and home.',
                'strengths': ['Empathy', 'Loyalty', 'Emotional depth', 'Nurturing nature', 'Intuition'],
                'challenges': ['Moodiness', 'Over-sensitivity', 'Clinginess', 'Defensive behavior'],
                'growth': 'Build emotional resilience and set healthy boundaries.'
            },
            ZodiacSign.LEO: {
                'personality': 'Confident, generous, and charismatic. You shine brightly and inspire others.',
                'strengths': ['Confidence', 'Generosity', 'Warmth', 'Creativity', 'Leadership'],
                'challenges': ['Arrogance', 'Stubbornness', 'Self-centeredness', 'Need for attention'],
                'growth': 'Practice humility and share the spotlight with others.'
            },
            ZodiacSign.VIRGO: {
                'personality': 'Analytical, practical, and helpful. You excel at organizing and improving things.',
                'strengths': ['Analysis', 'Practicality', 'Diligence', 'Attention to detail', 'Helpfulness'],
                'challenges': ['Over-criticism', 'Perfectionism', 'Worry', 'Fussiness'],
                'growth': 'Accept imperfection and practice self-compassion.'
            },
            ZodiacSign.LIBRA: {
                'personality': 'Diplomatic, fair-minded, and social. You seek harmony and balance in all things.',
                'strengths': ['Diplomacy', 'Fairness', 'Social grace', 'Cooperation', 'Idealism'],
                'challenges': ['Indecisiveness', 'Avoiding confrontation', 'People-pleasing', 'Superficiality'],
                'growth': 'Make decisions confidently and stand up for your own needs.'
            },
            ZodiacSign.SCORPIO: {
                'personality': 'Intense, passionate, and transformative. You seek deep connections and truth.',
                'strengths': ['Passion', 'Resourcefulness', 'Bravery', 'Loyalty', 'Determination'],
                'challenges': ['Jealousy', 'Secrecy', 'Resentment', 'Control issues'],
                'growth': 'Practice forgiveness and trust in the process of transformation.'
            },
            ZodiacSign.SAGITTARIUS: {
                'personality': 'Optimistic, adventurous, and philosophical. You seek truth and new experiences.',
                'strengths': ['Optimism', 'Freedom-loving', 'Honesty', 'Philosophical', 'Adventurous'],
                'challenges': ['Tactlessness', 'Restlessness', 'Irresponsibility', 'Overconfidence'],
                'growth': 'Develop tact and balance freedom with responsibility.'
            },
            ZodiacSign.CAPRICORN: {
                'personality': 'Ambitious, disciplined, and responsible. You build lasting structures and achieve goals.',
                'strengths': ['Discipline', 'Responsibility', 'Ambition', 'Self-control', 'Patience'],
                'challenges': ['Pessimism', 'Rigidity', 'Workaholism', 'Coldness'],
                'growth': 'Allow yourself to relax and express emotions more freely.'
            },
            ZodiacSign.AQUARIUS: {
                'personality': 'Independent, innovative, and humanitarian. You think outside the box and value freedom.',
                'strengths': ['Originality', 'Independence', 'Humanitarian', 'Progressive', 'Intellectual'],
                'challenges': ['Detachment', 'Stubbornness', 'Unpredictability', 'Aloofness'],
                'growth': 'Connect more deeply with emotions and personal relationships.'
            },
            ZodiacSign.PISCES: {
                'personality': 'Compassionate, artistic, and intuitive. You are deeply empathetic and imaginative.',
                'strengths': ['Compassion', 'Intuition', 'Artistic', 'Gentle', 'Wise'],
                'challenges': ['Escapism', 'Over-idealistic', 'Overly trusting', 'Victim mentality'],
                'growth': 'Develop healthy boundaries and stay grounded in reality.'
            }
        }
    
    def _load_moon_interpretations(self) -> Dict[ZodiacSign, str]:
        """Load Moon sign emotional interpretations."""
        return {
            ZodiacSign.ARIES: 'Emotionally direct and passionate. You react quickly and need independence.',
            ZodiacSign.TAURUS: 'Emotionally steady and security-seeking. You need comfort and routine.',
            ZodiacSign.GEMINI: 'Emotionally curious and changeable. You process feelings through communication.',
            ZodiacSign.CANCER: 'Deeply emotional and nurturing. You need emotional security and family connection.',
            ZodiacSign.LEO: 'Emotionally warm and dramatic. You need appreciation and creative expression.',
            ZodiacSign.VIRGO: 'Emotionally analytical and practical. You find comfort in being useful.',
            ZodiacSign.LIBRA: 'Emotionally balanced and relationship-oriented. You need harmony and partnership.',
            ZodiacSign.SCORPIO: 'Emotionally intense and transformative. You need deep emotional connections.',
            ZodiacSign.SAGITTARIUS: 'Emotionally optimistic and freedom-loving. You need space and adventure.',
            ZodiacSign.CAPRICORN: 'Emotionally reserved and responsible. You need structure and achievement.',
            ZodiacSign.AQUARIUS: 'Emotionally detached and rational. You need mental stimulation and independence.',
            ZodiacSign.PISCES: 'Emotionally sensitive and empathetic. You need creativity and spiritual connection.'
        }
    
    def _load_rising_interpretations(self) -> Dict[ZodiacSign, str]:
        """Load Rising sign (Ascendant) interpretations."""
        return {
            ZodiacSign.ARIES: 'You appear energetic, direct, and confident. Others see you as a go-getter.',
            ZodiacSign.TAURUS: 'You appear calm, stable, and reliable. Others see you as grounded and trustworthy.',
            ZodiacSign.GEMINI: 'You appear curious, talkative, and youthful. Others see you as intelligent and versatile.',
            ZodiacSign.CANCER: 'You appear nurturing, sensitive, and protective. Others see you as caring and empathetic.',
            ZodiacSign.LEO: 'You appear confident, charismatic, and warm. Others see you as a natural leader.',
            ZodiacSign.VIRGO: 'You appear practical, helpful, and detail-oriented. Others see you as competent and modest.',
            ZodiacSign.LIBRA: 'You appear charming, diplomatic, and balanced. Others see you as graceful and fair.',
            ZodiacSign.SCORPIO: 'You appear intense, mysterious, and powerful. Others see you as magnetic and deep.',
            ZodiacSign.SAGITTARIUS: 'You appear optimistic, adventurous, and honest. Others see you as fun and philosophical.',
            ZodiacSign.CAPRICORN: 'You appear serious, responsible, and ambitious. Others see you as mature and capable.',
            ZodiacSign.AQUARIUS: 'You appear unique, friendly, and progressive. Others see you as unconventional and intellectual.',
            ZodiacSign.PISCES: 'You appear gentle, dreamy, and compassionate. Others see you as artistic and spiritual.'
        }
    
    def _load_planet_house_meanings(self) -> Dict:
        """Load meanings for planets in different houses."""
        # Simplified - full implementation would have specific meanings for each planet in each house
        return {
            1: 'Strong focus on self-identity and personal expression',
            2: 'Emphasis on values, resources, and material security',
            3: 'Focus on communication, learning, and local connections',
            4: 'Deep connection to home, family, and emotional foundations',
            5: 'Creative expression, romance, and playful self-expression',
            6: 'Service, health, daily work, and practical matters',
            7: 'Partnerships, relationships, and one-on-one connections',
            8: 'Transformation, shared resources, and depth psychology',
            9: 'Higher learning, philosophy, travel, and expansion',
            10: 'Career, public image, and life direction',
            11: 'Community, friendships, and future aspirations',
            12: 'Spirituality, subconscious, and hidden matters'
        }
    
    def _load_aspect_interpretations(self) -> Dict[str, Dict]:
        """Load aspect interpretations."""
        return {
            'conjunction': {
                'meaning': 'Powerful blending of energies',
                'nature': 'Intensifies both planets\' qualities'
            },
            'opposition': {
                'meaning': 'Tension requiring balance',
                'nature': 'Creates awareness through contrast'
            },
            'trine': {
                'meaning': 'Harmonious flow of energy',
                'nature': 'Natural talents and ease'
            },
            'square': {
                'meaning': 'Dynamic tension and challenge',
                'nature': 'Motivates growth through friction'
            },
            'sextile': {
                'meaning': 'Opportunity and cooperation',
                'nature': 'Supportive potential requiring action'
            }
        }

    def _planet_in_sign_summary(self, planet: Planet, sign: ZodiacSign) -> str:
        """Provide a concise, professional summary of planet-in-sign behavior."""
        element_tone = {
            'Fire': 'bold, action-oriented',
            'Earth': 'practical, grounded',
            'Air': 'intellectual, communicative',
            'Water': 'intuitive, emotionally attuned'
        }
        modality_tone = {
            'Cardinal': 'initiating and proactive',
            'Fixed': 'steady and persistent',
            'Mutable': 'adaptable and flexible'
        }
        element = sign.element
        modality = sign.modality
        return (
            f"{planet.name.title()} expresses as {element_tone.get(element, element.lower())} energy, "
            f"with a {modality_tone.get(modality, modality.lower())} approach."
        )
    
    def generate_full_interpretation(self, chart: BirthChart) -> str:
        """Generate comprehensive chart interpretation."""
        lines = []
        
        lines.append("\n" + "=" * 60)
        lines.append("🔮 PERSONALIZED BIRTH CHART INTERPRETATION 🔮".center(60))
        lines.append("=" * 60)
        
        # Core Identity
        lines.append("\n" + "━" * 60)
        lines.append("💫 YOUR CORE IDENTITY")
        lines.append("━" * 60)
        
        sun_sign = chart.get_sun_sign()
        if sun_sign and sun_sign in self.sun_interpretations:
            sun_data = self.sun_interpretations[sun_sign]
            lines.append(f"\n☀️ Sun in {sun_sign.name}:")
            lines.append(f"   {sun_data['personality']}")
            lines.append(f"\n   ✨ Your Strengths:")
            for strength in sun_data['strengths']:
                lines.append(f"      • {strength}")
            lines.append(f"\n   🌱 Growth Opportunities:")
            for challenge in sun_data['challenges']:
                lines.append(f"      • Work on: {challenge}")
            lines.append(f"\n   💡 Advice: {sun_data['growth']}")
        
        # Emotional Nature
        moon_sign = chart.get_moon_sign()
        if moon_sign and moon_sign in self.moon_interpretations:
            lines.append(f"\n☽ Moon in {moon_sign.name}:")
            lines.append(f"   {self.moon_interpretations[moon_sign]}")
        
        # Public Persona
        rising_sign = chart.get_rising_sign()
        if rising_sign and rising_sign in self.rising_interpretations:
            lines.append(f"\n⬆️ Rising in {rising_sign.name}:")
            lines.append(f"   {self.rising_interpretations[rising_sign]}")
        
        # Personal Planets
        lines.append("\n" + "━" * 60)
        lines.append("🌟 YOUR PERSONAL PLANETS")
        lines.append("━" * 60)
        
        personal_planets = [Planet.MERCURY, Planet.VENUS, Planet.MARS]
        for planet in personal_planets:
            if planet in chart.planets:
                pos = chart.planets[planet]
                lines.append(f"\n{planet.symbol} {planet.name} in {pos.sign.name}:")
                lines.append(f"   {planet.meaning}")
                lines.append(f"   {self._planet_in_sign_summary(planet, pos.sign)}")
                lines.append(f"   Located in House {pos.house}: {self.planet_house_meanings[pos.house]}")
                if pos.retrograde:
                    lines.append("   Retrograde: The energy is more internalized and reflective.")
                if pos.dignity:
                    lines.append(f"   Dignity: {pos.dignity.title()} (how comfortable the planet feels in this sign)")

        # Outer Planets (generational themes)
        lines.append("\n" + "━" * 60)
        lines.append("🌌 OUTER PLANETS & GENERATIONAL THEMES")
        lines.append("━" * 60)

        for planet in [Planet.JUPITER, Planet.SATURN, Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO]:
            if planet in chart.planets:
                pos = chart.planets[planet]
                lines.append(f"\n{planet.symbol} {planet.name} in {pos.sign.name}:")
                lines.append(f"   {planet.meaning}")
                lines.append(f"   {self._planet_in_sign_summary(planet, pos.sign)}")
                lines.append(f"   House {pos.house}: {self.planet_house_meanings[pos.house]}")
                if pos.retrograde:
                    lines.append("   Retrograde: Internal mastery and delayed external expression.")
                if pos.dignity:
                    lines.append(f"   Dignity: {pos.dignity.title()} (how comfortably the planet expresses here)")
        
        # Major Aspects
        if chart.aspects:
            lines.append("\n" + "━" * 60)
            lines.append("🔗 KEY ASPECTS & DYNAMICS")
            lines.append("━" * 60)
            
            # Group and prioritize aspects
            important_aspects = [asp for asp in chart.aspects if asp.orb <= 3.0]
            
            for aspect in important_aspects[:8]:  # Show top 8 tight aspects
                asp_info = self.aspect_interpretations.get(aspect.aspect_type, {})
                lines.append(f"\n{aspect.planet1.name} {aspect.aspect_type} {aspect.planet2.name}:")
                if asp_info:
                    lines.append(f"   {asp_info.get('meaning', '')}")
                strength = f"{aspect.strength} " if getattr(aspect, 'strength', '') else ""
                lines.append(f"   {strength}Orb: {aspect.orb:.1f}° (tighter orbs show stronger effects)")

        # Special Points & Lunar Nodes
        if chart.points:
            lines.append("\n" + "━" * 60)
            lines.append("✨ SPECIAL POINTS")
            lines.append("━" * 60)
            point_notes = {
                "North Node": "Growth path and soul development.",
                "South Node": "Comfort zone and past-life patterns.",
                "Chiron": "Core wound and healing journey.",
                "Lilith": "Raw instincts, autonomy, and shadow integration.",
                "Part of Fortune": "Ease, flow, and where life feels aligned.",
            }
            for key, point in chart.points.items():
                note = point_notes.get(key, "")
                lines.append(f"\n{point.symbol} {point.name} in {point.sign.name} (House {point.house}):")
                if note:
                    lines.append(f"   {note}")

        # House Emphasis
        house_counts = {}
        for pos in chart.planets.values():
            house_counts[pos.house] = house_counts.get(pos.house, 0) + 1
        if house_counts:
            lines.append("\n" + "━" * 60)
            lines.append("🏠 HOUSE EMPHASIS")
            lines.append("━" * 60)
            for house, count in sorted(house_counts.items(), key=lambda x: (-x[1], x[0]))[:4]:
                lines.append(f"House {house}: {count} planet(s) — {self.planet_house_meanings.get(house, '')}")
        
        # Chart Summary
        lines.append("\n" + "━" * 60)
        lines.append("📊 CHART OVERVIEW")
        lines.append("━" * 60)
        
        lines.append(f"\n🔥 Dominant Element: {chart.dominant_element}")
        element_meanings = {
            'Fire': 'Passionate, enthusiastic, and action-oriented',
            'Earth': 'Practical, grounded, and security-conscious',
            'Air': 'Intellectual, communicative, and social',
            'Water': 'Emotional, intuitive, and empathetic'
        }
        lines.append(f"   {element_meanings.get(chart.dominant_element, '')}")
        
        lines.append(f"\n⚡ Dominant Modality: {chart.dominant_modality}")
        modality_meanings = {
            'Cardinal': 'Initiating, leading, and starting new things',
            'Fixed': 'Stable, persistent, and maintaining what exists',
            'Mutable': 'Adaptable, flexible, and open to change'
        }
        lines.append(f"   {modality_meanings.get(chart.dominant_modality, '')}")
        
        lines.append(f"\n👑 Chart Ruler: {chart.chart_ruler.name}")
        lines.append(f"   Your chart ruler governs your overall life approach")

        if chart.chart_sect:
            lines.append(f"\n🌗 Chart Sect: {chart.chart_sect.title()}")
            lines.append("   Day charts emphasize visibility and outward expression; night charts focus on inner development.")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def generate_life_areas_interpretation(self, chart: BirthChart) -> str:
        """Generate interpretations for specific life areas."""
        lines = []
        
        lines.append("\n" + "=" * 60)
        lines.append("🌍 LIFE AREAS & THEMES".center(60))
        lines.append("=" * 60)
        
        # Career & Life Path
        lines.append("\n💼 Career & Life Purpose:")
        if Planet.SUN in chart.planets:
            sun_house = chart.planets[Planet.SUN].house
            lines.append(f"   Sun in House {sun_house}: {self.planet_house_meanings[sun_house]}")
        
        # Relationships
        lines.append("\n💕 Love & Relationships:")
        if Planet.VENUS in chart.planets:
            venus_pos = chart.planets[Planet.VENUS]
            lines.append(f"   Venus in {venus_pos.sign.name}: Attracts {venus_pos.sign.element.lower()} qualities in love")
            lines.append(f"   House {venus_pos.house}: {self.planet_house_meanings[venus_pos.house]}")
        
        # Communication Style
        lines.append("\n💬 Communication & Learning:")
        if Planet.MERCURY in chart.planets:
            mercury_pos = chart.planets[Planet.MERCURY]
            lines.append(f"   Mercury in {mercury_pos.sign.name}: {mercury_pos.sign.element} communication style")
        
        # Energy & Drive
        lines.append("\n⚡ Energy & Action:")
        if Planet.MARS in chart.planets:
            mars_pos = chart.planets[Planet.MARS]
            lines.append(f"   Mars in {mars_pos.sign.name}: {mars_pos.sign.element} approach to action")
        
        # Growth & Expansion
        lines.append("\n🎯 Growth & Opportunities:")
        if Planet.JUPITER in chart.planets:
            jupiter_pos = chart.planets[Planet.JUPITER]
            lines.append(f"   Jupiter in {jupiter_pos.sign.name}: Expansion through {jupiter_pos.sign.element.lower()} experiences")
            lines.append(f"   House {jupiter_pos.house}: {self.planet_house_meanings[jupiter_pos.house]}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)

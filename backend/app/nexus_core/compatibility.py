"""Astrological compatibility analysis between two charts."""
from typing import List, Tuple
from dataclasses import dataclass
from .birth_chart import BirthChart, Planet, ZodiacSign


@dataclass
class CompatibilityScore:
    """Compatibility analysis result."""
    overall_score: float  # 0-100
    romantic_score: float
    friendship_score: float
    communication_score: float
    emotional_score: float
    
    strengths: List[str]
    challenges: List[str]
    advice: List[str]
    
    synastry_highlights: List[str]


class CompatibilityAnalyzer:
    """Analyze compatibility between two birth charts."""
    
    def __init__(self):
        self.element_compatibility = self._load_element_compatibility()
        self.sign_compatibility = self._load_sign_compatibility()
    
    def _load_element_compatibility(self) -> dict:
        """Load elemental compatibility matrix."""
        return {
            ('Fire', 'Fire'): 0.8,
            ('Fire', 'Earth'): 0.4,
            ('Fire', 'Air'): 0.9,
            ('Fire', 'Water'): 0.5,
            ('Earth', 'Earth'): 0.8,
            ('Earth', 'Air'): 0.4,
            ('Earth', 'Water'): 0.7,
            ('Air', 'Air'): 0.8,
            ('Air', 'Water'): 0.5,
            ('Water', 'Water'): 0.8
        }
    
    def _load_sign_compatibility(self) -> dict:
        """Load zodiac sign compatibility descriptions."""
        return {
            ZodiacSign.ARIES: {
                'best_match': [ZodiacSign.LEO, ZodiacSign.SAGITTARIUS, ZodiacSign.GEMINI],
                'challenging': [ZodiacSign.CANCER, ZodiacSign.CAPRICORN]
            },
            ZodiacSign.TAURUS: {
                'best_match': [ZodiacSign.VIRGO, ZodiacSign.CAPRICORN, ZodiacSign.CANCER],
                'challenging': [ZodiacSign.LEO, ZodiacSign.AQUARIUS]
            },
            ZodiacSign.GEMINI: {
                'best_match': [ZodiacSign.LIBRA, ZodiacSign.AQUARIUS, ZodiacSign.ARIES],
                'challenging': [ZodiacSign.VIRGO, ZodiacSign.PISCES]
            },
            ZodiacSign.CANCER: {
                'best_match': [ZodiacSign.SCORPIO, ZodiacSign.PISCES, ZodiacSign.TAURUS],
                'challenging': [ZodiacSign.ARIES, ZodiacSign.LIBRA]
            },
            ZodiacSign.LEO: {
                'best_match': [ZodiacSign.ARIES, ZodiacSign.SAGITTARIUS, ZodiacSign.GEMINI],
                'challenging': [ZodiacSign.TAURUS, ZodiacSign.SCORPIO]
            },
            ZodiacSign.VIRGO: {
                'best_match': [ZodiacSign.TAURUS, ZodiacSign.CAPRICORN, ZodiacSign.CANCER],
                'challenging': [ZodiacSign.GEMINI, ZodiacSign.SAGITTARIUS]
            },
            ZodiacSign.LIBRA: {
                'best_match': [ZodiacSign.GEMINI, ZodiacSign.AQUARIUS, ZodiacSign.LEO],
                'challenging': [ZodiacSign.CANCER, ZodiacSign.CAPRICORN]
            },
            ZodiacSign.SCORPIO: {
                'best_match': [ZodiacSign.CANCER, ZodiacSign.PISCES, ZodiacSign.VIRGO],
                'challenging': [ZodiacSign.LEO, ZodiacSign.AQUARIUS]
            },
            ZodiacSign.SAGITTARIUS: {
                'best_match': [ZodiacSign.ARIES, ZodiacSign.LEO, ZodiacSign.LIBRA],
                'challenging': [ZodiacSign.VIRGO, ZodiacSign.PISCES]
            },
            ZodiacSign.CAPRICORN: {
                'best_match': [ZodiacSign.TAURUS, ZodiacSign.VIRGO, ZodiacSign.SCORPIO],
                'challenging': [ZodiacSign.ARIES, ZodiacSign.LIBRA]
            },
            ZodiacSign.AQUARIUS: {
                'best_match': [ZodiacSign.GEMINI, ZodiacSign.LIBRA, ZodiacSign.SAGITTARIUS],
                'challenging': [ZodiacSign.TAURUS, ZodiacSign.SCORPIO]
            },
            ZodiacSign.PISCES: {
                'best_match': [ZodiacSign.CANCER, ZodiacSign.SCORPIO, ZodiacSign.CAPRICORN],
                'challenging': [ZodiacSign.GEMINI, ZodiacSign.SAGITTARIUS]
            }
        }
    
    def analyze_compatibility(self, chart1: BirthChart, chart2: BirthChart, 
                            person1_name: str = "Person 1", 
                            person2_name: str = "Person 2") -> CompatibilityScore:
        """Analyze compatibility between two charts."""
        scores = []
        strengths = []
        challenges = []
        advice = []
        highlights = []
        
        # Sun-Sun compatibility (core identity)
        sun1 = chart1.get_sun_sign()
        sun2 = chart2.get_sun_sign()
        
        sun_score = self._calculate_sign_compatibility(sun1, sun2)
        scores.append(sun_score * 1.5)  # Weight Sun compatibility higher
        
        if sun_score > 0.7:
            strengths.append(f"Strong Sun sign compatibility ({sun1.name}-{sun2.name})")
        elif sun_score < 0.5:
            challenges.append(f"Sun signs require understanding ({sun1.name}-{sun2.name})")
        
        # Moon-Moon compatibility (emotional)
        moon1 = chart1.get_moon_sign()
        moon2 = chart2.get_moon_sign()
        
        moon_score = self._calculate_sign_compatibility(moon1, moon2)
        emotional_score = moon_score * 100
        scores.append(moon_score * 1.3)  # Weight Moon compatibility
        
        if moon_score > 0.7:
            strengths.append(f"Excellent emotional understanding (Moon {moon1.name}-{moon2.name})")
        else:
            advice.append("Work on understanding each other's emotional needs")
        
        # Venus-Mars synastry (romantic attraction)
        venus1 = chart1.planets.get(Planet.VENUS)
        mars2 = chart2.planets.get(Planet.MARS)
        
        if venus1 and mars2:
            venus_mars_score = self._calculate_sign_compatibility(venus1.sign, mars2.sign)
            romantic_score = venus_mars_score * 100
            scores.append(venus_mars_score)
            
            if venus_mars_score > 0.7:
                highlights.append(f"Strong romantic chemistry: {person1_name}'s Venus {venus1.sign.name} harmonizes with {person2_name}'s Mars {mars2.sign.name}")
        else:
            romantic_score = 60.0
        
        # Mercury-Mercury (communication)
        merc1 = chart1.planets.get(Planet.MERCURY)
        merc2 = chart2.planets.get(Planet.MERCURY)
        
        if merc1 and merc2:
            comm_score = self._calculate_sign_compatibility(merc1.sign, merc2.sign)
            communication_score = comm_score * 100
            scores.append(comm_score)
            
            if comm_score > 0.7:
                strengths.append("Easy communication and intellectual connection")
            else:
                advice.append("Practice active listening and be patient with different communication styles")
        else:
            communication_score = 60.0
        
        # Rising sign compatibility (how you present to each other)
        rising1 = chart1.get_rising_sign()
        rising2 = chart2.get_rising_sign()
        
        rising_score = self._calculate_sign_compatibility(rising1, rising2)
        scores.append(rising_score * 0.8)
        
        if rising_score > 0.7:
            strengths.append("Natural comfort and ease in each other's presence")
        
        # Element balance
        elem1 = chart1.dominant_element
        elem2 = chart2.dominant_element
        
        elem_compat = self._get_element_compatibility(elem1, elem2)
        scores.append(elem_compat)
        
        if elem_compat > 0.7:
            strengths.append(f"Complementary energies ({elem1}-{elem2})")
        elif elem_compat < 0.5:
            challenges.append(f"Different elemental natures require balance ({elem1}-{elem2})")
            advice.append(f"Appreciate your differences - {elem1} and {elem2} can learn from each other")
        
        # Calculate overall score
        overall_score = (sum(scores) / len(scores)) * 100
        
        # Friendship score (Air/Fire elements boost this)
        friendship_score = overall_score
        if elem1 in ['Air', 'Fire'] and elem2 in ['Air', 'Fire']:
            friendship_score += 10
        
        # Add general advice
        if overall_score < 50:
            advice.append("Focus on understanding and appreciating your differences")
            advice.append("Build on your individual strengths to support each other")
        elif overall_score < 70:
            advice.append("You have a solid foundation - work on areas of challenge")
        else:
            advice.append("You have natural harmony - continue nurturing your connection")
        
        if not challenges:
            challenges.append("Minor adjustments may be needed in daily interactions")
        
        return CompatibilityScore(
            overall_score=min(overall_score, 100.0),
            romantic_score=min(romantic_score, 100.0),
            friendship_score=min(friendship_score, 100.0),
            communication_score=min(communication_score, 100.0),
            emotional_score=min(emotional_score, 100.0),
            strengths=strengths,
            challenges=challenges,
            advice=advice,
            synastry_highlights=highlights
        )
    
    def _calculate_sign_compatibility(self, sign1: ZodiacSign, sign2: ZodiacSign) -> float:
        """Calculate compatibility between two zodiac signs."""
        if sign1 == sign2:
            return 0.75  # Same sign - understanding but can be too similar
        
        # Check if in best match list
        sign1_data = self.sign_compatibility.get(sign1, {})
        if sign2 in sign1_data.get('best_match', []):
            return 0.9
        
        if sign2 in sign1_data.get('challenging', []):
            return 0.4
        
        # Element compatibility
        elem_compat = self._get_element_compatibility(sign1.element, sign2.element)
        return elem_compat
    
    def _get_element_compatibility(self, elem1: str, elem2: str) -> float:
        """Get compatibility score between two elements."""
        key = (elem1, elem2) if (elem1, elem2) in self.element_compatibility else (elem2, elem1)
        return self.element_compatibility.get(key, 0.6)
    
    def format_compatibility_report(self, score: CompatibilityScore, 
                                   name1: str = "Person 1", 
                                   name2: str = "Person 2") -> str:
        """Format compatibility analysis as readable report."""
        lines = []
        
        lines.append("\n" + "=" * 60)
        lines.append(f"💕 COMPATIBILITY ANALYSIS: {name1} & {name2} 💕".center(60))
        lines.append("=" * 60)
        
        # Overall Score with visual indicator
        lines.append(f"\n🎯 Overall Compatibility: {score.overall_score:.0f}%")
        lines.append(self._get_compatibility_bar(score.overall_score))
        
        interpretation = self._interpret_score(score.overall_score)
        lines.append(f"   {interpretation}")
        
        # Detailed Scores
        lines.append("\n📊 Detailed Compatibility Scores:")
        lines.append(f"   💖 Romantic: {score.romantic_score:.0f}%")
        lines.append(f"   🤝 Friendship: {score.friendship_score:.0f}%")
        lines.append(f"   💬 Communication: {score.communication_score:.0f}%")
        lines.append(f"   💓 Emotional: {score.emotional_score:.0f}%")
        
        # Strengths
        lines.append("\n✨ Relationship Strengths:")
        for strength in score.strengths:
            lines.append(f"   ✓ {strength}")
        
        # Challenges
        lines.append("\n⚠️ Areas of Growth:")
        for challenge in score.challenges:
            lines.append(f"   • {challenge}")
        
        # Synastry Highlights
        if score.synastry_highlights:
            lines.append("\n🌟 Special Connections:")
            for highlight in score.synastry_highlights:
                lines.append(f"   ★ {highlight}")
        
        # Advice
        lines.append("\n💡 Relationship Advice:")
        for tip in score.advice:
            lines.append(f"   → {tip}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def _get_compatibility_bar(self, score: float) -> str:
        """Generate visual compatibility bar."""
        filled = int(score / 5)
        empty = 20 - filled
        return f"   [{'█' * filled}{'░' * empty}]"
    
    def _interpret_score(self, score: float) -> str:
        """Interpret compatibility score."""
        if score >= 85:
            return "Exceptional compatibility! Natural harmony and understanding."
        elif score >= 70:
            return "Strong compatibility with great potential for lasting connection."
        elif score >= 55:
            return "Good compatibility with some areas requiring attention."
        elif score >= 40:
            return "Moderate compatibility - success requires conscious effort."
        else:
            return "Challenging compatibility - significant differences to navigate."

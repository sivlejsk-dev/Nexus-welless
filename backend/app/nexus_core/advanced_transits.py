"""
Advanced Transit Forecast System
Personalized predictions based on current planetary positions affecting user's birth chart
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import math

from .expertise import PLANETS, ZODIAC_SIGNS, ASPECTS


class TransitIntensity(Enum):
    """Transit impact levels"""
    MAJOR = "major"  # Life-changing
    SIGNIFICANT = "significant"  # Important
    MODERATE = "moderate"  # Notable
    MINOR = "minor"  # Subtle


class TransitType(Enum):
    """Types of transits"""
    CONJUNCTION = "conjunction"
    SEXTILE = "sextile"
    SQUARE = "square"
    TRINE = "trine"
    OPPOSITION = "opposition"
    QUINCUNX = "quincunx"


@dataclass
class ActiveTransit:
    """Represents an active planetary transit"""
    transiting_planet: str
    natal_planet: str
    transit_type: str
    exact_date: datetime
    orb: float  # Degrees from exact
    intensity: TransitIntensity
    meaning: str
    advice: str
    duration_days: int
    peak_dates: List[datetime]


@dataclass
class TransitForecast:
    """Complete transit forecast for a period"""
    start_date: datetime
    end_date: datetime
    active_transits: List[ActiveTransit]
    daily_guidance: Dict[str, str]  # Date -> guidance
    major_themes: List[str]
    best_days: List[Tuple[datetime, str]]  # Date, reason
    challenging_days: List[Tuple[datetime, str]]
    opportunities: List[str]
    warnings: List[str]


class PersonalizedTransitEngine:
    """Calculate and interpret personalized transits"""
    
    def __init__(self):
        # Current planetary positions (simplified - in production use Swiss Ephemeris)
        # These are approximate positions for January 2, 2026
        self.current_positions = {
            'Sun': {'sign': 'Capricorn', 'degree': 11.5},
            'Moon': {'sign': 'Pisces', 'degree': 23.0},
            'Mercury': {'sign': 'Capricorn', 'degree': 28.0},
            'Venus': {'sign': 'Aquarius', 'degree': 5.0},
            'Mars': {'sign': 'Cancer', 'degree': 15.0},
            'Jupiter': {'sign': 'Gemini', 'degree': 12.0},
            'Saturn': {'sign': 'Pisces', 'degree': 18.0},
            'Uranus': {'sign': 'Taurus', 'degree': 25.0},
            'Neptune': {'sign': 'Pisces', 'degree': 28.0},
            'Pluto': {'sign': 'Aquarius', 'degree': 2.0}
        }
        
        # Transit interpretation templates
        self.transit_meanings = self._build_transit_meanings()
    
    def _build_transit_meanings(self) -> Dict[str, Dict[str, str]]:
        """Build comprehensive transit interpretation database"""
        return {
            # Outer planet transits (most important)
            'Pluto_Sun': {
                'conjunction': "Major transformation of identity and life purpose. Death and rebirth of ego. Power struggles possible.",
                'square': "Crisis of power and control. Deep psychological transformation required. Resistance meets force.",
                'opposition': "Confrontation with shadow self. Power dynamics in relationships. Forced evolution.",
                'trine': "Natural empowerment and transformation. Ability to regenerate easily. Magnetic personal power.",
                'sextile': "Opportunities for positive transformation. Access to hidden strengths. Subtle empowerment."
            },
            'Pluto_Moon': {
                'conjunction': "Emotional death and rebirth. Deep psychological healing. Family/home transformation.",
                'square': "Emotional crisis and catharsis. Compulsive feelings. Need to release buried emotions.",
                'opposition': "Emotional power struggles. Deep feelings surface. Relationship intensity.",
                'trine': "Natural emotional healing ability. Deep intuitive insights. Powerful emotional connections.",
                'sextile': "Gentle emotional transformation. Intuitive growth. Healing opportunities."
            },
            'Neptune_Sun': {
                'conjunction': "Spiritual awakening and dissolution of ego. Dreams and confusion about identity.",
                'square': "Confusion about life direction. Illusions and deception. Need for grounding.",
                'opposition': "Relationship confusion. Idealization vs reality. Spiritual partnership lessons.",
                'trine': "Natural spiritual gifts activated. Creative inspiration flowing. Compassion increases.",
                'sextile': "Subtle spiritual growth. Creative opportunities. Imagination enhanced."
            },
            'Neptune_Moon': {
                'conjunction': "Psychic sensitivity heightened. Emotional boundaries dissolve. Spiritual mother issues.",
                'square': "Emotional confusion and deception. Addiction risks. Need clear boundaries.",
                'opposition': "Emotional idealization. Codependency patterns. Spiritual relationship lessons.",
                'trine': "Natural psychic abilities. Compassionate feelings. Artistic inspiration.",
                'sextile': "Gentle emotional opening. Creative feelings. Spiritual opportunities."
            },
            'Uranus_Sun': {
                'conjunction': "Revolutionary changes in identity. Liberation from old self. Sudden awakening.",
                'square': "Sudden life disruptions. Need for freedom. Rebellion against restrictions.",
                'opposition': "Unexpected relationship changes. Freedom vs commitment. Sudden separations.",
                'trine': "Natural innovation and originality. Easy changes. Exciting opportunities.",
                'sextile': "Gentle awakening. New perspectives. Creative breakthroughs."
            },
            'Uranus_Moon': {
                'conjunction': "Emotional liberation. Sudden changes at home. Breaking emotional patterns.",
                'square': "Emotional instability. Sudden mood changes. Need for emotional freedom.",
                'opposition': "Unexpected emotional events. Relationship surprises. Home disruptions.",
                'trine': "Natural emotional independence. Exciting feelings. Easy changes.",
                'sextile': "Gentle emotional breakthroughs. New feelings. Refreshing changes."
            },
            'Saturn_Sun': {
                'conjunction': "Major life restructuring. Taking on serious responsibilities. Maturity test.",
                'square': "Saturn square: Life obstacles and tests. Hard work required. Patience needed.",
                'opposition': "Relationship responsibilities. Commitment tests. Authority figures challenge.",
                'trine': "Natural discipline and achievement. Hard work pays off. Stable progress.",
                'sextile': "Opportunities through effort. Mentorship available. Steady advancement."
            },
            'Saturn_Moon': {
                'conjunction': "Emotional maturity required. Family responsibilities. Dealing with past.",
                'square': "Emotional depression possible. Isolation feelings. Hard emotional work needed.",
                'opposition': "Relationship duties. Emotional tests. Balancing needs vs obligations.",
                'trine': "Emotional stability achieved. Family structures. Practical nurturing.",
                'sextile': "Gradual emotional security. Supportive structures. Steady feelings."
            },
            'Jupiter_Sun': {
                'conjunction': "Major expansion of opportunities. Optimism and growth. Success potential.",
                'square': "Overextension and excess. Too many opportunities. Need for moderation.",
                'opposition': "Partnership benefits. Others bring opportunities. Balance growth.",
                'trine': "Natural good fortune. Easy success. Optimistic period.",
                'sextile': "Fortunate opportunities. Growth through others. Positive connections."
            },
            'Jupiter_Moon': {
                'conjunction': "Emotional abundance. Family growth. Generosity of spirit.",
                'square': "Emotional excess. Overindulgence. Too much of good thing.",
                'opposition': "Relationship generosity. Emotional growth through others.",
                'trine': "Natural emotional wellbeing. Lucky home life. Generous feelings.",
                'sextile': "Emotional opportunities. Growth in nurturing. Positive family."
            },
            # Inner planet transits (faster moving, more immediate)
            'Mars_Sun': {
                'conjunction': "Energy surge. Initiative and action. Assert yourself.",
                'square': "Conflicts and frustration. Anger management needed. Slow down.",
                'opposition': "Confrontations possible. Competitive situations. Channel energy wisely.",
                'trine': "Natural courage and drive. Physical vitality. Action flows easily.",
                'sextile': "Opportunities to assert. Productive energy. Motivated action."
            },
            'Venus_Sun': {
                'conjunction': "Charm and attractiveness increased. Love and money flow. Enjoy beauty.",
                'square': "Relationship tensions. Financial indecision. Balance give and take.",
                'opposition': "Relationship focus. Attractions. Compromise needed.",
                'trine': "Natural harmony and beauty. Love flows easily. Financial ease.",
                'sextile': "Pleasant opportunities. Social connections. Artistic pursuits."
            }
        }
    
    def calculate_current_transits(self, natal_chart: Dict, current_date: Optional[datetime] = None) -> List[ActiveTransit]:
        """
        Calculate all active transits for a natal chart
        
        Args:
            natal_chart: Dict with natal positions like {'Sun': {'sign': 'Leo', 'degree': 15}, ...}
        
        Returns:
            List of ActiveTransit objects
        """
        active_transits = []
        
        # Allow caller-specified date for compatibility (currently not ephemeris-driven)
        _ = current_date or datetime.now()

        # Check each transiting planet against natal planets
        for trans_planet, trans_pos in self.current_positions.items():
            for natal_planet, natal_pos in natal_chart.items():
                # Skip metadata and malformed entries
                if not isinstance(natal_pos, dict):
                    continue
                if 'sign' not in natal_pos or 'degree' not in natal_pos:
                    continue

                # Calculate aspect between transiting and natal planet
                aspect, orb = self._calculate_aspect(trans_pos, natal_pos)
                
                if aspect and orb <= 3.0:  # Within 3-degree orb
                    # Get interpretation
                    meaning, advice = self._interpret_transit(
                        trans_planet, natal_planet, aspect
                    )
                    
                    # Determine intensity
                    intensity = self._determine_intensity(
                        trans_planet, natal_planet, aspect, orb
                    )
                    
                    # Calculate duration
                    duration = self._estimate_duration(trans_planet, aspect)
                    
                    transit = ActiveTransit(
                        transiting_planet=trans_planet,
                        natal_planet=natal_planet,
                        transit_type=aspect,
                        exact_date=datetime.now(),  # Simplified
                        orb=orb,
                        intensity=intensity,
                        meaning=meaning,
                        advice=advice,
                        duration_days=duration,
                        peak_dates=[datetime.now()]
                    )
                    
                    active_transits.append(transit)
        
        # Sort by intensity
        active_transits.sort(
            key=lambda t: ['major', 'significant', 'moderate', 'minor'].index(t.intensity.value)
        )
        
        return active_transits

    def analyze_current_transits(self, natal_chart: Dict) -> Dict[str, Any]:
        """Compatibility wrapper for routers expecting summarized transit analysis."""
        transits = self.calculate_current_transits(natal_chart)

        major = [t for t in transits if t.intensity == TransitIntensity.MAJOR]
        significant = [t for t in transits if t.intensity == TransitIntensity.SIGNIFICANT]

        major_aspects = [
            f"{t.transiting_planet} {t.transit_type} natal {t.natal_planet} (orb {t.orb:.1f}°)"
            for t in (major + significant)[:8]
        ]

        opportunities = "; ".join(self._generate_opportunities(transits)[:3]) or "Use harmonious windows for important actions"
        challenges = "; ".join(self._generate_warnings(transits)[:3]) or "No major warnings"

        if major:
            summary = "Major long-term transits are active. Focus on intentional change and strategic timing."
        elif significant:
            summary = "Several significant transits are active. Prioritize key decisions and avoid impulsive reactions."
        else:
            summary = "Current transits are relatively light. This is a stable period for steady progress."

        return {
            "major_aspects": major_aspects,
            "summary": summary,
            "opportunities": opportunities,
            "challenges": challenges,
            "count": len(transits),
        }
    
    def _calculate_aspect(self, pos1: Dict, pos2: Dict) -> Tuple[Optional[str], float]:
        """Calculate aspect between two positions"""
        # Simplified calculation - convert sign + degree to absolute degree
        degree1 = self._sign_to_degrees(pos1['sign']) + pos1['degree']
        degree2 = self._sign_to_degrees(pos2['sign']) + pos2['degree']
        
        # Calculate angular difference
        diff = abs(degree1 - degree2)
        if diff > 180:
            diff = 360 - diff
        
        # Check aspects with orbs
        aspects = {
            'conjunction': (0, 8),
            'sextile': (60, 4),
            'square': (90, 7),
            'trine': (120, 8),
            'quincunx': (150, 2),
            'opposition': (180, 8)
        }
        
        for aspect_name, (angle, max_orb) in aspects.items():
            orb = abs(diff - angle)
            if orb <= max_orb:
                return aspect_name, orb
        
        return None, 999
    
    def _sign_to_degrees(self, sign: str) -> float:
        """Convert zodiac sign to degrees (0-360)"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        return signs.index(sign) * 30
    
    def _interpret_transit(self, trans_planet: str, natal_planet: str, aspect: str) -> Tuple[str, str]:
        """Get meaning and advice for a transit"""
        key = f"{trans_planet}_{natal_planet}"
        
        if key in self.transit_meanings:
            meaning = self.transit_meanings[key].get(aspect, "Significant planetary interaction.")
            
            # Generate advice based on transit type
            if aspect in ['square', 'opposition']:
                advice = f"Navigate {trans_planet} challenges with {natal_planet} awareness. Work through tensions consciously."
            elif aspect in ['trine', 'sextile']:
                advice = f"Embrace opportunities from {trans_planet} harmonizing with {natal_planet}. Flow with natural ease."
            else:  # conjunction
                advice = f"Major {trans_planet} energy merging with {natal_planet}. Be conscious of this powerful blend."
        else:
            meaning = f"{trans_planet} {aspect} your natal {natal_planet}: A time of planetary interaction."
            advice = f"Pay attention to how {trans_planet} themes affect your {natal_planet} areas."
        
        return meaning, advice
    
    def _determine_intensity(self, trans_planet: str, natal_planet: str, 
                           aspect: str, orb: float) -> TransitIntensity:
        """Determine transit intensity based on planets, aspect, and orb"""
        # Outer planets are more intense
        outer_planets = ['Pluto', 'Neptune', 'Uranus']
        social_planets = ['Saturn', 'Jupiter']
        
        # Check if involving outer planets
        if trans_planet in outer_planets:
            if aspect in ['conjunction', 'square', 'opposition']:
                return TransitIntensity.MAJOR
            else:
                return TransitIntensity.SIGNIFICANT
        
        if trans_planet in social_planets:
            if aspect in ['conjunction', 'square', 'opposition']:
                return TransitIntensity.SIGNIFICANT
            else:
                return TransitIntensity.MODERATE
        
        # Inner planets (faster moving)
        if aspect in ['conjunction', 'square', 'opposition'] and orb < 1.0:
            return TransitIntensity.MODERATE
        else:
            return TransitIntensity.MINOR
    
    def _estimate_duration(self, planet: str, aspect: str) -> int:
        """Estimate transit duration in days"""
        # Outer planets: long-lasting
        if planet in ['Pluto', 'Neptune', 'Uranus']:
            return 180  # ~6 months with retrograde
        
        if planet in ['Saturn', 'Jupiter']:
            return 60  # ~2 months
        
        if planet == 'Mars':
            return 21  # ~3 weeks
        
        if planet in ['Venus', 'Mercury']:
            return 7  # ~1 week
        
        if planet in ['Sun', 'Moon']:
            return 2  # ~2 days
        
        return 14  # Default 2 weeks
    
    def generate_daily_guidance(self, natal_chart: Dict, date: datetime) -> str:
        """Generate personalized daily guidance based on transits"""
        transits = self.calculate_current_transits(natal_chart)
        
        if not transits:
            return "Today is a quiet day astrologically. Focus on routine matters and self-care."
        
        # Get most important transit
        main_transit = transits[0]
        
        guidance = f"**Today's Cosmic Weather for You**\n\n"
        guidance += f"🌟 Primary Transit: {main_transit.transiting_planet} {main_transit.transit_type} your natal {main_transit.natal_planet}\n\n"
        guidance += f"{main_transit.meaning}\n\n"
        guidance += f"**Advice**: {main_transit.advice}\n\n"
        
        # Add secondary transits
        if len(transits) > 1:
            guidance += "**Also active today**:\n"
            for transit in transits[1:4]:  # Show up to 3 more
                guidance += f"• {transit.transiting_planet} → {transit.natal_planet}: {transit.transit_type}\n"
        
        return guidance
    
    def forecast_period(self, natal_chart: Dict, days: int = 30) -> TransitForecast:
        """Generate forecast for upcoming period"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        # Get current transits
        active_transits = self.calculate_current_transits(natal_chart)
        
        # Generate daily guidance
        daily_guidance = {}
        for i in range(days):
            date = start_date + timedelta(days=i)
            guidance = self.generate_daily_guidance(natal_chart, date)
            daily_guidance[date.strftime('%Y-%m-%d')] = guidance
        
        # Identify major themes
        major_themes = self._identify_themes(active_transits)
        
        # Find best and challenging days
        best_days, challenging_days = self._identify_best_worst_days(active_transits, days)
        
        # Generate opportunities and warnings
        opportunities = self._generate_opportunities(active_transits)
        warnings = self._generate_warnings(active_transits)
        
        return TransitForecast(
            start_date=start_date,
            end_date=end_date,
            active_transits=active_transits,
            daily_guidance=daily_guidance,
            major_themes=major_themes,
            best_days=best_days,
            challenging_days=challenging_days,
            opportunities=opportunities,
            warnings=warnings
        )
    
    def _identify_themes(self, transits: List[ActiveTransit]) -> List[str]:
        """Identify major themes from active transits"""
        themes = []
        
        for transit in transits:
            if transit.intensity == TransitIntensity.MAJOR:
                if 'Pluto' in transit.transiting_planet:
                    themes.append("Deep transformation and empowerment")
                elif 'Neptune' in transit.transiting_planet:
                    themes.append("Spiritual awakening and dissolving boundaries")
                elif 'Uranus' in transit.transiting_planet:
                    themes.append("Revolutionary changes and liberation")
                elif 'Saturn' in transit.transiting_planet:
                    themes.append("Building structures and facing responsibilities")
        
        return themes[:3]  # Top 3 themes
    
    def _identify_best_worst_days(self, transits: List[ActiveTransit], days: int) -> Tuple[List, List]:
        """Identify best and most challenging days"""
        best_days = []
        challenging_days = []
        
        # Simplified - look at transit types
        for transit in transits:
            if transit.intensity in [TransitIntensity.MAJOR, TransitIntensity.SIGNIFICANT]:
                if transit.transit_type in ['trine', 'sextile']:
                    best_days.append((transit.exact_date, f"{transit.transiting_planet} harmony"))
                elif transit.transit_type in ['square', 'opposition']:
                    challenging_days.append((transit.exact_date, f"{transit.transiting_planet} challenge"))
        
        return best_days[:5], challenging_days[:5]
    
    def _generate_opportunities(self, transits: List[ActiveTransit]) -> List[str]:
        """Generate list of opportunities from transits"""
        opportunities = []
        
        for transit in transits:
            if transit.transit_type in ['trine', 'sextile', 'conjunction']:
                if 'Jupiter' in transit.transiting_planet:
                    opportunities.append(f"Growth and expansion in {transit.natal_planet} areas")
                elif 'Venus' in transit.transiting_planet:
                    opportunities.append(f"Love, beauty, and harmony in {transit.natal_planet} matters")
                elif 'Sun' in transit.transiting_planet:
                    opportunities.append(f"Self-expression and vitality in {transit.natal_planet} domains")
        
        return opportunities[:5]
    
    def _generate_warnings(self, transits: List[ActiveTransit]) -> List[str]:
        """Generate warnings for challenging transits"""
        warnings = []
        
        for transit in transits:
            if transit.transit_type in ['square', 'opposition']:
                if transit.intensity == TransitIntensity.MAJOR:
                    warnings.append(f"Major {transit.transiting_planet} challenge requires conscious navigation")
                elif 'Mars' in transit.transiting_planet:
                    warnings.append(f"Potential conflicts or frustration in {transit.natal_planet} areas")
                elif 'Saturn' in transit.transiting_planet:
                    warnings.append(f"Tests and obstacles in {transit.natal_planet} domains - patience required")
        
        return warnings[:5]
    
    def get_transit_report(self, natal_chart: Dict, verbose: bool = True) -> str:
        """Generate human-readable transit report"""
        transits = self.calculate_current_transits(natal_chart)
        
        if not transits:
            return "No major transits currently active for your chart."
        
        report = "**PERSONALIZED TRANSIT REPORT**\n"
        report += f"Generated: {datetime.now().strftime('%B %d, %Y')}\n\n"
        
        # Major transits
        major = [t for t in transits if t.intensity == TransitIntensity.MAJOR]
        if major:
            report += "🔴 **MAJOR LIFE TRANSITS** (Life-changing)\n\n"
            for transit in major:
                report += f"**{transit.transiting_planet} {transit.transit_type.upper()} Natal {transit.natal_planet}**\n"
                report += f"Exact: {transit.exact_date.strftime('%B %d, %Y')} (Orb: {transit.orb:.1f}°)\n"
                report += f"Duration: ~{transit.duration_days} days\n"
                report += f"{transit.meaning}\n"
                report += f"**Advice**: {transit.advice}\n\n"
        
        # Significant transits
        significant = [t for t in transits if t.intensity == TransitIntensity.SIGNIFICANT]
        if significant and verbose:
            report += "🟡 **SIGNIFICANT TRANSITS** (Important)\n\n"
            for transit in significant[:3]:  # Show top 3
                report += f"• {transit.transiting_planet} {transit.transit_type} {transit.natal_planet}\n"
                report += f"  {transit.meaning}\n\n"
        
        # Current guidance
        report += "**TODAY'S GUIDANCE**\n\n"
        report += self.generate_daily_guidance(natal_chart, datetime.now())
        
        return report


# Global instance
transit_engine = PersonalizedTransitEngine()

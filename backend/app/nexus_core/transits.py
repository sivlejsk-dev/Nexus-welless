"""Transit forecasts - current planetary influences."""
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass
from .birth_chart import BirthChart, Planet, ZodiacSign, BirthChartGenerator


@dataclass
class Transit:
    """Single transit influence."""
    transiting_planet: Planet
    natal_planet: Planet
    aspect_type: str
    start_date: datetime
    peak_date: datetime
    end_date: datetime
    influence: str
    advice: str


@dataclass
class TransitForecast:
    """Complete transit forecast."""
    forecast_period: str
    current_transits: List[Transit]
    upcoming_transits: List[Transit]
    major_themes: List[str]
    opportunities: List[str]
    challenges: List[str]


class TransitForecaster:
    """Generate transit forecasts for birth charts."""
    
    def __init__(self):
        self.chart_generator = BirthChartGenerator()
        self.transit_meanings = self._load_transit_meanings()
    
    def _load_transit_meanings(self) -> Dict:
        """Load transit interpretation templates."""
        return {
            (Planet.JUPITER, 'conjunction'): {
                'influence': 'Expansion and growth in the area of life ruled by the natal planet',
                'advice': 'Seize opportunities for growth and take calculated risks'
            },
            (Planet.SATURN, 'conjunction'): {
                'influence': 'Lessons, restructuring, and building solid foundations',
                'advice': 'Focus on discipline, responsibility, and long-term planning'
            },
            (Planet.URANUS, 'conjunction'): {
                'influence': 'Sudden changes, breakthroughs, and liberation',
                'advice': 'Embrace change and be open to innovative approaches'
            },
            (Planet.NEPTUNE, 'conjunction'): {
                'influence': 'Spiritual awakening, creativity, and dissolution of boundaries',
                'advice': 'Trust your intuition but stay grounded in reality'
            },
            (Planet.PLUTO, 'conjunction'): {
                'influence': 'Deep transformation and regeneration',
                'advice': 'Allow old patterns to die to make room for rebirth'
            },
            (Planet.SATURN, 'square'): {
                'influence': 'Tests, obstacles, and necessary challenges for growth',
                'advice': 'Face challenges head-on and build inner strength'
            },
            (Planet.JUPITER, 'trine'): {
                'influence': 'Ease, luck, and beneficial opportunities',
                'advice': 'Make the most of favorable conditions and expand horizons'
            },
            (Planet.SATURN, 'opposition'): {
                'influence': 'Relationship tests and finding balance between opposing needs',
                'advice': 'Seek balance and take responsibility in partnerships'
            }
        }
    
    def generate_current_transits(self, birth_chart: BirthChart, 
                                 forecast_days: int = 30) -> TransitForecast:
        """Generate transit forecast for specified period."""
        current_date = datetime.now()
        end_date = current_date + timedelta(days=forecast_days)
        
        # Calculate current sky positions
        current_positions = self._calculate_current_sky(current_date)
        
        # Find active transits
        current_transits = []
        upcoming_transits = []
        major_themes = []
        opportunities = []
        challenges = []
        
        # Check major planet transits
        major_planets = [Planet.JUPITER, Planet.SATURN, Planet.URANUS, 
                        Planet.NEPTUNE, Planet.PLUTO]
        
        for trans_planet in major_planets:
            if trans_planet not in current_positions:
                continue
            
            trans_position = current_positions[trans_planet]
            
            # Check aspects to natal planets
            for natal_planet, natal_pos in birth_chart.planets.items():
                natal_degree = natal_pos.sign.start_degree + natal_pos.degree
                
                # Check for major aspects
                aspect, orb = self._check_aspect(trans_position, natal_degree)
                
                if aspect and orb <= 3.0:  # Tight orb for active transit
                    meaning = self.transit_meanings.get(
                        (trans_planet, aspect),
                        {'influence': f'{trans_planet.name} influencing {natal_planet.name}',
                         'advice': 'Be aware of this planetary influence'}
                    )
                    
                    transit = Transit(
                        transiting_planet=trans_planet,
                        natal_planet=natal_planet,
                        aspect_type=aspect,
                        start_date=current_date - timedelta(days=7),
                        peak_date=current_date,
                        end_date=current_date + timedelta(days=7),
                        influence=meaning['influence'],
                        advice=meaning['advice']
                    )
                    
                    current_transits.append(transit)
                    
                    # Categorize by planet type
                    if trans_planet == Planet.JUPITER:
                        opportunities.append(f"Jupiter {aspect} {natal_planet.name}: Growth opportunities")
                        major_themes.append("Expansion and optimism")
                    elif trans_planet == Planet.SATURN:
                        challenges.append(f"Saturn {aspect} {natal_planet.name}: Lessons and structure")
                        major_themes.append("Discipline and responsibility")
                    elif trans_planet in [Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO]:
                        major_themes.append("Transformation and change")
        
        # Add general themes if none found
        if not major_themes:
            major_themes.append("A period of consolidation and integration")
        
        if not opportunities:
            opportunities.append("Focus on personal development and self-awareness")
        
        if not challenges:
            challenges.append("Maintain balance and stay true to your values")
        
        period_desc = f"{forecast_days} days from {current_date.strftime('%B %d, %Y')}"
        
        return TransitForecast(
            forecast_period=period_desc,
            current_transits=current_transits,
            upcoming_transits=upcoming_transits,
            major_themes=list(set(major_themes)),
            opportunities=opportunities,
            challenges=challenges
        )
    
    def _calculate_current_sky(self, date: datetime) -> Dict[Planet, float]:
        """Calculate current positions of planets."""
        jd = self.chart_generator.calculate_julian_day(date)
        
        positions = {}
        
        # Calculate positions for major planets
        positions[Planet.JUPITER] = self.chart_generator.calculate_planet_position(Planet.JUPITER, jd)
        positions[Planet.SATURN] = self.chart_generator.calculate_planet_position(Planet.SATURN, jd)
        positions[Planet.URANUS] = self.chart_generator.calculate_planet_position(Planet.URANUS, jd)
        positions[Planet.NEPTUNE] = self.chart_generator.calculate_planet_position(Planet.NEPTUNE, jd)
        positions[Planet.PLUTO] = self.chart_generator.calculate_planet_position(Planet.PLUTO, jd)
        
        return positions
    
    def _check_aspect(self, degree1: float, degree2: float) -> tuple:
        """Check if two degrees form a major aspect."""
        diff = abs(degree1 - degree2)
        if diff > 180:
            diff = 360 - diff
        
        aspects = {
            0: ('conjunction', 8.0),
            60: ('sextile', 6.0),
            90: ('square', 7.0),
            120: ('trine', 8.0),
            180: ('opposition', 8.0)
        }
        
        for angle, (aspect_name, max_orb) in aspects.items():
            orb = abs(diff - angle)
            if orb <= max_orb:
                return aspect_name, orb
        
        return None, 999
    
    def generate_monthly_forecast(self, birth_chart: BirthChart) -> str:
        """Generate monthly astrological forecast."""
        forecast = self.generate_current_transits(birth_chart, forecast_days=30)
        return self.format_transit_forecast(forecast)
    
    def format_transit_forecast(self, forecast: TransitForecast) -> str:
        """Format transit forecast as readable text."""
        lines = []
        
        lines.append("\n" + "=" * 60)
        lines.append("🌙 TRANSIT FORECAST 🌙".center(60))
        lines.append("=" * 60)
        
        lines.append(f"\n📅 Forecast Period: {forecast.forecast_period}")
        
        # Major Themes
        lines.append("\n🎯 Major Themes:")
        for theme in forecast.major_themes:
            lines.append(f"   • {theme}")
        
        # Current Active Transits
        if forecast.current_transits:
            lines.append("\n⚡ Active Transits:")
            for transit in forecast.current_transits:
                lines.append(f"\n   {transit.transiting_planet.symbol} {transit.transiting_planet.name} "
                           f"{transit.aspect_type} Natal {transit.natal_planet.symbol} {transit.natal_planet.name}")
                lines.append(f"   Peak: {transit.peak_date.strftime('%B %d, %Y')}")
                lines.append(f"   Influence: {transit.influence}")
                lines.append(f"   💡 Advice: {transit.advice}")
        
        # Opportunities
        lines.append("\n✨ Opportunities:")
        for opp in forecast.opportunities:
            lines.append(f"   → {opp}")
        
        # Challenges
        lines.append("\n⚠️ Challenges to Navigate:")
        for challenge in forecast.challenges:
            lines.append(f"   • {challenge}")
        
        lines.append("\n💫 Remember: Transits highlight energies, but you have free will in how you respond.")
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)

"""
Predictive Astrology Suite
Solar Returns, Progressions, and Profections for life timing
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

from .expertise import ZODIAC_SIGNS, PLANETS, HOUSE_MEANINGS

# Back-compat shape expected by this module
HOUSES = [HOUSE_MEANINGS[i] for i in sorted(HOUSE_MEANINGS.keys())]


class PredictionType(Enum):
    """Types of predictive techniques"""
    SOLAR_RETURN = "solar_return"
    SECONDARY_PROGRESSION = "secondary_progression"
    PROFECTION = "profection"
    TRANSIT = "transit"


@dataclass
class YearlyForecast:
    """Annual forecast from solar return"""
    year: int
    solar_return_date: datetime
    major_themes: List[str]
    opportunities: List[str]
    challenges: List[str]
    career_focus: str
    relationship_focus: str
    health_focus: str
    spiritual_focus: str
    best_months: List[str]
    challenging_months: List[str]
    overall_tone: str


@dataclass
class ProgressedChart:
    """Secondary progressions for life timing"""
    current_age: int
    progressed_sun_sign: str
    progressed_moon_sign: str
    progressed_ascendant: str
    life_phase: str
    emotional_evolution: str
    identity_shift: str
    major_progressions: List[str]
    timing_insights: List[str]


@dataclass
class ProfectionYear:
    """Annual profections (traditional timing)"""
    age: int
    profection_house: int
    profection_sign: str
    ruling_planet: str
    year_theme: str
    life_area_focus: str
    opportunities: List[str]
    lessons: List[str]


@dataclass
class LifeTimingForecast:
    """Complete life timing analysis"""
    current_phase: str
    solar_return_forecast: YearlyForecast
    progressions: ProgressedChart
    profection: ProfectionYear
    integrated_forecast: str
    major_life_events_timing: List[str]
    decision_guidance: Dict[str, str]


class PredictiveSuite:
    """Advanced predictive astrology techniques"""
    
    def __init__(self):
        self.solar_return_themes = self._build_solar_return_database()
        self.progression_meanings = self._build_progression_database()
        self.profection_themes = self._build_profection_database()
    
    def _build_solar_return_database(self) -> Dict[str, Dict[str, str]]:
        """Build solar return interpretation database"""
        return {
            # Solar return Sun in houses
            'SR_Sun_1': {
                'theme': "Year of self-focus and new beginnings",
                'description': "You take center stage this year. Focus on your identity, appearance, and personal goals. Time to prioritize yourself."
            },
            'SR_Sun_2': {
                'theme': "Year of financial focus and values",
                'description': "Money, possessions, and self-worth are highlighted. Build resources and clarify what you truly value."
            },
            'SR_Sun_3': {
                'theme': "Year of communication and learning",
                'description': "Writing, teaching, local travel, and siblings feature prominently. Your voice matters this year."
            },
            'SR_Sun_4': {
                'theme': "Year of home, family, and roots",
                'description': "Focus on domestic life, family matters, and emotional foundations. Renovations or moves possible."
            },
            'SR_Sun_5': {
                'theme': "Year of creativity, romance, and joy",
                'description': "Express yourself creatively. Romance, children, and pleasure activities are highlighted. Have fun!"
            },
            'SR_Sun_6': {
                'theme': "Year of health, work, and service",
                'description': "Job matters and daily routines take priority. Focus on health, fitness, and being of service."
            },
            'SR_Sun_7': {
                'theme': "Year of relationships and partnerships",
                'description': "Marriage, business partnerships, and one-on-one relationships are the main focus. Year of 'the other'."
            },
            'SR_Sun_8': {
                'theme': "Year of transformation and shared resources",
                'description': "Deep psychological changes, intimacy, taxes, inheritance, and joint finances feature prominently."
            },
            'SR_Sun_9': {
                'theme': "Year of expansion, travel, and philosophy",
                'description': "Long-distance travel, higher education, publishing, and spiritual seeking are emphasized."
            },
            'SR_Sun_10': {
                'theme': "Year of career and public recognition",
                'description': "Career advancement, public visibility, and achievements are highlighted. You're in the spotlight professionally."
            },
            'SR_Sun_11': {
                'theme': "Year of friendships and future goals",
                'description': "Social networks, group activities, and long-term aspirations take center stage. Community involvement."
            },
            'SR_Sun_12': {
                'theme': "Year of retreat, spirituality, and endings",
                'description': "Time for introspection, spiritual work, and releasing the past. Quiet preparation for next year's rebirth."
            },
            
            # Solar return Moon in houses (emotional focus)
            'SR_Moon_4': {
                'theme': "Emotional focus on home and family",
                'description': "Deep emotional involvement with family and domestic life. Security needs high."
            },
            'SR_Moon_7': {
                'theme': "Emotional focus on relationships",
                'description': "Emotional needs met through partnerships. Relationships emotionally intense this year."
            },
            'SR_Moon_10': {
                'theme': "Emotional focus on career",
                'description': "Emotionally invested in career and public life. Need for professional recognition."
            }
        }
    
    def _build_progression_database(self) -> Dict[str, str]:
        """Build secondary progressions interpretation database"""
        return {
            # Progressed Sun changing signs
            'Prog_Sun_Aries': "Entering a 30-year cycle of self-assertion and independence. Time to be bold and pioneering.",
            'Prog_Sun_Taurus': "Entering a 30-year cycle of building stability and resources. Focus on security and pleasure.",
            'Prog_Sun_Gemini': "Entering a 30-year cycle of communication and learning. Your voice and ideas matter.",
            'Prog_Sun_Cancer': "Entering a 30-year cycle of emotional depth and nurturing. Family and home become central.",
            'Prog_Sun_Leo': "Entering a 30-year cycle of creative self-expression and leadership. Time to shine!",
            'Prog_Sun_Virgo': "Entering a 30-year cycle of service and refinement. Focus on health and meaningful work.",
            'Prog_Sun_Libra': "Entering a 30-year cycle of relationships and balance. Partnership becomes primary.",
            'Prog_Sun_Scorpio': "Entering a 30-year cycle of transformation and depth. Deep psychological work ahead.",
            'Prog_Sun_Sagittarius': "Entering a 30-year cycle of expansion and philosophy. Adventure and meaning seeking.",
            'Prog_Sun_Capricorn': "Entering a 30-year cycle of achievement and responsibility. Building legacy.",
            'Prog_Sun_Aquarius': "Entering a 30-year cycle of innovation and community. Social causes matter.",
            'Prog_Sun_Pisces': "Entering a 30-year cycle of spiritual development and compassion. Dissolving ego.",
            
            # Progressed Moon changing signs (2.5 year emotional cycles)
            'Prog_Moon_Aries': "2.5 years of emotional independence and new beginnings. Feeling bold and assertive.",
            'Prog_Moon_Taurus': "2.5 years of emotional stability and sensuality. Need for security and comfort.",
            'Prog_Moon_Gemini': "2.5 years of emotional curiosity and variety. Need to communicate feelings.",
            'Prog_Moon_Cancer': "2.5 years of emotional depth and sensitivity. Strong family focus.",
            'Prog_Moon_Leo': "2.5 years of emotional warmth and generosity. Need for recognition.",
            'Prog_Moon_Virgo': "2.5 years of emotional practicality and service. Analyzing feelings.",
            'Prog_Moon_Libra': "2.5 years of emotional harmony seeking. Relationships central to well-being.",
            'Prog_Moon_Scorpio': "2.5 years of emotional intensity and transformation. Deep emotional work.",
            'Prog_Moon_Sagittarius': "2.5 years of emotional optimism and adventure. Freedom needs high.",
            'Prog_Moon_Capricorn': "2.5 years of emotional maturity and responsibility. Serious emotional tone.",
            'Prog_Moon_Aquarius': "2.5 years of emotional detachment and independence. Intellectual processing.",
            'Prog_Moon_Pisces': "2.5 years of emotional sensitivity and spirituality. Dissolving boundaries."
        }
    
    def _build_profection_database(self) -> Dict[int, Dict[str, str]]:
        """Build annual profections interpretation database"""
        return {
            1: {'house': 1, 'theme': 'Self and identity', 'description': 'Focus on personal development and self-discovery'},
            2: {'house': 2, 'theme': 'Resources and values', 'description': 'Building financial security and clarifying values'},
            3: {'house': 3, 'theme': 'Communication and learning', 'description': 'Learning, writing, and local connections emphasized'},
            4: {'house': 4, 'theme': 'Home and family', 'description': 'Domestic life, family, and emotional foundations'},
            5: {'house': 5, 'theme': 'Creativity and pleasure', 'description': 'Romance, children, creative expression, and joy'},
            6: {'house': 6, 'theme': 'Health and work', 'description': 'Daily routines, health, and service to others'},
            7: {'house': 7, 'theme': 'Partnerships', 'description': 'Relationships, marriage, and one-on-one connections'},
            8: {'house': 8, 'theme': 'Transformation', 'description': 'Deep change, shared resources, and psychological growth'},
            9: {'house': 9, 'theme': 'Expansion and wisdom', 'description': 'Travel, higher learning, and philosophical development'},
            10: {'house': 10, 'theme': 'Career and status', 'description': 'Professional advancement and public recognition'},
            11: {'house': 11, 'theme': 'Community and goals', 'description': 'Friendships, groups, and future aspirations'},
            12: {'house': 12, 'theme': 'Spirituality and release', 'description': 'Inner work, spirituality, and letting go'}
        }
    
    def calculate_solar_return(self, birth_chart: Dict, current_year: int) -> YearlyForecast:
        """
        Calculate solar return for the year
        
        The solar return chart is cast for the moment the Sun returns to its exact natal position
        each year, revealing themes for the year ahead.
        """
        # Simplified calculation - in real implementation would calculate exact return moment
        birth_date = birth_chart.get('birth_date', datetime.now())
        solar_return_date = datetime(current_year, birth_date.month, birth_date.day)
        
        # Determine themes based on solar return Sun house position
        # Simplified - would normally calculate full return chart
        sr_sun_house = (current_year % 12) + 1  # Simplified cycle
        
        themes_key = f'SR_Sun_{sr_sun_house}'
        theme_data = self.solar_return_themes.get(themes_key, {
            'theme': 'Year of personal development',
            'description': 'Focus on growth and evolution this year.'
        })
        
        # Generate forecast
        forecast = YearlyForecast(
            year=current_year,
            solar_return_date=solar_return_date,
            major_themes=[theme_data['theme'], theme_data['description']],
            opportunities=[
                f"Opportunities in {self._house_focus_text(sr_sun_house)}",
                "Growth through new experiences",
                "Positive developments in key life areas"
            ],
            challenges=[
                "Balancing multiple priorities",
                "Adapting to change",
                "Maintaining focus amid distractions"
            ],
            career_focus=self._get_career_focus(sr_sun_house),
            relationship_focus=self._get_relationship_focus(sr_sun_house),
            health_focus=self._get_health_focus(sr_sun_house),
            spiritual_focus=self._get_spiritual_focus(sr_sun_house),
            best_months=self._determine_best_months(solar_return_date),
            challenging_months=self._determine_challenging_months(solar_return_date),
            overall_tone=theme_data['theme']
        )
        
        return forecast
    
    def _get_career_focus(self, house: int) -> str:
        """Determine career focus for the year"""
        career_themes = {
            1: "Building personal brand and visibility",
            2: "Increasing income and professional worth",
            3: "Communication and networking in career",
            4: "Working from home or in family business",
            5: "Creative projects and leadership roles",
            6: "Daily work routines and health at work",
            7: "Partnerships and collaborative projects",
            8: "Transformation in career direction",
            9: "International work or teaching",
            10: "Major career advancement and recognition",
            11: "Team projects and future-oriented work",
            12: "Behind-the-scenes or spiritual work"
        }
        return career_themes.get(house, "Professional development")
    
    def _get_relationship_focus(self, house: int) -> str:
        """Determine relationship focus for the year"""
        relationship_themes = {
            1: "Focus on self before relationships",
            2: "Building security in relationships",
            3: "Communication in partnerships",
            4: "Deepening emotional bonds",
            5: "Romance and dating emphasized",
            6: "Service and support in relationships",
            7: "Committed partnerships central",
            8: "Deep intimacy and transformation",
            9: "Relationships through travel or learning",
            10: "Public or traditional relationships",
            11: "Friendship and social connections",
            12: "Spiritual or karmic relationships"
        }
        return relationship_themes.get(house, "Relationship growth")
    
    def _get_health_focus(self, house: int) -> str:
        """Determine health focus for the year"""
        if house == 1:
            return "Vitality and physical appearance"
        elif house == 6:
            return "Health routines and preventive care priority"
        elif house == 12:
            return "Rest, retreat, and mental health"
        else:
            return "Maintain balance and wellness"
    
    def _get_spiritual_focus(self, house: int) -> str:
        """Determine spiritual focus for the year"""
        spiritual_themes = {
            9: "Philosophical exploration and higher learning",
            12: "Deep spiritual practice and meditation",
            4: "Emotional healing and inner work",
            8: "Transformation and shadow work"
        }
        return spiritual_themes.get(house, "Spiritual growth through daily experience")
    
    def _determine_best_months(self, solar_return_date: datetime) -> List[str]:
        """Determine best months of the year"""
        months = []
        # Simplified - would calculate based on transits to solar return chart
        start_month = solar_return_date.month
        best_month_offsets = [1, 4, 7]  # 1, 4, and 7 months after birthday
        
        for offset in best_month_offsets:
            month_num = (start_month + offset - 1) % 12 + 1
            month_name = datetime(2000, month_num, 1).strftime('%B')
            months.append(month_name)
        
        return months
    
    def _determine_challenging_months(self, solar_return_date: datetime) -> List[str]:
        """Determine challenging months of the year"""
        months = []
        start_month = solar_return_date.month
        challenging_offsets = [3, 6, 9]  # Square and opposition months
        
        for offset in challenging_offsets:
            month_num = (start_month + offset - 1) % 12 + 1
            month_name = datetime(2000, month_num, 1).strftime('%B')
            months.append(month_name)
        
        return months

    def _house_focus_text(self, house_number: int) -> str:
        """Return a readable house-focus label across schema variants."""
        idx = max(0, min(len(HOUSES) - 1, house_number - 1))
        house = HOUSES[idx] if HOUSES else {}
        if isinstance(house, dict):
            if house.get('life_area'):
                return str(house.get('life_area'))
            life_areas = house.get('life_areas')
            if isinstance(life_areas, list) and life_areas:
                return ", ".join(str(a) for a in life_areas[:2])
            if house.get('name'):
                return str(house.get('name'))
        return f"House {house_number} themes"
    
    def calculate_progressions(self, birth_chart: Dict, current_age: int) -> ProgressedChart:
        """
        Calculate secondary progressions
        
        Secondary progressions move the chart forward 1 day = 1 year
        Shows internal psychological and emotional evolution
        """
        # Get natal Sun sign
        natal_sun_sign = birth_chart.get('Sun', {}).get('sign', 'Aries')
        
        # Calculate progressed Sun (moves ~1° per year)
        natal_sun_degree = birth_chart.get('Sun', {}).get('degree', 0)
        progressed_degrees = natal_sun_degree + current_age
        
        # Determine progressed sign
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        natal_sign_index = signs.index(natal_sun_sign)
        sign_jumps = int(progressed_degrees / 30)
        progressed_sun_sign = signs[(natal_sign_index + sign_jumps) % 12]
        
        # Calculate progressed Moon (moves ~13° per year, ~2.5 years per sign)
        progressed_moon_cycles = int(current_age / 2.5) % 12
        progressed_moon_sign = signs[progressed_moon_cycles]
        
        # Progressed Ascendant (moves ~1° per year)
        progressed_asc = "Calculated from birth time"  # Simplified
        
        # Determine life phase
        life_phase = self._determine_life_phase(progressed_sun_sign, current_age)
        
        # Get progression meanings
        sun_meaning = self.progression_meanings.get(f'Prog_Sun_{progressed_sun_sign}', 
                                                    "Period of personal evolution")
        moon_meaning = self.progression_meanings.get(f'Prog_Moon_{progressed_moon_sign}',
                                                     "Emotional development phase")
        
        progression = ProgressedChart(
            current_age=current_age,
            progressed_sun_sign=progressed_sun_sign,
            progressed_moon_sign=progressed_moon_sign,
            progressed_ascendant=progressed_asc,
            life_phase=life_phase,
            emotional_evolution=moon_meaning,
            identity_shift=sun_meaning,
            major_progressions=[
                f"Progressed Sun in {progressed_sun_sign}",
                f"Progressed Moon in {progressed_moon_sign}"
            ],
            timing_insights=[
                "Secondary progressions show your internal maturation",
                "Major life themes unfold gradually over years",
                "Progressed Moon changes every 2.5 years mark emotional shifts"
            ]
        )
        
        return progression
    
    def _determine_life_phase(self, progressed_sun_sign: str, age: int) -> str:
        """Determine current life phase"""
        if age < 29:
            return f"Young Adult Phase - {progressed_sun_sign} identity emerging"
        elif age < 42:
            return f"Mature Adult Phase - {progressed_sun_sign} mastery developing"
        elif age < 56:
            return f"Wisdom Phase - {progressed_sun_sign} integration deepening"
        else:
            return f"Elder Phase - {progressed_sun_sign} legacy building"
    
    def calculate_profection(self, current_age: int, birth_chart: Dict) -> ProfectionYear:
        """
        Calculate annual profection
        
        Traditional technique where each year of life corresponds to a house,
        cycling through all 12 houses every 12 years
        """
        # Profection house is current age modulo 12, starting from 1st house at birth
        profection_house = (current_age % 12) + 1
        
        # Get profection data
        profection_data = self.profection_themes.get(current_age % 12 + 1, {
            'house': profection_house,
            'theme': 'Personal development',
            'description': 'Year of growth'
        })
        
        # Determine sign of profection year (starts from Ascendant)
        ascendant_sign = birth_chart.get('Ascendant', {}).get('sign', 'Aries')
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        asc_index = signs.index(ascendant_sign)
        profection_sign = signs[(asc_index + profection_house - 1) % 12]
        
        # Determine ruling planet of profection year
        rulers = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
        }
        ruling_planet = rulers.get(profection_sign, 'Sun')
        
        profection = ProfectionYear(
            age=current_age,
            profection_house=profection_house,
            profection_sign=profection_sign,
            ruling_planet=ruling_planet,
            year_theme=profection_data['theme'],
            life_area_focus=profection_data['description'],
            opportunities=[
                f"Growth in {self._house_focus_text(profection_house)}",
                f"Activation through {ruling_planet} transits",
                "Traditional timing indicates maturation in this area"
            ],
            lessons=[
                f"Master {profection_data['theme']} theme",
                f"Develop {profection_sign} qualities",
                f"Work with {ruling_planet} energy consciously"
            ]
        )
        
        return profection
    
    def get_complete_life_timing(self, birth_chart: Dict, current_age: int,
                                 current_year: int) -> LifeTimingForecast:
        """Generate complete predictive analysis integrating all techniques"""
        # Calculate all three techniques
        solar_return = self.calculate_solar_return(birth_chart, current_year)
        progressions = self.calculate_progressions(birth_chart, current_age)
        profection = self.calculate_profection(current_age, birth_chart)
        
        # Integrate techniques
        integrated = self._integrate_predictions(solar_return, progressions, profection)
        
        # Generate timing for major life events
        timing_events = self._generate_life_event_timing(solar_return, progressions, profection)
        
        # Decision guidance
        decision_guidance = {
            'career': self._get_career_decision_guidance(solar_return, profection),
            'relationship': self._get_relationship_decision_guidance(solar_return, profection),
            'relocation': self._get_relocation_guidance(solar_return, profection),
            'major_purchase': self._get_financial_timing(solar_return, profection)
        }
        
        return LifeTimingForecast(
            current_phase=progressions.life_phase,
            solar_return_forecast=solar_return,
            progressions=progressions,
            profection=profection,
            integrated_forecast=integrated,
            major_life_events_timing=timing_events,
            decision_guidance=decision_guidance
        )
    
    def _integrate_predictions(self, sr: YearlyForecast, prog: ProgressedChart, 
                              prof: ProfectionYear) -> str:
        """Integrate all three predictive techniques into unified forecast"""
        forecast = f"**INTEGRATED YEAR FORECAST**\n\n"
        forecast += f"This year ({sr.year}) is governed by the {prof.profection_house}{self._ordinal(prof.profection_house)} house theme: {prof.year_theme}.\n\n"
        forecast += f"Your solar return emphasizes: {sr.overall_tone}\n\n"
        forecast += f"Internally, your progressions show: {prog.identity_shift}\n\n"
        forecast += f"Emotionally: {prog.emotional_evolution}\n\n"
        forecast += "All three techniques point to this being a year of significant development in the areas they highlight."
        
        return forecast
    
    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = suffixes.get(n % 10, 'th')
        return suffix
    
    def _generate_life_event_timing(self, sr: YearlyForecast, prog: ProgressedChart,
                                    prof: ProfectionYear) -> List[str]:
        """Generate timing predictions for major life events"""
        events = []
        
        # Career events
        if prof.profection_house == 10 or 'career' in sr.overall_tone.lower():
            events.append("Career advancement or change likely this year")
        
        # Relationship events
        if prof.profection_house in [5, 7]:
            events.append("Significant relationship developments expected")
        
        # Home/family events
        if prof.profection_house == 4:
            events.append("Home, family, or relocation matters featured")
        
        # Education/travel events
        if prof.profection_house == 9:
            events.append("Educational or travel opportunities arise")
        
        return events
    
    def _get_career_decision_guidance(self, sr: YearlyForecast, prof: ProfectionYear) -> str:
        """Career decision timing guidance"""
        if prof.profection_house == 10:
            return f"Excellent year for career moves. Best months: {', '.join(sr.best_months[:2])}"
        elif prof.profection_house == 6:
            return "Focus on improving current work situation before major changes"
        else:
            return f"Career moves supported during: {', '.join(sr.best_months[:2])}"
    
    def _get_relationship_decision_guidance(self, sr: YearlyForecast, prof: ProfectionYear) -> str:
        """Relationship decision timing guidance"""
        if prof.profection_house == 7:
            return "Prime year for commitment and partnership decisions"
        elif prof.profection_house == 5:
            return "Great for dating and romance, commitments can wait"
        else:
            return "Relationship decisions best made in months emphasizing connection"
    
    def _get_relocation_guidance(self, sr: YearlyForecast, prof: ProfectionYear) -> str:
        """Relocation timing guidance"""
        if prof.profection_house == 4:
            return "Excellent year for moves, renovations, or real estate"
        else:
            return "Relocations best delayed unless necessary"
    
    def _get_financial_timing(self, sr: YearlyForecast, prof: ProfectionYear) -> str:
        """Financial decision timing guidance"""
        if prof.profection_house == 2:
            return "Excellent year for building wealth and major purchases"
        elif prof.profection_house == 8:
            return "Good for investments and shared financial ventures"
        else:
            return "Exercise financial caution; wait for better timing"
    
    def answer_predictive_question(self, birth_chart: Dict, question: str,
                                   current_age: int, current_year: int) -> str:
        """Answer specific predictive questions using all techniques"""
        question_lower = question.lower()
        
        # Get complete timing analysis
        timing = self.get_complete_life_timing(birth_chart, current_age, current_year)
        
        # Route to appropriate answer
        if 'career' in question_lower or 'job' in question_lower:
            return f"**Career Timing Answer:**\n\n{timing.decision_guidance['career']}\n\n{timing.solar_return_forecast.career_focus}"
        
        elif 'relationship' in question_lower or 'marriage' in question_lower or 'love' in question_lower:
            return f"**Relationship Timing Answer:**\n\n{timing.decision_guidance['relationship']}\n\n{timing.solar_return_forecast.relationship_focus}"
        
        elif 'move' in question_lower or 'relocate' in question_lower:
            return f"**Relocation Timing Answer:**\n\n{timing.decision_guidance['relocation']}"
        
        elif 'when' in question_lower:
            return f"**Life Timing Analysis:**\n\n{timing.integrated_forecast}\n\n**Key Events:** {', '.join(timing.major_life_events_timing)}"
        
        else:
            return f"**General Forecast:**\n\n{timing.integrated_forecast}"


# Global instance
predictive_suite = PredictiveSuite()
predictive_engine = predictive_suite

"""
Deep Synastry & Relationship Analysis
Comprehensive compatibility analysis beyond sun signs
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

from .expertise import ZODIAC_SIGNS, PLANETS, ASPECTS


class RelationshipArea(Enum):
    """Areas of relationship compatibility"""
    ROMANTIC = "romantic"
    SEXUAL = "sexual"
    EMOTIONAL = "emotional"
    INTELLECTUAL = "intellectual"
    SPIRITUAL = "spiritual"
    PRACTICAL = "practical"
    COMMUNICATION = "communication"
    VALUES = "values"
    GROWTH = "growth"


class AspectNature(Enum):
    """Nature of synastry aspects"""
    HIGHLY_HARMONIOUS = "highly_harmonious"
    HARMONIOUS = "harmonious"
    DYNAMIC = "dynamic"  # Challenging but growth-promoting
    TENSE = "tense"
    HIGHLY_TENSE = "highly_tense"


@dataclass
class SynastryAspect:
    """An aspect between two people's planets"""
    person1_planet: str
    person2_planet: str
    aspect_type: str
    orb: float
    nature: AspectNature
    meaning: str
    relationship_area: RelationshipArea
    advice: str
    intensity: float  # 0-10


@dataclass
class CompositePoint:
    """Midpoint between two charts"""
    point_name: str
    sign: str
    degree: float
    house: int
    meaning: str


@dataclass
class RelationshipCompatibility:
    """Complete relationship compatibility analysis"""
    overall_score: float  # 0-100
    romantic_score: float
    sexual_chemistry: float
    emotional_compatibility: float
    intellectual_harmony: float
    spiritual_connection: float
    communication_score: float
    values_alignment: float
    growth_potential: float
    
    strengths: List[str]
    challenges: List[str]
    synastry_aspects: List[SynastryAspect]
    composite_analysis: str
    relationship_purpose: str
    advice_for_success: List[str]
    potential_issues: List[str]
    timing_insights: str


@dataclass
class SoulMateIndicators:
    """Indicators of deep soul connection"""
    has_vertex_contact: bool
    has_node_contact: bool
    has_chiron_contact: bool
    has_part_of_fortune_contact: bool
    double_whammy_count: int  # Mutual aspects
    composite_stellium: Optional[str]  # Sign with many composite planets
    soul_mate_score: float  # 0-100
    soul_mate_indicators: List[str]


class DeepSynastryAnalyzer:
    """Advanced relationship compatibility analysis"""
    
    def __init__(self):
        self.synastry_interpretations = self._build_synastry_database()
        self.composite_meanings = self._build_composite_meanings()
    
    def _build_synastry_database(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Build comprehensive synastry interpretation database"""
        return {
            # Sun aspects in synastry
            'Sun_Sun': {
                'conjunction': {
                    'meaning': "You shine together! Same life purpose and identity. Understand each other deeply.",
                    'advice': "Celebrate your similarities but maintain individual identity. Support each other's goals.",
                    'area': RelationshipArea.ROMANTIC,
                    'intensity': 9.0
                },
                'trine': {
                    'meaning': "Natural harmony and mutual support. You bring out the best in each other.",
                    'advice': "Easy flow between you. Use this harmony to build together.",
                    'area': RelationshipArea.ROMANTIC,
                    'intensity': 8.0
                },
                'square': {
                    'meaning': "Ego clashes and different approaches to life. Growth through friction.",
                    'advice': "Respect differences. These tensions can strengthen you if navigated consciously.",
                    'area': RelationshipArea.GROWTH,
                    'intensity': 7.0
                },
                'opposition': {
                    'meaning': "You're opposite but complementary. Attraction through differences.",
                    'advice': "Balance each other. Learn from opposite perspectives.",
                    'area': RelationshipArea.ROMANTIC,
                    'intensity': 7.5
                }
            },
            'Sun_Moon': {
                'conjunction': {
                    'meaning': "Deep emotional understanding. Your identity meets their emotional needs perfectly.",
                    'advice': "Nurture this natural understanding. Honor both logic and feelings.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 10.0
                },
                'trine': {
                    'meaning': "Emotional ease and comfort. You instinctively know how to support each other.",
                    'advice': "This is one of the best aspects for long-term happiness. Cherish it.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 9.5
                },
                'square': {
                    'meaning': "Emotional needs clash with identity expression. Requires adjustment.",
                    'advice': "Learn each other's emotional language. Compromise on needs vs wants.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 6.0
                },
                'opposition': {
                    'meaning': "Intense attraction but emotional push-pull. Complementary but tense.",
                    'advice': "Balance masculine/feminine energies. Meet in the middle.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 7.0
                }
            },
            'Moon_Moon': {
                'conjunction': {
                    'meaning': "Same emotional wavelength. You feel each other's feelings deeply.",
                    'advice': "Beautiful emotional attunement. Be careful not to lose individual feelings.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 9.0
                },
                'trine': {
                    'meaning': "Emotional harmony and mutual understanding. Natural empathy.",
                    'advice': "Nurture this emotional ease. Create safe space for feelings.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 8.5
                },
                'square': {
                    'meaning': "Different emotional styles and needs. Can irritate each other.",
                    'advice': "Respect different emotional expressions. Learn new ways to feel.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 5.5
                },
                'opposition': {
                    'meaning': "Emotionally opposite but magnetically attracted. Intense feelings.",
                    'advice': "Balance opposite emotional needs. Find middle ground.",
                    'area': RelationshipArea.EMOTIONAL,
                    'intensity': 6.5
                }
            },
            'Venus_Venus': {
                'conjunction': {
                    'meaning': "Same love language and values. You want the same things in love.",
                    'advice': "Beautiful agreement on romance. Enjoy similar pleasures together.",
                    'area': RelationshipArea.ROMANTIC,
                    'intensity': 8.0
                },
                'trine': {
                    'meaning': "Natural romantic flow. Easy to please each other.",
                    'advice': "Lovely harmonious love. Keep appreciation alive.",
                    'area': RelationshipArea.ROMANTIC,
                    'intensity': 7.5
                },
                'square': {
                    'meaning': "Different values and love styles. What pleases one may not please the other.",
                    'advice': "Learn each other's love language. Compromise on values.",
                    'area': RelationshipArea.VALUES,
                    'intensity': 5.0
                }
            },
            'Mars_Mars': {
                'conjunction': {
                    'meaning': "Intense sexual chemistry and competitive energy. Same drive.",
                    'advice': "Channel shared energy positively. Can be explosive if not careful.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 8.5
                },
                'trine': {
                    'meaning': "Dynamic action together. Complementary drive and passion.",
                    'advice': "Great teamwork and bedroom compatibility. Take action together.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 8.0
                },
                'square': {
                    'meaning': "Power struggles and conflicts. Both want control.",
                    'advice': "Pick your battles. Take turns leading. Channel anger constructively.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 6.0
                },
                'opposition': {
                    'meaning': "Intense attraction but competitive. Sexual tension high.",
                    'advice': "Transform opposition into passionate partnership. Balance assertion.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 7.0
                }
            },
            'Sun_Venus': {
                'conjunction': {
                    'meaning': "Love and adoration. One shines, the other adores. Sweet connection.",
                    'advice': "Classic attraction aspect. Keep romance alive always.",
                    'area': RelationshipArea.ROMANTIC,
                    'intensity': 9.0
                },
                'trine': {
                    'meaning': "Natural affection and appreciation. Easy love flow.",
                    'advice': "Enjoy this easy love. Show appreciation regularly.",
                    'area': RelationshipArea.ROMANTIC,
                    'intensity': 8.5
                }
            },
            'Sun_Mars': {
                'conjunction': {
                    'meaning': "Energizing and activating. One inspires the other to act.",
                    'advice': "Dynamic connection. Watch for ego battles. Great motivation.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 8.0
                },
                'square': {
                    'meaning': "Friction and irritation. Ego vs action. Can be exhausting.",
                    'advice': "Give each other space. Respect different paces. Cool down periods needed.",
                    'area': RelationshipArea.GROWTH,
                    'intensity': 6.5
                },
                'opposition': {
                    'meaning': "Intense attraction but confrontational. Push-pull dynamic.",
                    'advice': "Transform conflict into passion. Take turns leading.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 7.5
                }
            },
            'Venus_Mars': {
                'conjunction': {
                    'meaning': "Classic sexual attraction! Masculine meets feminine perfectly.",
                    'advice': "One of the best sexual chemistry aspects. Keep passion alive.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 10.0
                },
                'trine': {
                    'meaning': "Natural romantic and sexual flow. Easy attraction.",
                    'advice': "Lovely chemistry. Balance romance with passion.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 9.0
                },
                'square': {
                    'meaning': "Attraction with tension. Different speeds in romance.",
                    'advice': "Negotiate timing. One wants romance, one wants action. Compromise.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 7.0
                },
                'opposition': {
                    'meaning': "Intense magnetic attraction. Sexual polarity high.",
                    'advice': "Use opposite energies to create spark. Balance give and take.",
                    'area': RelationshipArea.SEXUAL,
                    'intensity': 8.5
                }
            },
            'Mercury_Mercury': {
                'conjunction': {
                    'meaning': "You think alike. Same communication style and interests.",
                    'advice': "Great mental connection. Enjoy conversations together.",
                    'area': RelationshipArea.COMMUNICATION,
                    'intensity': 7.0
                },
                'trine': {
                    'meaning': "Easy communication and understanding. Finish each other's sentences.",
                    'advice': "Natural mental harmony. Share ideas freely.",
                    'area': RelationshipArea.COMMUNICATION,
                    'intensity': 7.5
                },
                'square': {
                    'meaning': "Miscommunication and mental friction. Talk past each other.",
                    'advice': "Listen more carefully. Speak each other's language. Patience in communication.",
                    'area': RelationshipArea.COMMUNICATION,
                    'intensity': 5.0
                }
            },
            'Jupiter_Jupiter': {
                'conjunction': {
                    'meaning': "Shared beliefs and growth together. Same philosophy of life.",
                    'advice': "Expand together. Share adventures and learning.",
                    'area': RelationshipArea.GROWTH,
                    'intensity': 7.5
                },
                'trine': {
                    'meaning': "Mutual encouragement and optimism. You uplift each other.",
                    'advice': "Support each other's growth. Stay positive together.",
                    'area': RelationshipArea.GROWTH,
                    'intensity': 7.0
                }
            },
            'Saturn_Saturn': {
                'conjunction': {
                    'meaning': "Same generation and shared responsibilities. Serious commitment.",
                    'advice': "Build together long-term. Honor commitments.",
                    'area': RelationshipArea.PRACTICAL,
                    'intensity': 6.5
                },
                'trine': {
                    'meaning': "Stable and reliable connection. Mutual respect and maturity.",
                    'advice': "Excellent for long-term stability. Build structures together.",
                    'area': RelationshipArea.PRACTICAL,
                    'intensity': 8.0
                },
                'square': {
                    'meaning': "Different approaches to responsibility and time. Burdens may clash.",
                    'advice': "Respect different maturity styles. Share burdens fairly.",
                    'area': RelationshipArea.PRACTICAL,
                    'intensity': 5.5
                }
            }
        }
    
    def _build_composite_meanings(self) -> Dict[str, str]:
        """Build composite chart interpretation database"""
        return {
            'Sun_1st': "The relationship's purpose is to develop identity and self-expression together.",
            'Moon_1st': "Emotional authenticity and nurturing define this relationship's core.",
            'Sun_7th': "Partnership itself is the central purpose. You exist to be together.",
            'Moon_7th': "Emotional bonding and domestic life are the relationship's heart.",
            'Venus_7th': "Love and harmony through partnership. Classic marriage placement.",
            'Mars_1st': "Active, energetic, pioneering relationship. You take action together.",
            'Jupiter_7th': "Growth through partnership. Expansive and fortunate union.",
            'Saturn_7th': "Serious, committed, lasting relationship. Built to endure.",
            'Stellium_Capricorn': "Achievement-oriented relationship. Building something lasting together.",
            'Stellium_Cancer': "Nurturing, home-centered relationship. Creating family and security.",
            'Stellium_Libra': "Harmony and balance focused. True partnership as goal.",
            'Stellium_Aries': "Independent but together. Pioneering new relationship territory."
        }
    
    def analyze_relationship(self, person1_chart: Dict, person2_chart: Dict,
                           person1_name: str = "Person 1", 
                           person2_name: str = "Person 2") -> RelationshipCompatibility:
        """
        Complete relationship compatibility analysis
        
        Args:
            person1_chart: First person's natal chart positions
            person2_chart: Second person's natal chart positions
            person1_name: First person's name (optional)
            person2_name: Second person's name (optional)
        
        Returns:
            RelationshipCompatibility object with complete analysis
        """
        # Calculate all synastry aspects
        synastry_aspects = self._calculate_synastry_aspects(person1_chart, person2_chart)
        
        # Calculate compatibility scores for each area
        scores = self._calculate_compatibility_scores(synastry_aspects)
        
        # Identify strengths and challenges
        strengths, challenges = self._identify_strengths_challenges(synastry_aspects)
        
        # Calculate composite chart
        composite_analysis = self._analyze_composite(person1_chart, person2_chart)
        
        # Determine relationship purpose
        purpose = self._determine_relationship_purpose(synastry_aspects, scores)
        
        # Generate advice
        advice = self._generate_relationship_advice(synastry_aspects, scores)
        
        # Identify potential issues
        issues = self._identify_potential_issues(synastry_aspects)
        
        # Timing insights
        timing = self._generate_timing_insights(synastry_aspects)
        
        return RelationshipCompatibility(
            overall_score=scores['overall'],
            romantic_score=scores['romantic'],
            sexual_chemistry=scores['sexual'],
            emotional_compatibility=scores['emotional'],
            intellectual_harmony=scores['intellectual'],
            spiritual_connection=scores['spiritual'],
            communication_score=scores['communication'],
            values_alignment=scores['values'],
            growth_potential=scores['growth'],
            strengths=strengths,
            challenges=challenges,
            synastry_aspects=synastry_aspects,
            composite_analysis=composite_analysis,
            relationship_purpose=purpose,
            advice_for_success=advice,
            potential_issues=issues,
            timing_insights=timing
        )
    
    def _calculate_synastry_aspects(self, chart1: Dict, chart2: Dict) -> List[SynastryAspect]:
        """Calculate all significant aspects between two charts"""
        aspects = []
        
        # Key planets to check
        important_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                           'Jupiter', 'Saturn']
        
        for planet1 in important_planets:
            if planet1 not in chart1:
                continue
            
            for planet2 in important_planets:
                if planet2 not in chart2:
                    continue
                
                # Calculate aspect
                aspect_type, orb = self._calculate_aspect_between_planets(
                    chart1[planet1], chart2[planet2]
                )
                
                if aspect_type and orb <= 8.0:  # Within orb
                    # Get interpretation
                    interpretation = self._get_synastry_interpretation(
                        planet1, planet2, aspect_type
                    )
                    
                    if interpretation:
                        aspect = SynastryAspect(
                            person1_planet=planet1,
                            person2_planet=planet2,
                            aspect_type=aspect_type,
                            orb=orb,
                            nature=interpretation['nature'],
                            meaning=interpretation['meaning'],
                            relationship_area=interpretation['area'],
                            advice=interpretation['advice'],
                            intensity=interpretation['intensity']
                        )
                        aspects.append(aspect)
        
        # Sort by intensity
        aspects.sort(key=lambda a: a.intensity, reverse=True)
        
        return aspects
    
    def _calculate_aspect_between_planets(self, pos1: Dict, pos2: Dict) -> Tuple[Optional[str], float]:
        """Calculate aspect between two planetary positions"""
        # Convert to degrees
        degree1 = self._sign_to_degrees(pos1['sign']) + pos1['degree']
        degree2 = self._sign_to_degrees(pos2['sign']) + pos2['degree']
        
        # Angular difference
        diff = abs(degree1 - degree2)
        if diff > 180:
            diff = 360 - diff
        
        # Check aspects
        aspects = {
            'conjunction': (0, 8),
            'sextile': (60, 6),
            'square': (90, 8),
            'trine': (120, 8),
            'opposition': (180, 8)
        }
        
        for aspect_name, (angle, max_orb) in aspects.items():
            orb = abs(diff - angle)
            if orb <= max_orb:
                return aspect_name, orb
        
        return None, 999
    
    def _sign_to_degrees(self, sign: str) -> float:
        """Convert sign to degrees"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        return signs.index(sign) * 30
    
    def _get_synastry_interpretation(self, planet1: str, planet2: str, 
                                    aspect: str) -> Optional[Dict]:
        """Get interpretation for synastry aspect"""
        key = f"{planet1}_{planet2}"
        
        if key in self.synastry_interpretations:
            if aspect in self.synastry_interpretations[key]:
                data = self.synastry_interpretations[key][aspect]
                
                # Determine nature
                if aspect in ['trine', 'sextile']:
                    nature = AspectNature.HARMONIOUS
                elif aspect == 'conjunction':
                    nature = AspectNature.DYNAMIC
                elif aspect == 'square':
                    nature = AspectNature.TENSE
                else:  # opposition
                    nature = AspectNature.DYNAMIC
                
                return {
                    'meaning': data['meaning'],
                    'advice': data['advice'],
                    'area': data['area'],
                    'intensity': data['intensity'],
                    'nature': nature
                }
        
        return None
    
    def _calculate_compatibility_scores(self, aspects: List[SynastryAspect]) -> Dict[str, float]:
        """Calculate compatibility scores for different areas"""
        scores = {
            'romantic': 0, 'sexual': 0, 'emotional': 0, 'intellectual': 0,
            'spiritual': 0, 'communication': 0, 'values': 0, 'growth': 0
        }
        counts = {key: 0 for key in scores}
        
        for aspect in aspects:
            area = aspect.relationship_area.value
            if area in scores:
                # Add score based on nature and intensity
                if aspect.nature == AspectNature.HARMONIOUS:
                    scores[area] += aspect.intensity * 10
                elif aspect.nature == AspectNature.DYNAMIC:
                    scores[area] += aspect.intensity * 5
                elif aspect.nature == AspectNature.TENSE:
                    scores[area] += aspect.intensity * 2
                
                counts[area] += 1
        
        # Average scores
        for key in scores:
            if counts[key] > 0:
                scores[key] = min(100, scores[key] / counts[key])
            else:
                scores[key] = 50  # Neutral if no aspects
        
        # Overall score is weighted average
        scores['overall'] = (
            scores['romantic'] * 0.25 +
            scores['emotional'] * 0.25 +
            scores['sexual'] * 0.15 +
            scores['communication'] * 0.15 +
            scores['values'] * 0.10 +
            scores['growth'] * 0.10
        )
        
        return scores
    
    def _identify_strengths_challenges(self, aspects: List[SynastryAspect]) -> Tuple[List[str], List[str]]:
        """Identify relationship strengths and challenges"""
        strengths = []
        challenges = []
        
        for aspect in aspects[:10]:  # Top 10 aspects
            if aspect.nature in [AspectNature.HARMONIOUS, AspectNature.HIGHLY_HARMONIOUS]:
                strengths.append(f"{aspect.person1_planet}-{aspect.person2_planet} {aspect.aspect_type}: {aspect.meaning}")
            elif aspect.nature in [AspectNature.TENSE, AspectNature.HIGHLY_TENSE]:
                challenges.append(f"{aspect.person1_planet}-{aspect.person2_planet} {aspect.aspect_type}: {aspect.meaning}")
        
        return strengths[:5], challenges[:5]
    
    def _analyze_composite(self, chart1: Dict, chart2: Dict) -> str:
        """Analyze composite chart (midpoints)"""
        composite = "**Composite Chart Analysis**\n\n"
        composite += "The composite chart represents the relationship itself as a third entity.\n\n"
        
        # Calculate some composite points
        composite += "Key composite placements reveal the relationship's essential nature and purpose."
        
        return composite
    
    def _determine_relationship_purpose(self, aspects: List[SynastryAspect], 
                                       scores: Dict[str, float]) -> str:
        """Determine the karmic/spiritual purpose of the relationship"""
        # Look at dominant themes
        if scores['spiritual'] > 70:
            return "This relationship exists for spiritual growth and awakening. You're meant to evolve together."
        elif scores['growth'] > 70:
            return "This relationship catalyzes personal transformation. You challenge each other to become better."
        elif scores['emotional'] > 80:
            return "This relationship heals emotional wounds and teaches about love. Deep bonding is your purpose."
        elif scores['romantic'] > 80:
            return "This is a romantic soulmate connection. You're meant to experience true love together."
        else:
            return "This relationship teaches important life lessons and supports mutual development."
    
    def _generate_relationship_advice(self, aspects: List[SynastryAspect], 
                                     scores: Dict[str, float]) -> List[str]:
        """Generate practical advice for relationship success"""
        advice = []
        
        if scores['communication'] < 60:
            advice.append("Prioritize clear communication. Listen actively and express needs clearly.")
        
        if scores['emotional'] < 60:
            advice.append("Build emotional safety. Create space for vulnerable sharing.")
        
        if scores['values'] < 60:
            advice.append("Discuss and align on core values. Find common ground on important issues.")
        
        if scores['growth'] > 70:
            advice.append("Embrace challenges as growth opportunities. Support each other's evolution.")
        
        advice.append("Honor both individual needs and relationship needs. Balance 'me' and 'we'.")
        advice.append("Celebrate strengths and work consciously on challenges together.")
        
        return advice
    
    def _identify_potential_issues(self, aspects: List[SynastryAspect]) -> List[str]:
        """Identify potential relationship pitfalls"""
        issues = []
        
        # Look for tense aspects
        tense = [a for a in aspects if a.nature == AspectNature.TENSE]
        
        for aspect in tense[:3]:
            issues.append(f"Watch for {aspect.relationship_area.value} tensions from {aspect.person1_planet}-{aspect.person2_planet} {aspect.aspect_type}")
        
        return issues
    
    def _generate_timing_insights(self, aspects: List[SynastryAspect]) -> str:
        """Generate insights about relationship timing"""
        return "Transits to your synastry aspects will activate relationship themes. Major transits indicate important relationship periods."
    
    def get_compatibility_report(self, person1_chart: Dict, person2_chart: Dict,
                                person1_name: str = "Person 1",
                                person2_name: str = "Person 2") -> str:
        """Generate human-readable compatibility report"""
        compat = self.analyze_relationship(person1_chart, person2_chart, person1_name, person2_name)
        
        report = f"**DEEP SYNASTRY ANALYSIS: {person1_name} & {person2_name}**\n\n"
        report += f"Overall Compatibility: **{compat.overall_score:.0f}%**\n\n"
        
        report += "**COMPATIBILITY BREAKDOWN**\n\n"
        report += f"💖 Romantic Chemistry: {compat.romantic_score:.0f}%\n"
        report += f"🔥 Sexual Compatibility: {compat.sexual_chemistry:.0f}%\n"
        report += f"💕 Emotional Harmony: {compat.emotional_compatibility:.0f}%\n"
        report += f"🧠 Intellectual Connection: {compat.intellectual_harmony:.0f}%\n"
        report += f"✨ Spiritual Bond: {compat.spiritual_connection:.0f}%\n"
        report += f"💬 Communication: {compat.communication_score:.0f}%\n"
        report += f"⚖️ Values Alignment: {compat.values_alignment:.0f}%\n"
        report += f"🌱 Growth Potential: {compat.growth_potential:.0f}%\n\n"
        
        report += "**RELATIONSHIP STRENGTHS**\n\n"
        for strength in compat.strengths:
            report += f"✅ {strength}\n"
        report += "\n"
        
        if compat.challenges:
            report += "**GROWTH AREAS**\n\n"
            for challenge in compat.challenges:
                report += f"⚠️ {challenge}\n"
            report += "\n"
        
        report += f"**RELATIONSHIP PURPOSE**\n\n{compat.relationship_purpose}\n\n"
        
        report += "**ADVICE FOR SUCCESS**\n\n"
        for i, advice in enumerate(compat.advice_for_success, 1):
            report += f"{i}. {advice}\n"
        
        return report


# Global instance
synastry_analyzer = DeepSynastryAnalyzer()

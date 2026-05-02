"""Chart Rectification & Advanced Analysis Tools.

This module provides:
- Automated birth time rectification using event correlations
- Advanced Composite and Davison charts for relationships
- Astro-mapping (relocation astrology)
- Locality correction and planetary angles
- Event chart analysis and validation
- Advanced chart pattern recognition
- Life event prediction accuracy verification
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class RectificationMethod(Enum):
    """Different methods for birth time rectification."""
    EVENT_CORRELATION = "event_correlation"
    PROGRESSED_METHOD = "progressed_method"
    SECONDARY_PROGRESSIONS = "secondary_progressions"
    SYMBOLIC_ARC = "symbolic_arc"
    SOLAR_ARC = "solar_arc"


class ChartPatternType(Enum):
    """Advanced chart pattern types."""
    GRAND_TRINE = "grand_trine"  # 3 planets 120° apart
    GRAND_CROSS = "grand_cross"  # 4 planets 90° apart
    KITE = "kite"  # Grand trine + planet 150° from base
    MYSTIC_RECTANGLE = "mystic_rectangle"  # 4 planets, 2 trines + 2 sextiles
    THOR_HAMMER = "thor_hammer"  # Yod variant
    YOD = "yod"  # 2 planets quincunx 3rd
    PENTAGRAM = "pentagram"  # 5 planets equally spaced
    STELLIUM = "stellium"  # 3+ planets in same sign/house
    T_SQUARE = "t_square"  # 3 planets forming T


@dataclass
class RectificationEvent:
    """A known event used for birth time rectification."""
    event_date: datetime
    event_type: str  # "birth", "marriage", "accident", "promotion", etc.
    event_description: str
    expected_aspect: str  # e.g., "Sun square Progressed Venus"
    confidence: float  # How confident we are about the event


@dataclass
class RectificationResult:
    """Result of birth time rectification analysis."""
    original_birth_time: datetime
    corrected_birth_time: datetime
    time_correction: timedelta  # How much to adjust
    confidence: float  # 0.0 to 1.0
    method_used: RectificationMethod
    verification_score: float  # Based on event correlations
    supporting_events: List[str]
    additional_notes: str


@dataclass
class CompositeChart:
    """Composite chart of two people's synastry."""
    person1_name: str
    person2_name: str
    composite_positions: Dict[str, float]
    house_cusps: Dict[int, float]
    composite_ascendant: str
    chart_patterns: List[str]
    strongest_aspects: List[str]


@dataclass
class AstroMapData:
    """Astro-mapping data for relocation astrology."""
    original_location: Tuple[float, float]  # lat, long
    new_location: Tuple[float, float]
    angle_shifts: Dict[str, float]  # How angles shift
    power_locations: List[Dict]  # Best places for planets
    challenging_locations: List[Dict]
    recommendations: List[str]


@dataclass
class AdvancedChartPattern:
    """An advanced pattern found in the chart."""
    pattern_type: ChartPatternType
    planets_involved: List[str]
    interpretation: str
    significance: str  # "major", "moderate", "minor"
    influence_area: str  # Life areas influenced


class ChartRectification:
    """Advanced birth time rectification engine."""
    
    def __init__(self):
        self.known_events: List[RectificationEvent] = []
        self.aspect_orbs = {
            "conjunction": 8.0,
            "opposition": 8.0,
            "square": 8.0,
            "trine": 8.0,
            "sextile": 6.0,
            "quincunx": 3.0,
            "semisextile": 2.0,
        }
    
    def add_event(self, event: RectificationEvent):
        """Add a known life event for rectification."""
        self.known_events.append(event)
    
    def rectify_birth_time(
        self,
        birth_date: datetime,
        approximate_time: datetime,
        location_lat: float,
        location_long: float
    ) -> RectificationResult:
        """Rectify birth time using event correlation method.
        
        This method correlates known life events with transits/progressions
        to find the most likely accurate birth time.
        """
        if not self.known_events:
            return RectificationResult(
                original_birth_time=approximate_time,
                corrected_birth_time=approximate_time,
                time_correction=timedelta(0),
                confidence=0.0,
                method_used=RectificationMethod.EVENT_CORRELATION,
                verification_score=0.0,
                supporting_events=[],
                additional_notes="No events provided for rectification"
            )
        
        # Try different times around the approximate time
        best_correction = timedelta(0)
        best_score = 0.0
        supporting_events = []
        
        # Search window: ±6 hours from approximate time
        search_window_hours = 6
        time_step = timedelta(minutes=5)  # Check every 5 minutes
        
        current_test_time = approximate_time - timedelta(hours=search_window_hours)
        end_time = approximate_time + timedelta(hours=search_window_hours)
        
        while current_test_time <= end_time:
            score = 0.0
            event_matches = []
            
            # For each known event, check if progressions match
            for event in self.known_events:
                # Calculate what aspects should be active at event date
                # with this test birth time
                days_elapsed = (event.event_date - current_test_time).days
                
                # Simple progression: 1 day = 1 year
                progressed_position = (days_elapsed % 365) / 365.0 * 360.0
                
                # Check for expected aspects
                if self._aspect_matches(days_elapsed, event.expected_aspect):
                    score += event.confidence * 10
                    event_matches.append(f"{event.event_type}: {event.event_description}")
            
            # Update best if this is better
            if score > best_score:
                best_score = score
                best_correction = current_test_time - approximate_time
                supporting_events = event_matches
            
            current_test_time += time_step
        
        # Normalize confidence
        confidence = min(best_score / 100.0, 1.0)  # Scale to 0-1
        
        corrected_time = approximate_time + best_correction
        
        return RectificationResult(
            original_birth_time=approximate_time,
            corrected_birth_time=corrected_time,
            time_correction=best_correction,
            confidence=confidence,
            method_used=RectificationMethod.EVENT_CORRELATION,
            verification_score=best_score / 100.0,
            supporting_events=supporting_events,
            additional_notes=f"Tested time window ±{search_window_hours} hours, found {len(supporting_events)} event correlations"
        )
    
    def _aspect_matches(self, days_elapsed: int, expected_aspect: str) -> bool:
        """Check if progressed aspect matches expected."""
        # Simplified: just check if a major aspect is forming
        days_mod = days_elapsed % 365
        year_fraction = days_mod / 365.0
        
        # Check for major progression markers
        major_markers = [0.25, 0.33, 0.5, 0.66, 0.75, 1.0]
        tolerance = 0.05
        
        for marker in major_markers:
            if abs(year_fraction - marker) < tolerance:
                return True
        
        return False


class CompositeChartAnalysis:
    """Advanced composite and davison chart analysis."""
    
    def create_composite_chart(
        self,
        person1_chart: Dict,
        person2_chart: Dict,
        person1_name: str = "Person 1",
        person2_name: str = "Person 2"
    ) -> CompositeChart:
        """Create composite chart - midpoints of two charts.
        
        The composite chart represents the relationship itself,
        showing the dynamic between two people.
        """
        # Calculate midpoint positions for all planets
        composite_positions = {}
        for planet in person1_chart.keys():
            if planet in person2_chart:
                pos1 = person1_chart[planet]
                pos2 = person2_chart[planet]
                
                # Calculate midpoint (accounting for 360° wrap)
                diff = (pos2 - pos1) % 360
                if diff > 180:
                    diff = diff - 360
                
                midpoint = (pos1 + diff / 2) % 360
                composite_positions[planet] = midpoint
        
        # Determine composite ascendant (midpoint of ascendants)
        if "Ascendant" in composite_positions:
            asc_value = composite_positions["Ascendant"]
            asc_sign = self._get_sign(asc_value)
        else:
            asc_sign = "Unknown"
        
        # Find chart patterns
        patterns = self._find_chart_patterns(composite_positions)
        pattern_descriptions = [p.pattern_type.value for p in patterns]
        
        # Find strongest aspects in composite
        strongest_aspects = self._find_strongest_aspects(composite_positions)
        
        # Calculate house cusps (simplified - would use proper calculation)
        house_cusps = self._calculate_composite_houses(asc_value if "Ascendant" in composite_positions else 0)
        
        return CompositeChart(
            person1_name=person1_name,
            person2_name=person2_name,
            composite_positions=composite_positions,
            house_cusps=house_cusps,
            composite_ascendant=asc_sign,
            chart_patterns=pattern_descriptions,
            strongest_aspects=strongest_aspects
        )
    
    def create_davison_chart(
        self,
        birth1_date: datetime,
        birth2_date: datetime,
        location1: Tuple[float, float],
        location2: Tuple[float, float],
        person1_name: str = "Person 1",
        person2_name: str = "Person 2"
    ) -> Dict:
        """Create Davison chart - fixed in time and space.
        
        The Davison chart calculates the midpoint in time and space
        between two people's births. It represents the relationship
        genesis point in space-time.
        """
        # Calculate midpoint time
        time_diff = (birth2_date - birth1_date).total_seconds() / 2
        davison_datetime = birth1_date + timedelta(seconds=time_diff)
        
        # Calculate midpoint location
        davison_lat = (location1[0] + location2[0]) / 2
        davison_long = (location1[1] + location2[1]) / 2
        davison_location = (davison_lat, davison_long)
        
        return {
            "datetime": davison_datetime,
            "location": davison_location,
            "person1": person1_name,
            "person2": person2_name,
            "interpretation": self._interpret_davison_chart(
                davison_datetime,
                davison_location,
                person1_name,
                person2_name
            )
        }
    
    def _find_chart_patterns(self, positions: Dict[str, float]) -> List[AdvancedChartPattern]:
        """Find advanced chart patterns (Grand Trines, Grand Crosses, etc.)."""
        patterns = []
        
        # Check for Grand Trine (3 planets 120° apart)
        grand_trine = self._find_grand_trine(positions)
        if grand_trine:
            patterns.append(AdvancedChartPattern(
                pattern_type=ChartPatternType.GRAND_TRINE,
                planets_involved=grand_trine,
                interpretation="Three planets in harmonious triangle - easy flow of energy",
                significance="major",
                influence_area="Overall life flow and natural talents"
            ))
        
        # Check for Grand Cross (4 planets 90° apart)
        grand_cross = self._find_grand_cross(positions)
        if grand_cross:
            patterns.append(AdvancedChartPattern(
                pattern_type=ChartPatternType.GRAND_CROSS,
                planets_involved=grand_cross,
                interpretation="Four planets in square formation - dynamic tension and challenges",
                significance="major",
                influence_area="Life lessons and karmic challenges"
            ))
        
        # Check for Yod (2 planets quincunx 3rd)
        yod = self._find_yod(positions)
        if yod:
            patterns.append(AdvancedChartPattern(
                pattern_type=ChartPatternType.YOD,
                planets_involved=yod,
                interpretation="Finger of Fate - special purpose or unique gift",
                significance="major",
                influence_area="Life purpose and spiritual path"
            ))
        
        # Check for T-Square (3 planets forming T)
        t_square = self._find_t_square(positions)
        if t_square:
            patterns.append(AdvancedChartPattern(
                pattern_type=ChartPatternType.T_SQUARE,
                planets_involved=t_square,
                interpretation="Focal point and challenge - drive for achievement",
                significance="major",
                influence_area="Career and personal challenges"
            ))
        
        # Check for Stellium (3+ planets in same sign/house)
        stellium = self._find_stellium(positions)
        if stellium:
            patterns.append(AdvancedChartPattern(
                pattern_type=ChartPatternType.STELLIUM,
                planets_involved=stellium,
                interpretation="Concentrated power in one area - intense focus",
                significance="moderate",
                influence_area="Specialized talents and focus"
            ))
        
        return patterns
    
    def _find_grand_trine(self, positions: Dict[str, float]) -> Optional[List[str]]:
        """Find Grand Trine pattern (3 planets 120° apart)."""
        planets = list(positions.keys())
        tolerance = 8.0  # degrees
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                for k in range(j + 1, len(planets)):
                    p1, p2, p3 = planets[i], planets[j], planets[k]
                    
                    # Calculate angles
                    angle12 = self._normalize_angle(positions[p1] - positions[p2])
                    angle23 = self._normalize_angle(positions[p2] - positions[p3])
                    angle31 = self._normalize_angle(positions[p3] - positions[p1])
                    
                    # Check if all are ~120°
                    if (self._is_aspect(angle12, 120, tolerance) and
                        self._is_aspect(angle23, 120, tolerance) and
                        self._is_aspect(angle31, 120, tolerance)):
                        return [p1, p2, p3]
        
        return None
    
    def _find_grand_cross(self, positions: Dict[str, float]) -> Optional[List[str]]:
        """Find Grand Cross pattern (4 planets 90° apart)."""
        planets = list(positions.keys())
        tolerance = 8.0
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                for k in range(j + 1, len(planets)):
                    for l in range(k + 1, len(planets)):
                        p1, p2, p3, p4 = planets[i], planets[j], planets[k], planets[l]
                        
                        angles = [
                            self._normalize_angle(positions[p1] - positions[p2]),
                            self._normalize_angle(positions[p2] - positions[p3]),
                            self._normalize_angle(positions[p3] - positions[p4]),
                            self._normalize_angle(positions[p4] - positions[p1]),
                        ]
                        
                        if all(self._is_aspect(a, 90, tolerance) for a in angles):
                            return [p1, p2, p3, p4]
        
        return None
    
    def _find_yod(self, positions: Dict[str, float]) -> Optional[List[str]]:
        """Find Yod pattern (2 planets quincunx 3rd)."""
        planets = list(positions.keys())
        tolerance = 3.0  # Quincunx has tighter orb
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                for k in range(j + 1, len(planets)):
                    p1, p2, p3 = planets[i], planets[j], planets[k]
                    
                    angle12 = self._normalize_angle(positions[p1] - positions[p2])
                    angle13 = self._normalize_angle(positions[p1] - positions[p3])
                    angle23 = self._normalize_angle(positions[p2] - positions[p3])
                    
                    # Two quincunx (150°) aspects
                    quincunx_count = 0
                    if self._is_aspect(angle12, 150, tolerance) or self._is_aspect(angle12, 210, tolerance):
                        quincunx_count += 1
                    if self._is_aspect(angle13, 150, tolerance) or self._is_aspect(angle13, 210, tolerance):
                        quincunx_count += 1
                    
                    if quincunx_count >= 2:
                        return [p1, p2, p3]
        
        return None
    
    def _find_t_square(self, positions: Dict[str, float]) -> Optional[List[str]]:
        """Find T-Square pattern (3 planets with 2 squares and 1 opposition)."""
        planets = list(positions.keys())
        tolerance = 8.0
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                for k in range(j + 1, len(planets)):
                    p1, p2, p3 = planets[i], planets[j], planets[k]
                    
                    angle12 = self._normalize_angle(positions[p1] - positions[p2])
                    angle23 = self._normalize_angle(positions[p2] - positions[p3])
                    angle31 = self._normalize_angle(positions[p3] - positions[p1])
                    
                    # Check for 2 squares and 1 opposition
                    square_count = sum([
                        self._is_aspect(angle12, 90, tolerance),
                        self._is_aspect(angle23, 90, tolerance),
                        self._is_aspect(angle31, 90, tolerance),
                    ])
                    
                    opp_count = sum([
                        self._is_aspect(angle12, 180, tolerance),
                        self._is_aspect(angle23, 180, tolerance),
                        self._is_aspect(angle31, 180, tolerance),
                    ])
                    
                    if square_count == 2 and opp_count == 1:
                        return [p1, p2, p3]
        
        return None
    
    def _find_stellium(self, positions: Dict[str, float]) -> Optional[List[str]]:
        """Find Stellium (3+ planets in same sign)."""
        # Group planets by sign
        signs = {}
        for planet, position in positions.items():
            sign_index = int(position / 30)
            if sign_index not in signs:
                signs[sign_index] = []
            signs[sign_index].append(planet)
        
        # Find signs with 3+ planets
        for sign_planets in signs.values():
            if len(sign_planets) >= 3:
                return sign_planets
        
        return None
    
    def _find_strongest_aspects(self, positions: Dict[str, float]) -> List[str]:
        """Find the strongest aspects in the chart."""
        aspects = []
        planets = list(positions.keys())
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1, p2 = planets[i], planets[j]
                angle = self._normalize_angle(positions[p1] - positions[p2])
                
                # Check for major aspects
                for aspect_name, aspect_degree in [
                    ("Conjunction", 0),
                    ("Sextile", 60),
                    ("Square", 90),
                    ("Trine", 120),
                    ("Opposition", 180),
                ]:
                    if self._is_aspect(angle, aspect_degree, 8.0):
                        orb = self._calculate_orb(angle, aspect_degree)
                        aspects.append(f"{p1} {aspect_name} {p2} ({orb:.1f}°)")
        
        # Sort by orb (tightest first)
        aspects.sort()
        return aspects[:10]  # Return top 10
    
    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to 0-360 range."""
        angle = angle % 360
        if angle > 180:
            angle = 360 - angle
        return angle
    
    def _is_aspect(self, angle: float, target: float, tolerance: float) -> bool:
        """Check if angle matches target aspect."""
        normalized = self._normalize_angle(angle)
        normalized_target = self._normalize_angle(target)
        return abs(normalized - normalized_target) <= tolerance
    
    def _calculate_orb(self, angle: float, target: float) -> float:
        """Calculate exact orb from target aspect."""
        normalized = self._normalize_angle(angle)
        normalized_target = self._normalize_angle(target)
        return abs(normalized - normalized_target)
    
    def _get_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude."""
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign_index = int(longitude / 30) % 12
        return signs[sign_index]
    
    def _calculate_composite_houses(self, asc: float) -> Dict[int, float]:
        """Calculate composite house cusps (simplified Whole Sign)."""
        houses = {}
        for i in range(1, 13):
            houses[i] = (asc + (i - 1) * 30) % 360
        return houses
    
    def _interpret_davison_chart(
        self,
        davison_datetime: datetime,
        davison_location: Tuple[float, float],
        person1_name: str,
        person2_name: str
    ) -> str:
        """Generate interpretation of Davison chart."""
        return (
            f"**DAVISON CHART - Relationship Genesis Point**\n\n"
            f"The Davison chart represents the midpoint in time and space between "
            f"{person1_name} and {person2_name}'s births. This chart shows the "
            f"fundamental nature of the relationship in the cosmos.\n\n"
            f"Calculated: {davison_datetime.strftime('%B %d, %Y at %H:%M')}\n"
            f"Location: {davison_location[0]:.2f}°N, {davison_location[1]:.2f}°E\n\n"
            f"This chart reveals the deeper purpose and karmic connection between "
            f"the two individuals."
        )


class AstroMapping:
    """Relocation astrology - where to move for best planetary influence."""
    
    def create_astro_map(
        self,
        birth_chart: Dict,
        current_location: Tuple[float, float],
        new_location: Tuple[float, float]
    ) -> AstroMapData:
        """Create astro-map showing how moving affects planetary positions."""
        
        # Calculate angle shifts
        angle_shifts = self._calculate_angle_shifts(
            current_location,
            new_location,
            birth_chart
        )
        
        # Identify power locations
        power_locations = self._identify_power_locations(birth_chart)
        
        # Identify challenging locations
        challenging_locations = self._identify_challenging_locations(birth_chart)
        
        # Generate recommendations
        recommendations = self._generate_relocation_recommendations(
            birth_chart,
            angle_shifts
        )
        
        return AstroMapData(
            original_location=current_location,
            new_location=new_location,
            angle_shifts=angle_shifts,
            power_locations=power_locations,
            challenging_locations=challenging_locations,
            recommendations=recommendations
        )
    
    def _calculate_angle_shifts(
        self,
        current: Tuple[float, float],
        new: Tuple[float, float],
        chart: Dict
    ) -> Dict[str, float]:
        """Calculate how angles shift with relocation."""
        # Simplified calculation - production would use proper astro-mapping math
        lat_diff = new[0] - current[0]
        long_diff = new[1] - current[1]
        
        shifts = {}
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
            if planet in chart:
                # Angle shifts based on latitude/longitude changes
                shift = (lat_diff + long_diff) / 2
                shifts[planet] = shift
        
        return shifts
    
    def _identify_power_locations(self, chart: Dict) -> List[Dict]:
        """Identify locations where planets are strong."""
        power_locations = []
        
        # Venus on IC = Venus line - great for love, beauty, arts
        if "Venus" in chart:
            power_locations.append({
                "planet": "Venus",
                "line_type": "IC/MC",
                "description": "Venus strength - ideal for romance, arts, beauty",
                "benefit": "Enhanced relationships and creative expression"
            })
        
        # Jupiter on angles = great fortune
        if "Jupiter" in chart:
            power_locations.append({
                "planet": "Jupiter",
                "line_type": "Angle",
                "description": "Jupiter strength - luck and expansion",
                "benefit": "Business success, opportunities, growth"
            })
        
        return power_locations
    
    def _identify_challenging_locations(self, chart: Dict) -> List[Dict]:
        """Identify locations with challenging planetary influence."""
        challenging = []
        
        # Saturn on angles = restrictions
        if "Saturn" in chart:
            challenging.append({
                "planet": "Saturn",
                "description": "Saturn strength - restrictions and limitations",
                "caution": "May experience delays and challenges in that location"
            })
        
        return challenging
    
    def _generate_relocation_recommendations(
        self,
        chart: Dict,
        shifts: Dict[str, float]
    ) -> List[str]:
        """Generate relocation recommendations."""
        recommendations = []
        
        recommendations.append("For love and relationships: Consider moving to a Venus line")
        recommendations.append("For business success: Look for Jupiter line areas")
        recommendations.append("For spiritual growth: Find Neptune or Moon line areas")
        recommendations.append("Avoid Saturn line for 7 years after relocation if possible")
        
        return recommendations


# Create singletons
rectification_engine = ChartRectification()
composite_chart_analyzer = CompositeChartAnalysis()
astro_mapper = AstroMapping()

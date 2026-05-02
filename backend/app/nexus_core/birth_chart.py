"""Birth chart generation with astronomical calculations."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import os
import math
from enum import Enum

try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except Exception:
    swe = None
    SWISSEPH_AVAILABLE = False


class ZodiacSign(Enum):
    """Zodiac signs with their degrees."""
    ARIES = (0, 30, "♈", "Fire", "Cardinal")
    TAURUS = (30, 60, "♉", "Earth", "Fixed")
    GEMINI = (60, 90, "♊", "Air", "Mutable")
    CANCER = (90, 120, "♋", "Water", "Cardinal")
    LEO = (120, 150, "♌", "Fire", "Fixed")
    VIRGO = (150, 180, "♍", "Earth", "Mutable")
    LIBRA = (180, 210, "♎", "Air", "Cardinal")
    SCORPIO = (210, 240, "♏", "Water", "Fixed")
    SAGITTARIUS = (240, 270, "♐", "Fire", "Mutable")
    CAPRICORN = (270, 300, "♑", "Earth", "Cardinal")
    AQUARIUS = (300, 330, "♒", "Air", "Fixed")
    PISCES = (330, 360, "♓", "Water", "Mutable")

    @property
    def start_degree(self):
        return self.value[0]
    
    @property
    def end_degree(self):
        return self.value[1]
    
    @property
    def symbol(self):
        return self.value[2]
    
    @property
    def element(self):
        return self.value[3]
    
    @property
    def modality(self):
        return self.value[4]


class Planet(Enum):
    """Major planets and luminaries."""
    SUN = ("☉", "Self, vitality, core essence")
    MOON = ("☽", "Emotions, instincts, inner self")
    MERCURY = ("☿", "Communication, thought, learning")
    VENUS = ("♀", "Love, beauty, values")
    MARS = ("♂", "Action, drive, passion")
    JUPITER = ("♃", "Growth, expansion, luck")
    SATURN = ("♄", "Structure, discipline, lessons")
    URANUS = ("♅", "Innovation, rebellion, awakening")
    NEPTUNE = ("♆", "Dreams, spirituality, illusion")
    PLUTO = ("♇", "Transformation, power, rebirth")
    
    @property
    def symbol(self):
        return self.value[0]
    
    @property
    def meaning(self):
        return self.value[1]


@dataclass
class ChartPoint:
    """Chart points like Nodes, Chiron, Lilith, Part of Fortune."""
    name: str
    symbol: str
    sign: ZodiacSign
    degree: float
    house: int

    def __str__(self):
        return f"{self.symbol} {self.name} in {self.sign.name} {self.degree:.1f}° (House {self.house})"


class House(Enum):
    """Twelve astrological houses."""
    FIRST = (1, "Self, appearance, identity")
    SECOND = (2, "Values, possessions, security")
    THIRD = (3, "Communication, siblings, short trips")
    FOURTH = (4, "Home, family, roots")
    FIFTH = (5, "Creativity, romance, children")
    SIXTH = (6, "Health, service, daily routine")
    SEVENTH = (7, "Partnerships, marriage, contracts")
    EIGHTH = (8, "Transformation, shared resources, intimacy")
    NINTH = (9, "Philosophy, travel, higher learning")
    TENTH = (10, "Career, reputation, public life")
    ELEVENTH = (11, "Friends, groups, aspirations")
    TWELFTH = (12, "Spirituality, subconscious, hidden matters")
    
    @property
    def number(self):
        return self.value[0]
    
    @property
    def meaning(self):
        return self.value[1]


@dataclass
class PlanetPosition:
    """Position of a planet in the chart."""
    planet: Planet
    sign: ZodiacSign
    degree: float
    house: int
    retrograde: bool = False
    dignity: Optional[str] = None
    
    def __str__(self):
        retro = "℞" if self.retrograde else ""
        dignity = f" [{self.dignity}]" if self.dignity else ""
        return f"{self.planet.symbol} {self.sign.name} {self.degree:.1f}° (House {self.house}){retro}{dignity}"


@dataclass
class Aspect:
    """Aspect between two planets."""
    planet1: Planet
    planet2: Planet
    angle: float
    aspect_type: str
    orb: float
    strength: str = ""
    
    def __str__(self):
        strength = f" {self.strength}" if self.strength else ""
        return f"{self.planet1.symbol} {self.aspect_type}{strength} {self.planet2.symbol} (orb: {self.orb:.1f}°)"


@dataclass
class BirthChart:
    """Complete birth chart data."""
    birth_date: datetime
    latitude: float
    longitude: float
    location_name: str
    
    # Chart components
    ascendant_sign: ZodiacSign
    ascendant_degree: float
    midheaven_sign: ZodiacSign
    midheaven_degree: float
    
    planets: Dict[Planet, PlanetPosition] = field(default_factory=dict)
    houses: Dict[int, float] = field(default_factory=dict)  # House cusps
    aspects: List[Aspect] = field(default_factory=list)
    points: Dict[str, ChartPoint] = field(default_factory=dict)
    
    # Chart ruler and dominant elements
    chart_ruler: Optional[Planet] = None
    dominant_element: Optional[str] = None
    dominant_modality: Optional[str] = None
    lunar_phase: Optional[str] = None
    lunar_phase_angle: Optional[float] = None
    element_counts: Dict[str, int] = field(default_factory=dict)
    modality_counts: Dict[str, int] = field(default_factory=dict)
    aspect_summary: Dict[str, int] = field(default_factory=dict)
    house_system: str = "equal"
    ephemeris_engine: str = "builtin"
    julian_day: Optional[float] = None
    utc_datetime: Optional[datetime] = None
    timezone_offset_hours: Optional[int] = None
    chart_sect: Optional[str] = None
    
    def get_sun_sign(self) -> ZodiacSign:
        """Get the Sun sign (zodiac sign)."""
        return self.planets[Planet.SUN].sign if Planet.SUN in self.planets else None
    
    def get_moon_sign(self) -> ZodiacSign:
        """Get the Moon sign."""
        return self.planets[Planet.MOON].sign if Planet.MOON in self.planets else None
    
    def get_rising_sign(self) -> ZodiacSign:
        """Get the Rising sign (Ascendant)."""
        return self.ascendant_sign


class BirthChartGenerator:
    """Generate birth charts with astronomical calculations."""
    
    def __init__(self):
        self.aspect_orbs = {
            'conjunction': 8.0,
            'opposition': 8.0,
            'trine': 8.0,
            'square': 7.0,
            'sextile': 6.0,
            'quincunx': 3.0
        }
        self.ephemeris_engine = "swisseph" if SWISSEPH_AVAILABLE else "builtin"
        if SWISSEPH_AVAILABLE:
            try:
                ephe_path = os.getenv("SWISSEPH_PATH")
                if not ephe_path:
                    local_ephe = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "ephemeris"))
                    ephe_path = local_ephe if os.path.exists(local_ephe) else None
                if ephe_path:
                    swe.set_ephe_path(ephe_path)
            except Exception:
                pass
    
    def parse_birth_data(self, text: str) -> Optional[Dict]:
        """Parse birth data from natural language input."""
        import re
        from dateutil import parser as date_parser
        
        result = {
            'date': None,
            'time': None,
            'location': None,
            'latitude': None,
            'longitude': None
        }
        
        # Try to extract date
        date_patterns = [
            r'(?:born|birth|birthday)?\s*(?:on\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:born|birth|birthday)?\s*(?:on\s+)?(\w+\s+\d{1,2},?\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['date'] = date_parser.parse(match.group(1))
                    break
                except:
                    continue
        
        # Extract time
        time_patterns = [
            r'(?:at\s+)?(\d{1,2}:\d{2}(?:\s*(?:AM|PM|am|pm))?)',
            r'(?:at\s+)?(\d{1,2}\s*(?:AM|PM|am|pm))'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    time_str = match.group(1)
                    result['time'] = date_parser.parse(time_str).time()
                    break
                except:
                    continue
        
        # Extract location (simplified - would need geocoding API for real implementation)
        location_pattern = r'(?:in|at|from)\s+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2})?)'
        match = re.search(location_pattern, text)
        if match:
            result['location'] = match.group(1).strip()
        
        return result if result['date'] else None
    
    def geocode_location(self, location: str) -> Tuple[float, float]:
        """Convert location name to coordinates (simplified).
        
        In production, would use a geocoding API like Google Maps or OpenStreetMap.
        """
        # Simplified major city coordinates
        known_locations = {
            'new york': (40.7128, -74.0060),
            'los angeles': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'london': (51.5074, -0.1278),
            'paris': (48.8566, 2.3522),
            'tokyo': (35.6762, 139.6503),
            'sydney': (-33.8688, 151.2093),
            'mumbai': (19.0760, 72.8777),
            'beijing': (39.9042, 116.4074),
            'moscow': (55.7558, 37.6173)
        }
        
        location_lower = location.lower()
        for city, coords in known_locations.items():
            if city in location_lower:
                return coords
        
        # Default to Greenwich if unknown
        return (51.4769, 0.0)

    def estimate_timezone_offset(self, longitude: float) -> int:
        """Estimate timezone offset (hours) from longitude.

        Uses a simple 15 degrees per hour approximation and rounds to nearest hour.
        """
        return int(round(longitude / 15.0))

    def _normalize_datetime(self, dt: datetime, longitude: float, tz_offset_hours: Optional[int]) -> datetime:
        """Normalize birth datetime to UTC for calculations.

        If timezone info is missing, estimate offset from longitude or use provided offset.
        """
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc)

        offset = tz_offset_hours
        if offset is None:
            offset = self.estimate_timezone_offset(longitude)
        return dt.replace(tzinfo=timezone.utc) - timedelta(hours=offset)

    def _is_retrograde(self, lon_now: float, lon_prev: float) -> bool:
        """Determine retrograde motion from longitude change with wrap handling."""
        delta = (lon_now - lon_prev + 540.0) % 360.0 - 180.0
        return delta < 0
    
    def calculate_julian_day(self, dt: datetime) -> float:
        """Calculate Julian Day Number for given datetime."""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Add time fraction
        time_fraction = (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
        
        return jdn + time_fraction

    def _use_swisseph(self, requested: Optional[str]) -> bool:
        if not SWISSEPH_AVAILABLE:
            return False
        if not requested:
            return True
        return requested.strip().lower() in {"swisseph", "swe", "swiss"}

    def _swe_julian_day(self, dt: datetime) -> float:
        """Calculate Julian Day using Swiss Ephemeris (UTC)."""
        hour = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0)
        return float(swe.julday(dt.year, dt.month, dt.day, hour))

    def _swe_planet_longitude(self, planet: Planet, jd: float) -> Tuple[float, float]:
        """Return (longitude, speed_longitude) for a planet using Swiss Ephemeris."""
        planet_map = {
            Planet.SUN: swe.SUN,
            Planet.MOON: swe.MOON,
            Planet.MERCURY: swe.MERCURY,
            Planet.VENUS: swe.VENUS,
            Planet.MARS: swe.MARS,
            Planet.JUPITER: swe.JUPITER,
            Planet.SATURN: swe.SATURN,
            Planet.URANUS: swe.URANUS,
            Planet.NEPTUNE: swe.NEPTUNE,
            Planet.PLUTO: swe.PLUTO,
        }
        swe_id = planet_map.get(planet, swe.SUN)
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result = swe.calc_ut(jd, swe_id, flags)
        if isinstance(result, tuple) and len(result) == 2:
            values = result[0]
        else:
            values = result
        lon, _lat, _dist, speed_lon, _speed_lat, _speed_dist = values
        return float(lon), float(speed_lon)

    def _swe_point_longitude(self, swe_id: int, jd: float) -> Tuple[float, float]:
        """Return (longitude, speed_longitude) for chart points via Swiss Ephemeris."""
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result = swe.calc_ut(jd, swe_id, flags)
        if isinstance(result, tuple) and len(result) == 2:
            values = result[0]
        else:
            values = result
        lon, _lat, _dist, speed_lon, _speed_lat, _speed_dist = values
        return float(lon), float(speed_lon)

    def _swe_house_cusps(self, jd: float, latitude: float, longitude: float, house_system: str) -> Tuple[Dict[int, float], float, float]:
        """Return (house_cusps, asc_degree, mc_degree) using Swiss Ephemeris."""
        system_key = (house_system or "equal").lower()
        system_map = {
            "equal": "E",
            "whole_sign": "W",
            "whole": "W",
            "placidus": "P",
            "pl": "P",
        }
        hs = system_map.get(system_key, "E")
        try:
            cusps, ascmc = swe.houses_ex(jd, latitude, longitude, hs.encode("ascii"))
            house_cusps = {i: float(cusps[i]) for i in range(1, 13) if i < len(cusps)}
            if len(house_cusps) < 12 or len(ascmc) < 2:
                raise IndexError("Swiss Ephemeris house cusp data incomplete")
            asc_degree = float(ascmc[0])
            mc_degree = float(ascmc[1])
            return house_cusps, asc_degree, mc_degree
        except Exception:
            # Fallback to simplified house calculations when Swiss Ephemeris output is incomplete.
            asc_sign, asc_degree = self.calculate_ascendant(jd, latitude, longitude)
            mc_sign, mc_degree = self.calculate_midheaven(jd, longitude)
            asc_full_degree = asc_sign.start_degree + asc_degree
            mc_full_degree = mc_sign.start_degree + mc_degree
            house_cusps = self.calculate_house_cusps(asc_full_degree, mc_full_degree, house_system=house_system)
            return house_cusps, asc_full_degree, mc_full_degree
    
    def calculate_sun_position(self, jd: float) -> float:
        """Calculate Sun's ecliptic longitude (simplified)."""
        # Days since J2000.0
        T = (jd - 2451545.0) / 36525.0
        
        # Mean longitude of Sun
        L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
        
        # Mean anomaly
        M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
        M_rad = math.radians(M)
        
        # Equation of center
        C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad)
        C += (0.019993 - 0.000101 * T) * math.sin(2 * M_rad)
        C += 0.000289 * math.sin(3 * M_rad)
        
        # True longitude
        sun_lon = (L0 + C) % 360
        
        return sun_lon
    
    def calculate_moon_position(self, jd: float) -> float:
        """Calculate Moon's ecliptic longitude (simplified)."""
        T = (jd - 2451545.0) / 36525.0
        
        # Moon's mean longitude
        L = 218.316 + 481267.881 * T
        
        # Simplified calculation
        moon_lon = L % 360
        
        return moon_lon
    
    def calculate_planet_position(self, planet: Planet, jd: float) -> float:
        """Calculate planet position (simplified using mean motion)."""
        T = (jd - 2451545.0) / 36525.0
        
        # Simplified mean longitudes (degrees per century)
        mean_motions = {
            Planet.MERCURY: (252.25 + 149472.68 * T) % 360,
            Planet.VENUS: (181.98 + 58517.82 * T) % 360,
            Planet.MARS: (355.43 + 19140.30 * T) % 360,
            Planet.JUPITER: (34.35 + 3034.91 * T) % 360,
            Planet.SATURN: (50.08 + 1222.11 * T) % 360,
            Planet.URANUS: (314.05 + 428.46 * T) % 360,
            Planet.NEPTUNE: (304.35 + 218.46 * T) % 360,
            Planet.PLUTO: (238.96 + 145.18 * T) % 360
        }
        
        return mean_motions.get(planet, 0.0)
    
    def degree_to_sign(self, degree: float) -> Tuple[ZodiacSign, float]:
        """Convert ecliptic longitude to zodiac sign and degree within sign."""
        degree = degree % 360
        
        for sign in ZodiacSign:
            if sign.start_degree <= degree < sign.end_degree:
                degree_in_sign = degree - sign.start_degree
                return sign, degree_in_sign
        
        return ZodiacSign.ARIES, 0.0
    
    def calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> Tuple[ZodiacSign, float]:
        """Calculate Ascendant (Rising sign)."""
        # Local Sidereal Time
        T = (jd - 2451545.0) / 36525.0
        gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T
        lst = (gmst + longitude) % 360
        
        # Obliquity of the ecliptic
        epsilon = 23.439291 - 0.0130042 * T
        epsilon_rad = math.radians(epsilon)
        
        # Ascendant calculation (simplified)
        lat_rad = math.radians(latitude)
        lst_rad = math.radians(lst)
        
        # Calculate ascendant degree
        asc_degree = math.degrees(math.atan2(
            math.sin(lst_rad),
            math.cos(lst_rad) * math.cos(epsilon_rad) + math.tan(lat_rad) * math.sin(epsilon_rad)
        )) % 360
        
        return self.degree_to_sign(asc_degree)
    
    def calculate_midheaven(self, jd: float, longitude: float) -> Tuple[ZodiacSign, float]:
        """Calculate Midheaven (MC)."""
        # Simplified MC calculation
        T = (jd - 2451545.0) / 36525.0
        gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T
        lst = (gmst + longitude) % 360
        
        mc_degree = lst % 360
        
        return self.degree_to_sign(mc_degree)
    
    def calculate_house_cusps(self, asc_degree: float, mc_degree: float, house_system: str = "equal") -> Dict[int, float]:
        """Calculate house cusps using a simplified house system.

        Supported systems:
        - equal: 30° houses from Ascendant degree
        - whole_sign: 30° houses from Ascendant sign start degree
        """
        houses = {}
        
        system = (house_system or "equal").lower()
        if system == "whole_sign":
            # Use the Ascendant sign start degree as the 1st house cusp
            asc_sign, _asc_deg = self.degree_to_sign(asc_degree)
            base_degree = asc_sign.start_degree
        else:
            base_degree = asc_degree

        # Ascendant is 1st house cusp
        houses[1] = base_degree
        
        # MC is 10th house cusp
        houses[10] = mc_degree
        
        # Calculate intermediate cusps (simplified equal house system)
        houses[4] = (mc_degree + 180) % 360  # IC
        houses[7] = (asc_degree + 180) % 360  # Descendant
        
        # Divide the quadrants
        for i in range(1, 4):
            houses[i + 1] = (houses[1] + i * 30) % 360
            houses[i + 4] = (houses[4] + i * 30) % 360
            houses[i + 7] = (houses[7] + i * 30) % 360
            houses[i + 10] = (houses[10] + i * 30) % 360
        
        return houses

    def calculate_lunar_phase(self, sun_lon: float, moon_lon: float) -> Tuple[str, float]:
        """Calculate lunar phase name and elongation angle."""
        phase_angle = (moon_lon - sun_lon) % 360.0
        # Phase boundaries (approximate)
        if phase_angle < 22.5 or phase_angle >= 337.5:
            phase = "New Moon"
        elif 22.5 <= phase_angle < 67.5:
            phase = "Waxing Crescent"
        elif 67.5 <= phase_angle < 112.5:
            phase = "First Quarter"
        elif 112.5 <= phase_angle < 157.5:
            phase = "Waxing Gibbous"
        elif 157.5 <= phase_angle < 202.5:
            phase = "Full Moon"
        elif 202.5 <= phase_angle < 247.5:
            phase = "Waning Gibbous"
        elif 247.5 <= phase_angle < 292.5:
            phase = "Last Quarter"
        else:
            phase = "Waning Crescent"

        return phase, phase_angle

    def _planet_dignity(self, planet: Planet, sign: ZodiacSign) -> Optional[str]:
        """Return classical essential dignity for a planet in a sign."""
        domiciles = {
            Planet.SUN: [ZodiacSign.LEO],
            Planet.MOON: [ZodiacSign.CANCER],
            Planet.MERCURY: [ZodiacSign.GEMINI, ZodiacSign.VIRGO],
            Planet.VENUS: [ZodiacSign.TAURUS, ZodiacSign.LIBRA],
            Planet.MARS: [ZodiacSign.ARIES, ZodiacSign.SCORPIO],
            Planet.JUPITER: [ZodiacSign.SAGITTARIUS, ZodiacSign.PISCES],
            Planet.SATURN: [ZodiacSign.CAPRICORN, ZodiacSign.AQUARIUS],
        }
        exaltations = {
            Planet.SUN: ZodiacSign.ARIES,
            Planet.MOON: ZodiacSign.TAURUS,
            Planet.MERCURY: ZodiacSign.VIRGO,
            Planet.VENUS: ZodiacSign.PISCES,
            Planet.MARS: ZodiacSign.CAPRICORN,
            Planet.JUPITER: ZodiacSign.CANCER,
            Planet.SATURN: ZodiacSign.LIBRA,
        }
        detriments = {
            Planet.SUN: [ZodiacSign.AQUARIUS],
            Planet.MOON: [ZodiacSign.CAPRICORN],
            Planet.MERCURY: [ZodiacSign.SAGITTARIUS, ZodiacSign.PISCES],
            Planet.VENUS: [ZodiacSign.SCORPIO, ZodiacSign.ARIES],
            Planet.MARS: [ZodiacSign.LIBRA, ZodiacSign.TAURUS],
            Planet.JUPITER: [ZodiacSign.GEMINI, ZodiacSign.VIRGO],
            Planet.SATURN: [ZodiacSign.CANCER, ZodiacSign.LEO],
        }
        falls = {
            Planet.SUN: ZodiacSign.LIBRA,
            Planet.MOON: ZodiacSign.SCORPIO,
            Planet.MERCURY: ZodiacSign.PISCES,
            Planet.VENUS: ZodiacSign.VIRGO,
            Planet.MARS: ZodiacSign.CANCER,
            Planet.JUPITER: ZodiacSign.CAPRICORN,
            Planet.SATURN: ZodiacSign.ARIES,
        }

        if planet in domiciles and sign in domiciles[planet]:
            return "domicile"
        if planet in exaltations and sign == exaltations[planet]:
            return "exaltation"
        if planet in detriments and sign in detriments[planet]:
            return "detriment"
        if planet in falls and sign == falls[planet]:
            return "fall"
        return None

    def _calculate_sect(self, sun_lon: float, house_cusps: Dict[int, float]) -> str:
        """Determine chart sect (day/night) based on Sun's house location."""
        sun_house = self._find_house(sun_lon, house_cusps)
        return "day" if sun_house >= 7 else "night"

    def _calculate_part_of_fortune(self, asc_degree: float, sun_lon: float, moon_lon: float, chart_sect: str) -> float:
        """Calculate Part of Fortune using sect-appropriate formula."""
        if chart_sect == "day":
            pof = asc_degree + moon_lon - sun_lon
        else:
            pof = asc_degree + sun_lon - moon_lon
        return pof % 360.0
    
    def calculate_aspects(self, planets: Dict[Planet, PlanetPosition]) -> List[Aspect]:
        """Calculate major aspects between planets."""
        aspects = []
        planet_list = list(planets.keys())
        
        aspect_angles = {
            0: 'conjunction',
            60: 'sextile',
            90: 'square',
            120: 'trine',
            150: 'quincunx',
            180: 'opposition'
        }
        
        for i, p1 in enumerate(planet_list):
            for p2 in planet_list[i+1:]:
                # Calculate angular distance
                deg1 = planets[p1].sign.start_degree + planets[p1].degree
                deg2 = planets[p2].sign.start_degree + planets[p2].degree
                
                diff = abs(deg1 - deg2)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for aspects
                for angle, asp_type in aspect_angles.items():
                    orb = abs(diff - angle)
                    max_orb = self.aspect_orbs.get(asp_type, 5.0)
                    
                    if orb <= max_orb:
                        if orb <= 1.0:
                            strength = "exact"
                        elif orb <= 3.0:
                            strength = "strong"
                        elif orb <= 5.0:
                            strength = "moderate"
                        else:
                            strength = "wide"
                        aspects.append(Aspect(
                            planet1=p1,
                            planet2=p2,
                            angle=angle,
                            aspect_type=asp_type,
                            orb=orb,
                            strength=strength
                        ))
                        break
        
        return aspects
    
    def determine_chart_ruler(self, ascendant_sign: ZodiacSign) -> Planet:
        """Determine chart ruler based on Ascendant sign."""
        rulers = {
            ZodiacSign.ARIES: Planet.MARS,
            ZodiacSign.TAURUS: Planet.VENUS,
            ZodiacSign.GEMINI: Planet.MERCURY,
            ZodiacSign.CANCER: Planet.MOON,
            ZodiacSign.LEO: Planet.SUN,
            ZodiacSign.VIRGO: Planet.MERCURY,
            ZodiacSign.LIBRA: Planet.VENUS,
            ZodiacSign.SCORPIO: Planet.PLUTO,
            ZodiacSign.SAGITTARIUS: Planet.JUPITER,
            ZodiacSign.CAPRICORN: Planet.SATURN,
            ZodiacSign.AQUARIUS: Planet.URANUS,
            ZodiacSign.PISCES: Planet.NEPTUNE
        }
        
        return rulers.get(ascendant_sign, Planet.SUN)
    
    def calculate_dominant_element(self, planets: Dict[Planet, PlanetPosition]) -> str:
        """Calculate dominant element in the chart."""
        element_counts = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
        
        for planet_pos in planets.values():
            element_counts[planet_pos.sign.element] += 1
        
        return max(element_counts, key=element_counts.get)
    
    def calculate_dominant_modality(self, planets: Dict[Planet, PlanetPosition]) -> str:
        """Calculate dominant modality in the chart."""
        modality_counts = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}
        
        for planet_pos in planets.values():
            modality_counts[planet_pos.sign.modality] += 1
        
        return max(modality_counts, key=modality_counts.get)

    def _count_elements(self, planets: Dict[Planet, PlanetPosition]) -> Dict[str, int]:
        counts = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
        for pos in planets.values():
            counts[pos.sign.element] += 1
        return counts

    def _count_modalities(self, planets: Dict[Planet, PlanetPosition]) -> Dict[str, int]:
        counts = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}
        for pos in planets.values():
            counts[pos.sign.modality] += 1
        return counts

    def _summarize_aspects(self, aspects: List[Aspect]) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for aspect in aspects:
            summary[aspect.aspect_type] = summary.get(aspect.aspect_type, 0) + 1
        return summary
    
    def generate_chart(self, birth_date: datetime, latitude: float, longitude: float, 
                      location_name: str = "Unknown", tz_offset_hours: Optional[int] = None,
                      house_system: str = "equal", ephemeris_engine: Optional[str] = None) -> BirthChart:
        """Generate complete birth chart."""
        # Normalize to UTC and calculate Julian Day
        normalized_birth_date = self._normalize_datetime(birth_date, longitude, tz_offset_hours)
        use_swisseph = self._use_swisseph(ephemeris_engine)
        jd = self._swe_julian_day(normalized_birth_date) if use_swisseph else self.calculate_julian_day(normalized_birth_date)
        
        # Calculate Ascendant and Midheaven
        if use_swisseph:
            house_cusps, asc_full_degree, mc_full_degree = self._swe_house_cusps(jd, latitude, longitude, house_system)
            asc_sign, asc_degree = self.degree_to_sign(asc_full_degree)
            mc_sign, mc_degree = self.degree_to_sign(mc_full_degree)
        else:
            asc_sign, asc_degree = self.calculate_ascendant(jd, latitude, longitude)
            mc_sign, mc_degree = self.calculate_midheaven(jd, longitude)
        
        # Calculate house cusps
        if not use_swisseph:
            asc_full_degree = asc_sign.start_degree + asc_degree
            mc_full_degree = mc_sign.start_degree + mc_degree
            house_cusps = self.calculate_house_cusps(asc_full_degree, mc_full_degree, house_system=house_system)
        
        # Calculate planet positions
        planets = {}
        if use_swisseph:
            sun_lon, sun_speed = self._swe_planet_longitude(Planet.SUN, jd)
            sun_sign, sun_deg = self.degree_to_sign(sun_lon)
            sun_house = self._find_house(sun_lon, house_cusps)
            sun_dignity = self._planet_dignity(Planet.SUN, sun_sign)
            planets[Planet.SUN] = PlanetPosition(Planet.SUN, sun_sign, sun_deg, sun_house, dignity=sun_dignity)

            moon_lon, moon_speed = self._swe_planet_longitude(Planet.MOON, jd)
            moon_sign, moon_deg = self.degree_to_sign(moon_lon)
            moon_house = self._find_house(moon_lon, house_cusps)
            moon_dignity = self._planet_dignity(Planet.MOON, moon_sign)
            planets[Planet.MOON] = PlanetPosition(Planet.MOON, moon_sign, moon_deg, moon_house, dignity=moon_dignity)

            for planet in [Planet.MERCURY, Planet.VENUS, Planet.MARS, Planet.JUPITER,
                          Planet.SATURN, Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO]:
                planet_lon, planet_speed = self._swe_planet_longitude(planet, jd)
                planet_sign, planet_deg = self.degree_to_sign(planet_lon)
                planet_house = self._find_house(planet_lon, house_cusps)
                retrograde = planet_speed < 0
                dignity = self._planet_dignity(planet, planet_sign)
                planets[planet] = PlanetPosition(planet, planet_sign, planet_deg, planet_house, retrograde=retrograde, dignity=dignity)
        else:
            # Sun
            sun_lon = self.calculate_sun_position(jd)
            sun_sign, sun_deg = self.degree_to_sign(sun_lon)
            sun_house = self._find_house(sun_lon, house_cusps)
            sun_dignity = self._planet_dignity(Planet.SUN, sun_sign)
            planets[Planet.SUN] = PlanetPosition(Planet.SUN, sun_sign, sun_deg, sun_house, dignity=sun_dignity)

            # Moon
            moon_lon = self.calculate_moon_position(jd)
            moon_sign, moon_deg = self.degree_to_sign(moon_lon)
            moon_house = self._find_house(moon_lon, house_cusps)
            moon_dignity = self._planet_dignity(Planet.MOON, moon_sign)
            planets[Planet.MOON] = PlanetPosition(Planet.MOON, moon_sign, moon_deg, moon_house, dignity=moon_dignity)

            # Other planets
            for planet in [Planet.MERCURY, Planet.VENUS, Planet.MARS, Planet.JUPITER, 
                          Planet.SATURN, Planet.URANUS, Planet.NEPTUNE, Planet.PLUTO]:
                planet_lon = self.calculate_planet_position(planet, jd)
                planet_prev = self.calculate_planet_position(planet, jd - 1.0)
                planet_sign, planet_deg = self.degree_to_sign(planet_lon)
                planet_house = self._find_house(planet_lon, house_cusps)
                retrograde = self._is_retrograde(planet_lon, planet_prev)
                dignity = self._planet_dignity(planet, planet_sign)
                planets[planet] = PlanetPosition(planet, planet_sign, planet_deg, planet_house, retrograde=retrograde, dignity=dignity)
        
        # Calculate aspects
        aspects = self.calculate_aspects(planets)
        
        # Calculate lunar phase
        lunar_phase, lunar_phase_angle = self.calculate_lunar_phase(sun_lon, moon_lon)

        # Determine chart characteristics
        chart_ruler = self.determine_chart_ruler(asc_sign)
        dominant_element = self.calculate_dominant_element(planets)
        dominant_modality = self.calculate_dominant_modality(planets)
        element_counts = self._count_elements(planets)
        modality_counts = self._count_modalities(planets)
        aspect_summary = self._summarize_aspects(aspects)

        # Chart sect + Part of Fortune
        asc_full_degree = asc_sign.start_degree + asc_degree
        chart_sect = self._calculate_sect(sun_lon, house_cusps)
        part_of_fortune_deg = self._calculate_part_of_fortune(asc_full_degree, sun_lon, moon_lon, chart_sect)

        # Additional points (Nodes, Chiron, Lilith)
        points: Dict[str, ChartPoint] = {}
        if use_swisseph:
            try:
                nn_lon, _ = self._swe_point_longitude(swe.TRUE_NODE, jd)
                sn_lon = (nn_lon + 180.0) % 360.0
                nn_sign, nn_deg = self.degree_to_sign(nn_lon)
                sn_sign, sn_deg = self.degree_to_sign(sn_lon)
                points["North Node"] = ChartPoint("North Node", "☊", nn_sign, nn_deg, self._find_house(nn_lon, house_cusps))
                points["South Node"] = ChartPoint("South Node", "☋", sn_sign, sn_deg, self._find_house(sn_lon, house_cusps))
            except Exception:
                pass

            try:
                chiron_lon, chiron_speed = self._swe_point_longitude(swe.CHIRON, jd)
                chiron_sign, chiron_deg = self.degree_to_sign(chiron_lon)
                points["Chiron"] = ChartPoint("Chiron", "⚷", chiron_sign, chiron_deg, self._find_house(chiron_lon, house_cusps))
            except Exception:
                pass

            try:
                lilith_lon, _ = self._swe_point_longitude(swe.MEAN_APOG, jd)
                lilith_sign, lilith_deg = self.degree_to_sign(lilith_lon)
                points["Lilith"] = ChartPoint("Lilith", "⚸", lilith_sign, lilith_deg, self._find_house(lilith_lon, house_cusps))
            except Exception:
                pass

        # Part of Fortune as a point
        pof_sign, pof_deg = self.degree_to_sign(part_of_fortune_deg)
        points["Part of Fortune"] = ChartPoint("Part of Fortune", "⊕", pof_sign, pof_deg, self._find_house(part_of_fortune_deg, house_cusps))
        
        # Create birth chart
        chart = BirthChart(
            birth_date=birth_date,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            ascendant_sign=asc_sign,
            ascendant_degree=asc_degree,
            midheaven_sign=mc_sign,
            midheaven_degree=mc_degree,
            planets=planets,
            houses=house_cusps,
            aspects=aspects,
            points=points,
            chart_ruler=chart_ruler,
            dominant_element=dominant_element,
            dominant_modality=dominant_modality,
            lunar_phase=lunar_phase,
            lunar_phase_angle=lunar_phase_angle,
            element_counts=element_counts,
            modality_counts=modality_counts,
            aspect_summary=aspect_summary,
            house_system=house_system,
            ephemeris_engine="swisseph" if use_swisseph else "builtin",
            julian_day=jd,
            utc_datetime=normalized_birth_date,
            timezone_offset_hours=tz_offset_hours,
            chart_sect=chart_sect
        )
        
        return chart
    
    def _find_house(self, planet_degree: float, house_cusps: Dict[int, float]) -> int:
        """Determine which house a planet is in."""
        for house_num in range(1, 13):
            next_house = (house_num % 12) + 1
            cusp = house_cusps[house_num]
            next_cusp = house_cusps[next_house]
            
            if cusp < next_cusp:
                if cusp <= planet_degree < next_cusp:
                    return house_num
            else:  # Handles wrap around 360
                if planet_degree >= cusp or planet_degree < next_cusp:
                    return house_num
        
        return 1  # Default to 1st house
    
    def format_chart(self, chart: BirthChart) -> str:
        """Format birth chart for display."""
        lines = []
        lines.append("=" * 60)
        lines.append("✨ BIRTH CHART ✨".center(60))
        lines.append("=" * 60)
        lines.append(f"\n📅 Birth Data:")
        lines.append(f"   Date & Time: {chart.birth_date.strftime('%B %d, %Y at %I:%M %p')}")
        if chart.utc_datetime:
            lines.append(f"   UTC Time: {chart.utc_datetime.strftime('%B %d, %Y at %I:%M %p')} UTC")
        lines.append(f"   Location: {chart.location_name}")
        lines.append(f"   Coordinates: {chart.latitude:.4f}°, {chart.longitude:.4f}°")
        lines.append(f"   House System: {chart.house_system}")
        lines.append(f"   Ephemeris: {chart.ephemeris_engine}")
        if chart.chart_sect:
            lines.append(f"   Chart Sect: {chart.chart_sect.title()}")
        
        lines.append(f"\n🔮 Core Identity:")
        sun = chart.planets.get(Planet.SUN)
        moon = chart.planets.get(Planet.MOON)
        lines.append(f"   Sun in {sun.sign.name} {sun.sign.symbol} (Your core self)")
        lines.append(f"   Moon in {moon.sign.name} {moon.sign.symbol} (Your emotions)")
        lines.append(f"   Rising in {chart.ascendant_sign.name} {chart.ascendant_sign.symbol} (How others see you)")
        
        lines.append(f"\n🌟 Planetary Positions:")
        for planet, position in chart.planets.items():
            lines.append(f"   {str(position)}")

        if chart.points:
            lines.append(f"\n✨ Special Points:")
            for point in chart.points.values():
                lines.append(f"   {str(point)}")
        
        lines.append(f"\n🏠 House System:")
        lines.append(f"   Ascendant (1st House): {chart.ascendant_sign.name} {chart.ascendant_degree:.1f}°")
        lines.append(f"   Midheaven (10th House): {chart.midheaven_sign.name} {chart.midheaven_degree:.1f}°")
        if chart.houses:
            lines.append("   House Cusps:")
            for house in range(1, 13):
                cusp = chart.houses.get(house)
                if cusp is None:
                    continue
                cusp_sign, cusp_deg = self.degree_to_sign(cusp)
                lines.append(f"     House {house}: {cusp_sign.name} {cusp_deg:.1f}°")
        
        lines.append(f"\n🔗 Major Aspects ({len(chart.aspects)} total):")
        for aspect in chart.aspects[:10]:  # Show top 10
            lines.append(f"   {str(aspect)}")
        
        lines.append(f"\n📊 Chart Characteristics:")
        lines.append(f"   Chart Ruler: {chart.chart_ruler.symbol} {chart.chart_ruler.name}")
        lines.append(f"   Dominant Element: {chart.dominant_element}")
        lines.append(f"   Dominant Modality: {chart.dominant_modality}")
        if chart.lunar_phase:
            phase_angle = chart.lunar_phase_angle if chart.lunar_phase_angle is not None else 0.0
            lines.append(f"   Lunar Phase: {chart.lunar_phase} ({phase_angle:.1f}°)")
        if chart.element_counts:
            lines.append(f"   Element Balance: {chart.element_counts}")
        if chart.modality_counts:
            lines.append(f"   Modality Balance: {chart.modality_counts}")
        if chart.aspect_summary:
            lines.append(f"   Aspect Summary: {chart.aspect_summary}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)

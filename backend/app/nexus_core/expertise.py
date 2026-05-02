"""
Comprehensive Astrology Expertise Module
Deep knowledge base for astrology reasoning, Q&A, and interpretations
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

# ==================== ZODIAC SIGNS ====================

@dataclass
class ZodiacSign:
    """Complete zodiac sign information"""
    name: str
    symbol: str
    element: str  # Fire, Earth, Air, Water
    modality: str  # Cardinal, Fixed, Mutable
    ruling_planet: str
    exaltation: str  # Exalted planet
    detriment: str  # Planet in detriment
    fall: str  # Planet in fall
    dates: Tuple[str, str]  # Start-end dates
    keywords: List[str]
    strengths: List[str]
    challenges: List[str]
    compatible_signs: List[str]
    opposite_sign: str
    tarot_major_arcana: str


ZODIAC_SIGNS = {
    'Aries': ZodiacSign(
        name='Aries',
        symbol='♈',
        element='Fire',
        modality='Cardinal',
        ruling_planet='Mars',
        exaltation='Sun',
        detriment='Venus',
        fall='Saturn',
        dates=('March 21', 'April 19'),
        keywords=['Courage', 'Initiative', 'Passion', 'Impulsiveness', 'Leadership'],
        strengths=['Bold', 'Confident', 'Energetic', 'Pioneers', 'Direct'],
        challenges=['Impulsive', 'Aggressive', 'Self-centered', 'Impatient', 'Reckless'],
        compatible_signs=['Leo', 'Sagittarius', 'Gemini', 'Aquarius'],
        opposite_sign='Libra',
        tarot_major_arcana='The Emperor'
    ),
    'Taurus': ZodiacSign(
        name='Taurus',
        symbol='♉',
        element='Earth',
        modality='Fixed',
        ruling_planet='Venus',
        exaltation='Moon',
        detriment='Mars',
        fall='Mercury',
        dates=('April 20', 'May 20'),
        keywords=['Stability', 'Sensuality', 'Loyalty', 'Stubbornness', 'Material'],
        strengths=['Reliable', 'Patient', 'Practical', 'Artistic', 'Loyal'],
        challenges=['Stubborn', 'Possessive', 'Rigid', 'Lazy', 'Jealous'],
        compatible_signs=['Virgo', 'Capricorn', 'Cancer', 'Pisces'],
        opposite_sign='Scorpio',
        tarot_major_arcana='The Hierophant'
    ),
    'Gemini': ZodiacSign(
        name='Gemini',
        symbol='♊',
        element='Air',
        modality='Mutable',
        ruling_planet='Mercury',
        exaltation='Mercury',
        detriment='Jupiter',
        fall='Neptune',
        dates=('May 21', 'June 20'),
        keywords=['Communication', 'Curiosity', 'Adaptability', 'Duality', 'Wit'],
        strengths=['Communicative', 'Witty', 'Adaptable', 'Intellectual', 'Social'],
        challenges=['Superficial', 'Nervous', 'Inconsistent', 'Deceptive', 'Scattered'],
        compatible_signs=['Libra', 'Aquarius', 'Aries', 'Leo'],
        opposite_sign='Sagittarius',
        tarot_major_arcana='The Lovers'
    ),
    'Cancer': ZodiacSign(
        name='Cancer',
        symbol='♋',
        element='Water',
        modality='Cardinal',
        ruling_planet='Moon',
        exaltation='Jupiter',
        detriment='Saturn',
        fall='Mars',
        dates=('June 21', 'July 22'),
        keywords=['Emotion', 'Nurture', 'Intuition', 'Moodiness', 'Protection'],
        strengths=['Intuitive', 'Protective', 'Emotional', 'Nurturing', 'Loyal'],
        challenges=['Moody', 'Overly sensitive', 'Clingy', 'Defensive', 'Insecure'],
        compatible_signs=['Scorpio', 'Pisces', 'Taurus', 'Virgo'],
        opposite_sign='Capricorn',
        tarot_major_arcana='The Chariot'
    ),
    'Leo': ZodiacSign(
        name='Leo',
        symbol='♌',
        element='Fire',
        modality='Fixed',
        ruling_planet='Sun',
        exaltation='Neptune',
        detriment='Mercury',
        fall='Saturn',
        dates=('July 23', 'August 22'),
        keywords=['Pride', 'Creativity', 'Drama', 'Generosity', 'Royal'],
        strengths=['Creative', 'Generous', 'Warm', 'Confident', 'Charismatic'],
        challenges=['Prideful', 'Arrogant', 'Self-centered', 'Stubborn', 'Boastful'],
        compatible_signs=['Aries', 'Sagittarius', 'Gemini', 'Libra'],
        opposite_sign='Aquarius',
        tarot_major_arcana='Strength'
    ),
    'Virgo': ZodiacSign(
        name='Virgo',
        symbol='♍',
        element='Earth',
        modality='Mutable',
        ruling_planet='Mercury',
        exaltation='Mercury',
        detriment='Jupiter',
        fall='Venus',
        dates=('August 23', 'September 22'),
        keywords=['Analysis', 'Perfectionism', 'Service', 'Practicality', 'Health'],
        strengths=['Practical', 'Analytical', 'Detail-oriented', 'Helpful', 'Honest'],
        challenges=['Critical', 'Perfectionist', 'Anxious', 'Judgmental', 'Fussy'],
        compatible_signs=['Taurus', 'Capricorn', 'Cancer', 'Scorpio'],
        opposite_sign='Pisces',
        tarot_major_arcana='The Hermit'
    ),
    'Libra': ZodiacSign(
        name='Libra',
        symbol='♎',
        element='Air',
        modality='Cardinal',
        ruling_planet='Venus',
        exaltation='Saturn',
        detriment='Mars',
        fall='Sun',
        dates=('September 23', 'October 22'),
        keywords=['Balance', 'Harmony', 'Justice', 'Indecision', 'Aesthetics'],
        strengths=['Diplomatic', 'Fair', 'Artistic', 'Social', 'Thoughtful'],
        challenges=['Indecisive', 'Passive', 'People-pleaser', 'Superficial', 'Vain'],
        compatible_signs=['Gemini', 'Aquarius', 'Leo', 'Sagittarius'],
        opposite_sign='Aries',
        tarot_major_arcana='Justice'
    ),
    'Scorpio': ZodiacSign(
        name='Scorpio',
        symbol='♏',
        element='Water',
        modality='Fixed',
        ruling_planet='Pluto',
        exaltation='Uranus',
        detriment='Venus',
        fall='Moon',
        dates=('October 23', 'November 21'),
        keywords=['Intensity', 'Mystery', 'Power', 'Secrecy', 'Transformation'],
        strengths=['Passionate', 'Determined', 'Perceptive', 'Magnetic', 'Loyal'],
        challenges=['Secretive', 'Jealous', 'Vengeful', 'Obsessive', 'Controlling'],
        compatible_signs=['Cancer', 'Pisces', 'Taurus', 'Capricorn'],
        opposite_sign='Taurus',
        tarot_major_arcana='Death'
    ),
    'Sagittarius': ZodiacSign(
        name='Sagittarius',
        symbol='♐',
        element='Fire',
        modality='Mutable',
        ruling_planet='Jupiter',
        exaltation='Sun',
        detriment='Mercury',
        fall='Venus',
        dates=('November 22', 'December 21'),
        keywords=['Adventure', 'Optimism', 'Philosophy', 'Recklessness', 'Expansion'],
        strengths=['Optimistic', 'Adventurous', 'Philosophical', 'Honest', 'Generous'],
        challenges=['Reckless', 'Over-optimistic', 'Tactless', 'Irresponsible', 'Impatient'],
        compatible_signs=['Aries', 'Leo', 'Libra', 'Aquarius'],
        opposite_sign='Gemini',
        tarot_major_arcana='The Hermit'
    ),
    'Capricorn': ZodiacSign(
        name='Capricorn',
        symbol='♑',
        element='Earth',
        modality='Cardinal',
        ruling_planet='Saturn',
        exaltation='Mars',
        detriment='Moon',
        fall='Jupiter',
        dates=('December 22', 'January 19'),
        keywords=['Ambition', 'Discipline', 'Authority', 'Restriction', 'Structure'],
        strengths=['Ambitious', 'Disciplined', 'Responsible', 'Practical', 'Self-controlled'],
        challenges=['Pessimistic', 'Cold', 'Rigid', 'Unforgiving', 'Overly cautious'],
        compatible_signs=['Taurus', 'Virgo', 'Cancer', 'Scorpio'],
        opposite_sign='Cancer',
        tarot_major_arcana='The Goat'
    ),
    'Aquarius': ZodiacSign(
        name='Aquarius',
        symbol='♒',
        element='Air',
        modality='Fixed',
        ruling_planet='Uranus',
        exaltation='Mercury',
        detriment='Sun',
        fall='Neptune',
        dates=('January 20', 'February 18'),
        keywords=['Innovation', 'Individuality', 'Rebellion', 'Detachment', 'Idealism'],
        strengths=['Innovative', 'Humanitarian', 'Intellectual', 'Unique', 'Progressive'],
        challenges=['Detached', 'Aloof', 'Unpredictable', 'Stubborn', 'Unemotional'],
        compatible_signs=['Gemini', 'Libra', 'Aries', 'Sagittarius'],
        opposite_sign='Leo',
        tarot_major_arcana='The Star'
    ),
    'Pisces': ZodiacSign(
        name='Pisces',
        symbol='♓',
        element='Water',
        modality='Mutable',
        ruling_planet='Neptune',
        exaltation='Venus',
        detriment='Mercury',
        fall='Mercury',
        dates=('February 19', 'March 20'),
        keywords=['Intuition', 'Dreaminess', 'Compassion', 'Escapism', 'Spirituality'],
        strengths=['Compassionate', 'Artistic', 'Intuitive', 'Wise', 'Gentle'],
        challenges=['Overly trusting', 'Escapist', 'Overly emotional', 'Confused', 'Fearful'],
        compatible_signs=['Cancer', 'Scorpio', 'Taurus', 'Virgo'],
        opposite_sign='Virgo',
        tarot_major_arcana='The Moon'
    ),
}

# ==================== PLANETS ====================

@dataclass
class Planet:
    """Complete planet information"""
    name: str
    symbol: str
    represents: str
    ruling_sign: str
    exalted_in: str
    detriment_in: str
    fall_in: str
    keywords: List[str]
    light_side: List[str]
    shadow_side: List[str]
    orbital_period: str
    retrograde_significance: str


PLANETS = {
    'Sun': Planet(
        name='Sun',
        symbol='☉',
        represents='Core identity, life purpose, vitality',
        ruling_sign='Leo',
        exalted_in='Aries',
        detriment_in='Libra',
        fall_in='Libra',
        keywords=['Identity', 'Will', 'Ego', 'Vitality', 'Purpose'],
        light_side=['Creative', 'Confident', 'Vital', 'Generous', 'Radiant'],
        shadow_side=['Egocentric', 'Arrogant', 'Domineering', 'Stubborn', 'Vain'],
        orbital_period='1 year',
        retrograde_significance='Sun does not retrograde'
    ),
    'Moon': Planet(
        name='Moon',
        symbol='☽',
        represents='Emotions, instincts, subconscious',
        ruling_sign='Cancer',
        exalted_in='Taurus',
        detriment_in='Capricorn',
        fall_in='Scorpio',
        keywords=['Emotions', 'Instinct', 'Home', 'Mother', 'Nurture'],
        light_side=['Nurturing', 'Intuitive', 'Emotional', 'Protective', 'Supportive'],
        shadow_side=['Moody', 'Clingy', 'Overly sensitive', 'Defensive', 'Manipulative'],
        orbital_period='27.3 days',
        retrograde_significance='Moon does not retrograde'
    ),
    'Mercury': Planet(
        name='Mercury',
        symbol='☿',
        represents='Communication, intellect, learning',
        ruling_sign='Gemini, Virgo',
        exalted_in='Virgo',
        detriment_in='Sagittarius, Pisces',
        fall_in='Pisces',
        keywords=['Communication', 'Mind', 'Learning', 'Travel', 'Commerce'],
        light_side=['Communicative', 'Intelligent', 'Witty', 'Curious', 'Adaptable'],
        shadow_side=['Deceptive', 'Gossipy', 'Scattered', 'Nervous', 'Superficial'],
        orbital_period='88 days',
        retrograde_significance='Retrograde: Miscommunication, technology issues, travel delays'
    ),
    'Venus': Planet(
        name='Venus',
        symbol='♀',
        represents='Love, values, aesthetics, money',
        ruling_sign='Taurus, Libra',
        exalted_in='Pisces',
        detriment_in='Aries, Scorpio',
        fall_in='Virgo',
        keywords=['Love', 'Beauty', 'Value', 'Desire', 'Pleasure'],
        light_side=['Loving', 'Artistic', 'Charming', 'Diplomatic', 'Harmonious'],
        shadow_side=['Vain', 'Materialistic', 'Superficial', 'Indulgent', 'Possessive'],
        orbital_period='225 days',
        retrograde_significance='Retrograde: Relationship review, financial reassessment, values clarification'
    ),
    'Mars': Planet(
        name='Mars',
        symbol='♂',
        represents='Action, desire, courage, aggression',
        ruling_sign='Aries, Scorpio',
        exalted_in='Capricorn',
        detriment_in='Libra, Taurus',
        fall_in='Cancer',
        keywords=['Action', 'Desire', 'Energy', 'Passion', 'War'],
        light_side=['Courageous', 'Passionate', 'Energetic', 'Direct', 'Motivated'],
        shadow_side=['Aggressive', 'Impulsive', 'Violent', 'Reckless', 'Inflammatory'],
        orbital_period='687 days',
        retrograde_significance='Retrograde: Low energy, reassess goals, internalize anger'
    ),
    'Jupiter': Planet(
        name='Jupiter',
        symbol='♃',
        represents='Expansion, luck, philosophy, abundance',
        ruling_sign='Sagittarius, Pisces',
        exalted_in='Cancer',
        detriment_in='Gemini, Virgo',
        fall_in='Capricorn',
        keywords=['Expansion', 'Luck', 'Wisdom', 'Growth', 'Optimism'],
        light_side=['Optimistic', 'Generous', 'Wise', 'Lucky', 'Adventurous'],
        shadow_side=['Over-indulgent', 'Arrogant', 'Reckless', 'Scattered', 'Excessive'],
        orbital_period='12 years',
        retrograde_significance='Retrograde: Inner growth, philosophical questioning, delayed expansion'
    ),
    'Saturn': Planet(
        name='Saturn',
        symbol='♄',
        represents='Limitations, discipline, responsibility, time',
        ruling_sign='Capricorn, Aquarius',
        exalted_in='Libra',
        detriment_in='Cancer, Leo',
        fall_in='Aries',
        keywords=['Limitation', 'Discipline', 'Time', 'Responsibility', 'Maturity'],
        light_side=['Disciplined', 'Responsible', 'Practical', 'Wise', 'Cautious'],
        shadow_side=['Pessimistic', 'Restrictive', 'Cold', 'Fearful', 'Controlling'],
        orbital_period='29 years',
        retrograde_significance='Retrograde: Internal restructuring, clearing old patterns, facing fears'
    ),
    'Uranus': Planet(
        name='Uranus',
        symbol='♅',
        represents='Revolution, innovation, awakening, chaos',
        ruling_sign='Aquarius',
        exalted_in='Scorpio',
        detriment_in='Leo',
        fall_in='None',
        keywords=['Innovation', 'Revolution', 'Awakening', 'Rebellion', 'Freedom'],
        light_side=['Innovative', 'Progressive', 'Awakened', 'Unique', 'Liberated'],
        shadow_side=['Rebellious', 'Chaotic', 'Unpredictable', 'Disruptive', 'Cold'],
        orbital_period='84 years',
        retrograde_significance='Retrograde: Internal revolution, breakthrough insights, unconventional breakthroughs'
    ),
    'Neptune': Planet(
        name='Neptune',
        symbol='♆',
        represents='Dreams, illusion, spirituality, compassion',
        ruling_sign='Pisces',
        exalted_in='Leo',
        detriment_in='Virgo',
        fall_in='Virgo',
        keywords=['Dreams', 'Illusion', 'Spirituality', 'Compassion', 'Transcendence'],
        light_side=['Spiritual', 'Compassionate', 'Artistic', 'Intuitive', 'Transcendent'],
        shadow_side=['Delusional', 'Escapist', 'Confused', 'Addicted', 'Victim-oriented'],
        orbital_period='165 years',
        retrograde_significance='Retrograde: Spiritual awakening, illusion dissolves, inner clarity'
    ),
    'Pluto': Planet(
        name='Pluto',
        symbol='♇',
        represents='Transformation, power, death/rebirth, hidden forces',
        ruling_sign='Scorpio',
        exalted_in='Aries',
        detriment_in='Libra',
        fall_in='Taurus',
        keywords=['Transformation', 'Power', 'Death/Rebirth', 'Secrets', 'Intensity'],
        light_side=['Transformative', 'Empowered', 'Reborn', 'Intense', 'Investigative'],
        shadow_side=['Obsessive', 'Controlling', 'Destructive', 'Secretive', 'Vengeful'],
        orbital_period='248 years',
        retrograde_significance='Retrograde: Internal power struggles, psychological insights, transformation'
    ),
}

# ==================== ASTROLOGICAL ASPECTS ====================

@dataclass
class AspectInterpretation:
    """Aspect meanings and interpretations"""
    name: str
    angle: int
    orb: int
    nature: str  # Harmonious, Challenging, Neutral
    themes: List[str]
    keywords: List[str]
    explanation: str


ASPECTS = {
    'Conjunction': AspectInterpretation(
        name='Conjunction (0°)',
        angle=0,
        orb=10,
        nature='Neutral/Amplifying',
        themes=['Unity', 'Combined Power', 'Merger', 'Focus'],
        keywords=['Blending', 'Intensification', 'New Beginning', 'Unified Energy'],
        explanation='The two planets blend their energies completely. They work as one unit, creating intense focus. Can be positive or challenging depending on planets involved.'
    ),
    'Sextile': AspectInterpretation(
        name='Sextile (60°)',
        angle=60,
        orb=6,
        nature='Harmonious',
        themes=['Opportunity', 'Support', 'Ease', 'Natural Flow'],
        keywords=['Talent', 'Grace', 'Opportunity', 'Cooperation'],
        explanation='Two planets work well together, supporting each other effortlessly. Creates opportunities and natural talents. Generally positive, though subtle.'
    ),
    'Square': AspectInterpretation(
        name='Square (90°)',
        angle=90,
        orb=8,
        nature='Challenging',
        themes=['Tension', 'Growth', 'Conflict', 'Action'],
        keywords=['Friction', 'Challenge', 'Motivation', 'Dynamic'],
        explanation='Two planets create friction and tension. Squares push for growth and action. Challenging but productive - they get things done through conflict and resolution.'
    ),
    'Trine': AspectInterpretation(
        name='Trine (120°)',
        angle=120,
        orb=8,
        nature='Harmonious',
        themes=['Flow', 'Talent', 'Harmony', 'Natural Ability'],
        keywords=['Luck', 'Natural Talent', 'Ease', 'Gifted'],
        explanation='Two planets in element harmony. Creates natural talents and easy flow. Very positive but can create complacency - talents come so easily you may not develop them fully.'
    ),
    'Quincunx': AspectInterpretation(
        name='Quincunx (150°)',
        angle=150,
        orb=3,
        nature='Challenging',
        themes=['Adjustment', 'Refinement', 'Growth', 'Integration'],
        keywords=['Adaptation', 'Fine-tuning', 'Learning', 'Slight Tension'],
        explanation='Two planets operate on different wavelengths. Creates a need to constantly adjust and integrate. Subtle tension that requires fine-tuning and adaptability.'
    ),
    'Opposition': AspectInterpretation(
        name='Opposition (180°)',
        angle=180,
        orb=10,
        nature='Challenging',
        themes=['Polarity', 'Balance', 'Awareness', 'Projection'],
        keywords=['Opposite Forces', 'Awareness', 'Projection', 'Partnership'],
        explanation='Two planets pull in opposite directions. Creates strong awareness of both energies. Can be polarizing but also creates balance if integrated. Often shown in relationships.'
    ),
}

# ==================== HOUSES ====================

HOUSE_MEANINGS = {
    1: {
        'name': '1st House',
        'symbol': 'Ascendant',
        'meaning': 'Self, Identity, Appearance, Personality',
        'keywords': ['Self-expression', 'First impressions', 'Personality', 'Physical appearance', 'Initiative'],
        'life_areas': ['How you present yourself', 'Your personality', 'Physical appearance', 'Early life experiences', 'Your approach to life'],
        'questions': ['Who am I?', 'How do others see me?', 'What is my natural personality?']
    },
    2: {
        'name': '2nd House',
        'symbol': '',
        'meaning': 'Finances, Values, Possessions, Self-Worth',
        'keywords': ['Money', 'Values', 'Possessions', 'Self-worth', 'Talents'],
        'life_areas': ['Financial resources', 'Personal possessions', 'Values and priorities', 'Self-worth', 'Earning ability'],
        'questions': ['What do I value?', 'How do I handle money?', 'What is my self-worth?']
    },
    3: {
        'name': '3rd House',
        'symbol': '',
        'meaning': 'Communication, Learning, Siblings, Short Journeys',
        'keywords': ['Communication', 'Learning', 'Siblings', 'Short trips', 'Neighbors', 'Writing'],
        'life_areas': ['Communication style', 'Learning and education', 'Relationships with siblings', 'Short journeys', 'Neighborhood'],
        'questions': ['How do I communicate?', 'What is my learning style?', 'How do I think?']
    },
    4: {
        'name': '4th House',
        'symbol': 'Imum Coeli',
        'meaning': 'Home, Family, Roots, Foundation',
        'keywords': ['Home', 'Family', 'Ancestry', 'Foundation', 'Private life', 'Parent'],
        'life_areas': ['Home environment', 'Family relationships', 'Roots and heritage', 'Private life', 'Foundation of life'],
        'questions': ['What is home for me?', 'How is my family?', 'What are my roots?']
    },
    5: {
        'name': '5th House',
        'symbol': '',
        'meaning': 'Creativity, Romance, Children, Pleasure',
        'keywords': ['Creativity', 'Romance', 'Children', 'Pleasure', 'Self-expression', 'Play'],
        'life_areas': ['Creative expression', 'Romantic relationships', 'Children', 'Pleasure and hobbies', 'Entertainment'],
        'questions': ['How do I express creativity?', 'What brings me joy?', 'How do I love?']
    },
    6: {
        'name': '6th House',
        'symbol': '',
        'meaning': 'Health, Work, Service, Daily Routine',
        'keywords': ['Health', 'Work', 'Service', 'Routine', 'Pets', 'Habits'],
        'life_areas': ['Health and wellness', 'Work environment', 'Service to others', 'Daily routines', 'Pets and animals'],
        'questions': ['How is my health?', 'What is my work style?', 'What are my habits?']
    },
    7: {
        'name': '7th House',
        'symbol': 'Descendant',
        'meaning': 'Partnerships, Marriage, Relationships, Others',
        'keywords': ['Marriage', 'Partnerships', 'Relationships', 'Others', 'Public', 'Open enemies'],
        'life_areas': ['Marriage and partnerships', 'Close relationships', 'How we relate to others', 'Business partnerships', 'Public image'],
        'questions': ['What am I looking for in relationships?', 'How do I partner?', 'What attracts me?']
    },
    8: {
        'name': '8th House',
        'symbol': '',
        'meaning': 'Transformation, Sexuality, Shared Resources, Death/Rebirth',
        'keywords': ['Transformation', 'Sexuality', 'Shared resources', 'Death', 'Inheritance', 'Intimacy'],
        'life_areas': ['Transformation and change', 'Sexuality and intimacy', 'Shared finances', 'Inheritance', 'Psychology'],
        'questions': ['How do I transform?', 'What am I afraid of?', 'What is my sexuality?']
    },
    9: {
        'name': '9th House',
        'symbol': '',
        'meaning': 'Philosophy, Higher Learning, Travel, Spirituality',
        'keywords': ['Philosophy', 'Higher learning', 'Travel', 'Spirituality', 'Religion', 'Foreign'],
        'life_areas': ['Higher learning and education', 'Philosophy and beliefs', 'Long-distance travel', 'Spirituality', 'Wisdom'],
        'questions': ['What do I believe?', 'What is my purpose?', 'What draws me to expand?']
    },
    10: {
        'name': '10th House',
        'symbol': 'Midheaven',
        'meaning': 'Career, Public Image, Authority, Achievement',
        'keywords': ['Career', 'Public image', 'Authority', 'Achievement', 'Father', 'Reputation'],
        'life_areas': ['Career and vocation', 'Public reputation', 'Achievement and status', 'Authority figures', 'Legacy'],
        'questions': ['What is my career path?', 'How do I want to be known?', 'What will I achieve?']
    },
    11: {
        'name': '11th House',
        'symbol': '',
        'meaning': 'Friendship, Groups, Hopes, Ideals',
        'keywords': ['Friendship', 'Groups', 'Hopes', 'Ideals', 'Technology', 'Community'],
        'life_areas': ['Friendships', 'Group activities', 'Hopes and wishes', 'Technology and innovation', 'Community involvement'],
        'questions': ['Who are my people?', 'What are my dreams?', 'How do I contribute to society?']
    },
    12: {
        'name': '12th House',
        'symbol': '',
        'meaning': 'Spirituality, Subconscious, Hidden, Transcendence',
        'keywords': ['Spirituality', 'Subconscious', 'Hidden', 'Endings', 'Prisons', 'Transcendence'],
        'life_areas': ['Spirituality and meditation', 'Subconscious mind', 'Hidden talents', 'Institutions', 'Karma and past life'],
        'questions': ['What is my spiritual path?', 'What am I not seeing?', 'What am I working on internally?']
    },
}

# ==================== ASTROLOGY EXPERTISE SYSTEM ====================

class AstrologyExpertise:
    """Expert astrology knowledge system"""
    
    def __init__(self):
        self.zodiac_signs = ZODIAC_SIGNS
        self.planets = PLANETS
        self.aspects = ASPECTS
        self.houses = HOUSE_MEANINGS
    
    def get_sign_profile(self, sign_name: str) -> str:
        """Get comprehensive profile of a zodiac sign"""
        sign = self.zodiac_signs.get(sign_name)
        if not sign:
            return f"Sign '{sign_name}' not found"
        
        profile = f"""
🌟 **{sign.name.upper()} PROFILE**

Symbol: {sign.symbol} | Element: {sign.element} | Modality: {sign.modality}
Ruling Planet: {sign.ruling_planet}
Dates: {sign.dates[0]} - {sign.dates[1]}

**Core Keywords:**
{', '.join(sign.keywords)}

**Strengths:**
{', '.join(sign.strengths)}

**Challenges:**
{', '.join(sign.challenges)}

**Compatible Signs:**
{', '.join(sign.compatible_signs)}

**Opposite Sign:** {sign.opposite_sign}
(Complementary lessons and balance)

**Astrological Rulers:**
• Exalted Planet: {sign.exaltation}
• Detriment: {sign.detriment}
• Fall: {sign.fall}

**Tarot Association:** {sign.tarot_major_arcana}

**Life Lesson:**
The {sign.name} learns about {sign.keywords[0].lower()} and {sign.keywords[1].lower()}.
"""
        return profile
    
    def get_planet_profile(self, planet_name: str) -> str:
        """Get comprehensive profile of a planet"""
        planet = self.planets.get(planet_name)
        if not planet:
            return f"Planet '{planet_name}' not found"
        
        profile = f"""
🪐 **{planet.name.upper()} PROFILE**

Symbol: {planet.symbol}
Represents: {planet.represents}

**Ruling Sign(s):** {planet.ruling_sign}
**Exalted In:** {planet.exalted_in}
**Detriment In:** {planet.detriment_in}
**Fall In:** {planet.fall_in}

**Keywords:**
{', '.join(planet.keywords)}

**Light Side (Positive Expression):**
{', '.join(planet.light_side)}

**Shadow Side (Negative Expression):**
{', '.join(planet.shadow_side)}

**Orbital Period:** {planet.orbital_period}

**Retrograde Significance:**
{planet.retrograde_significance}

**Life Principle:**
{planet.name} governs {planet.represents.lower()}. 
When well-aspected, it manifests as {', '.join(planet.light_side).lower()}.
When challenged, it can manifest as {', '.join(planet.shadow_side).lower()}.
"""
        return profile
    
    def get_aspect_meaning(self, aspect_name: str) -> str:
        """Get interpretation of an astrological aspect"""
        aspect = self.aspects.get(aspect_name)
        if not aspect:
            return f"Aspect '{aspect_name}' not found"
        
        interpretation = f"""
⚡ **{aspect.name.upper()}**

Angle: {aspect.angle}°
Orb: ±{aspect.orb}°
Nature: {aspect.nature}

**Keywords:**
{', '.join(aspect.keywords)}

**Themes:**
{', '.join(aspect.themes)}

**Meaning:**
{aspect.explanation}

**Life Manifestation:**
When two planets form a {aspect.name.lower()}, they create energies of {', '.join(aspect.keywords).lower()}.
"""
        return interpretation
    
    def get_house_meaning(self, house_number: int) -> str:
        """Get interpretation of a house"""
        house = self.houses.get(house_number)
        if not house:
            return f"House {house_number} not found"
        
        meaning = f"""
🏘️ **{house['name'].upper()}** {house['symbol']}

**Meaning:** {house['meaning']}

**Keywords:**
{', '.join(house['keywords'])}

**Life Areas:**
"""
        for area in house['life_areas']:
            meaning += f"\n• {area}"
        
        meaning += "\n\n**Key Questions:**\n"
        for q in house['questions']:
            meaning += f"\n• {q}"
        
        return meaning
    
    def get_compatibility_score(self, sign1: str, sign2: str) -> Tuple[int, str]:
        """Calculate compatibility between two signs"""
        s1 = self.zodiac_signs.get(sign1)
        s2 = self.zodiac_signs.get(sign2)
        
        if not s1 or not s2:
            return 0, "Sign not found"
        
        # Compatibility logic
        score = 50  # Base score
        
        # Same element = 20 points
        if s1.element == s2.element:
            score += 20
        
        # Compatible signs = 15 points
        if s2.name in s1.compatible_signs:
            score += 15
        
        # Trine (120°) elements = 15 points
        trine_elements = {
            'Fire': ['Fire', 'Air'],
            'Water': ['Water', 'Earth'],
            'Air': ['Air', 'Fire'],
            'Earth': ['Earth', 'Water']
        }
        if s2.element in trine_elements.get(s1.element, []):
            score += 10
        
        # Opposite signs = relationship dynamic
        if s2.name == s1.opposite_sign:
            score = 65  # Opposites attract
        
        description = self._get_compatibility_description(score, s1.name, s2.name)
        return min(100, score), description
    
    def _get_compatibility_description(self, score: int, sign1: str, sign2: str) -> str:
        """Generate compatibility description based on score"""
        if score >= 90:
            return f"🔥 Excellent compatibility! {sign1} and {sign2} are highly compatible soulmates."
        elif score >= 75:
            return f"💚 Strong compatibility. {sign1} and {sign2} work well together with understanding."
        elif score >= 60:
            return f"💛 Good compatibility. {sign1} and {sign2} have potential with effort."
        elif score >= 50:
            return f"🤝 Moderate compatibility. {sign1} and {sign2} require patience and compromise."
        elif score >= 40:
            return f"⚠️ Challenge ahead. {sign1} and {sign2} need to work on differences."
        else:
            return f"❌ Difficult compatibility. {sign1} and {sign2} have fundamentally different approaches."
    
    def answer_astrology_question(self, question: str) -> str:
        """Answer general astrology questions"""
        q_lower = question.lower()
        
        # Element questions
        if 'element' in q_lower or 'elements' in q_lower:
            return """
🔥 **THE FOUR ELEMENTS**

**FIRE (Action, Passion, Inspiration)**
Signs: Aries, Leo, Sagittarius
Keywords: Courage, Energy, Enthusiasm, Creativity
Strength: Bold, confident, inspiring
Challenge: Impatient, reckless, scattered

**EARTH (Stability, Practicality, Material)**
Signs: Taurus, Virgo, Capricorn
Keywords: Grounded, Practical, Reliable, Sensible
Strength: Stable, dependable, productive
Challenge: Rigid, overly cautious, materialistic

**AIR (Communication, Intellect, Ideas)**
Signs: Gemini, Libra, Aquarius
Keywords: Curious, Social, Intellectual, Communicative
Strength: Smart, flexible, social
Challenge: Scattered, detached, superficial

**WATER (Emotion, Intuition, Feeling)**
Signs: Cancer, Scorpio, Pisces
Keywords: Emotional, Intuitive, Sensitive, Deep
Strength: Empathetic, intuitive, compassionate
Challenge: Moody, overly emotional, clingy

**Element Compatibility:**
• Fire + Air = Excellent (action + ideas)
• Fire + Water = Challenging (conflict)
• Earth + Water = Excellent (grounded + intuitive)
• Earth + Air = Challenging (practical vs. abstract)
"""
        
        elif 'modality' in q_lower:
            return """
**THE THREE MODALITIES**

**CARDINAL (Initiators, Leaders)**
Signs: Aries, Cancer, Libra, Capricorn
Characteristics: Start projects, lead, take initiative
Strength: Pioneering, ambitious, action-oriented
Challenge: May not finish, need to delegate

**FIXED (Stabilizers, Consolidators)**
Signs: Taurus, Leo, Scorpio, Aquarius
Characteristics: Stick with things, build foundations, persistent
Strength: Reliable, dedicated, thorough
Challenge: Stubborn, resistant to change, inflexible

**MUTABLE (Adapters, Communicators)**
Signs: Gemini, Virgo, Sagittarius, Pisces
Characteristics: Adaptable, flexible, communicative
Strength: Versatile, curious, quick to learn
Challenge: Scattered, inconsistent, indecisive
"""
        
        elif 'retrograde' in q_lower:
            return """
♻️ **RETROGRADE PERIODS - WHAT THEY MEAN**

**What is Retrograde?**
When a planet appears to move backward in the sky from our perspective on Earth.
It's an optical illusion, but has real astrological significance.

**Mercury Retrograde (3-4x per year, ~3 weeks each)**
Effects: Communication mishaps, technology glitches, travel delays
What to avoid: Signing contracts, major purchases, starting new projects
What to do: Review, revise, redo, revisit

**Venus Retrograde (rare, ~6 weeks every 18-19 months)**
Effects: Relationship review, financial reassessment, values questioning
What to avoid: New romantic relationships, major purchases
What to do: Heal relationships, clarify values, release unhealthy patterns

**Mars Retrograde (~2 years, ~10 weeks)**
Effects: Low energy, need to process anger, reassess goals
What to avoid: Aggressive confrontation, new projects requiring energy
What to do: Develop strategy, work internally, reflect

**Jupiter Retrograde (~4 months annually)**
Effects: Internal growth, philosophical questioning, delayed expansion
What to avoid: Overcommitting to expansion
What to do: Inner development, spiritual work

**Saturn Retrograde (~4-5 months annually)**
Effects: Clearing karma, facing fears, restructuring life
What to avoid: Major commitments
What to do: Face challenges, reform structures, process responsibility

**The Silver Lining:**
Retrogrades offer opportunities to fix past mistakes and make corrections.
They're not evil - they're course-correction periods.
"""
        
        else:
            return "I can answer questions about zodiac signs, planets, aspects, houses, elements, modalities, retrograde, and compatibility. What would you like to know?"

    def answer_question(self, question: str) -> str:
        """Compatibility alias used by advanced routing layers."""
        return self.answer_astrology_question(question)

# ==================== SINGLETON INSTANCE ====================

astrology_expertise = AstrologyExpertise()

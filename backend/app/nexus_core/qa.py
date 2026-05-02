"""
Astrology Question Answering System
Expert responses to astrological queries
"""

import re
from typing import Optional, Dict, List
from .expertise import astrology_expertise


class AstrologyQA:
    """Comprehensive astrology Q&A system for expert-level answers"""
    
    def __init__(self):
        self.expertise = astrology_expertise
        self.knowledge_cache = {}
    
    def answer_question(self, question: str) -> str:
        """Answer astrology questions with expert knowledge"""
        q_lower = question.lower()
        signs_in_query = self._extract_signs(q_lower)
        planets_in_query = self._extract_planets(q_lower)
        aspects_in_query = self._extract_aspects(q_lower)
        
        # Check for cached answer
        if q_lower in self.knowledge_cache:
            return self.knowledge_cache[q_lower]

        # ===== COMPATIBILITY / COMPARISON FIRST (before generic sign matching) =====
        if any(word in q_lower for word in ['compatible', 'compatibility', 'match']) and len(signs_in_query) >= 2:
            answer = self._handle_compatibility_question(question)
            self.knowledge_cache[q_lower] = answer
            return answer

        if any(word in q_lower for word in ['compare', 'difference', 'vs', 'versus']) and len(signs_in_query) >= 2:
            answer = self._compare_signs(signs_in_query[0], signs_in_query[1])
            self.knowledge_cache[q_lower] = answer
            return answer

        # ===== SYNTHESIS: PLANET IN SIGN =====
        if planets_in_query and signs_in_query and (' in ' in q_lower or 'means' in q_lower or 'meaning' in q_lower):
            answer = self._explain_planet_in_sign(planets_in_query[0], signs_in_query[0])
            self.knowledge_cache[q_lower] = answer
            return answer
        
        # ===== SIGN QUESTIONS =====
        # "Tell me about [sign]"
        if signs_in_query:
            answer = self.expertise.get_sign_profile(signs_in_query[0])
            self.knowledge_cache[q_lower] = answer
            return answer
        
        # ===== PLANET QUESTIONS =====
        # "What does [planet] mean?"
        if planets_in_query:
            answer = self.expertise.get_planet_profile(planets_in_query[0])
            self.knowledge_cache[q_lower] = answer
            return answer
        
        # ===== ASPECT QUESTIONS =====
        if aspects_in_query:
            answer = self.expertise.get_aspect_meaning(aspects_in_query[0])
            self.knowledge_cache[q_lower] = answer
            return answer
        
        # ===== HOUSE QUESTIONS =====
        if 'house' in q_lower:
            match = re.search(r'\b(1[0-2]|[1-9])(?:st|nd|rd|th)?\s+house\b', q_lower)
            if match:
                answer = self.expertise.get_house_meaning(int(match.group(1)))
                self.knowledge_cache[q_lower] = answer
                return answer
            for i in range(1, 13):
                if str(i) in q_lower or self._get_house_ordinal(i).lower() in q_lower:
                    answer = self.expertise.get_house_meaning(i)
                    self.knowledge_cache[q_lower] = answer
                    return answer
        
        # ===== GENERAL ASTROLOGY QUESTIONS =====
        if any(word in q_lower for word in ['element', 'modality', 'retrograde', 'house']):
            answer = self.expertise.answer_astrology_question(question)
            self.knowledge_cache[q_lower] = answer
            return answer
        
        # ===== SUN/MOON/RISING QUESTIONS =====
        if 'sun sign' in q_lower or 'solar' in q_lower:
            return self._explain_sun_sign()
        if 'moon sign' in q_lower or 'lunar' in q_lower:
            return self._explain_moon_sign()
        if 'rising' in q_lower or 'ascendant' in q_lower:
            return self._explain_rising_sign()
        
        # ===== ASPECTS OF ASTROLOGY =====
        if 'big three' in q_lower or 'big 3' in q_lower:
            return self._explain_big_three()
        if 'north node' in q_lower or 'south node' in q_lower:
            return self._explain_nodes()
        if 'chiron' in q_lower or 'wounded healer' in q_lower:
            return self._explain_chiron()
        if 'lunar node' in q_lower or 'nodes' in q_lower:
            return self._explain_lunar_nodes()
        if 'vertex' in q_lower or 'fate' in q_lower:
            return self._explain_vertex()
        
        # ===== TIMING QUESTIONS =====
        if 'saturn return' in q_lower:
            return self._explain_saturn_return()
        if 'quarter life crisis' in q_lower or 'quarter-life' in q_lower:
            return self._explain_quarter_life()
        if 'eclipse' in q_lower:
            return self._explain_eclipses()
        if 'moon phase' in q_lower or 'lunar phase' in q_lower:
            return self._explain_moon_phases()
        
        # ===== CHART QUESTIONS =====
        if 'chart' in q_lower or 'birth chart' in q_lower or 'natal chart' in q_lower:
            if 'read' in q_lower or 'interpret' in q_lower or 'understand' in q_lower:
                return self._how_to_read_chart()
        
        # ===== ZODIAC QUESTIONS =====
        if 'zodiac' in q_lower:
            return self._explain_zodiac()
        
        # ===== CAREER/MONEY QUESTIONS =====
        if 'career' in q_lower or 'work' in q_lower:
            return self._career_astrology_guide()
        if 'money' in q_lower or 'finance' in q_lower:
            return self._financial_astrology_guide()
        
        # ===== RELATIONSHIP QUESTIONS =====
        if 'love' in q_lower or 'relationship' in q_lower or 'romance' in q_lower:
            if 'venus' in q_lower or 'mars' in q_lower:
                return self._love_compatibility_guide()
        
        # ===== HEALTH QUESTIONS =====
        if 'health' in q_lower or 'wellness' in q_lower:
            return self._health_astrology_guide()
        
        # Default
        return self._general_astrology_guidance()
    
    def _handle_compatibility_question(self, question: str) -> str:
        """Handle compatibility questions"""
        # Try to extract two signs
        signs = self._extract_signs(question.lower())
        
        if len(signs) >= 2:
            score, desc = self.expertise.get_compatibility_score(signs[0], signs[1])
            
            s1 = self.expertise.zodiac_signs[signs[0]]
            s2 = self.expertise.zodiac_signs[signs[1]]
            
            response = f"""
💕 **{signs[0].upper()} + {signs[1].upper()} COMPATIBILITY**

**Score: {score}/100**

{desc}

**Why This Works:**
{signs[0]} is {s1.element} element ({s1.modality} modality)
{signs[1]} is {s2.element} element ({s2.modality} modality)

**Complementary Traits:**
{signs[0]}: {', '.join(s1.strengths[:2])}
{signs[1]}: {', '.join(s2.strengths[:2])}

**Potential Challenges:**
{signs[0]}: {', '.join(s1.challenges[:2])}
{signs[1]}: {', '.join(s2.challenges[:2])}

**Tips for Success:**
• Appreciate your differences
• Play to each other's strengths
• Work through challenges together
• Remember: Individual charts matter more than Sun signs alone!

**Remember:** Sun sign compatibility is just one piece. 
Venus placements (love), Mars placements (passion), and Moon placements (emotions) 
are equally important in romantic compatibility.
"""
            return response
        else:
            return "To check compatibility, please provide two zodiac signs. Example: 'Are Aries and Libra compatible?'"

    def _extract_signs(self, text: str) -> List[str]:
        """Extract unique zodiac signs preserving query order."""
        found = []
        lower = text.lower()
        for sign in self.expertise.zodiac_signs.keys():
            if sign.lower() in lower and sign not in found:
                found.append(sign)
        return found

    def _extract_planets(self, text: str) -> List[str]:
        """Extract unique planets preserving query order."""
        found = []
        lower = text.lower()
        for planet in self.expertise.planets.keys():
            if planet.lower() in lower and planet not in found:
                found.append(planet)
        return found

    def _extract_aspects(self, text: str) -> List[str]:
        """Extract unique aspects preserving query order."""
        found = []
        lower = text.lower()
        for aspect in self.expertise.aspects.keys():
            if aspect.lower() in lower and aspect not in found:
                found.append(aspect)
        return found

    def _compare_signs(self, sign1: str, sign2: str) -> str:
        """Provide concise comparative reasoning between two signs."""
        s1 = self.expertise.zodiac_signs.get(sign1)
        s2 = self.expertise.zodiac_signs.get(sign2)
        if not s1 or not s2:
            return "I couldn't compare those signs."

        score, desc = self.expertise.get_compatibility_score(sign1, sign2)
        return (
            f"⚖️ **{sign1.upper()} vs {sign2.upper()}**\n\n"
            f"{sign1}: {s1.element} / {s1.modality} / ruled by {s1.ruling_planet}\n"
            f"{sign2}: {s2.element} / {s2.modality} / ruled by {s2.ruling_planet}\n\n"
            f"Big strengths:\n"
            f"• {sign1}: {', '.join(s1.strengths[:3])}\n"
            f"• {sign2}: {', '.join(s2.strengths[:3])}\n\n"
            f"Potential friction:\n"
            f"• {sign1}: {', '.join(s1.challenges[:2])}\n"
            f"• {sign2}: {', '.join(s2.challenges[:2])}\n\n"
            f"Compatibility score: {score}/100\n{desc}"
        )

    def _explain_planet_in_sign(self, planet_name: str, sign_name: str) -> str:
        """Synthesize planet function with sign style for better chart logic."""
        planet = self.expertise.planets.get(planet_name)
        sign = self.expertise.zodiac_signs.get(sign_name)
        if not planet or not sign:
            return "I couldn't interpret that placement."

        return (
            f"🔮 **{planet_name} in {sign_name}**\n\n"
            f"{planet_name} governs: {planet.represents}.\n"
            f"{sign_name} expresses energy through {sign.element.lower()} ({sign.modality.lower()}) style.\n\n"
            f"Likely expression:\n"
            f"• Strengths: {', '.join(sign.strengths[:3])} + {', '.join(planet.light_side[:2])}\n"
            f"• Growth edge: {', '.join(sign.challenges[:2])} + {', '.join(planet.shadow_side[:2])}\n\n"
            f"Practical advice:\n"
            f"Channel this placement into intentional actions aligned with {planet.keywords[0].lower()} and {sign.keywords[0].lower()}."
        )
    
    def _explain_sun_sign(self) -> str:
        return """
☀️ **THE SUN SIGN - Your Core Identity**

Your Sun sign is your core identity, ego, and conscious will.
It's what you came here to develop and express.

**What the Sun Sign Represents:**
• Your core identity and essence
• Your conscious self and ego
• Your life purpose and direction
• What energizes you
• Your creative expression

**How to Use It:**
The Sun sign shows your life's main themes and what you're here to master.
All Sun signs want to "shine" - they just do it differently:
• Aries wants to lead
• Taurus wants to build
• Gemini wants to communicate
• Cancer wants to nurture
• Leo wants to create
• And so on...

**Important Note:**
Your Sun sign is just the tip of the iceberg!
Your birth chart also contains 8 other planets + houses.
Sun sign astrology is simplified compared to your full natal chart.
"""
    
    def _explain_moon_sign(self) -> str:
        return """
🌙 **THE MOON SIGN - Your Emotional Nature**

Your Moon sign is your emotional inner world, subconscious needs, and instincts.
It's how you process feelings and what makes you feel secure.

**What the Moon Sign Represents:**
• Your emotional nature and needs
• Your subconscious mind
• How you nurture and are nurtured
• Your instinctive reactions
• Your sense of security

**How to Use It:**
The Moon sign shows your emotional baseline and what you need to feel safe:
• Moon in Aries needs excitement and independence
• Moon in Taurus needs stability and comfort
• Moon in Gemini needs communication and variety
• Moon in Cancer needs emotional connection
• Moon in Leo needs to feel valued
• And so on...

**Important Note:**
Your Moon sign is more "private" - fewer people see it initially.
But it's crucial for understanding your emotional inner life.
In relationships, the Moon is more important than the Sun!
"""
    
    def _explain_rising_sign(self) -> str:
        return """
⬆️ **THE RISING SIGN (ASCENDANT) - Your Mask**

Your Rising sign is how others perceive you at first glance.
It's the "mask" you wear and the first impression you give.

**What the Rising Sign Represents:**
• How others see you initially
• Your appearance and energy
• Your personality presentation
• Your social mask
• Your first impression

**How to Use It:**
The Rising sign is the "packaging" of your personality:
• Aries Rising appears bold and pioneering
• Taurus Rising appears stable and sensual
• Gemini Rising appears curious and communicative
• Cancer Rising appears caring and protective
• Leo Rising appears confident and dramatic
• And so on...

**The Big Three:**
Sun Sign = Who you are
Moon Sign = How you feel
Rising Sign = How others see you

All three together create your personality.
Someone might be a serious Capricorn Sun, but a bubbly Gemini Rising,
so they appear fun initially even though they're internally serious.
"""
    
    def _explain_big_three(self) -> str:
        return """
🌟 **THE BIG THREE - Your Core Personality**

The Big Three are the most important placements in your birth chart:

**1. ☀️ SUN SIGN**
Identity, Purpose, Ego
How you express yourself to the world

**2. 🌙 MOON SIGN**
Emotions, Needs, Instinct
Your inner emotional world

**3. ⬆️ RISING SIGN (ASCENDANT)**
Appearance, First Impression, Mask
How others perceive you

**How They Work Together:**

Someone could be:
Sun in Capricorn (serious, ambitious)
Moon in Pisces (dreamy, sensitive)
Rising in Leo (confident, dramatic)

This person might:
• Internally: Ambitious and driven (Capricorn Sun)
• Emotionally: Sensitive and intuitive (Pisces Moon)
• Externally: Appear confident and charismatic (Leo Rising)

**Reading the Big Three:**
The Big Three work together like:
Sun = Your internal driver
Moon = Your emotional autopilot
Rising = Your external presentation

To understand someone, look at all three!
"""
    
    def _explain_nodes(self) -> str:
        return """
🔄 **LUNAR NODES - Your Soul's Purpose**

The Lunar Nodes show your soul's evolutionary path in this lifetime.

**North Node (Destiny):**
What you're meant to develop and grow toward
Your soul's purpose
The qualities you need to cultivate

**South Node (Past):**
Natural talents and comfort zone
What you already know well
What you might over-rely on

**North Node by Sign:**

North Node in Aries: Learn courage, independence, assertiveness
North Node in Taurus: Learn stability, sensuality, worthiness
North Node in Gemini: Learn communication, curiosity, mental flexibility
North Node in Cancer: Learn emotional connection, vulnerability, nurturing
North Node in Leo: Learn self-expression, creativity, confidence
North Node in Virgo: Learn analysis, service, daily discipline
North Node in Libra: Learn relationships, balance, diplomacy
North Node in Scorpio: Learn depth, transformation, trust
North Node in Sagittarius: Learn expansion, faith, philosophy
North Node in Capricorn: Learn responsibility, structure, authority
North Node in Aquarius: Learn humanity, innovation, detachment
North Node in Pisces: Learn spirituality, compassion, surrender

**Your Soul's Journey:**
The Nodes show the spiritual curriculum you're in this lifetime.
Challenges often arise around your North Node (growth edge).
When you step into your North Node qualities, life flows more easily.
"""
    
    def _explain_chiron(self) -> str:
        return """
🔑 **CHIRON - The Wounded Healer**

Chiron is the "Wounded Healer" asteroid in your chart.
It shows your deepest wound and your gift for healing others with it.

**Chiron's Message:**
Your greatest wound often becomes your greatest strength.
By healing yourself, you develop wisdom to help others.

**Chiron by Sign:**

Chiron in Aries: Wound = Lack of courage → Healing gift = Empowering others
Chiron in Taurus: Wound = Worthiness issues → Healing gift = Teaching value
Chiron in Gemini: Wound = Communication difficulty → Healing gift = Teaching expression
Chiron in Cancer: Wound = Emotional pain → Healing gift = Emotional wisdom
Chiron in Leo: Wound = Self-doubt → Healing gift = Creative confidence
Chiron in Virgo: Wound = Perfectionism → Healing gift = Practical healing
Chiron in Libra: Wound = Relationship pain → Healing gift = Relationship wisdom
Chiron in Scorpio: Wound = Trust issues → Healing gift = Deep transformation
Chiron in Sagittarius: Wound = Loss of faith → Healing gift = Philosophical wisdom
Chiron in Capricorn: Wound = Authority pain → Healing gift = Leadership wisdom
Chiron in Aquarius: Wound = Feeling alien → Healing gift = Community belonging
Chiron in Pisces: Wound = Spiritual confusion → Healing gift = Spiritual guidance

**Working with Chiron:**
Acknowledge your deepest wound
Understand how you've healed
Use your wisdom to help others
Your pain has purpose
"""
    
    def _explain_lunar_nodes(self) -> str:
        return self._explain_nodes()
    
    def _explain_vertex(self) -> str:
        return """
✨ **THE VERTEX - Point of Fate**

The Vertex is your "point of fate" - significant encounters and destined meetings.
It's where you meet important people and experience fated events.

**How to Use It:**
When someone's planet conjuncts your Vertex, there's a fated connection.
The Vertex often marks important relationships and life turning points.

**Vertex by House:**
Vertex in 1st: Fated personal meetings that change your identity
Vertex in 5th: Fated creative or romantic encounters
Vertex in 7th: Fated partnerships and important relationships
Vertex in 9th: Fated meeting with higher wisdom or travel companions
Vertex in 10th: Fated career meetings or authority figures
Vertex in 11th: Fated friendships that shape your future

**Twin Flame Indicator:**
The Vertex is sometimes called the "point of fateful meetings."
If your Vertex aspects someone's inner planets, there's karmic connection.
"""
    
    def _explain_saturn_return(self) -> str:
        return """
⏰ **SATURN RETURN - Life's Major Turning Point**

Saturn Return happens around age 29-30 (approximately every 29.5 years).
It's when Saturn returns to the place it was at your birth.

**What It Means:**
Life evaluation and restructuring period
Review what's working and what isn't
Release what no longer serves you
Build stronger foundations

**The Saturn Return Process:**

Age 29-30 First Saturn Return:
• Reality check on your life
• Question your path, relationships, career
• May experience crisis or major changes
• Usually takes 2-3 years
• Results: Stronger, clearer life foundation

Age 58-60 Second Saturn Return:
• Another major life review
• Reassess your legacy and impact
• Shift toward wisdom and mentoring
• May make major life changes
• Results: Wisdom and deeper purpose

Age 87-90 Third Saturn Return:
• Life review and completion
• Preparation for legacy
• Spiritual maturation

**Common Saturn Return Experiences:**
• Feeling of pressure to "grow up"
• Questioning life direction
• Relationship changes
• Career shifts
• Financial restructuring
• Health wake-up calls

**Silver Lining:**
Saturn Return is uncomfortable but necessary.
You emerge with authentic life aligned with your values.
After Saturn Return, you finally feel like yourself.
"""
    
    def _explain_quarter_life(self) -> str:
        return """
🌓 **QUARTER LIFE CRISIS (Around Age 22-23)**

The Quarter Life Crisis coincides with Uranus forming a square to your natal Uranus.
This is your first major personal crisis and awakening.

**What Happens:**
Sudden need to break free and be authentic
Question everything you've been taught
Feel pulled to discover yourself
Restlessness and rebellion

**Common Experiences:**
• Desire to change major life direction
• Breaking from family expectations
• Career or education changes
• Relationship reassessment
• "Is this really what I want?" questions

**The Bigger Picture:**
This is actually a positive transit!
It's your first major awakening to authenticity.
You're beginning to become yourself.

**Related Transit:**
Uranus Square Uranus (age 21-23)
Neptune Square Neptune (age 42)
Uranus Opposition Uranus (age 41-42)

All of these create major life reviews and shifts.
"""
    
    def _explain_eclipses(self) -> str:
        return """
🌑 **ECLIPSES - Cosmic Turning Points**

Eclipses are powerful markers of change and new beginnings/endings.

**Solar Eclipse (New Moon Eclipse):**
New beginnings, new projects, planting seeds
Energy of initiation
Visibility: Sun is blocked by Moon

**Lunar Eclipse (Full Moon Eclipse):**
Release, completion, culmination
Energy of realization
Visibility: Moon is in Earth's shadow

**Saros Cycles:**
Eclipses happen in series (Saros cycles)
Each series lasts about 1200+ years
Same Saros cycle repeats every 18 years 11 days (Saros cycle)

**Working with Eclipses:**

During Solar Eclipse:
• Set new intentions
• Plant seeds for new projects
• Embrace new beginnings

During Lunar Eclipse:
• Release what's no longer serving
• Culminate projects
• See clarity on situations

**Eclipse Season Effects:**
Usually +/- 2 weeks from eclipse
Life moves faster during eclipse season
Fated meetings and events common
Major announcements and changes

**Your Eclipse Node:**
Check which house eclipses fall in your chart.
That house area will see major changes.
"""
    
    def _explain_moon_phases(self) -> str:
        return """
🌙 **LUNAR PHASES - Monthly Rhythms**

The Moon cycles through 4 main phases every ~29.5 days.
Each phase has different energy and purposes.

**🌑 NEW MOON (Solar Conjunction)**
Energy: Beginnings, Intentions, Darkness
What to do: Set intentions, plant seeds, begin projects
Visibility: Moon between Earth and Sun (invisible)
Best for: New initiatives, fresh starts

**🌒 Waxing Crescent (0-90° from Sun)**
Energy: Growth, Building, Momentum
What to do: Take action on intentions, build, move forward
Timing: 7-8 days after New Moon
Best for: Action and momentum

**🌓 First Quarter (90° from Sun)**
Energy: Crisis of Action, Challenges, Momentum
What to do: Overcome obstacles, push through resistance
Timing: ~7 days after Waxing Crescent
Best for: Working through challenges

**🌕 FULL MOON (Opposition to Sun)**
Energy: Culmination, Completion, Illumination, Realization
What to do: Harvest, celebrate, release
Visibility: Moon fully illuminated
Best for: Finishing projects, clarity, full-moon rituals

**🌖 Waning Gibbous (90-180° after Full Moon)**
Energy: Gratitude, Sharing, Giving
What to do: Share your gifts, express gratitude
Timing: 7-8 days after Full Moon
Best for: Sharing and giving back

**🌗 Last Quarter (90° before New Moon)**
Energy: Rest, Release, Reflection, Surrendering
What to do: Release, let go, reflect, rest
Timing: ~7 days after Waning Gibbous
Best for: Letting go and rest

**🌘 Waning Crescent (New Moon Approaches)**
Energy: Final Release, Completion, Rest
What to do: Complete, close out, rest, prepare for new beginning
Timing: ~3 days before New Moon
Best for: Final release and rest

**Your Moon Phase:**
Your natal Moon phase shows your life's rhythm:
Waxing Moon (New → Full) = Life building, growth-oriented
Waning Moon (Full → New) = Life releasing, wisdom-oriented
"""
    
    def _how_to_read_chart(self) -> str:
        return """
📖 **HOW TO READ YOUR BIRTH CHART - A Guide**

Your birth chart is a snapshot of the sky at your birth moment.
Here's how to read it systematically:

**STEP 1: Identify the Big Three**
• Sun sign (your identity and ego)
• Moon sign (your emotions and inner world)
• Rising sign (how others see you, your mask)

**STEP 2: Identify Planet Placements**
For each planet, note:
• Which sign it's in
• Which house it's in
• Any aspects it makes

**STEP 3: Understand the Houses**
Each house governs different life areas.
• 1st: Self, appearance
• 2nd: Money, values
• 3rd: Communication, learning
• 4th: Home, family
• 5th: Creativity, romance
• 6th: Health, work
• 7th: Relationships, partnerships
• 8th: Transformation, sexuality
• 9th: Philosophy, travel
• 10th: Career, public image
• 11th: Friendship, groups
• 12th: Spirituality, subconscious

**STEP 4: Look for Patterns**
• Stelliums (3+ planets in one sign or house)
• Grand Trines (special harmonious patterns)
• T-Squares (challenging patterns)
• Dominant elements and modalities

**STEP 5: Consider Aspects**
Major aspects:
• Conjunction: Blended energy
• Sextile: Easy flow
• Square: Challenge/growth
• Trine: Natural talent
• Opposition: Awareness/projection

**STEP 6: Find Your Personal Planets**
Personal planets (day-to-day):
• Sun, Moon, Mercury, Venus, Mars

Social planets (collective timing):
• Jupiter, Saturn

Generational planets:
• Uranus, Neptune, Pluto

**Reading Order:**
1. Big Three first
2. Then personal planets
3. Then chart patterns
4. Then aspects
5. Then outer planets for deeper meaning

**Remember:**
Your chart is like a symphony - all parts together create the music.
No single element defines you.
Integration is key!
"""
    
    def _explain_zodiac(self) -> str:
        return """
🔄 **THE ZODIAC - Ancient Wisdom Modern Application**

The zodiac is a 360° circle divided into 12 equal signs.
It represents the full spectrum of human experience and growth.

**Why 12 Signs?**
12 is a sacred number representing wholeness and completion.
The signs progress through all four elements and three modalities.

**The Zodiac Wheel:**
Starting with Aries (Spring Equinox in Northern Hemisphere)

FIRE SIGNS: Aries, Leo, Sagittarius
(Action, Passion, Intuition)

EARTH SIGNS: Taurus, Virgo, Capricorn
(Stability, Practicality, Material)

AIR SIGNS: Gemini, Libra, Aquarius
(Communication, Intellect, Ideas)

WATER SIGNS: Cancer, Scorpio, Pisces
(Emotion, Intuition, Feeling)

**The Three Modalities:**

CARDINAL (Initiators): Aries, Cancer, Libra, Capricorn
FIXED (Consolidators): Taurus, Leo, Scorpio, Aquarius
MUTABLE (Adapters): Gemini, Virgo, Sagittarius, Pisces

**The Full Spectrum:**
Each sign is necessary and complete.
None is "better" than another.
Each sign's strengths are others' opportunities for growth.

**Working with the Zodiac:**
Understand your own sign deeply.
Appreciate every sign's gifts and challenges.
Use zodiac knowledge for self-understanding.
"""
    
    def _career_astrology_guide(self) -> str:
        return """
💼 **ASTROLOGY & CAREER - Finding Your Calling**

Your birth chart shows your work style, talents, and career direction.

**Key Placements for Career:**

**10th House & Midheaven (Career Point):**
Primary indicator of career direction and public reputation
What career path suits you
How you're known professionally

**6th House (Work):**
Your actual work environment and style
How you approach daily work
Workplace relationships

**Sun Sign:**
Your core identity and creative expression through work
What energizes you professionally
Natural talents and strengths

**Saturn Placements:**
Your career responsibilities and limitations
Long-term career structure
Patience and persistence in career

**Mars Placements:**
Your work drive and ambition
How you take action professionally
Energy and assertiveness in work

**Mercury Placements:**
How you communicate at work
Your mental approach to problems
Learning and teaching style

**Career By Sign:**

Aries: Pioneer, entrepreneur, military, sports
Taurus: Finance, banking, real estate, agriculture
Gemini: Communication, teaching, writing, sales
Cancer: Counseling, nursing, real estate, hospitality
Leo: Entertainment, management, leadership, education
Virgo: Healthcare, analysis, service, planning
Libra: Law, diplomacy, arts, design, HR
Scorpio: Psychology, research, finance, investigation
Sagittarius: Travel, education, publishing, law
Capricorn: Government, business, engineering, management
Aquarius: Technology, innovation, humanitarian, science
Pisces: Arts, spirituality, psychology, medicine

**Finding Your Career:**
Look at your 10th house sign
Check your Mars (drive) and Saturn (structure)
Consider your Sun sign talents
Look at 6th house for work environment
Check aspects to career planets
"""
    
    def _financial_astrology_guide(self) -> str:
        return """
💰 **ASTROLOGY & MONEY - Financial Wisdom**

Your birth chart shows your money psychology, values, and financial path.

**Key Placements for Finances:**

**2nd House (Money & Values):**
Your primary financial house
Your money psychology
What you value most
Your earning ability

**8th House (Shared Resources):**
Inheritance and shared money
Tax, debt, other's money
Financial transformation

**Jupiter (Expansion & Luck):**
Where money naturally flows
Financial opportunities
Expansion in finances
Abundance areas

**Saturn (Limitation & Discipline):**
Financial responsibilities
Where you must be careful
Lessons about money
Long-term financial structure

**Venus (Values & Money):**
What you spend on
Financial attractions
Values and possessions
How you attract abundance

**Moon (Emotional Money Relationship):**
Your emotional connection to money
Security needs
Money memories from childhood

**Financial Psychology by Sign:**

Aries: Impulsive spender, quick investments, entrepreneurial
Taurus: Saver, values security, steady accumulation
Gemini: Variable income, multiple streams, trades ideas
Cancer: Saves for security, emotional spending, property
Leo: Generous spender, luxury items, creative investments
Virgo: Budget-conscious, analytical, practical investments
Libra: Balanced spending, aesthetic purchases, partnerships
Scorpio: Hidden investments, transformation, power/control money
Sagittarius: Expansive, travels, philosophical about money
Capricorn: Long-term planner, investments, wealth building
Aquarius: Unconventional investments, technology, groups
Pisces: Gives away money, spiritual investments, dreamy about finances

**Financial Transits:**
Jupiter transits: Times of financial expansion (every 12 years)
Saturn transits: Times of financial discipline and structure
Venus transits: Times of financial attraction and spending
Mercury transits: Financial communications and decisions
"""
    
    def _love_compatibility_guide(self) -> str:
        return """
💕 **ASTROLOGY & LOVE - The Complete Picture**

Sun sign compatibility is just the beginning!
For true romantic compatibility, look at THREE placements:

**THE VENUS SIGN:**
How you love and show affection
What attracts you in romance
Your love language and needs
Most important for romantic attraction!

**THE MARS SIGN:**
Your passion and desire
Sexual chemistry
How you pursue what you want
Energy in intimate relationships

**THE MOON SIGN:**
Emotional compatibility
What makes you feel secure
Emotional intimacy needs
Long-term compatibility indicator

**Complete Compatibility Check:**

Compare:
• Venus with Venus (Love compatibility)
• Mars with Mars (Passion compatibility)
• Moon with Moon (Emotional compatibility)
• Sun with Sun (Life direction compatibility)
• Aspects between charts (Synastry)

**Venus Sign Meanings in Love:**

Venus in Fire (Aries, Leo, Sagittarius): Passionate, direct, enthusiastic lovers
Venus in Earth (Taurus, Virgo, Capricorn): Sensual, committed, loyal lovers
Venus in Air (Gemini, Libra, Aquarius): Mental, communicative, social lovers
Venus in Water (Cancer, Scorpio, Pisces): Emotional, intuitive, devoted lovers

**Mars Sign Meanings in Passion:**

Mars in Fire: Bold, passionate, direct approach
Mars in Earth: Sensual, steady, grounded approach
Mars in Air: Mental, communicative, varied approach
Mars in Water: Emotional, intuitive, sensitive approach

**Moon Sign Emotional Compatibility:**

Same element: Natural emotional understanding
Trine/Sextile: Easy emotional flow
Square: Emotional friction but growth
Opposition: Complementary but requires work

**The Real Truth:**
Challenging combinations CAN work with effort.
Harmonious combinations can fail without effort.
Love requires more than astrology!
But astrology helps you understand each other.
"""
    
    def _health_astrology_guide(self) -> str:
        return """
⚕️ **ASTROLOGY & HEALTH - Holistic Wellness**

Your birth chart reveals health tendencies and wellness needs.

**Health Vulnerabilities by Sign:**

Aries: Headaches, fever, inflammation, accidents
Taurus: Sore throat, thyroid, neck tension, overeating
Gemini: Nervousness, respiratory issues, arm/hand problems
Cancer: Digestive issues, breasts, emotional eating, water retention
Leo: Heart issues, back problems, circulation, ego-related stress
Virgo: Digestion, anxiety, nervous tension, perfectionism stress
Libra: Lower back, kidney issues, imbalance, indecision stress
Scorpio: Reproductive, elimination, obsessive behaviors, intensity stress
Sagittarius: Hips, thighs, liver, over-extension, excess
Capricorn: Bones, joints, skin, arthritis, restriction stress
Aquarius: Circulation, nervous system, legs, detachment stress
Pisces: Immune system, feet, addiction, escapism stress

**Health by Modality:**

CARDINAL (Aries, Cancer, Libra, Capricorn):
Health issues from over-initiation and constant activity
Need: Rest and boundaries

FIXED (Taurus, Leo, Scorpio, Aquarius):
Health issues from rigidity and resistance to change
Need: Flexibility and flow

MUTABLE (Gemini, Virgo, Sagittarius, Pisces):
Health issues from nervousness and scatter
Need: Focus and grounding

**Wellness Practices by Sign:**

Aries: High-intensity exercise, competition
Taurus: Yoga, walking, sensual practices
Gemini: Variety in exercise, dancing, mental health focus
Cancer: Home practices, emotional healing, swimming
Leo: Creative movement, strength training, heart-opening
Virgo: Consistent routines, detailed nutrition, analysis
Libra: Partner exercise, balance practices, beauty/spa
Scorpio: Deep work, transformation, detective health
Sagittarius: Travel sports, philosophy, expansion practices
Capricorn: Structured programs, long-term goals, discipline
Aquarius: Group activities, innovation, community wellness
Pisces: Meditation, water activities, spiritual practices

**Key Health Planets:**

6th House: Day-to-day health and wellness
Chiron: Your wound and healing gift
Saturn: Health challenges and structure needed
Moon: Emotional health foundation
Mars: Energy and vitality
"""
    
    def _general_astrology_guidance(self) -> str:
        return """
✨ **GENERAL ASTROLOGY WISDOM**

Here are some core astrology principles:

**Core Concepts:**

1. **Astrology is Symbolic**
Planets represent archetypes and principles
Signs show how energy expresses
Houses show life areas

2. **No "Bad" Placements**
Every placement has shadow and light side
Challenging aspects create growth
Nothing is fixed or determined

3. **Free Will Exists**
Astrology shows potential, not destiny
You choose how to work with your chart
Awareness empowers choice

4. **Everything is Connected**
Micro and macro reflect each other
Your chart reflects universal principles
Individual and cosmos mirror each other

5. **Timing is Sacred**
Transits show current influences
Progressions show inner development
Returns mark major life cycles

**Using Astrology Wisely:**

✓ Use for self-understanding
✓ Use for personal growth
✓ Use for timing important decisions
✓ Use to appreciate others' differences
✓ Use as a mirror for reflection

✗ Don't use for absolute prediction
✗ Don't use to avoid responsibility
✗ Don't use to label people negatively
✗ Don't use to feel victimized by placements
✗ Don't neglect practical action

**Remember:**
Astrology is a tool for wisdom and self-understanding.
Combined with action, awareness, and choice, it's powerful.
But astrology is not deterministic - you have free will.
Use your chart as a guide, not a cage.
"""
    
    def _get_house_ordinal(self, num: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        ordinals = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth',
                   6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth',
                   11: 'eleventh', 12: 'twelfth'}
        return ordinals.get(num, f'{num}th')


# ==================== SINGLETON INSTANCE ====================

astrology_qa = AstrologyQA()

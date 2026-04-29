"""AI Astrology Coach - Proactive personalized guidance and decision support.

This module provides an intelligent coaching system that learns user patterns,
offers timing recommendations, and provides daily proactive guidance based on
current transits, progressions, and the user's unique natal chart.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

# Import other astrology modules for integrated analysis
from .expertise import PLANETS, ZODIAC_SIGNS, ASPECTS
from .advanced_transits import transit_engine
from .predictive_suite import predictive_engine


class DecisionCategory(Enum):
    """Categories of decisions the coach can advise on."""
    CAREER = "career"
    LOVE = "love"
    HEALTH = "health"
    FINANCES = "finances"
    TRAVEL = "travel"
    COMMUNICATION = "communication"
    CREATIVITY = "creativity"
    SPIRITUALITY = "spirituality"


class TimingQuality(Enum):
    """Quality assessment of current timing."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    CHALLENGING = "challenging"
    AVOID = "avoid"


@dataclass
class CoachingRecommendation:
    """A specific recommendation from the AI coach."""
    category: DecisionCategory
    timing_quality: TimingQuality
    recommendation: str
    reasoning: str
    best_days: List[str]  # Days of week or specific dates
    avoid_days: List[str]
    confidence: float  # 0.0 to 1.0
    astrological_factors: List[str]


@dataclass
class UserChartProfile:
    """Learned profile of user's chart patterns over time."""
    natal_chart: Dict
    query_history: List[Dict] = field(default_factory=list)
    decision_patterns: Dict[str, List[str]] = field(default_factory=dict)
    timing_preferences: Dict[str, str] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class AIAstrologyCoach:
    """Proactive AI astrology coach with personalized guidance."""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserChartProfile] = {}
        
        # Decision timing factors database
        self.decision_timing_factors = self._build_timing_factors()
        
        # Daily guidance themes
        self.guidance_themes = self._build_guidance_themes()
    
    def _build_timing_factors(self) -> Dict[str, Dict]:
        """Build database of optimal timing factors for different decisions."""
        return {
            "career": {
                "best_transits": [
                    "Jupiter transiting 10th house",
                    "Saturn transiting 10th house (for long-term)",
                    "Sun transiting 10th house",
                    "Mars transiting 10th house (for action)",
                ],
                "avoid_transits": [
                    "Saturn square Midheaven",
                    "Mars opposite Midheaven",
                    "Neptune square Midheaven (confusion)",
                ],
                "best_progressions": [
                    "Progressed Sun entering 10th house",
                    "Progressed MC changing signs",
                ],
                "best_days": ["Tuesday (Mars)", "Thursday (Jupiter)", "Sunday (Sun)"],
                "avoid_days": ["Saturday (Saturn - unless long-term commitment)"],
            },
            "love": {
                "best_transits": [
                    "Venus transiting 5th or 7th house",
                    "Jupiter transiting 5th or 7th house",
                    "Venus trine natal Venus",
                    "Mars trine natal Venus (attraction)",
                ],
                "avoid_transits": [
                    "Saturn square Venus",
                    "Mars square Venus (conflicts)",
                    "Venus retrograde (reconsider)",
                ],
                "best_progressions": [
                    "Progressed Venus changing signs",
                    "Progressed Venus entering 7th house",
                ],
                "best_days": ["Friday (Venus)", "Monday (Moon - emotions)"],
                "avoid_days": ["Saturday (Saturn - coldness)"],
            },
            "health": {
                "best_transits": [
                    "Jupiter transiting 1st or 6th house",
                    "Sun transiting 1st or 6th house",
                    "Mars transiting 1st house (energy boost)",
                ],
                "avoid_transits": [
                    "Saturn transiting 1st or 6th house (caution needed)",
                    "Mars square natal Mars (injury risk)",
                    "Neptune square 6th house (health confusion)",
                ],
                "best_progressions": [
                    "Progressed Sun entering 1st house",
                    "Progressed Mars in harmonious aspect",
                ],
                "best_days": ["Sunday (Sun - vitality)", "Tuesday (Mars - energy)"],
                "avoid_days": [],
            },
            "finances": {
                "best_transits": [
                    "Jupiter transiting 2nd or 8th house",
                    "Venus transiting 2nd house",
                    "Sun transiting 2nd house",
                ],
                "avoid_transits": [
                    "Saturn square 2nd house ruler",
                    "Uranus transiting 2nd house (instability)",
                    "Neptune square 2nd house (confusion)",
                ],
                "best_progressions": [
                    "Progressed Jupiter entering 2nd house",
                    "Progressed Sun entering 2nd house",
                ],
                "best_days": ["Thursday (Jupiter - expansion)", "Friday (Venus - money)"],
                "avoid_days": ["Saturday (Saturn - restriction)"],
            },
            "travel": {
                "best_transits": [
                    "Jupiter transiting 9th house",
                    "Sun transiting 9th house",
                    "Mercury transiting 9th house (short trips)",
                ],
                "avoid_transits": [
                    "Mercury retrograde (delays, lost luggage)",
                    "Saturn transiting 9th house (restrictions)",
                    "Mars square 9th house (accidents)",
                ],
                "best_progressions": [
                    "Progressed Sun entering 9th house",
                ],
                "best_days": ["Wednesday (Mercury)", "Thursday (Jupiter)"],
                "avoid_days": ["Mercury retrograde periods"],
            },
            "communication": {
                "best_transits": [
                    "Mercury transiting 3rd house",
                    "Sun transiting 3rd house",
                    "Venus transiting 3rd house (harmonious)",
                ],
                "avoid_transits": [
                    "Mercury retrograde",
                    "Mercury square natal Mercury",
                    "Saturn square 3rd house (blocks)",
                ],
                "best_progressions": [
                    "Progressed Mercury changing signs",
                ],
                "best_days": ["Wednesday (Mercury)", "Sunday (Sun - clarity)"],
                "avoid_days": ["Mercury retrograde periods", "Saturn days for negotiations"],
            },
            "creativity": {
                "best_transits": [
                    "Sun transiting 5th house",
                    "Venus transiting 5th house",
                    "Jupiter transiting 5th house",
                    "Neptune trine natal Venus (inspiration)",
                ],
                "avoid_transits": [
                    "Saturn square 5th house",
                    "Mars opposite 5th house (blocked)",
                ],
                "best_progressions": [
                    "Progressed Venus entering 5th house",
                    "Progressed Sun entering 5th house",
                ],
                "best_days": ["Sunday (Sun - creativity)", "Friday (Venus - arts)"],
                "avoid_days": [],
            },
            "spirituality": {
                "best_transits": [
                    "Neptune transiting 9th or 12th house",
                    "Jupiter transiting 9th or 12th house",
                    "Sun transiting 12th house",
                ],
                "avoid_transits": [
                    "Saturn square 12th house (spiritual crisis)",
                    "Mars transiting 12th house (hidden enemies)",
                ],
                "best_progressions": [
                    "Progressed Sun entering 12th house",
                    "Progressed Moon in 12th house",
                ],
                "best_days": ["Monday (Moon - intuition)", "Thursday (Jupiter - expansion)"],
                "avoid_days": [],
            },
        }
    
    def _build_guidance_themes(self) -> Dict[str, List[str]]:
        """Build daily guidance theme templates."""
        return {
            "career_opportunity": [
                "Today's cosmic weather favors professional advancement.",
                "Strong energy for making career moves today.",
                "Excellent day for networking and professional connections.",
                "Leadership opportunities may present themselves.",
            ],
            "love_harmony": [
                "Romantic energy is flowing beautifully today.",
                "Great day for heart-to-heart conversations.",
                "Venus brings harmony to relationships.",
                "Perfect timing for romantic gestures.",
            ],
            "caution_needed": [
                "Exercise caution in major decisions today.",
                "Not the best day for important commitments.",
                "Energy is challenging - patience required.",
                "Avoid conflicts and wait for better timing.",
            ],
            "high_energy": [
                "Your energy is peaking - take action!",
                "Mars gives you drive and determination.",
                "Excellent day for physical activity and initiatives.",
                "Time to tackle challenging projects.",
            ],
            "introspection": [
                "Good day for reflection and inner work.",
                "Focus on understanding your deeper motivations.",
                "Spiritual practices will be especially rewarding.",
                "Time to pause and reassess your direction.",
            ],
        }
    
    def register_user(self, user_id: str, natal_chart: Dict):
        """Register a new user and store their chart."""
        self.user_profiles[user_id] = UserChartProfile(
            natal_chart=natal_chart,
            query_history=[],
            decision_patterns={},
            timing_preferences={},
            goals=[],
            last_updated=datetime.now()
        )
    
    def get_recommendation(
        self,
        user_id: str,
        decision: str,
        category: Optional[DecisionCategory] = None,
        current_date: Optional[datetime] = None
    ) -> CoachingRecommendation:
        """Get personalized recommendation for a specific decision.
        
        Args:
            user_id: User identifier
            decision: The decision or action being considered (e.g., "Should I ask for a promotion?")
            category: Category of decision (auto-detected if not provided)
            current_date: Date to analyze (defaults to today)
            
        Returns:
            CoachingRecommendation with timing quality and advice
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Get user profile
        if user_id not in self.user_profiles:
            return self._generate_generic_recommendation(decision, category, current_date)
        
        profile = self.user_profiles[user_id]
        natal_chart = profile.natal_chart
        
        # Auto-detect category if not provided
        if category is None:
            category = self._detect_category(decision)
        
        # Analyze current transits
        current_transits = transit_engine.calculate_current_transits(
            natal_chart,
            current_date
        )
        
        # Get timing factors for this category
        timing_factors = self.decision_timing_factors.get(category.value, {})
        
        # Assess timing quality
        timing_quality, factors = self._assess_timing_quality(
            current_transits,
            timing_factors,
            natal_chart
        )
        
        # Generate specific recommendation
        recommendation_text = self._generate_recommendation_text(
            decision,
            category,
            timing_quality,
            factors
        )
        
        # Get best and avoid days
        best_days = timing_factors.get("best_days", [])
        avoid_days = timing_factors.get("avoid_days", [])
        
        # Calculate confidence based on factors
        confidence = self._calculate_confidence(timing_quality, len(factors))
        
        # Create recommendation
        recommendation = CoachingRecommendation(
            category=category,
            timing_quality=timing_quality,
            recommendation=recommendation_text,
            reasoning=self._build_reasoning(factors, timing_quality),
            best_days=best_days,
            avoid_days=avoid_days,
            confidence=confidence,
            astrological_factors=factors
        )
        
        # Record this query in user history
        self._record_query(user_id, decision, category, recommendation)
        
        return recommendation
    
    def _detect_category(self, decision: str) -> DecisionCategory:
        """Auto-detect decision category from text."""
        decision_lower = decision.lower()
        
        # Career keywords
        if any(word in decision_lower for word in [
            "job", "career", "promotion", "raise", "work", "boss", "interview",
            "business", "project", "meeting", "negotiate", "quit"
        ]):
            return DecisionCategory.CAREER
        
        # Love keywords
        if any(word in decision_lower for word in [
            "love", "relationship", "date", "partner", "marriage", "propose",
            "breakup", "romance", "boyfriend", "girlfriend", "spouse"
        ]):
            return DecisionCategory.LOVE
        
        # Health keywords
        if any(word in decision_lower for word in [
            "health", "doctor", "surgery", "exercise", "diet", "fitness",
            "medical", "therapy", "wellness"
        ]):
            return DecisionCategory.HEALTH
        
        # Finance keywords
        if any(word in decision_lower for word in [
            "money", "invest", "buy", "sell", "purchase", "finance", "loan",
            "debt", "savings", "stock", "crypto"
        ]):
            return DecisionCategory.FINANCES
        
        # Travel keywords
        if any(word in decision_lower for word in [
            "travel", "trip", "vacation", "journey", "flight", "move", "relocate"
        ]):
            return DecisionCategory.TRAVEL
        
        # Communication keywords
        if any(word in decision_lower for word in [
            "talk", "speak", "communicate", "tell", "discuss", "conversation",
            "email", "message", "call"
        ]):
            return DecisionCategory.COMMUNICATION
        
        # Creativity keywords
        if any(word in decision_lower for word in [
            "create", "art", "write", "music", "design", "creative", "project"
        ]):
            return DecisionCategory.CREATIVITY
        
        # Spirituality keywords
        if any(word in decision_lower for word in [
            "spiritual", "meditation", "prayer", "enlightenment", "soul",
            "consciousness"
        ]):
            return DecisionCategory.SPIRITUALITY
        
        # Default to career if unclear
        return DecisionCategory.CAREER
    
    def _assess_timing_quality(
        self,
        current_transits: List,
        timing_factors: Dict,
        natal_chart: Dict
    ) -> Tuple[TimingQuality, List[str]]:
        """Assess quality of current timing based on transits."""
        positive_factors = []
        negative_factors = []
        
        # Check for best transits
        best_transits = timing_factors.get("best_transits", [])
        for transit in current_transits:
            aspect_label = transit.transit_type if isinstance(transit.transit_type, str) else str(transit.transit_type)
            transit_desc = f"{transit.transiting_planet} {aspect_label} {transit.natal_planet}"
            
            # Simplified matching (in production, would be more sophisticated)
            if any(best in transit_desc or best.split()[0] in transit_desc for best in best_transits):
                positive_factors.append(f"✓ {transit_desc}: {transit.meaning[:100]}")
        
        # Check for challenging transits
        avoid_transits = timing_factors.get("avoid_transits", [])
        for transit in current_transits:
            aspect_label = transit.transit_type if isinstance(transit.transit_type, str) else str(transit.transit_type)
            transit_desc = f"{transit.transiting_planet} {aspect_label} {transit.natal_planet}"
            
            if any(avoid in transit_desc or avoid.split()[0] in transit_desc for avoid in avoid_transits):
                negative_factors.append(f"✗ {transit_desc}: {transit.meaning[:100]}")
        
        # Determine overall quality
        if len(positive_factors) >= 3 and len(negative_factors) == 0:
            return TimingQuality.EXCELLENT, positive_factors
        elif len(positive_factors) >= 2 and len(negative_factors) <= 1:
            return TimingQuality.GOOD, positive_factors + negative_factors
        elif len(positive_factors) >= len(negative_factors):
            return TimingQuality.FAIR, positive_factors + negative_factors
        elif len(negative_factors) > len(positive_factors) and len(negative_factors) <= 2:
            return TimingQuality.CHALLENGING, negative_factors + positive_factors
        else:
            return TimingQuality.AVOID, negative_factors
    
    def _generate_recommendation_text(
        self,
        decision: str,
        category: DecisionCategory,
        timing_quality: TimingQuality,
        factors: List[str]
    ) -> str:
        """Generate specific recommendation text."""
        if timing_quality == TimingQuality.EXCELLENT:
            return f"✓ YES - Excellent timing for {category.value} decisions! The stars are aligned in your favor. {decision} This is an optimal moment to move forward."
        
        elif timing_quality == TimingQuality.GOOD:
            return f"✓ YES - Good timing for {category.value} actions. While not perfect, the cosmic energy supports your decision. {decision} Proceed with confidence."
        
        elif timing_quality == TimingQuality.FAIR:
            return f"⚠ PROCEED WITH CAUTION - Fair timing for {category.value}. {decision} The energy is mixed. Consider the pros and cons carefully, but moving forward is possible."
        
        elif timing_quality == TimingQuality.CHALLENGING:
            return f"⚠ NOT IDEAL - Challenging timing for {category.value}. {decision} Consider waiting if possible. If you must proceed, be extra prepared and patient."
        
        else:  # AVOID
            return f"✗ NOT RECOMMENDED - Poor timing for {category.value} decisions. {decision} Strong advice to wait for better cosmic conditions. Delay if at all possible."
    
    def _build_reasoning(self, factors: List[str], timing_quality: TimingQuality) -> str:
        """Build detailed reasoning explanation."""
        if not factors:
            return "No significant astrological factors detected at this time."
        
        reasoning = f"Current timing is {timing_quality.value.upper()} based on:\n\n"
        for factor in factors[:5]:  # Show top 5 factors
            reasoning += f"{factor}\n"
        
        return reasoning
    
    def _calculate_confidence(self, timing_quality: TimingQuality, factor_count: int) -> float:
        """Calculate confidence score for recommendation."""
        base_confidence = {
            TimingQuality.EXCELLENT: 0.95,
            TimingQuality.GOOD: 0.80,
            TimingQuality.FAIR: 0.65,
            TimingQuality.CHALLENGING: 0.50,
            TimingQuality.AVOID: 0.85,  # High confidence in avoid recommendation
        }
        
        confidence = base_confidence[timing_quality]
        
        # Adjust based on number of factors
        if factor_count >= 3:
            confidence += 0.05
        elif factor_count == 0:
            confidence -= 0.15
        
        return min(max(confidence, 0.0), 1.0)
    
    def _generate_generic_recommendation(
        self,
        decision: str,
        category: Optional[DecisionCategory],
        current_date: datetime
    ) -> CoachingRecommendation:
        """Generate recommendation without user profile."""
        if category is None:
            category = self._detect_category(decision)
        
        # Basic recommendation without personalization
        return CoachingRecommendation(
            category=category,
            timing_quality=TimingQuality.FAIR,
            recommendation=f"For {category.value} decisions like '{decision}', general timing advice suggests proceeding with careful consideration. Register your birth chart for personalized guidance.",
            reasoning="Generic recommendation - no natal chart registered.",
            best_days=[],
            avoid_days=[],
            confidence=0.4,
            astrological_factors=["No personalized analysis available"]
        )
    
    def _record_query(
        self,
        user_id: str,
        decision: str,
        category: DecisionCategory,
        recommendation: CoachingRecommendation
    ):
        """Record user query for learning."""
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        profile.query_history.append({
            "timestamp": datetime.now(),
            "decision": decision,
            "category": category.value,
            "timing_quality": recommendation.timing_quality.value,
            "recommendation": recommendation.recommendation
        })
        
        # Update decision patterns
        if category.value not in profile.decision_patterns:
            profile.decision_patterns[category.value] = []
        profile.decision_patterns[category.value].append(decision)
        
        profile.last_updated = datetime.now()
    
    def generate_daily_guidance(
        self,
        user_id: str,
        date: Optional[datetime] = None
    ) -> str:
        """Generate proactive daily guidance without being asked.
        
        Args:
            user_id: User identifier
            date: Date to generate guidance for (defaults to today)
            
        Returns:
            Human-readable daily guidance text
        """
        if date is None:
            date = datetime.now()
        
        if user_id not in self.user_profiles:
            return "Register your birth chart to receive personalized daily guidance."
        
        profile = self.user_profiles[user_id]
        natal_chart = profile.natal_chart
        
        # Calculate current transits
        current_transits = transit_engine.calculate_current_transits(natal_chart, date)
        
        # Get daily guidance from transit engine
        transit_guidance = transit_engine.generate_daily_guidance(natal_chart, date)
        
        # Analyze what user typically cares about
        top_categories = self._get_top_user_categories(profile)
        
        # Build comprehensive guidance
        guidance = f"🌟 DAILY GUIDANCE for {date.strftime('%A, %B %d, %Y')}\n\n"
        
        # Add cosmic weather summary
        guidance += "**COSMIC WEATHER:**\n"
        guidance += f"{transit_guidance}\n\n"
        
        # Add category-specific guidance
        if top_categories:
            guidance += "**PERSONALIZED ADVICE:**\n"
            for category_name in top_categories[:2]:  # Top 2 categories user cares about
                category = DecisionCategory(category_name)
                timing_factors = self.decision_timing_factors.get(category.value, {})
                
                timing_quality, factors = self._assess_timing_quality(
                    current_transits,
                    timing_factors,
                    natal_chart
                )
                
                guidance += f"\n**{category.value.upper()}:** "
                if timing_quality in [TimingQuality.EXCELLENT, TimingQuality.GOOD]:
                    guidance += f"✓ Great day for {category.value} matters! "
                elif timing_quality == TimingQuality.FAIR:
                    guidance += f"⚖️ Mixed energy for {category.value}. Proceed thoughtfully. "
                else:
                    guidance += f"⚠️ Exercise caution with {category.value} today. "
                
                if factors:
                    guidance += factors[0].split(':')[1].strip() if ':' in factors[0] else ""
                guidance += "\n"
        
        # Add opportunities and warnings
        opportunities, warnings = self._identify_opportunities_warnings(current_transits)
        
        if opportunities:
            guidance += f"\n**⭐ OPPORTUNITIES TODAY:**\n"
            for opp in opportunities[:2]:
                guidance += f"• {opp}\n"
        
        if warnings:
            guidance += f"\n**⚠️ WATCH OUT FOR:**\n"
            for warn in warnings[:2]:
                guidance += f"• {warn}\n"
        
        # Add best activities for today
        best_activities = self._suggest_best_activities(current_transits, natal_chart)
        if best_activities:
            guidance += f"\n**💡 BEST ACTIVITIES TODAY:**\n"
            for activity in best_activities[:3]:
                guidance += f"• {activity}\n"
        
        return guidance
    
    def _get_top_user_categories(self, profile: UserChartProfile) -> List[str]:
        """Get top categories user frequently asks about."""
        if not profile.decision_patterns:
            return ["career", "love"]  # Default priorities
        
        # Count queries per category
        category_counts = {cat: len(queries) for cat, queries in profile.decision_patterns.items()}
        
        # Sort by frequency
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [cat for cat, count in sorted_categories]
    
    def _identify_opportunities_warnings(
        self,
        current_transits: List
    ) -> Tuple[List[str], List[str]]:
        """Identify opportunities and warnings from transits."""
        opportunities = []
        warnings = []
        
        for transit in current_transits:
            intensity = transit.intensity
            transit_type = transit.transit_type

            aspect_label = transit_type if isinstance(transit_type, str) else str(transit_type)
            positive_aspects = {"trine", "sextile", "conjunction"}
            challenging_aspects = {"square", "opposition", "quincunx"}
            is_high_intensity = intensity.value in ["major", "significant"]

            if is_high_intensity and aspect_label in positive_aspects:
                opportunities.append(
                    f"{transit.transiting_planet} {aspect_label} {transit.natal_planet}: "
                    f"{transit.meaning[:80]}..."
                )

            if is_high_intensity and aspect_label in challenging_aspects:
                warnings.append(
                    f"{transit.transiting_planet} {aspect_label} {transit.natal_planet}: "
                    f"{transit.meaning[:80]}..."
                )
        
        return opportunities[:3], warnings[:3]
    
    def _suggest_best_activities(
        self,
        current_transits: List,
        natal_chart: Dict
    ) -> List[str]:
        """Suggest best activities based on current transits."""
        activities = []
        
        for transit in current_transits:
            planet = transit.transiting_planet
            aspect = transit.aspect_type.value
            
            # Suggest activities based on planet and aspect
            if planet == "Mars" and aspect in ["trine", "sextile"]:
                activities.append("Physical exercise, competitive activities, taking initiative")
            
            if planet == "Venus" and aspect in ["trine", "sextile"]:
                activities.append("Social activities, artistic pursuits, romance")
            
            if planet == "Mercury" and aspect in ["trine", "sextile"]:
                activities.append("Communication, writing, learning, short trips")
            
            if planet == "Jupiter" and aspect in ["trine", "sextile"]:
                activities.append("Expansion, learning, teaching, networking")
            
            if planet == "Sun" and aspect in ["trine", "sextile"]:
                activities.append("Leadership, creative expression, confidence-building")
        
        return list(set(activities))  # Remove duplicates
    
    def get_weekly_forecast(
        self,
        user_id: str,
        start_date: Optional[datetime] = None
    ) -> str:
        """Generate week-ahead guidance."""
        if start_date is None:
            start_date = datetime.now()
        
        if user_id not in self.user_profiles:
            return "Register your birth chart to receive personalized forecasts."
        
        profile = self.user_profiles[user_id]
        natal_chart = profile.natal_chart
        
        forecast = f"📅 WEEK-AHEAD GUIDANCE\n"
        forecast += f"{start_date.strftime('%B %d')} - {(start_date + timedelta(days=6)).strftime('%B %d, %Y')}\n\n"
        
        # Analyze each day
        best_days = []
        challenging_days = []
        
        for day_offset in range(7):
            day = start_date + timedelta(days=day_offset)
            day_name = day.strftime("%A")
            
            # Get transits for this day
            transits = transit_engine.calculate_current_transits(natal_chart, day)
            
            # Quick assessment
            positive_count = sum(1 for t in transits if t.transit_type.value == "positive")
            challenging_count = sum(1 for t in transits if t.transit_type.value == "challenging")
            
            if positive_count > challenging_count:
                best_days.append(f"{day_name} ({day.strftime('%b %d')})")
            elif challenging_count > positive_count + 1:
                challenging_days.append(f"{day_name} ({day.strftime('%b %d')})")
        
        forecast += "**BEST DAYS THIS WEEK:**\n"
        for day in best_days:
            forecast += f"✓ {day}\n"
        
        forecast += "\n**CHALLENGING DAYS:**\n"
        for day in challenging_days:
            forecast += f"⚠️ {day}\n"
        
        forecast += "\n**WEEKLY PRIORITIES:**\n"
        forecast += "• Focus on opportunities during best days\n"
        forecast += "• Exercise patience during challenging days\n"
        forecast += "• Plan important activities for supportive cosmic windows\n"
        
        return forecast
    
    def add_goal(self, user_id: str, goal: str):
        """Add a personal goal for the user."""
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        if goal not in profile.goals:
            profile.goals.append(goal)
            profile.last_updated = datetime.now()
    
    def get_goal_timing(
        self,
        user_id: str,
        goal: str,
        timeframe_months: int = 12
    ) -> str:
        """Get optimal timing for achieving a specific goal."""
        if user_id not in self.user_profiles:
            return "Register your birth chart to receive personalized timing guidance."
        
        profile = self.user_profiles[user_id]
        natal_chart = profile.natal_chart
        
        # Detect goal category
        category = self._detect_category(goal)
        
        # Use predictive engine to find best timing windows
        events = predictive_engine.predict_event(
            natal_chart,
            goal,
            timeframe_years=timeframe_months / 12
        )
        
        if not events:
            return f"No strong astrological indicators found for '{goal}' in the next {timeframe_months} months. Continue working toward it steadily."
        
        timing = f"🎯 OPTIMAL TIMING FOR: {goal}\n\n"
        
        # Sort by probability
        events.sort(key=lambda e: e.probability, reverse=True)
        
        for i, event in enumerate(events[:3], 1):
            timing += f"**WINDOW {i}:** {event.timing.strftime('%B %Y')}\n"
            timing += f"Probability: {event.probability:.0%}\n"
            timing += f"Indicators: {', '.join(event.astrological_indicators[:2])}\n"
            timing += f"Advice: {event.advice}\n\n"
        
        return timing


# Create singleton instance
ai_coach = AIAstrologyCoach()

"""Integration layer connecting all advanced astrology modules to interpreter.

This module provides the query routing and natural language interpretation
for all 6 advanced astrology features, enabling seamless user interaction
with the complete astrology system.
"""

from datetime import datetime
from typing import Dict, Tuple, Optional, Any
import re

# Import all advanced modules
from .advanced_transits import transit_engine
from .deep_synastry import synastry_analyzer
from .predictive_suite import predictive_engine
from .ai_coach import ai_coach, DecisionCategory
from .vedic_system import vedic_engine
from .advanced_analysis import (
    rectification_engine,
    composite_chart_analyzer,
    astro_mapper
)
from .expertise import astrology_expertise


class AdvancedAstrologyRouter:
    """Routes natural language queries to appropriate advanced modules."""
    
    def __init__(self):
        self.transit_engine = transit_engine
        self.synastry_analyzer = synastry_analyzer
        self.predictive_engine = predictive_engine
        self.ai_coach = ai_coach
        self.vedic_engine = vedic_engine
        self.rectification = rectification_engine
        self.composite_analyzer = composite_chart_analyzer
        self.astro_mapper = astro_mapper
        self.expertise = astrology_expertise
        
        # User chart cache (in production, use database)
        self.user_charts = {}
        self.user_names = {}
    
    def process_query(self, query: str, user_chart: Optional[Dict] = None) -> Tuple[str, Dict]:
        """Process natural language astrology query and route to appropriate module.
        
        Returns: (response_text, metadata_dict)
        """
        query_lower = query.lower()
        
        # ===== DAILY GUIDANCE & COACHING =====
        if any(phrase in query_lower for phrase in [
            "should i", "should i today", "best day", "avoid today",
            "timing", "when should", "is today good", "decision"
        ]):
            return self._handle_coaching_query(query, user_chart)
        
        # ===== TRANSIT ANALYSIS =====
        if any(phrase in query_lower for phrase in [
            "transit", "what transits", "experiencing", "current planet",
            "planet moving", "saturn return", "jupiter", "mars"
        ]):
            return self._handle_transit_query(query, user_chart)
        
        # ===== PREDICTIVE / TIMING =====
        if any(phrase in query_lower for phrase in [
            "when will i", "when will", "when should i", "timing",
            "forecast", "year ahead", "time for", "happen",
            "marriage", "promotion", "move", "meet"
        ]):
            return self._handle_predictive_query(query, user_chart)
        
        # ===== RELATIONSHIP / SYNASTRY =====
        if any(phrase in query_lower for phrase in [
            "compatible", "compatibility", "synastry", "relationship",
            "us together", "we", "between", "and me",
            "romantic", "love", "marriage", "soulmate"
        ]):
            return self._handle_synastry_query(query, user_chart)
        
        # ===== VEDIC ASTROLOGY =====
        if any(phrase in query_lower for phrase in [
            "vedic", "nakshatra", "dasha", "sidereal", "rahu", "ketu",
            "vimshottari", "remedy", "gemstone", "mantra"
        ]):
            return self._handle_vedic_query(query, user_chart)
        
        # ===== ADVANCED ANALYSIS / RECTIFICATION =====
        if any(phrase in query_lower for phrase in [
            "rectif", "accurate birth", "birth time", "relocation", "astro map",
            "composite", "davison", "chart pattern", "grand trine", "grand cross"
        ]):
            return self._handle_advanced_analysis_query(query, user_chart)
        
        # ===== GENERAL ASTROLOGY =====
        # Fall back to expertise Q&A system
        return self._handle_general_query(query)
    
    def _handle_coaching_query(self, query: str, user_chart: Optional[Dict]) -> Tuple[str, Dict]:
        """Handle "Should I..." and decision-making queries."""
        if not user_chart:
            return (
                "I'd love to help with decision timing! To give personalized advice, "
                "I need your birth chart (date, time, location). Could you provide that?",
                {"module": "ai_coach", "status": "needs_chart"}
            )
        
        # Extract decision type
        category = self._extract_decision_category(query)
        
        # Get recommendation
        try:
            user_id = "default_user"
            if user_id not in self.ai_coach.user_profiles:
                self.ai_coach.register_user(user_id, user_chart)

            try:
                category_enum = DecisionCategory(category)
            except Exception:
                category_enum = None

            recommendation = self.ai_coach.get_recommendation(
                user_id=user_id,
                decision=query,
                category=category_enum
            )
            
            return (
                self._format_coaching_response(recommendation),
                {
                    "module": "ai_coach",
                    "category": category,
                    "timing_quality": recommendation.timing_quality.value,
                    "confidence": recommendation.confidence
                }
            )
        except Exception as e:
            return (f"Coaching analysis error: {str(e)}", {"module": "ai_coach", "error": str(e)})
    
    def _handle_transit_query(self, query: str, user_chart: Optional[Dict]) -> Tuple[str, Dict]:
        """Handle transit analysis queries."""
        if not user_chart:
            return (
                "To analyze your current transits, I need your birth chart. "
                "Please provide your birth date, time, and location.",
                {"module": "transit_engine", "status": "needs_chart"}
            )
        
        try:
            analysis = self.transit_engine.analyze_current_transits(user_chart)
            
            response = f"**YOUR CURRENT TRANSITS**\n\n"
            response += f"Major Aspects Active:\n"
            for aspect in analysis.get("major_aspects", [])[:5]:
                response += f"• {aspect}\n"
            
            response += f"\n**Interpretation:**\n{analysis.get('summary', 'Analysis complete')}\n"
            response += f"\n**Challenges:** {analysis.get('challenges', 'None predicted')}\n"
            response += f"**Opportunities:** {analysis.get('opportunities', 'Present')}\n"
            
            return (response, {"module": "transit_engine", "status": "success"})
        except Exception as e:
            return (f"Transit analysis error: {str(e)}", {"module": "transit_engine", "error": str(e)})
    
    def _handle_predictive_query(self, query: str, user_chart: Optional[Dict]) -> Tuple[str, Dict]:
        """Handle 'When will...' predictive timing queries."""
        if not user_chart:
            return (
                "To predict timing, I need your birth chart. "
                "Please share your birth date, time, and location.",
                {"module": "predictive_engine", "status": "needs_chart"}
            )
        
        # Extract event type
        event_type = self._extract_event_type(query)
        
        try:
            birth_date = user_chart.get("birth_date") if isinstance(user_chart, dict) else None
            now = datetime.now()
            current_year = now.year
            current_age = 30
            if isinstance(birth_date, datetime):
                current_age = max(1, int((now - birth_date).days / 365.25))

            prediction_text = self.predictive_engine.answer_predictive_question(
                birth_chart=user_chart,
                question=query,
                current_age=current_age,
                current_year=current_year
            )
            
            response = f"**TIMING PREDICTION**\n\n"
            response += f"Event: {event_type}\n"
            response += f"\n{prediction_text}\n"
            
            return (response, {"module": "predictive_engine", "event_type": event_type})
        except Exception as e:
            return (f"Prediction error: {str(e)}", {"module": "predictive_engine", "error": str(e)})
    
    def _handle_synastry_query(self, query: str, user_chart: Optional[Dict]) -> Tuple[str, Dict]:
        """Handle relationship compatibility queries."""
        # Extract names if mentioned
        match = re.search(r'(me|i).*(?:and|with)\s+(.+?)(?:\?|$)', query, re.IGNORECASE)
        if not match or not user_chart:
            return (
                "To analyze relationship compatibility, I need:\n"
                "1. Your birth chart (date, time, location)\n"
                "2. Their birth chart information\n\n"
                "Please provide both birth details.",
                {"module": "synastry_analyzer", "status": "needs_charts"}
            )
        
        other_name = match.group(2).strip()
        
        # In production, would look up other person's chart from database
        # For now, provide instructions
        return (
            f"To compare your chart with {other_name}'s, I need their birth information:\n"
            f"• Birth date (MM/DD/YYYY)\n"
            f"• Birth time (HH:MM)\n"
            f"• Birth location (City, Country)\n\n"
            f"Once you provide that, I can generate a detailed compatibility analysis including:\n"
            f"✓ Synastry aspects between your charts\n"
            f"✓ Romantic chemistry (Venus/Mars)\n"
            f"✓ Emotional connection (Moon/Mercury)\n"
            f"✓ Composite chart insights\n"
            f"✓ Overall compatibility score (0-100)\n"
            f"✓ Strengths and challenges",
            {"module": "synastry_analyzer", "status": "awaiting_other_chart"}
        )
    
    def _handle_vedic_query(self, query: str, user_chart: Optional[Dict]) -> Tuple[str, Dict]:
        """Handle Vedic astrology queries."""
        query_lower = query.lower()
        
        if not user_chart:
            return (
                "To provide Vedic astrology insights, I need your birth chart. "
                "Please share your birth date, time, and location.",
                {"module": "vedic_engine", "status": "needs_chart"}
            )
        
        try:
            # Generate Vedic chart
            vedic_chart = self.vedic_engine.calculate_vedic_chart(user_chart)
            
            # Determine what to show based on query
            if "nakshatra" in query_lower:
                response = f"**YOUR VEDIC ASTROLOGY PROFILE**\n\n"
                response += f"**Moon Nakshatra:** {vedic_chart.get('moon_nakshatra', 'Unknown')}\n"
                response += f"This lunar mansion indicates your emotional nature and inner self.\n"
            elif "dasha" in query_lower or "period" in query_lower:
                response = f"**YOUR CURRENT DASHA PERIOD**\n\n"
                current_dasha = vedic_chart.get('current_dasha', {})
                response += f"Mahadasha: {current_dasha.get('mahadasha', '?')}\n"
                response += f"Bhukti (Sub-period): {current_dasha.get('bhukti', '?')}\n"
                response += f"Period: {current_dasha.get('dates', 'Calculating...')}\n"
            elif "remedy" in query_lower:
                response = f"**RECOMMENDED REMEDIES**\n\n"
                remedies = self.vedic_engine.recommend_remedies(user_chart)
                for remedy in remedies[:5]:
                    response += f"• {remedy.get('remedy_type')}: {remedy.get('description')}\n"
            else:
                # Full Vedic report
                response = self.vedic_engine.generate_vedic_report(user_chart)
            
            return (response, {"module": "vedic_engine", "status": "success"})
        except Exception as e:
            return (f"Vedic analysis error: {str(e)}", {"module": "vedic_engine", "error": str(e)})
    
    def _handle_advanced_analysis_query(self, query: str, user_chart: Optional[Dict]) -> Tuple[str, Dict]:
        """Handle advanced analysis queries (rectification, composite, astro-mapping)."""
        query_lower = query.lower()
        
        if "rectif" in query_lower or "birth time" in query_lower:
            return (
                "**Birth Time Rectification**\n\n"
                "To rectify your birth time, I need:\n"
                "1. Your approximate birth time (within ±2 hours)\n"
                "2. Major life events (marriage, accidents, promotions, etc.) with dates\n\n"
                "This helps me find the exact birth time by correlating events with "
                "astrological progressions and transits.",
                {"module": "advanced_analysis", "submodule": "rectification"}
            )
        
        if "composite" in query_lower or "davison" in query_lower:
            return (
                "**Composite & Davison Charts**\n\n"
                "These represent the relationship entity itself:\n"
                "• **Composite Chart:** Midpoints of two people's planets\n"
                "• **Davison Chart:** Midpoint in space and time of two births\n\n"
                "Provide both birth charts for analysis.",
                {"module": "advanced_analysis", "submodule": "composite"}
            )
        
        if "relocation" in query_lower or "astro map" in query_lower:
            if not user_chart:
                return (
                    "To create an astro-map showing where you should live, I need your birth chart. "
                    "Also tell me locations you're considering.",
                    {"module": "advanced_analysis", "submodule": "relocation"}
                )
            
            return (
                "**Relocation Astrology (Astro-Mapping)**\n\n"
                "I can identify the best locations for your planets:\n"
                "• Venus line: Romance, beauty, arts\n"
                "• Jupiter line: Business, growth, luck\n"
                "• Saturn line: Career focus, responsibility\n"
                "• Neptune line: Spirituality, creativity\n\n"
                "Tell me locations you're considering, and I'll analyze them.",
                {"module": "advanced_analysis", "submodule": "relocation"}
            )
        
        if "pattern" in query_lower or "grand" in query_lower:
            if not user_chart:
                return (
                    "To analyze your chart patterns, I need your birth chart. "
                    "I can identify Grand Trines, Grand Crosses, Yods, and other formations.",
                    {"module": "advanced_analysis", "submodule": "patterns"}
                )
            
            patterns = self.composite_analyzer._find_chart_patterns(user_chart)
            if patterns:
                response = f"**ADVANCED CHART PATTERNS**\n\n"
                for pattern in patterns:
                    response += f"**{pattern.pattern_type.value.upper()}**\n"
                    response += f"Planets: {', '.join(pattern.planets_involved)}\n"
                    response += f"Interpretation: {pattern.interpretation}\n"
                    response += f"Significance: {pattern.significance}\n"
                    response += f"Life Areas: {pattern.influence_area}\n\n"
                return (response, {"module": "advanced_analysis", "submodule": "patterns"})
            else:
                return (
                    "No major advanced patterns found in your chart. "
                    "Your chart has a more harmonious, evenly distributed energy.",
                    {"module": "advanced_analysis", "submodule": "patterns"}
                )
        
        return (
            "Advanced analysis module ready. Ask about:\n"
            "• Birth time rectification\n"
            "• Composite/Davison charts\n"
            "• Relocation astrology\n"
            "• Chart patterns",
            {"module": "advanced_analysis", "status": "ready"}
        )
    
    def _handle_general_query(self, query: str) -> Tuple[str, Dict]:
        """Fall back to general astrology expertise system."""
        response = self.expertise.answer_question(query)
        return (response, {"module": "expertise", "status": "success"})
    
    def _extract_decision_category(self, query: str) -> str:
        """Extract decision category from query."""
        query_lower = query.lower()
        
        categories = {
            "career": ["job", "promotion", "work", "career", "resign", "apply", "interview"],
            "love": ["date", "relationship", "romantic", "love", "propose", "confession"],
            "health": ["health", "surgery", "doctor", "medical", "therapy", "treatment"],
            "finances": ["invest", "money", "buy", "sell", "loan", "financial"],
            "travel": ["travel", "move", "relocate", "trip", "journey", "vacation"],
            "communication": ["call", "message", "email", "speak", "conversation", "talk"],
            "creativity": ["creative", "art", "music", "write", "design", "project"],
            "spirituality": ["spiritual", "meditation", "retreat", "practice", "prayer", "cleanse"],
        }
        
        for category, keywords in categories.items():
            if any(kw in query_lower for kw in keywords):
                return category
        
        return "general"
    
    def _extract_event_type(self, query: str) -> str:
        """Extract event type from predictive query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["marriage", "marry", "married", "proposal"]):
            return "marriage"
        elif any(word in query_lower for word in ["promotion", "promoted", "job", "hired", "career"]):
            return "career"
        elif any(word in query_lower for word in ["move", "relocated", "relocation", "house"]):
            return "relocation"
        elif any(word in query_lower for word in ["pregnant", "pregnancy", "baby", "child"]):
            return "pregnancy"
        elif any(word in query_lower for word in ["meet", "encounter", "find"]):
            return "meeting_person"
        elif any(word in query_lower for word in ["money", "income", "wealth", "rich"]):
            return "financial"
        else:
            return "general_event"
    
    def _format_coaching_response(self, recommendation: Any) -> str:
        """Format coaching recommendation for display."""
        response = f"**Decision Guidance**\n\n"
        response += f"**Timing Quality:** {recommendation.timing_quality.value.upper()}\n"
        response += f"**Recommendation:** {recommendation.recommendation}\n"
        response += f"\n**Astrological Factors:**\n{recommendation.reasoning}\n"
        response += f"\n**Best Days:** {', '.join(recommendation.best_days)}\n"
        response += f"**Avoid Days:** {', '.join(recommendation.avoid_days)}\n"
        response += f"\n**Confidence:** {recommendation.confidence:.0%}"
        return response


# Create singleton router
advanced_router = AdvancedAstrologyRouter()

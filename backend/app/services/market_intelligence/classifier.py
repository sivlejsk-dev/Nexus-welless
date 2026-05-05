"""
Event classification engine - determines type, impact, direction, sentiment.
Uses NLP and keyword-based heuristics (production would use ML models).
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from collections import Counter

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

from .base import BaseEventClassifier
from .schemas import (
    EventClassification,
    EventType,
    ImpactSeverity,
    Direction,
    TimeHorizon,
    SentimentAnalysis,
    MarketEvent,
)

log = logging.getLogger(__name__)


class EventClassifier(BaseEventClassifier):
    """
    Classifies market events using a combination of:
    1. Keyword pattern matching
    2. Sentiment analysis (TextBlob or simple heuristic)
    3. Magnitude estimation (word strength, source credibility)
    4. Sector mapping
    """

    # Keyword sets for event type detection
    EVENT_KEYWORDS = {
        EventType.EARNINGS: {
            'earnings', 'eps', 'quarterly', 'q1', 'q2', 'q3', 'q4',
            'beat', 'miss', 'guidance', 'revenue', 'profit', 'loss',
            'report', 'announce', 'release', 'fy', 'quarter',
        },
        EventType.MERGER_ACQUISITION: {
            'merger', 'acquisition', 'acquire', 'buyout', 'takeover',
            'deal', 'merge', 'combination', 'propose', 'offer',
            'bid', 'purchase', 'divest',
        },
        EventType.REGULATORY: {
            'regulatory', 'fda', 'sec', 'approval', 'approve', 'reject',
            'rejected', 'denied', 'filing', ' investigation', 'audit',
            'compliance', 'regulation', 'lawsuit', 'settlement',
        },
        EventType.PRODUCT_LAUNCH: {
            'launch', 'announce', 'unveil', 'release', 'introduce',
            'new product', 'pipeline', 'patent', 'r&d', 'innovation',
            'prototype', 'preview', 'beta',
        },
        EventType.MANAGEMENT_CHANGE: {
            'ceo', 'cfo', 'executive', 'appoint', 'appointment',
            'resign', 'resignation', 'replace', 'management',
            'chairman', 'board', 'leadership', 'step down',
        },
        EventType.LEGAL: {
            'lawsuit', 'litigation', 'court', 'judge', 'legal',
            'settlement', 'patent', 'copyright', 'trademark',
            'breach', 'liability', 'damages',
        },
        EventType.MACROECONOMIC: {
            'fed', 'interest rate', 'inflation', 'cpi', 'gdp',
            'unemployment', 'jobs', 'nonfarm', 'central bank',
            'monetary policy', 'quantitative', 'treasury',
            'economic', 'economy', 'recession', 'growth',
        },
        EventType.GEOPOLITICAL: {
            'war', 'conflict', 'sanction', 'embargo', 'treaty',
            'trade war', 'tariff', 'diplomatic', 'geopolitical',
            'china', 'russia', 'ukraine', 'middle east',
        },
        EventType.ANALYST_UPGRADE: {
            'upgrade', 'downgrade', 'analyst', 'rating', 'target',
            'price target', 'buy', 'sell', 'hold', 'overweight',
            'undervalue', 'overvalue',
        },
        EventType.VIRAL_TREND: {
            'viral', 'trending', 'meme', 'reddit', 'twitter',
            'social media', 'hype', 'frenzy', 'mania',
            'crowd', 'retail', 'wbs', 'wsb',
        },
        EventType.INSTITUTIONAL_ACTION: {
            'institution', 'fund', 'hedge fund', 'buyback', 'dividend',
            'insider', '13f', '13g', '13d', 'institutional',
            'large shareholder', 'whale',
        },
    }

    # Keywords that impact magnitude (amplify the severity)
    IMPACT_AMPLIFIERS = {
        'unexpected', 'surprise', 'sudden', 'emergency', 'breaking',
        'major', 'significant', 'substantial', 'massive', 'huge',
        'critical', 'urgent', 'crisis',
    }

    # Words that suggest direction
    BULLISH_TERMS = {
        'buy', 'bull', 'up', 'rise', 'gain', 'positive', 'upgrade',
        'beat', 'surpass', 'exceed', 'growth', 'strong', 'robust',
        'recovery', 'rally', 'breakthrough', 'opportunity',
    }

    BEARISH_TERMS = {
        'sell', 'bear', 'down', 'fall', 'drop', 'negative', 'downgrade',
        'miss', 'below', 'weak', 'decline', 'crash', 'concern',
        'risk', 'worry', 'warning', 'threat', 'danger',
    }

    # Sector mapping keywords
    SECTOR_KEYWORDS = {
        'technology': {'tech', 'software', 'hardware', 'semiconductor', 'ai', 'cloud', 'chip'},
        'healthcare': {'pharma', 'biotech', 'healthcare', 'medical', 'drug', 'fda'},
        'finance': {'bank', 'financial', 'insurance', 'interest', 'mortgage', 'fintech'},
        'energy': {'oil', 'gas', 'renewable', 'energy', 'solar', 'wind', 'petroleum'},
        'consumer': {'retail', 'consumer', 'discretionary', 'staples', 'ecommerce'},
        'industrial': {'industrial', 'manufacturing', 'aerospace', 'defense', 'transport'},
        'materials': {'materials', 'mining', 'chemical', 'metals', 'steel'},
        'utilities': {'utility', 'electric', 'water', 'power', 'grid'},
        'real_estate': {'reit', 'real estate', 'property', 'estate'},
    }

    def __init__(self, config):
        super().__init__(config)
        self.sentiment_analyzer = SentimentAnalyzer()

    async def classify(self, event: MarketEvent) -> EventClassification:
        """
        Full classification pipeline for a single event.
        """
        text = event.get_text_for_analysis()
        
        # 1. Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze(text)
        
        # 2. Event type detection
        event_type, type_confidence = self._detect_event_type(text, event.tags)
        
        # 3. Impact severity estimation
        impact = self._estimate_impact_severity(text, sentiment, event, type_confidence)
        
        # 4. Direction bias
        direction = self._estimate_direction(text, sentiment, event_type)
        
        # 5. Time horizon
        time_horizon = self._estimate_time_horizon(text, event_type)
        
        # 6. Sector/ticker mapping
        sectors = self._map_to_sectors(text, event.metadata.get('detected_tickers', []))
        tickers = event.metadata.get('detected_tickers', [])
        
        # 7. Breaking news detection
        is_breaking = self._is_breaking_news(event, text)
        
        # 8. Viral detection
        is_viral = event.metadata.get('viral_score', 0) > 100 or 'viral' in event.tags
        
        # 9. Overall confidence
        confidence = self._calculate_confidence(
            type_confidence, sentiment.confidence, impact, len(tickers) > 0
        )
        
        classification = EventClassification(
            event_type=event_type,
            impact_severity=impact,
            direction_bias=direction,
            time_horizon=time_horizon,
            affected_sectors=sectors,
            affected_tickers=tickers,
            keywords=self._extract_key_terms(text),
            confidence=confidence,
            sentiment=sentiment,
            is_breaking=is_breaking,
            is_viral=is_viral,
            classification_notes=self._generate_notes(event_type, impact, direction)
        )
        
        return classification

    async def batch_classify(self, events: List[MarketEvent]) -> List[EventClassification]:
        """
        Classify multiple events with parallel processing.
        """
        # Process concurrently but with controlled concurrency
        from asyncio import Semaphore
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent classifications
        
        async def classify_one(event):
            async with semaphore:
                return await self.classify(event)
        
        tasks = [classify_one(e) for e in events]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and replace with minimal classification
        results = []
        for r in raw_results:
            if isinstance(r, Exception):
                log.error(f"Classification error: {r}")
                # Return minimal classification
                results.append(EventClassification(
                    event_type=EventType.UNKNOWN,
                    impact_severity=ImpactSeverity.MINIMAL,
                    direction_bias=Direction.NEUTRAL,
                    time_horizon=TimeHorizon.UNKNOWN,
                    affected_sectors=[],
                    affected_tickers=[],
                    keywords=[],
                    confidence=0.0,
                    sentiment=SentimentAnalysis(polarity=0, subjectivity=0, confidence=0, emotion_labels=[], key_phrases=[]),
                ))
            else:
                results.append(r)
        return results

    def _detect_event_type(self, text: str, tags: List[str]) -> Tuple[EventType, float]:
        """Detect event type via keyword overlap"""
        text_lower = text.lower()
        
        best_type = EventType.UNKNOWN
        best_score = 0.0
        
        for event_type, keywords in self.EVENT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                score = matches / len(keywords)
                if score > best_score:
                    best_score = score
                    best_type = event_type
        
        # Check tags as additional signal
        if best_score < 0.3 and tags:
            tag_str = ' '.join(tags).lower()
            for event_type, keywords in self.EVENT_KEYWORDS.items():
                if any(kw in tag_str for kw in keywords):
                    best_type = event_type
                    best_score = 0.5
                    break
        
        return best_type, best_score

    def _estimate_impact_severity(
        self, 
        text: str, 
        sentiment: SentimentAnalysis,
        event: MarketEvent,
        type_confidence: float
    ) -> ImpactSeverity:
        """
        Estimate market impact severity (0-5 scale).
        Considers: sentiment strength, source credibility, content length, amplification keywords.
        """
        # Base score from sentiment absolute value
        base_score = abs(sentiment.polarity) * 2.0  # 0-2
        
        # Amplifier keywords add 0-1
        amp_count = sum(1 for amp in self.IMPACT_AMPLIFIERS if amp in text.lower())
        amp_score = min(1.0, amp_count * 0.25)
        
        # Source credibility
        source_bonus = 0.0
        if event.source in (DataSource.NEWS_RSS, DataSource.NEWS_API, DataSource.NEWS_财经):
            source_bonus = 0.3
        elif event.source == DataSource.TWITTER:
            # High follower count increases credibility
            followers = event.metadata.get('followers', 0)
            if followers > 100000:
                source_bonus = 0.2
            elif followers > 10000:
                source_bonus = 0.1
        
        # Viral factor
        viral_bonus = 0.0
        if event.metadata.get('retweets', 0) > 1000:
            viral_bonus = 0.2
        elif event.metadata.get('viral_score', 0) > 100:
            viral_bonus = 0.15
        
        # Event-specific multipliers
        type_multipliers = {
            EventType.EARNINGS: 1.2,
            EventType.MERGER_ACQUISITION: 1.5,
            EventType.REGULATORY: 1.3,
            EventType.MACROECONOMIC: 1.4,
            EventType.GEOPOLITICAL: 1.3,
            EventType.VIRAL_TREND: 1.1,
        }
        type_mult = type_multipliers.get(event.classification.event_type if hasattr(event, 'classification') and event.classification else EventType.UNKNOWN, 1.0)
        
        total_score = (base_score + amp_score + source_bonus + viral_bonus) * type_mult
        total_score = min(3.0, total_score)  # Cap base
        
        # Map to severity
        if total_score >= 2.4:
            return ImpactSeverity.EXTREME
        elif total_score >= 1.8:
            return ImpactSeverity.CRITICAL
        elif total_score >= 1.2:
            return ImpactSeverity.HIGH
        elif total_score >= 0.7:
            return ImpactSeverity.MEDIUM
        elif total_score >= 0.3:
            return ImpactSeverity.LOW
        else:
            return ImpactSeverity.MINIMAL

    def _estimate_direction(self, text: str, sentiment: SentimentAnalysis, event_type: EventType) -> Direction:
        """
        Estimate direction bias from text and sentiment.
        """
        text_lower = text.lower()
        
        # Count bullish/bearish terms
        bullish_count = sum(1 for term in self.BULLISH_TERMS if term in text_lower)
        bearish_count = sum(1 for term in self.BEARISH_TERMS if term in text_lower)
        
        # Weight by sentiment polarity
        polarity_weight = sentiment.polarity  # -1 to 1
        
        # Combine
        score = (bullish_count - bearish_count) * 0.5 + polarity_weight
        
        if score > 0.3:
            return Direction.BULLISH
        elif score < -0.3:
            return Direction.BEARISH
        elif -0.3 <= score <= 0.3:
            return Direction.NEUTRAL
        else:
            return Direction.MIXED

    def _estimate_time_horizon(self, text: str, event_type: EventType) -> TimeHorizon:
        """
        Estimate how quickly the market will price in this event.
        """
        text_lower = text.lower()
        
        # Immediate impact keywords
        immediate_keywords = ['breaking', 'just in', 'now', 'immediate', 'today', 'live']
        if any(kw in text_lower for kw in immediate_keywords):
            return TimeHorizon.IMMEDIATE
        
        # Event-type defaults
        horizon_defaults = {
            EventType.EARNINGS: TimeHorizon.IMMEDIATE,  # After earnings release
            EventType.MERGER_ACQUISITION: TimeHorizon.MEDIUM_TERM,  # Takes time to close
            EventType.REGULATORY: TimeHorizon.MEDIUM_TERM,
            EventType.PRODUCT_LAUNCH: TimeHorizon.SHORT_TERM,  # Product cycle
            EventType.MACROECONOMIC: TimeHorizon.IMMEDIATE,
            EventType.VIRAL_TREND: TimeHorizon.IMMEDIATE,
        }
        
        return horizon_defaults.get(event_type, TimeHorizon.UNKNOWN)

    def _map_to_sectors(self, text: str, tickers: List[str]) -> List[str]:
        """
        Map event to economic sectors using keywords and ticker sector mapping.
        """
        text_lower = text.lower()
        sectors = set()
        
        # Keyword mapping
        for sector, keywords in self.SECTOR_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                sectors.add(sector)
        
        # Ticker-based mapping (simplified - would use actual ticker->sector database)
        sector_by_ticker = {
            'AAPL': 'technology', 'MSFT': 'technology', 'GOOGL': 'technology',
            'AMZN': 'consumer', 'TSLA': 'consumer', 'NVDA': 'technology',
            'JPM': 'finance', 'BAC': 'finance', 'GS': 'finance',
            'XOM': 'energy', 'CVX': 'energy',
            'JNJ': 'healthcare', 'PFE': 'healthcare',
        }
        for ticker in tickers:
            ticker_upper = ticker.upper().replace('$', '')
            if ticker_upper in sector_by_ticker:
                sectors.add(sector_by_ticker[ticker_upper])
        
        return sorted(list(sectors))

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms/phrases from event text"""
        import re
        # Simple extraction: capitalized phrases, numbers with %, $ amounts
        patterns = [
            r'\$[\d,]+\.?\d*[kmb]?',  # Dollar amounts
            r'\d+%',                  # Percentages
            r'\$\w+(?:/\$\w+)?',      # Ticker pairs
            r'[A-Z][a-z]+ [A-Z][a-z]+',  # Proper noun pairs
        ]
        
        key_terms = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            key_terms.extend(matches[:5])  # Limit per pattern
        
        # Also include detected tickers
        tickers = self.extract_tickers(text)
        key_terms.extend(tickers)
        
        return list(set(key_terms))[:20]

    def _is_breaking_news(self, event: MarketEvent, text: str) -> bool:
        """Detect if this is breaking/urgent news"""
        text_lower = text.lower()
        breaking_terms = ['breaking', 'just in', 'alert', 'urgent', 'developing']
        return any(term in text_lower for term in breaking_terms)

    def _calculate_confidence(
        self,
        type_confidence: float,
        sentiment_confidence: float,
        impact: ImpactSeverity,
        has_tickers: bool
    ) -> float:
        """Overall confidence in classification"""
        base = (type_confidence + sentiment_confidence) / 2
        
        # Known tickers increases confidence
        if has_tickers:
            base += 0.15
        
        # Impact severity clarity
        impact_confidence = {
            ImpactSeverity.EXTREME: 0.95,
            ImpactSeverity.CRITICAL: 0.9,
            ImpactSeverity.HIGH: 0.85,
            ImpactSeverity.MEDIUM: 0.75,
            ImpactSeverity.LOW: 0.6,
            ImpactSeverity.MINIMAL: 0.5,
        }
        base = (base + impact_confidence[impact]) / 2
        
        return min(1.0, base)

    def _generate_notes(self, event_type: EventType, impact: ImpactSeverity, direction: Direction) -> str:
        notes = []
        notes.append(f"Type: {event_type.value}")
        notes.append(f"Impact: {impact.value}")
        notes.append(f"Bias: {direction.value}")
        return " | ".join(notes)


class ImpactAnalyzer(BaseEventClassifier):
    """
    Specialized classifier focused solely on impact magnitude.
    Uses more sophisticated analysis including:
    - Source reliability scoring
    - Cross-source validation
    - Historical accuracy tracking
    """
    pass


class TopicCategorizer(BaseEventClassifier):
    """
    Multi-label topic categorization beyond event type.
    Assigns multiple category labels from a controlled vocabulary.
    """
    pass


class SentimentAnalyzer:
    """
    Sentiment analysis using TextBlob or fallback heuristic.
    Provides polarity (-1 to +1) and confidence.
    """

    def __init__(self):
        self.use_textblob = TEXTBLOB_AVAILABLE

    def analyze(self, text: str) -> SentimentAnalysis:
        """
        Perform sentiment analysis on text.
        Returns SentimentAnalysis object.
        """
        if not text:
            return SentimentAnalysis(
                polarity=0.0,
                subjectivity=0.5,
                confidence=0.0,
                emotion_labels=[],
                key_phrases=[]
            )

        if self.use_textblob:
            return self._analyze_textblob(text)
        else:
            return self._analyze_heuristic(text)

    def _analyze_textblob(self, text: str) -> SentimentAnalysis:
        """Use TextBlob for sentiment"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to +1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Extract key phrases (noun phrases)
            key_phrases = list(blob.noun_phrases)[:10]
            
            # Simple emotion detection based on keywords
            emotion_keywords = {
                'fear': ['fear', 'worry', 'concern', 'risk', 'danger', 'warning'],
                'greed': ['surge', 'soar', 'rally', 'boom', 'bullish'],
                'excitement': ['excited', 'amazing', 'incredible', 'breakthrough'],
                'panic': ['crash', 'plunge', 'collapse', 'selloff', 'panic'],
            }
            detected_emotions = []
            for emotion, keywords in emotion_keywords.items():
                if any(kw in text.lower() for kw in keywords):
                    detected_emotions.append(emotion)
            
            # Confidence - longer texts generally more reliable
            word_count = len(text.split())
            confidence = min(1.0, 0.5 + word_count / 200) * (0.7 + subjectivity * 0.3)
            
            return SentimentAnalysis(
                polarity=polarity,
                subjectivity=subjectivity,
                confidence=confidence,
                emotion_labels=detected_emotions,
                key_phrases=key_phrases,
            )
        except Exception as e:
            log.debug(f"TextBlob failed: {e}")
            return self._analyze_heuristic(text)

    def _analyze_heuristic(self, text: str) -> SentimentAnalysis:
        """Simple keyword-based sentiment fallback"""
        text_lower = text.lower()
        
        positive_words = [
            'good', 'great', 'excellent', 'positive', 'up', 'rise', 'gain',
            'profit', 'success', 'strong', 'beat', 'exceed', 'growth',
            'bullish', 'optimistic', 'opportunity', 'benefit', 'advantage',
        ]
        negative_words = [
            'bad', 'terrible', 'negative', 'down', 'fall', 'drop', 'loss',
            'fail', 'weak', 'miss', 'below', 'decline', 'concern',
            'bearish', 'pessimistic', 'risk', 'threat', 'disadvantage',
        ]
        
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        total = pos_count + neg_count
        
        if total == 0:
            polarity = 0.0
            confidence = 0.3
        else:
            polarity = (pos_count - neg_count) / total
            confidence = min(0.9, 0.4 + total / 20)
        
        return SentimentAnalysis(
            polarity=polarity,
            subjectivity=confidence,
            confidence=confidence,
            emotion_labels=[],
            key_phrases=[],
        )

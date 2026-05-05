"""
Base classes and abstractions for Market Intelligence data pipeline.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID
import logging
from collections import defaultdict

from .schemas import (
    MarketEvent,
    EventClassification,
    DataSource,
    EventType,
    ImpactSeverity,
    Direction,
    TimeHorizon,
    SentimentAnalysis,
    MarketIntelligenceConfig,
)

log = logging.getLogger(__name__)


class BaseDataSource(ABC):
    """
    Abstract base class for all data sources (news, social media, APIs).
    
    Implementations must:
    - Connect to the data source
    - Fetch new data since last check
    - Normalize data into MarketEvent objects
    - Handle rate limits and errors gracefully
    """

    def __init__(self, config: MarketIntelligenceConfig):
        self.config = config
        self.source_type: DataSource = DataSource.UNKNOWN
        self.last_fetch: Optional[datetime] = None
        self.error_count = 0
        self.total_events_fetched = 0

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source. Return True on success."""
        pass

    @abstractmethod
    async def fetch_events(self, since: Optional[datetime] = None) -> List[MarketEvent]:
        """
        Fetch events from the source.
        
        Args:
            since: Only fetch events newer than this timestamp
            
        Returns:
            List of MarketEvent objects
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify the data source is accessible."""
        pass

    def mark_fetched(self, count: int):
        """Update fetch statistics"""
        self.last_fetch = datetime.utcnow()
        self.total_events_fetched += count

    def record_error(self):
        """Increment error counter"""
        self.error_count += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get source statistics"""
        return {
            "source": self.source_type.value,
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "total_events": self.total_events_fetched,
            "error_count": self.error_count,
            "health": "ok" if self.error_count < 5 else "degraded",
        }


class BaseEventClassifier(ABC):
    """
    Abstract base class for event classification.
    
    Takes raw MarketEvent and produces EventClassification with:
    - Event type (earnings, M&A, regulatory, etc.)
    - Impact severity (minimal to extreme)
    - Direction bias (bullish/bearish/neutral)
    - Affected tickers and sectors
    - Time horizon for impact
    """

    def __init__(self, config: MarketIntelligenceConfig):
        self.config = config

    @abstractmethod
    async def classify(self, event: MarketEvent) -> EventClassification:
        """
        Classify a market event.
        
        Args:
            event: Raw market event to classify
            
        Returns:
            EventClassification with full analysis
        """
        pass

    @abstractmethod
    async def batch_classify(self, events: List[MarketEvent]) -> List[EventClassification]:
        """Classify multiple events efficiently"""
        pass

    def extract_tickers(self, text: str) -> List[str]:
        """
        Extract stock tickers from text using regex patterns.
        Basic implementation; override for more sophisticated extraction.
        """
        import re
        # Match $TICKER format
        dollar_tickers = re.findall(r'\$([A-Z]{1,5})', text)
        # Match (TICKER) format
        paren_tickers = re.findall(r'\(([A-Z]{1,5})\)', text)
        # Match standalone uppercase 1-5 letter words that look like tickers
        # (avoid matching all-caps words like "THE", "AND", etc.)
        common_words = {'THE', 'AND', 'FOR', 'WITH', 'FROM', 'THIS', 'THAT', 'HAVE', 'WERE', 'WAS', 'HAS', 'HAD'}
        words = re.findall(r'\b([A-Z]{2,5})\b', text)
        word_tickers = [w for w in words if w not in common_words]
        
        all_tickers = set(dollar_tickers + paren_tickers + word_tickers)
        return sorted(list(all_tickers))

    def estimate_impact_from_sentiment(self, sentiment: SentimentAnalysis) -> ImpactSeverity:
        """Estimate impact severity based on sentiment strength"""
        abs_polarity = abs(sentiment.polarity)
        if abs_polarity > 0.8:
            return ImpactSeverity.HIGH
        elif abs_polarity > 0.5:
            return ImpactSeverity.MEDIUM
        elif abs_polarity > 0.3:
            return ImpactSeverity.LOW
        else:
            return ImpactSeverity.MINIMAL


class BaseHistoricalAnalyzer(ABC):
    """
    Abstract base class for historical pattern analysis.
    
    Responsibilities:
    - Store historical events and their outcomes
    - Find similar past events to current ones
    - Calculate statistical outcomes from similar patterns
    - Update pattern database with new results
    """

    def __init__(self, config: MarketIntelligenceConfig):
        self.config = config
        self.patterns: Dict[str, HistoricalPattern] = {}
        self.historical_events: List[Dict[str, Any]] = []

    @abstractmethod
    async def find_similar_patterns(
        self,
        event: MarketEvent,
        classification: EventClassification,
        max_results: int = 5
    ) -> List[HistoricalPattern]:
        """
        Find historical patterns similar to the current event.
        
        Args:
            event: Current market event
            classification: Event classification
            max_results: Maximum patterns to return
            
        Returns:
            List of matching historical patterns, ranked by similarity
        """
        pass

    @abstractmethod
    async def record_outcome(
        self,
        event_id: UUID,
        actual_price_move: float,
        actual_direction: Direction,
        success: bool,
        notes: Optional[str] = None
    ) -> None:
        """
        Record the actual outcome of a predicted event.
        
        Args:
            event_id: ID of the original event
            actual_price_move: % price change realized
            actual_direction: Actual direction price moved
            success: Whether prediction was correct
            notes: Optional notes about the outcome
        """
        pass

    @abstractmethod
    async def build_pattern_database(self) -> None:
        """Construct or refresh the pattern database from historical data."""
        pass

    def similarity_score(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """
        Calculate similarity between two events (0-1).
        Override for domain-specific similarity logic.
        """
        score = 0.0
        
        # Event type match
        if event1.get('event_type') == event2.get('event_type'):
            score += 0.3
        
        # Sector overlap
        sectors1 = set(event1.get('affected_sectors', []))
        sectors2 = set(event2.get('affected_sectors', []))
        if sectors1 and sectors2:
            jaccard = len(sectors1 & sectors2) / len(sectors1 | sectors2)
            score += 0.2 * jaccard
        
        # Sentiment similarity
        sent1 = event1.get('sentiment', {}).get('polarity', 0)
        sent2 = event2.get('sentiment', {}).get('polarity', 0)
        sent_sim = 1.0 - abs(sent1 - sent2)  # 0-1
        score += 0.2 * sent_sim
        
        # Impact severity match
        if event1.get('impact_severity') == event2.get('impact_severity'):
            score += 0.2
        
        # Timestamp recency (more recent = more similar context)
        # Simplified: assume both have 'timestamp' fields
        # Override with more sophisticated time decay
        
        return min(1.0, score)


class BaseOptionsAnalyzer(ABC):
    """
    Abstract base class for options-specific impact analysis.
    
    Translates event classifications into concrete options strategies:
    - Which options (calls or puts) to buy/sell
    - Strike selection logic
    - Expiry timing
    - Position sizing
    - Risk metrics (Greeks exposure)
    """

    def __init__(self, config: MarketIntelligenceConfig):
        self.config = config

    @abstractmethod
    async def analyze_options_impact(
        self,
        event: MarketEvent,
        classification: EventClassification,
        historical_patterns: List[HistoricalPattern],
        current_market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze how event should affect options pricing and strategy.
        
        Returns:
            Dict with keys:
            - iv_impact: expected IV change
            - skew_shift: how smile/skew will change
            - recommended_strategy: str
            - optimal_strikes: List[float]
            - expiry_horizon: str
            - risk_metrics: Dict[str, float]
        """
        pass

    @abstractmethod
    def select_strike_price(
        self,
        ticker: str,
        direction: Direction,
        current_price: float,
        volatility: float,
        target_probability: float = 0.7
    ) -> float:
        """
        Select optimal strike price based on probability targets.
        
        Args:
            ticker: Stock symbol
            direction: Bullish (calls) or Bearish (puts)
            current_price: Current stock price
            volatility: Implied volatility (annualized %)
            target_probability: Desired probability of expiring ITM
            
        Returns:
            Strike price to use
        """
        pass

    def calculate_greeks(
        self,
        option_type: str,  # 'call' or 'put'
        strike: float,
        expiry_days: int,
        current_price: float,
        volatility: float,
        interest_rate: float = 0.05
    ) -> Dict[str, float]:
        """
        Simplified Black-Scholes Greeks calculation.
        For production, use a proper options pricing library.
        """
        import math
        from math import sqrt, exp, log, erf

        if option_type not in ('call', 'put'):
            raise ValueError("option_type must be 'call' or 'put'")

        S = current_price
        K = strike
        T = expiry_days / 365.0
        sigma = volatility
        r = interest_rate

        if T <= 0:
            # Expired
            if option_type == 'call':
                return {'price': max(0, S - K), 'delta': 1.0 if S > K else 0.0}
            else:
                return {'price': max(0, K - S), 'delta': -1.0 if S < K else 0.0}

        d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)

        # Standard normal CDF
        def N(x):
            return 0.5 * (1 + erf(x / sqrt(2)))

        def N_prime(x):
            return exp(-0.5 * x**2) / sqrt(2 * 3.14159)

        if option_type == 'call':
            price = S * N(d1) - K * exp(-r * T) * N(d2)
            delta = N(d1)
        else:
            price = K * exp(-r * T) * N(-d2) - S * N(-d1)
            delta = N(d1) - 1

        gamma = N_prime(d1) / (S * sigma * sqrt(T))
        vega = S * N_prime(d1) * sqrt(T) / 100  # per 1% IV change
        theta = (-S * N_prime(d1) * sigma / (2 * sqrt(T)) - r * K * exp(-r * T) * N(d2)) / 365  # per day

        return {
            'price': price,
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta,
        }


class EventPipeline:
    """
    Orchestrates the full event processing pipeline:
    
    1. Ingest raw events from all sources
    2. Classify events (type, impact, direction)
    3. Retrieve historical patterns
    4. Analyze options implications
    5. Generate trading signals
    6. Record for learning
    """

    def __init__(
        self,
        ingestor: BaseDataSource,
        classifier: BaseEventClassifier,
        historical: BaseHistoricalAnalyzer,
        options_analyzer: BaseOptionsAnalyzer,
        decision_engine: 'DecisionEngine',
        config: MarketIntelligenceConfig,
    ):
        self.ingestor = ingestor
        self.classifier = classifier
        self.historical = historical
        self.options_analyzer = options_analyzer
        self.decision_engine = decision_engine
        self.config = config
        self.processed_events: List[MarketEvent] = []
        self.signals: List[OptionsSignal] = []

    async def run_cycle(self) -> List[OptionsSignal]:
        """
        Execute one full processing cycle.
        
        Returns:
            List of generated trading signals
        """
        log.info("Starting market intelligence cycle")
        
        try:
            # 1. Ingest
            events = await self.ingestor.fetch_events()
            log.info(f"Ingested {len(events)} events from {self.ingestor.source_type}")
            
            if not events:
                return []
            
            # 2. Classify
            classifications = await self.classifier.batch_classify(events)
            for event, classification in zip(events, classifications):
                event.classification = classification
            log.info(f"Classified {len(classifications)} events")
            
            # 3. Historical patterns
            pattern_matches: Dict[UUID, List[HistoricalPattern]] = {}
            for event in events:
                if event.classification and event.classification.confidence >= self.config.min_confidence_threshold:
                    patterns = await self.historical.find_similar_patterns(event, event.classification)
                    pattern_matches[event.event_id] = patterns
            
            # 4. Options analysis (needs market data - mocked for now)
            # In production, fetch real-time data from market data provider
            mock_market_data = await self._fetch_market_data(events)
            options_analysis = {}
            for event in events:
                patterns = pattern_matches.get(event.event_id, [])
                analysis = await self.options_analyzer.analyze_options_impact(
                    event,
                    event.classification,
                    patterns,
                    mock_market_data.get(event.classification.affected_tickers[0] if event.classification.affected_tickers else 'SPY')
                )
                options_analysis[event.event_id] = analysis
            
            # 5. Generate signals using decision engine
            new_signals = await self.decision_engine.generate_signals(
                events,
                classifications,
                pattern_matches,
                options_analysis
            )
            
            self.processed_events.extend(events)
            self.signals.extend(new_signals)
            
            log.info(f"Generated {len(new_signals)} trading signals")
            
            # 6. Learning integration would happen here (if event outcomes tracked)
            
            return new_signals
            
        except Exception as e:
            log.error(f"Pipeline cycle failed: {e}", exc_info=True)
            self.ingestor.record_error()
            return []

    async def _fetch_market_data(self, events: List[MarketEvent]) -> Dict[str, Any]:
        """
        Fetch current market data for affected tickers.
        Placeholder - integrate with real market data provider.
        """
        # Mock data structure
        tickers = set()
        for event in events:
            if event.classification:
                tickers.update(event.classification.affected_tickers)
        
        mock_data = {}
        for ticker in tickers:
            import random
            mock_data[ticker] = {
                'price': random.uniform(50, 500),
                'iv': random.uniform(0.2, 0.8),
                'volume': random.randint(100000, 10000000),
                'bid_ask_spread': random.uniform(0.01, 0.5),
            }
        
        return mock_data

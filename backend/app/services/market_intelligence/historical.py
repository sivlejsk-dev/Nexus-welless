"""
Historical Pattern Matcher - finds similar past events and predicts outcomes.

Stores historical market events with their realized outcomes:
- Price movement (%, absolute)
- Options volume changes (call/put ratio)
- Volatility shifts
- Sector rotation effects

Uses similarity scoring to match current events with historical precedents.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import numpy as np
from uuid import UUID

from .base import BaseHistoricalAnalyzer
from .schemas import (
    HistoricalPattern,
    EventClassification,
    ImpactSeverity,
    Direction,
    TimeHorizon,
    MarketEvent,
)

log = logging.getLogger(__name__)


class HistoricalPatternMatcher(BaseHistoricalAnalyzer):
    """
    Matches current events to historical patterns.
    
    Maintains:
    - Historical events database (in-memory or persistent)
    - Pattern clusters (events that produced similar outcomes)
    - Outcome statistics per pattern
    - Similarity scoring engine
    
    The matcher can operate in two modes:
    1. Offline training: Build pattern database from years of historical data
    2. Online querying: Find matches for new events
    """

    def __init__(self, config):
        super().__init__(config)
        self.event_outcomes: List[Dict[str, Any]] = []
        self.pattern_clusters: Dict[str, List[Dict]] = defaultdict(list)
        self._sim_engine = SimilarityEngine()
        
        # In production, these would be database models
        # For now, in-memory with periodic persistence
        self._outcomes_file = "/tmp/market_intelligence_outcomes.json"

    async def connect(self) -> bool:
        """Load historical data if available"""
        try:
            import json
            import os
            if os.path.exists(self._outcomes_file):
                with open(self._outcomes_file, 'r') as f:
                    data = json.load(f)
                    self.event_outcomes = data.get('outcomes', [])
                    self.pattern_clusters = defaultdict(list, data.get('clusters', {}))
                log.info(f"Loaded {len(self.event_outcomes)} historical outcomes")
            return True
        except Exception as e:
            log.error(f"Failed to load historical data: {e}")
            return False

    async def find_similar_patterns(
        self,
        event: MarketEvent,
        classification: EventClassification,
        max_results: int = 5
    ) -> List[HistoricalPattern]:
        """
        Find historical patterns matching current event.
        
        Algorithm:
        1. Candidate retrieval - find events matching at least 2 of:
           - Same event type
           - Same sector(s)
           - Similar sentiment range
           - Similar magnitude
        2. Score each candidate using multi-factor similarity
        3. Cluster similar outcomes into patterns
        4. Return top N patterns with statistics
        """
        if not self.event_outcomes:
            log.warning("No historical outcomes loaded")
            return []
        
        # Build event signature for matching
        current_signature = {
            'event_type': classification.event_type,
            'sectors': set(classification.affected_sectors),
            'sentiment': classification.sentiment.polarity,
            'impact': classification.impact_severity.value,
            'tickers': set(classification.affected_tickers),
        }
        
        # Score all historical events
        scored_events = []
        for hist_event in self.event_outcomes:
            score = self._sim_engine.calculate_similarity(current_signature, hist_event)
            if score >= self.config.pattern_similarity_threshold:
                scored_events.append((score, hist_event))
        
        # Sort by similarity
        scored_events.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_events:
            return []
        
        # Group into patterns (clusters of similar outcomes)
        patterns = self._cluster_into_patterns(scored_events[:50])  # Top 50 candidates
        
        # Return top N patterns aggregated
        return sorted(patterns, key=lambda p: p.pattern_strength, reverse=True)[:max_results]

    def _cluster_into_patterns(self, scored_events: List[Tuple[float, Dict]]) -> List[HistoricalPattern]:
        """
        Cluster similar events into a pattern with aggregate statistics.
        """
        from collections import defaultdict
        
        # Group by coarse attributes (event_type + sector + impact_range)
        clusters = defaultdict(list)
        
        for score, event in scored_events:
            cluster_key = self._get_cluster_key(event)
            clusters[cluster_key].append((score, event))
        
        patterns = []
        for cluster_key, members in clusters.items():
            if len(members) < self.config.min_pattern_samples:
                continue
            
            # Calculate aggregate statistics
            price_moves = [e.get('actual_price_move', 0) for _, e in members]
            call_put_ratios = [e.get('call_put_ratio', 1.0) for _, e in members]
            direction_counts = defaultdict(int)
            for _, e in members:
                direction_counts[e.get('actual_direction', 'neutral')] += 1
            
            # Dominant direction
            dominant_dir = max(direction_counts, key=direction_counts.get)
            
            # Win rate (success of predictions matching actual direction)
            # In practice, would track prediction vs outcome
            win_rate = direction_counts.get(dominant_dir, 0) / len(members)
            
            # Average return (simplified - would use actual P&L)
            avg_return = np.mean(price_moves) if price_moves else 0.0
            
            pattern = HistoricalPattern(
                pattern_id=UUID(hashlib.md5(cluster_key.encode()).hexdigest()),
                name=f"Pattern: {cluster_key}",
                description=f"Historical pattern for {cluster_key} events",
                event_signature=self._parse_cluster_key(cluster_key),
                matching_events=[self._summarize_event(e) for _, e in members[:20]],
                avg_price_move=np.mean(price_moves) if price_moves else 0.0,
                avg_iv_change=np.mean([e.get('iv_change', 0) for _, e in members]) if members else 0.0,
                call_put_ratio=np.mean(call_put_ratios) if call_put_ratios else 1.0,
                typical_time_horizon=TimeHorizon.SHORT_TERM,  # Would infer from outcomes
                sample_size=len(members),
                win_rate=win_rate,
                avg_return=avg_return,
                max_drawdown=min(price_moves) if price_moves else 0.0,
                pattern_strength=np.mean([s for s, _ in members]),
                recency_weight=self._calculate_recency_weight(members),
            )
            patterns.append(pattern)
        
        return patterns

    def _get_cluster_key(self, event: Dict) -> str:
        """Generate string key for clustering"""
        event_type = event.get('event_type', 'unknown')
        sectors = '-'.join(sorted(event.get('affected_sectors', []))) or 'none'
        severity = event.get('impact_severity', 'unknown')
        return f"{event_type}|{sectors}|{severity}"

    def _parse_cluster_key(self, key: str) -> Dict[str, Any]:
        """Parse cluster key back to signature"""
        parts = key.split('|')
        return {
            'event_type': parts[0],
            'sectors': parts[1].split('-') if parts[1] != 'none' else [],
            'impact_range': [parts[2]] if parts[2] != 'unknown' else [],
        }

    def _summarize_event(self, event: Dict) -> Dict[str, Any]:
        """Create condensed summary of historical event"""
        return {
            'date': event.get('date', ''),
            'event_type': event.get('event_type'),
            'ticker': event.get('ticker', ''),
            'price_move': event.get('actual_price_move', 0),
            'success': event.get('success', False),
        }

    def _calculate_recency_weight(self, members: List) -> float:
        """
        Calculate weight favor recent patterns (0-1).
        More recent = higher weight.
        """
        if not members:
            return 0.5
        
        # Extract years (simplified)
        current_year = datetime.now().year
        years = []
        for _, event in members:
            date_str = event.get('date', '')
            try:
                year = int(date_str[:4]) if date_str else current_year
                years.append(year)
            except:
                years.append(current_year)
        
        age_factor = 1.0 - ((current_year - np.mean(years)) / 10.0)  # 10-year half-life
        return max(0.1, min(1.0, age_factor))

    async def record_outcome(
        self,
        event_id: UUID,
        actual_price_move: float,
        actual_direction: Direction,
        success: bool,
        notes: Optional[str] = None
    ) -> None:
        """
        Record actual market outcome for a predicted event.
        
        This data becomes part of the historical database for future pattern matching.
        """
        # Find the event in our processed list
        event = next((e for e in self.processed_events if e.event_id == event_id), None)
        if not event:
            log.warning(f"Event {event_id} not found for outcome recording")
            return
        
        outcome = {
            'event_id': str(event_id),
            'date': datetime.utcnow().isoformat(),
            'event_type': event.classification.event_type.value if event.classification else 'unknown',
            'affected_sectors': event.classification.affected_sectors if event.classification else [],
            'affected_tickers': event.classification.affected_tickers if event.classification else [],
            'sentiment': event.classification.sentiment.polarity if event.classification else 0,
            'impact_severity': event.classification.impact_severity.value if event.classification else 'minimal',
            'actual_price_move': actual_price_move,
            'actual_direction': actual_direction.value,
            'success': success,
            'notes': notes or '',
        }
        
        self.event_outcomes.append(outcome)
        
        # Optionally persist
        self._persist_outcomes()
        
        log.info(f"Recorded outcome for event {event_id}: move={actual_price_move:.2%}, success={success}")

    async def build_pattern_database(self) -> None:
        """
        Build pattern database from accumulated historical outcomes.
        
        This is an offline process that analyzes all outcomes to identify
        statistically significant patterns, then saves them for fast lookup.
        """
        log.info("Building pattern database from historical outcomes...")
        
        # This would typically run periodically (daily/weekly)
        # For now, just ensure data is loaded
        if not self.event_outcomes:
            log.warning("No historical outcomes to process")
            return
        
        # Re-cluster all data
        scored = [(1.0, e) for e in self.event_outcomes]  # All events get score 1 for now
        patterns = self._cluster_into_patterns(scored)
        
        log.info(f"Built {len(patterns)} historical patterns from {len(self.event_outcomes)} outcomes")

    def _persist_outcomes(self) -> None:
        """Save outcomes to disk (simple JSON; use DB in production)"""
        try:
            import json
            data = {
                'outcomes': self.event_outcomes[-5000:],  # Keep last 5k to limit size
                'clusters': {k: v for k, v in self.pattern_clusters.items()},
            }
            with open(self._outcomes_file, 'w') as f:
                json.dump(data, f, default=str)
        except Exception as e:
            log.error(f"Failed to persist outcomes: {e}")


class SimilarityEngine:
    """
    Computes multi-factor similarity between events.
    
    Factors:
    - Event type match (30%)
    - Sector overlap (20%)
    - Sentiment similarity (20%)
    - Impact severity (15%)
    - Source similarity (10%)
    - Ticker overlap (5%)
    """

    def __init__(self):
        self.weights = {
            'event_type': 0.30,
            'sector_overlap': 0.20,
            'sentiment': 0.20,
            'impact': 0.15,
            'source': 0.10,
            'ticker': 0.05,
        }

    def calculate_similarity(self, sig1: Dict, sig2: Dict) -> float:
        """
        Compute weighted similarity score (0-1).
        """
        score = 0.0
        
        # Event type
        if sig1.get('event_type') == sig2.get('event_type'):
            score += self.weights['event_type']
        
        # Sector overlap (Jaccard)
        s1 = set(sig1.get('sectors', []))
        s2 = set(sig2.get('sectors', []))
        if s1 and s2:
            jaccard = len(s1 & s2) / len(s1 | s2)
            score += self.weights['sector_overlap'] * jaccard
        
        # Sentiment similarity (continuous 0-1)
        sent1 = sig1.get('sentiment', 0)
        sent2 = sig2.get('sentiment', 0)
        sent_sim = 1.0 - abs(sent1 - sent2)  # Perfect match = 1, opposite = 0
        score += self.weights['sentiment'] * sent_sim
        
        # Impact severity match
        if sig1.get('impact_severity') == sig2.get('impact_severity'):
            score += self.weights['impact']
        
        # Source similarity
        src1 = sig1.get('source', DataSource.UNKNOWN)
        src2 = sig2.get('source', DataSource.UNKNOWN)
        if src1 == src2:
            score += self.weights['source']
        
        # Ticker overlap at least partial
        t1 = set(sig1.get('tickers', []))
        t2 = set(sig2.get('tickers', []))
        if t1 and t2:
            overlap = len(t1 & t2) / max(len(t1), len(t2))
            score += self.weights['ticker'] * overlap
        
        return score


class OutcomeAnalyzer:
    """
    Analyzes historical pattern outcomes to derive insights.
    
    Computes:
    - Precision/recall of pattern-based predictions
    - Optimal holding periods
    - Risk-adjusted returns (Sharpe/Sortino)
    - Regime-dependent performance
    """
    
    def __init__(self):
        self.outcomes: List[Dict] = []
    
    def add_outcome(self, outcome: Dict):
        self.outcomes.append(outcome)
    
    def analyze_pattern(self, pattern_name: str) -> Dict[str, Any]:
        """Statistical analysis of a pattern's historical performance"""
        pattern_outs = [o for o in self.outcomes if o.get('pattern') == pattern_name]
        
        if not pattern_outs:
            return {}
        
        returns = [o.get('return', 0) for o in pattern_outs]
        
        return {
            'count': len(pattern_outs),
            'mean_return': np.mean(returns),
            'std_return': np.std(returns),
            'win_rate': sum(1 for r in returns if r > 0) / len(returns),
            'sharpe': np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0,
            'max_return': max(returns),
            'max_drawdown': min(returns),
            'recent_performance': np.mean(returns[-10:]) if len(returns) >= 10 else np.mean(returns),
        }

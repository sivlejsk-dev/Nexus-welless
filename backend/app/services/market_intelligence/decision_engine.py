"""
Decision Engine - aggregates multiple factors into trading signals.

Combines:
- News impact score
- Social sentiment
- Historical pattern matching
- Volatility skew analysis
- Liquidity metrics

Produces weighted composite scores and final options signals.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from .base import BaseDataSource
from .schemas import (
    MarketEvent,
    EventClassification,
    HistoricalPattern,
    OptionsSignal,
    Direction,
    ImpactSeverity,
    DataSource,
    MarketIntelligenceConfig,
)

log = logging.getLogger(__name__)


class SignalStrength(str, Enum):
    """Signal confidence levels"""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class FactorScore:
    """Score from a single factor"""
    factor_name: str
    score: float  # -1 to +1
    weight: float
    confidence: float  # 0-1
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def weighted_score(self) -> float:
        """Apply confidence weighting"""
        return self.score * self.weight * self.confidence


@dataclass
class CompositeSignal:
    """Aggregated signal before finalization"""
    ticker: str
    direction: Direction
    total_score: float  # -1 to +1
    factor_scores: List[FactorScore]
    raw_confidence: float
    adjusted_confidence: float
    supports: List[str]
    contradicts: List[str]


class DecisionEngine:
    """
    Aggregates all analysis factors into final trading signals.
    
    Weights (configurable):
    - News impact (30%): severity, urgency, source credibility
    - Social sentiment (25%): viral metrics, retail sentiment
    - Historical patterns (30%): similarity-weighted past outcomes
    - Technical skew (10%): options flow, volatility structure
    - Liquidity (5%): ability to enter/exit positions
    
    Produces OptionsSignal objects with actionable trade recommendations.
    """

    def __init__(self, config: MarketIntelligenceConfig):
        self.config = config
        self.weights = config.weights
        self.signal_history: List[OptionsSignal] = []
        self.performance_tracker = PerformanceTracker()
        
        # Signal thresholds
        self.min_signal_score = 0.4  # Minimum for actionable signal
        self.max_signals_per_ticker = 2

    async def generate_signals(
        self,
        events: List[MarketEvent],
        classifications: List[EventClassification],
        pattern_matches: Dict[UUID, List[HistoricalPattern]],
        options_analysis: Dict[UUID, Dict[str, Any]]
    ) -> List[OptionsSignal]:
        """
        Generate options trading signals from analyzed events.
        
        Pipeline:
        1. Filter low-confidence events
        2. Calculate factor scores per event
        3. Aggregate signals by ticker
        4. Generate final trading recommendations
        5. Enforce risk limits
        """
        signals = []
        
        # Process each classified event
        for event, classification in zip(events, classifications):
            if classification.confidence < self.config.min_confidence_threshold:
                continue
                
            # Skip if no tickers identified
            if not classification.affected_tickers:
                continue
            
            # Gather factor scores
            factor_scores = await self._calculate_factor_scores(
                event, classification, 
                pattern_matches.get(event.event_id, []),
                options_analysis.get(event.event_id, {})
            )
            
            # Compute composite signal
            composite = self._compute_composite(factor_scores)
            
            # Generate one signal per affected ticker
            for ticker in classification.affected_tickers:
                signal = await self._create_signal(
                    ticker=ticker,
                    event=event,
                    classification=classification,
                    composite=composite,
                    options_data=options_analysis.get(event.event_id, {})
                )
                if signal:
                    signals.append(signal)
        
        # Deduplicate and rank by confidence
        signals = self._deduplicate_and_rank(signals)
        
        # Enforce limits
        signals = self._apply_risk_limits(signals)
        
        self.signal_history.extend(signals)
        log.info(f"Generated {len(signals)} trading signals")
        return signals

    async def _calculate_factor_scores(
        self,
        event: MarketEvent,
        classification: EventClassification,
        patterns: List[HistoricalPattern],
        options_data: Dict[str, Any]
    ) -> List[FactorScore]:
        """
        Calculate individual factor contributions.
        """
        scores = []
        
        # 1. News Impact Factor (30%)
        news_factor = self._score_news_impact(event, classification)
        scores.append(news_factor)
        
        # 2. Social Sentiment Factor (25%)
        social_factor = self._score_social_sentiment(event, classification)
        scores.append(social_factor)
        
        # 3. Historical Pattern Factor (30%)
        if patterns:
            hist_factor = self._score_historical_patterns(patterns, classification)
            scores.append(hist_factor)
        else:
            # Neutral score with very low confidence
            scores.append(FactorScore(
                factor_name="historical_patterns",
                score=0.0,
                weight=self.weights.get('historical_pattern', 0.30),
                confidence=0.1,
                details={'reason': 'no_similar_patterns'}
            ))
        
        # 4. Volatility Skew Factor (10%)
        if options_data:
            vol_factor = self._score_volatility_skew(options_data)
            scores.append(vol_factor)
        else:
            scores.append(FactorScore(
                factor_name="volatility_skew",
                score=0.0,
                weight=self.weights.get('volatility_skew', 0.10),
                confidence=0.2,
                details={'reason': 'no_options_data'}
            ))
        # 5. Liquidity Factor (5%)
        liq_factor = self._score_liquidity(event, options_data)
        scores.append(liq_factor)
        
        return scores

    def _score_news_impact(self, event: MarketEvent, classification: EventClassification) -> FactorScore:
        """
        Score news impact based on source, urgency, and classification.
        """
        base_score = 0.0
        details = {}
        
        # Source credibility
        source_scores = {
            DataSource.NEWS_RSS: 0.8,
            DataSource.NEWS_API: 0.8,
            DataSource.NEWS_财经: 0.7,
            DataSource.TWITTER: 0.4,
            DataSource.REDDIT: 0.3,
            DataSource.STOCKTWITS: 0.3,
            DataSource.SENTIMENT_API: 0.5,
        }
        source_bonus = source_scores.get(event.source, 0.2)
        
        # Impact magnitude from classification
        impact_scores = {
            ImpactSeverity.EXTREME: 1.0,
            ImpactSeverity.CRITICAL: 0.9,
            ImpactSeverity.HIGH: 0.7,
            ImpactSeverity.MEDIUM: 0.4,
            ImpactSeverity.LOW: 0.2,
            ImpactSeverity.MINIMAL: 0.0,
        }
        impact_score = impact_scores.get(classification.impact_severity, 0.0)
        
        # Urgency/broadcast nature
        urgency_bonus = 0.2 if classification.is_breaking else 0.0
        viral_bonus = 0.1 if classification.is_viral else 0.0
        
        # Direction alignment (more extreme = higher score)
        dir_score = {
            Direction.BULLISH: 0.3 if classification.sentiment.polarity > 0 else -0.3,
            Direction.BEARISH: 0.3 if classification.sentiment.polarity < 0 else -0.3,
            Direction.NEUTRAL: 0.0,
            Direction.MIXED: 0.0,
        }.get(classification.direction_bias, 0.0)
        
        # Combine
        raw_score = (source_bonus * 0.2 + impact_score * 0.5 + dir_score * 0.3 + urgency_bonus + viral_bonus)
        # Normalize to -1 to +1
        normalized = max(-1.0, min(1.0, raw_score))
        
        details = {
            'source_score': source_bonus,
            'impact_score': impact_score,
            'direction_score': dir_score,
            'urgency_bonus': urgency_bonus,
            'viral_bonus': viral_bonus,
        }
        
        return FactorScore(
            factor_name="news_impact",
            score=normalized,
            weight=self.weights.get('news_impact', 0.30),
            confidence=classification.confidence,
            details=details
        )

    def _score_social_sentiment(self, event: MarketEvent, classification: EventClassification) -> FactorScore:
        """
        Score social media sentiment impact.
        Considers: viral spread, engagement, influencer amplification.
        """
        score = 0.0
        details = {}
        
        if event.source in (DataSource.TWITTER, DataSource.REDDIT, DataSource.STOCKTWITS):
            metadata = event.metadata
            
            # Viral multiplier
            viral_score = metadata.get('viral_score', metadata.get('retweets', 0) * 2 + metadata.get('likes', 0))
            viral_norm = min(1.0, viral_score / 10000)  # Normalize 0-10k engagement
            score += viral_norm * 0.4
            
            # Social sentiment polarity
            sentiment_polarity = classification.sentiment.polarity
            score += sentiment_polarity * 0.4
            
            # Source amplification (follower count)
            followers = metadata.get('followers', 0)
            influence = min(0.2, followers / 1000000)  # Cap at 0.2 for 1M+ followers
            score += influence
            
            details = {
                'viral_score': viral_score,
                'viral_norm': viral_norm,
                'sentiment_polarity': sentiment_polarity,
                'follower_influence': influence,
            }
        else:
            # Not a social source - minimal contribution
            score = 0.0
            details = {'reason': 'non-social_source'}
        
        return FactorScore(
            factor_name="social_sentiment",
            score=max(-1.0, min(1.0, score)),
            weight=self.weights.get('social_sentiment', 0.25),
            confidence=classification.sentiment.confidence,
            details=details
        )

    def _score_historical_patterns(
        self, 
        patterns: List[HistoricalPattern], 
        classification: EventClassification
    ) -> FactorScore:
        """
        Score based on historical pattern matches.
        Uses pattern strength and historical win rate.
        """
        if not patterns:
            return FactorScore("historical_patterns", 0.0, 0.30, 0.0, {})
        
        # Weight by pattern strength and similarity
        weighted_scores = []
        total_weight = 0.0
        
        for pattern in patterns:
            base_direction = 1.0 if pattern.avg_price_move > 0 else -1.0
            magnitude = abs(pattern.avg_price_move)
            
            # Pattern-level score
            pattern_score = base_direction * min(1.0, magnitude / 5.0)  # Normalize to ±1
            
            weight = pattern.pattern_strength * pattern.win_rate * min(1.0, pattern.sample_size / 20)
            weighted_scores.append(pattern_score * weight)
            total_weight += weight
        
        if total_weight > 0:
            composite_score = sum(weighted_scores) / total_weight
        else:
            composite_score = 0.0
        
        # Confidence from pattern quality
        avg_confidence = np.mean([p.pattern_strength for p in patterns])
        
        details = {
            'pattern_count': len(patterns),
            'avg_strength': avg_confidence,
            'avg_win_rate': np.mean([p.win_rate for p in patterns]),
            'total_weight': total_weight,
        }
        
        return FactorScore(
            factor_name="historical_patterns",
            score=composite_score,
            weight=self.weights.get('historical_pattern', 0.30),
            confidence=avg_confidence,
            details=details
        )

    def _score_volatility_skew(self, options_data: Dict[str, Any]) -> FactorScore:
        """
        Score based on options skew and flow anomalies.
        """
        skew_shift = options_data.get('skew_shift', 0.0)
        iv_impact = options_data.get('iv_impact', 0.0)
        
        # Directional bias from skew
        # Positive skew = calls expensive → market bullish; Negative = puts expensive → bearish
        skew_direction = np.sign(skew_shift)
        
        # Magnitude of skew anomaly (standard deviations from normal)
        skew_magnitude = abs(skew_shift)
        
        score = skew_direction * min(1.0, skew_magnitude * 2)  # Amplify strong skews
        
        details = {
            'skew_shift': skew_shift,
            'iv_impact': iv_impact,
        }
        
        return FactorScore(
            factor_name="volatility_skew",
            score=score,
            weight=self.weights.get('volatility_skew', 0.10),
            confidence=0.7,  # Options data typically high quality
            details=details
        )

    def _score_liquidity(self, event: MarketEvent, options_data: Dict[str, Any]) -> FactorScore:
        """
        Score based on liquidity/ability to execute trade.
        """
        # Default moderate liquidity
        score = 0.5
        confidence = 0.5
        
        # If involving SPY/QQQ, high liquidity
        tickers = [t.upper() for t in (event.classification.affected_tickers if event.classification else [])]
        liquid_tickers = {'SPY', 'QQQ', 'IWM', 'DIA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'}
        
        if any(t in liquid_tickers for t in tickers):
            score = 0.8
            confidence = 0.8
        
        # Options-specific liquidity
        if options_data and options_data.get('liquidity_risk', 1.0) < 0.3:
            score = 0.9
            confidence = 0.9
        elif options_data and options_data.get('liquidity_risk', 1.0) > 0.7:
            score = 0.3
            confidence = 0.6
        
        details = {
            'ticker_liquidity': any(t in liquid_tickers for t in tickers),
            'options_liquidity': options_data.get('liquidity_risk', 'unknown'),
        }
        
        return FactorScore(
            factor_name="liquidity",
            score=score,
            weight=self.weights.get('liquidity', 0.05),
            confidence=confidence,
            details=details
        )

    def _compute_composite(self, factor_scores: List[FactorScore]) -> CompositeSignal:
        """
        Aggregate weighted scores into composite signal.
        """
        if not factor_scores:
            return CompositeSignal(
                ticker="", direction=Direction.NEUTRAL, total_score=0.0,
                factor_scores=[], raw_confidence=0.0, adjusted_confidence=0.0,
                supports=[], contradicts=[]
            )
        
        # Weighted sum
        total_weighted = sum(fs.weighted_score for fs in factor_scores)
        total_weights = sum(fs.weight for fs in factor_scores)
        
        if total_weights > 0:
            composite_score = total_weighted / total_weights
        else:
            composite_score = 0.0
        
        # Confidence weighted average
        confidences = [fs.confidence for fs in factor_scores]
        raw_confidence = np.mean(confidences) if confidences else 0.0
        
        # Adjust confidence by score magnitude (more extreme signals often more credible)
        magnitude_bonus = abs(composite_score) * 0.2
        adjusted_confidence = min(1.0, raw_confidence + magnitude_bonus)
        
        # Determine direction
        if composite_score > 0.1:
            direction = Direction.BULLISH
        elif composite_score < -0.1:
            direction = Direction.BEARISH
        else:
            direction = Direction.NEUTRAL
        
        # Extract supporting/contradicting factors
        supports = [fs.factor_name for fs in factor_scores if fs.score > 0.2]
        contradicts = [fs.factor_name for fs in factor_scores if fs.score < -0.2]
        
        ticker = factor_scores[0].details.get('ticker', 'SPY') if factor_scores and factor_scores[0].details else 'SPY'
        
        return CompositeSignal(
            ticker=ticker,
            direction=direction,
            total_score=composite_score,
            factor_scores=factor_scores,
            raw_confidence=raw_confidence,
            adjusted_confidence=adjusted_confidence,
            supports=supports,
            contradicts=contradicts,
        )

    async def _create_signal(
        self,
        ticker: str,
        event: MarketEvent,
        classification: EventClassification,
        composite: CompositeSignal,
        options_data: Dict[str, Any]
    ) -> Optional[OptionsSignal]:
        """
        Create final OptionsSignal from composite analysis.
        """
        # Skip neutral signals
        if composite.total_score < self.min_signal_score and composite.total_score > -self.min_signal_score:
            return None
        
        # Enforce max signals per ticker
        recent_signals = [s for s in self.signal_history[-20:] if s.ticker == ticker]
        if len(recent_signals) >= self.max_signals_per_ticker:
            log.debug(f"Skipping signal for {ticker}: limit reached")
            return None
        
        # Direction based on composite score
        direction = composite.direction
        
        # Extract strategy from options_data
        strategy = options_data.get('recommended_strategy', 'Unknown')
        risk_metrics = options_data.get('risk_metrics', {})
        
        # Confidence (adjusted by ticker-specific factors)
        base_conf = composite.adjusted_confidence
        # Reduce confidence if ticker is highly volatile
        ticker_volatility_adjustment = {
            'TSLA': -0.1,
            'NVDA': -0.05,
            'AAPL': 0.0,
            'SPY': 0.05,  # ETF = more reliable
        }.get(ticker.upper(), 0.0)
        final_confidence = max(0.1, min(0.95, base_conf + ticker_volatility_adjustment))
        
        # Calculate composite weights for signal metadata
        historical_similarity = next(
            (fs.weighted_score for fs in composite.factor_scores if fs.factor_name == "historical_patterns"),
            0.0
        )
        social_weight = next(
            (fs.weighted_score for fs in composite.factor_scores if fs.factor_name == "social_sentiment"),
            0.0
        )
        news_weight = next(
            (fs.weighted_score for fs in composite.factor_scores if fs.factor_name == "news_impact"),
            0.0
        )
        
        signal = OptionsSignal(
            event_id=event.event_id,
            ticker=ticker,
            direction=direction,
            confidence=final_confidence,
            recommendation=strategy,
            target_strike=options_data.get('optimal_strikes', [None])[0] if options_data.get('optimal_strikes') else None,
            target_expiry=event.published_at.strftime('%Y-%m-%d') if event.published_at else None,
            expected_return=risk_metrics.get('expected_value_pct', 0) / 100,
            max_loss=risk_metrics.get('max_loss_pct', 0.05),
            contributing_factors=[
                {'factor': fs.factor_name, 'score': fs.score, 'weight': fs.weight}
                for fs in composite.factor_scores
            ],
            historical_similarity=abs(historical_similarity),
            sentiment_weight=abs(social_weight),
            news_urgency=abs(news_weight),
            implied_volatility_impact=options_data.get('iv_impact', 0.0),
            time_decay_risk=risk_metrics.get('greeks', {}).get('theta', 0.0),
            liquidity_risk=risk_metrics.get('risk_level', 3) / 5.0,
        )
        
        return signal

    def _deduplicate_and_rank(self, signals: List[OptionsSignal]) -> List[OptionsSignal]:
        """
        Remove duplicates (same ticker, similar direction) and rank by confidence.
        """
        # Keep highest confidence signal per ticker+direction
        seen = {}
        for signal in signals:
            key = (signal.ticker.upper(), signal.direction.value)
            if key not in seen or signal.confidence > seen[key].confidence:
                seen[key] = signal
        
        unique_signals = list(seen.values())
        
        # Rank by confidence * expected return
        ranked = sorted(
            unique_signals,
            key=lambda s: s.confidence * abs(s.expected_return or 0),
            reverse=True
        )
        
        return ranked

    def _apply_risk_limits(self, signals: List[OptionsSignal]) -> List[OptionsSignal]:
        """
        Enforce risk management limits.
        """
        limited = []
        total_exposure = 0.0
        
        for signal in signals:
            position_size = signal.max_loss or 0.05
            
            # Check portfolio-level limit (simplified - would query account)
            if total_exposure + position_size > self.config.max_position_size_pct:
                continue
                
            limited.append(signal)
            total_exposure += position_size
        
        # Also cap by configured daily limit
        return limited[:self.config.max_daily_signals]


class PerformanceTracker:
    """
    Track signal performance over time for adaptive weighting.
    
    Metrics:
    - Win rate by event type
    - Win rate by source
    - Sharpe ratio of signals
    - Calibration (do confidence scores match realized probabilities?)
    """
    
    def __init__(self):
        self.signals: List[OptionsSignal] = []
        self.outcomes: Dict[UUID, Dict] = {}
        
    def record_signal(self, signal: OptionsSignal):
        self.signals.append(signal)
    
    def record_outcome(self, signal_id: UUID, realized_return: float, success: bool):
        self.outcomes[signal_id] = {
            'return': realized_return,
            'success': success,
        }
    
    def get_factor_performance(self) -> Dict[str, Dict[str, float]]:
        """Calculate win rates and returns by factor attribute"""
        # Would analyze by event type, source, etc.
        return {}
    
    def recalibrate_weights(self) -> Dict[str, float]:
        """Adjust factor weights based on historical performance"""
        # Placeholder - would use Bayesian optimization or ML
        return {}

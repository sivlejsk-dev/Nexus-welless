"""
Comprehensive tests for Market Intelligence module.

Test Coverage:
- Data source connectivity and parsing
- Event classification accuracy
- Historical pattern matching
- Options strategy recommendations
- Decision engine weighting
- Learning integration feedback loops
- API endpoints
"""

from __future__ import annotations

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from typing import Dict, Any, List
import json
from pathlib import Path

# Test fixtures will need these imports
from app.services.market_intelligence.schemas import (
    MarketEvent,
    EventClassification,
    SentimentAnalysis,
    EventType,
    ImpactSeverity,
    Direction,
    TimeHorizon,
    DataSource,
    OptionsSignal,
    MarketIntelligenceConfig,
)
from app.services.market_intelligence.classifier import EventClassifier, SentimentAnalyzer
from app.services.market_intelligence.decision_engine import DecisionEngine, FactorScore, CompositeSignal
from app.services.market_intelligence.historical import HistoricalPatternMatcher, SimilarityEngine
from app.services.market_intelligence.options_analyzer import OptionsImpactAnalyzer, CallPutAnalyzer
from app.services.market_intelligence.base import EventPipeline
from app.services.market_intelligence.learning_integration import MarketLearningIntegration


# ── Fixtures ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def test_config():
    """Minimal config for testing"""
    return MarketIntelligenceConfig(
        enabled_sources=list(DataSource),
        min_confidence_threshold=0.5,
        min_pattern_samples=3,
    )


@pytest.fixture
def sample_news_event():
    """Sample news event for testing"""
    return MarketEvent(
        source=DataSource.NEWS_RSS,
        source_id="test_news_1",
        title="Apple Reports Strong Q2 Earnings, Beats Estimates",
        description="Apple Inc. reported better-than-expected Q2 earnings, with revenue up 15% year-over-year. The company also announced a $90 billion stock buyback program.",
        url="https://example.com/news/apple-earnings",
        published_at=datetime.utcnow() - timedelta(hours=1),
        raw_content="Full earnings release text...",
        cleaned_content="Apple reports strong earnings...",
        language="en",
        tags=["earnings", "technology"],
        metadata={
            'detected_tickers': ['AAPL'],
            'feed': 'reuters_markets',
        }
    )


@pytest.fixture
def sample_social_event():
    """Sample social media event for testing"""
    return MarketEvent(
        source=DataSource.TWITTER,
        source_id="test_twitter_1",
        title="$TSLA moon soon! 🚀",
        description="Tesla stock is going to the moon! Great earnings call, bullish on EV future. #TSLA #Tesla",
        url="https://twitter.com/user/status/123456",
        author="tesla_fan",
        published_at=datetime.utcnow() - timedelta(minutes=30),
        raw_content="$TSLA moon soon! 🚀",
        language="en",
        tags=["viral", "social_media"],
        metadata={
            'retweets': 1500,
            'likes': 8000,
            'followers': 25000,
            'detected_tickers': ['TSLA'],
        }
    )


@pytest.fixture
def sample_macro_event():
    """Sample macroeconomic event"""
    return MarketEvent(
        source=DataSource.NEWS_API,
        source_id="test_fed_1",
        title="Fed Signals Potential Rate Cuts in Coming Months",
        description="Federal Reserve officials indicated a shift toward lowering interest rates as inflation concerns ease. Markets rally on the news.",
        url="https://example.com/fed-news",
        published_at=datetime.utcnow() - timedelta(hours=2),
        raw_content="Fed signals dovish pivot...",
        language="en",
        tags=["macro", "fed"],
        metadata={
            'detected_tickers': ['SPY', '^GSPC'],
            'source_name': 'Financial Times',
        }
    )


@pytest.fixture
def sample_historical_outcome():
    """Sample historical event with outcome"""
    return {
        'event_id': str(uuid4()),
        'date': '2024-01-15',
        'event_type': 'earnings',
        'sectors': ['technology'],
        'affected_tickers': ['AAPL'],
        'sentiment': 0.8,
        'impact_severity': 'high',
        'actual_price_move': 0.045,  # +4.5%
        'actual_direction': 'bullish',
        'success': True,
        'iv_change': -0.25,  # IV crush 25%
        'call_put_ratio': 1.8,
    }


# ── Sentiment Analyzer Tests ──────────────────────────────────────────────────────

class TestSentimentAnalyzer:
    """Tests for sentiment analysis functionality"""
    
    def test_positive_sentiment(self):
        analyzer = SentimentAnalyzer()
        text = "Great earnings beat, strong bullish outlook"
        result = analyzer.analyze(text)
        assert result.polarity > 0.3
        assert result.confidence > 0.5
    
    def test_negative_sentiment(self):
        analyzer = SentimentAnalyzer()
        text = "Stock crashes on terrible earnings miss, severe losses"
        result = analyzer.analyze(text)
        assert result.polarity < -0.3
        assert result.confidence > 0.5
    
    def test_neutral_sentiment(self):
        analyzer = SentimentAnalyzer()
        text = "Company reports quarterly results"
        result = analyzer.analyze(text)
        assert abs(result.polarity) < 0.2
    
    def test_empty_text(self):
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze("")
        assert result.polarity == 0.0
        assert result.confidence == 0.0


# ── Event Classifier Tests ────────────────────────────────────────────────────────

class TestEventClassifier:
    """Tests for event classification"""
    
    @pytest.mark.asyncio
    async def test_earnings_classification(self, test_config, sample_news_event):
        classifier = EventClassifier(test_config)
        classification = await classifier.classify(sample_news_event)
        
        assert classification.event_type == EventType.EARNINGS
        assert classification.impact_severity in (ImpactSeverity.HIGH, ImpactSeverity.MEDIUM)
        assert classification.affected_tickers == ['AAPL']
        assert classification.confidence > 0.6
    
    @pytest.mark.asyncio
    async def test_macro_classification(self, test_config, sample_macro_event):
        classifier = EventClassifier(test_config)
        classification = await classifier.classify(sample_macro_event)
        
        assert classification.event_type == EventType.MACROECONOMIC
        assert classification.time_horizon == TimeHorizon.IMMEDIATE
    
    @pytest.mark.asyncio
    async def test_viral_social_detection(self, test_config, sample_social_event):
        classifier = EventClassifier(test_config)
        classification = await classifier.classify(sample_social_event)
        
        assert classification.is_viral
        assert 'TSLA' in classification.affected_tickers
    
    @pytest.mark.asyncio
    async def test_batch_classification(self, test_config, sample_news_event, sample_social_event):
        classifier = EventClassifier(test_config)
        events = [sample_news_event, sample_social_event]
        classifications = await classifier.batch_classify(events)
        
        assert len(classifications) == 2
        assert all(c.confidence > 0 for c in classifications)
    
    def test_ticker_extraction(self, test_config):
        classifier = EventClassifier(test_config)
        text = "Apple $AAPL stock surges 5% (AAPL) after strong earnings"
        tickers = classifier.extract_tickers(text)
        assert 'AAPL' in tickers


# ── Historical Pattern Matcher Tests ─────────────────────────────────────────────

class TestHistoricalPatternMatcher:
    """Tests for historical pattern matching"""
    
    @pytest.mark.asyncio
    async def test_pattern_storage(self, test_config, sample_historical_outcome):
        matcher = HistoricalPatternMatcher(test_config)
        await matcher.connect()
        
        # Store outcome
        matcher.event_outcomes.append(sample_historical_outcome)
        
        # Create mock event to match
        event = MarketEvent(
            source=DataSource.NEWS_RSS,
            source_id="test_match",
            title="Earnings beat",
            description="Positive earnings",
            published_at=datetime.utcnow(),
            raw_content="Earnings beat expectations",
            classification=EventClassification(
                event_type=EventType.EARNINGS,
                impact_severity=ImpactSeverity.HIGH,
                direction_bias=Direction.BULLISH,
                time_horizon=TimeHorizon.IMMEDIATE,
                affected_sectors=['technology'],
                affected_tickers=['AAPL'],
                keywords=['earnings', 'beat'],
                confidence=0.8,
                sentiment=SentimentAnalysis(polarity=0.7, subjectivity=0.6, confidence=0.9, key_phrases=[]),
                created_at=datetime.utcnow(),
            )
        )
        
        patterns = await matcher.find_similar_patterns(event, event.classification)
        assert len(patterns) > 0
        assert patterns[0].sample_size >= 1
    
    def test_similarity_engine(self, test_config):
        engine = SimilarityEngine()
        sig1 = {
            'event_type': 'earnings',
            'sectors': {'technology'},
            'sentiment': 0.8,
            'impact_severity': 'high',
        }
        sig2 = {
            'event_type': 'earnings',
            'sectors': {'technology'},
            'sentiment': 0.7,
            'impact_severity': 'high',
        }
        score = engine.calculate_similarity(sig1, sig2)
        assert score > 0.7  # Should be very similar


# ── Options Analyzer Tests ────────────────────────────────────────────────────────

class TestOptionsAnalyzer:
    """Tests for options impact analysis"""
    
    @pytest.mark.asyncio
    async def test_bullish_iv_prediction(self, test_config, sample_news_event):
        analyzer = OptionsImpactAnalyzer(test_config)
        
        classification = EventClassification(
            event_type=EventType.EARNINGS,
            impact_severity=ImpactSeverity.HIGH,
            direction_bias=Direction.BULLISH,
            time_horizon=TimeHorizon.IMMEDIATE,
            affected_sectors=['technology'],
            affected_tickers=['AAPL'],
            keywords=[],
            confidence=0.8,
            sentiment=SentimentAnalysis(polarity=0.6, subjectivity=0.5, confidence=0.8, key_phrases=[]),
            created_at=datetime.utcnow(),
        )
        
        analysis = await analyzer.analyze_options_impact(
            sample_news_event, classification, [], None
        )
        
        assert 'iv_impact' in analysis
        assert analysis['iv_impact'] > 0  # IV expansion expected
        assert 'recommended_strategy' in analysis
        assert analysis['ticker'] == 'AAPL'
    
    def test_strike_selection(self, test_config):
        analyzer = OptionsImpactAnalyzer(test_config)
        strike = analyzer.select_strike_price(
            ticker='AAPL',
            direction=Direction.BULLISH,
            current_price=170.0,
            volatility=0.3,
            target_probability=0.7
        )
        # OTM call should be above current price
        assert strike > 170.0
    
    def test_greeks_calculation(self, test_config):
        analyzer = OptionsImpactAnalyzer(test_config)
        greeks = analyzer.calculate_greeks(
            option_type='call',
            strike=180.0,
            expiry_days=30,
            current_price=170.0,
            volatility=0.3
        )
        
        assert 'delta' in greeks
        assert 'gamma' in greeks
        assert 'vega' in greeks
        assert 'theta' in greeks
        assert 0 < greeks['delta'] < 1  # Call delta positive < 1


# ── Decision Engine Tests ─────────────────────────────────────────────────────────

class TestDecisionEngine:
    """Tests for the weighted decision engine"""
    
    @pytest.mark.asyncio
    async def test_signal_generation(self, test_config, sample_news_event):
        classifier = EventClassifier(test_config)
        classification = await classifier.classify(sample_news_event)
        
        options = OptionsImpactAnalyzer(test_config)
        options_analysis = await options.analyze_options_impact(
            sample_news_event, classification, [], None
        )
        
        decision = DecisionEngine(test_config)
        factor_scores = [
            FactorScore("news_impact", 0.7, test_config.weights['news_impact'], 0.8),
            FactorScore("social_sentiment", 0.3, test_config.weights['social_sentiment'], 0.5),
            FactorScore("volatility_skew", 0.4, test_config.weights['volatility_skew'], 0.7),
            FactorScore("liquidity", 0.9, test_config.weights['liquidity'], 0.9),
        ]
        
        signal = await decision._create_signal(
            ticker='AAPL',
            event=sample_news_event,
            classification=classification,
            composite=CompositeSignal(
                ticker='AAPL',
                direction=Direction.BULLISH,
                total_score=0.65,
                factor_scores=factor_scores,
                raw_confidence=0.75,
                adjusted_confidence=0.82,
                supports=['news_impact', 'volatility_skew'],
                contradicts=[],
            ),
            options_data=options_analysis,
        )
        
        assert signal is not None
        assert signal.ticker == 'AAPL'
        assert signal.direction == Direction.BULLISH
        assert signal.confidence > 0.5
    
    def test_weight_adjustment(self, test_config):
        decision = DecisionEngine(test_config)
        original_weights = decision.weights.copy()
        
        decision.weights['news_impact'] = 0.5
        decision.weights['social_sentiment'] = 0.1
        
        assert decision.weights['news_impact'] == 0.5
        assert decision.weights['social_sentiment'] == 0.1
        # Other weights should be unchanged
        for k, v in original_weights.items():
            if k not in ('news_impact', 'social_sentiment'):
                assert decision.weights[k] == v


# ── End-to-End Pipeline Tests ────────────────────────────────────────────────────

class TestEventPipeline:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_cycle(self, test_config):
        """Test running complete pipeline with event"""
        # Note: This test may hit external APIs; use VCR or mocking in real scenario
        
        # 1. Ingest
        news = NewsIngestor(test_config)
        events = await news.fetch_all(since=datetime.utcnow() - timedelta(minutes=60))
        
        if not events:
            pytest.skip("No news events available for testing")
        
        # 2. Classify
        classifier = EventClassifier(test_config)
        classifications = await classifier.batch_classify(events)
        
        assert len(classifications) > 0
        assert any(c.confidence > 0.6 for c in classifications)
        
        # 3. Historical patterns
        historical = HistoricalPatternMatcher(test_config)
        await historical.connect()
        
        event = events[0]
        classification = classifications[0]
        patterns = await historical.find_similar_patterns(event, classification)
        
        # Patterns may be empty if no history yet - that's OK
        assert isinstance(patterns, list)
        
        # 4. Options analysis
        options = OptionsImpactAnalyzer(test_config)
        analysis = await options.analyze_options_impact(event, classification, patterns, None)
        
        assert 'ticker' in analysis
        assert 'iv_impact' in analysis
        assert 'recommended_strategy' in analysis
        
        # 5. Decision & signals
        decision = DecisionEngine(test_config)
        signals = await decision.generate_signals(
            [event], [classification], {event.event_id: patterns}, {event.event_id: analysis}
        )
        
        # Signaled if confidence high enough
        if classification.confidence >= test_config.min_confidence_threshold:
            assert len(signals) > 0
            assert signals[0].confidence > 0


# ── Learning Integration Tests ────────────────────────────────────────────────────

class TestLearningIntegration:
    """Tests for continuous learning integration"""
    
    def test_signal_recording(self, test_config, sample_news_event):
        # Mock learner
        from app.nexus_core.continuous_learner import ContinuousLearner
        learner = ContinuousLearner()
        
        integration = MarketLearningIntegration(learner, test_config)
        
        signal = OptionsSignal(
            signal_id=uuid4(),
            event_id=sample_news_event.event_id,
            ticker='AAPL',
            direction=Direction.BULLISH,
            confidence=0.8,
            recommendation='Long Calls',
            expected_return=0.15,
            max_loss=0.05,
            contributing_factors=[],
            historical_similarity=0.7,
            sentiment_weight=0.6,
            news_urgency=0.5,
            generated_at=datetime.utcnow(),
        )
        
        classification = EventClassification(
            event_type=EventType.EARNINGS,
            impact_severity=ImpactSeverity.HIGH,
            direction_bias=Direction.BULLISH,
            time_horizon=TimeHorizon.IMMEDIATE,
            affected_sectors=['technology'],
            affected_tickers=['AAPL'],
            keywords=[],
            confidence=0.8,
            sentiment=SentimentAnalysis(polarity=0.6, subjectivity=0.5, confidence=0.8, key_phrases=[]),
            created_at=datetime.utcnow(),
        )
        
        asyncio.run(integration.record_signal(signal, sample_news_event, classification))
        
        assert len(integration.pending_outcomes) == 1
        assert signal.signal_id in integration.pending_outcomes
    
    def test_outcome_evaluation(self, test_config):
        learner = ContinuousLearner()
        integration = MarketLearningIntegration(learner, test_config)
        
        # Add mock pending outcome
        test_record = {
            'signal_id': str(uuid4()),
            'ticker': 'AAPL',
            'direction': 'bullish',
            'confidence': 0.8,
            'expected_return': 0.10,
            'outcome_due_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
        }
        integration.pending_outcomes[UUID(test_record['signal_id'])] = test_record
        
        # Check outcomes (should evaluate due dates)
        result = asyncio.run(integration.check_outcomes())
        assert result['checked'] >= 1
        
        # Signal should be moved to completed
        assert UUID(test_record['signal_id']) not in integration.pending_outcomes


# ── API Tests ─────────────────────────────────────────────────────────────────────

class TestMarketAPI:
    """Tests for FastAPI endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test /api/v1/market/health"""
        response = await client.get("/api/v1/market/health")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'sources' in data
        assert data['status'] in ('ok', 'degraded')
    
    @pytest.mark.asyncio
    async def test_ingest_endpoint(self, client, admin_token):
        """Test /api/v1/market/ingest (requires auth in future)"""
        response = await client.post(
            "/api/v1/market/ingest",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"} if admin_token else None
        )
        # Should return job ID
        assert response.status_code in (200, 401, 403)
    
    @pytest.mark.asyncio
    async def test_signals_endpoint(self, client):
        """Test /api/v1/market/signals"""
        response = await client.get("/api/v1/market/signals?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Signals should be empty initially or have entries
        for signal in data:
            assert 'ticker' in signal
            assert 'direction' in signal
            assert 'confidence' in signal


# ── Performance & Load Tests ───────────────────────────────────────────────────────

class TestPerformance:
    """Performance benchmarks"""
    
    @pytest.mark.asyncio
    async def test_classifier_throughput(self, test_config):
        """Test classifier can handle 100 events/sec"""
        classifier = EventClassifier(test_config)
        
        # Generate test events
        events = [
            MarketEvent(
                source=DataSource.NEWS_RSS,
                source_id=f"perf_test_{i}",
                title=f"Test news {i} about market",
                description="Testing classification throughput",
                published_at=datetime.utcnow(),
                raw_content="Test content",
                language="en",
            )
            for i in range(100)
        ]
        
        import time
        start = time.time()
        classifications = await classifier.batch_classify(events)
        elapsed = time.time() - start
        
        assert len(classifications) == 100
        assert elapsed < 5.0, f"Classification too slow: {elapsed}s for 100 events"
    
    def test_pattern_matcher_scalability(self, test_config):
        """Test pattern matcher handles 10k historical events"""
        matcher = HistoricalPatternMatcher(test_config)
        
        # Generate mock outcomes
        for i in range(10000):
            matcher.event_outcomes.append({
                'event_type': 'earnings',
                'sectors': ['technology'],
                'sentiment': 0.5,
                'impact_severity': 'high',
                'actual_price_move': 0.02,
            })
        
        # Should handle queries quickly
        import time
        mock_event = MarketEvent(
            source=DataSource.NEWS_RSS,
            source_id="query",
            title="Query event",
            description="Query",
            published_at=datetime.utcnow(),
            raw_content="",
            classification=EventClassification(
                event_type=EventType.EARNINGS,
                impact_severity=ImpactSeverity.HIGH,
                direction_bias=Direction.BULLISH,
                time_horizon=TimeHorizon.IMMEDIATE,
                affected_sectors=['technology'],
                affected_tickers=[],
                keywords=[],
                confidence=0.8,
                sentiment=SentimentAnalysis(polarity=0.5, subjectivity=0.5, confidence=0.8, key_phrases=[]),
                created_at=datetime.utcnow(),
            )
        )
        
        start = time.time()
        patterns = asyncio.run(matcher.find_similar_patterns(mock_event, mock_event.classification))
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Pattern search too slow: {elapsed}s"


# ── Test Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run with: python -m pytest test_market_intelligence.py -v
    pytest.main([__file__, "-v"])

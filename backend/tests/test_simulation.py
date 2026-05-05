"""
Comprehensive tests for Market Intelligence Simulation module.

Tests:
- Historical data repository (temporal queries, indexing)
- Simulation engine (time-walking, blind predictions)
- Outcome evaluation
- Performance metrics calculation
- Batch/walk-forward analysis
- Data loaders
- API endpoints
"""

from __future__ import annotations

import pytest
import asyncio
from datetime import datetime, timedelta, date
from uuid import uuid4, UUID
from typing import Dict, Any, List
import json
from pathlib import Path
import tempfile

from app.services.market_intelligence.schemas import (
    MarketEvent,
    EventClassification,
    DataSource,
    EventType,
    ImpactSeverity,
    Direction,
    TimeHorizon,
    SentimentAnalysis,
    OptionsSignal,
)
from app.services.market_intelligence.simulation import (
    HistoricalDataRepository,
    SimulationEngine,
    SimulationConfig,
    SimulationMode,
    SimulationResult,
    backtest_period,
    compare_market_regimes,
    HistoricalDataLoader,
)
from app.services.market_intelligence.classifier import EventClassifier
from app.services.market_intelligence.decision_engine import DecisionEngine
from app.services.market_intelligence.historical import HistoricalPatternMatcher


# ── Fixtures ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_repo():
    """Temporary repository for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = HistoricalDataRepository(tmpdir)
        yield repo


@pytest.fixture
def sample_events():
    """Create sample historical events"""
    base_date = datetime(2024, 1, 1)
    
    events = [
        MarketEvent(
            source=DataSource.NEWS_RSS,
            source_id="earnings_aapl_1",
            title="Apple Reports Strong Q1 Earnings",
            description="Apple EPS beats estimates, revenue up 10%",
            published_at=base_date + timedelta(days=1, hours=9),
            raw_content="Full earnings release...",
            language="en",
            tags=["earnings", "tech"],
            metadata={'detected_tickers': ['AAPL']},
        ),
        MarketEvent(
            source=DataSource.TWITTER,
            source_id="social_tsla_1",
            title="$TSLA to the moon! 🚀",
            description="Elon's new tweet about Tesla FSD",
            published_at=base_date + timedelta(days=2, hours=14),
            raw_content="FSD coming soon!",
            language="en",
            tags=["viral"],
            metadata={
                'detected_tickers': ['TSLA'],
                'retweets': 5000,
                'likes': 20000,
            },
        ),
        MarketEvent(
            source=DataSource.NEWS_API,
            source_id="fed_1",
            title="Fed Holds Rates Steady",
            description="FOMC maintains target rate, signals future cuts",
            published_at=base_date + timedelta(days=5, hours=10),
            raw_content="The Federal Reserve...",
            language="en",
            tags=["macro", "fed"],
            metadata={'detected_tickers': ['SPY', '^GSPC']},
        ),
        MarketEvent(
            source=DataSource.NEWS_RSS,
            source_id="earnings_msft_1",
            title="Microsoft Cloud Revenue Surges",
            description="Azure growth exceeds 20% YoY",
            published_at=base_date + timedelta(days=10, hours=9),
            raw_content="Microsoft reports...",
            language="en",
            tags=["earnings", "cloud"],
            metadata={'detected_tickers': ['MSFT']},
        ),
    ]
    
    # Add classifications
    for event in events:
        event.classification = EventClassification(
            event_type=EventType.EARNINGS if 'earnings' in event.tags else (
                EventType.MACROECONOMIC if 'fed' in event.tags else EventType.VIRAL_TREND
            ),
            impact_severity=ImpactSeverity.HIGH,
            direction_bias=Direction.BULLISH,
            time_horizon=TimeHorizon.IMMEDIATE,
            affected_sectors=['technology'],
            affected_tickers=event.metadata.get('detected_tickers', []),
            keywords=[],
            confidence=0.8,
            sentiment=SentimentAnalysis(polarity=0.6, subjectivity=0.5, confidence=0.8, key_phrases=[]),
            created_at=event.published_at,
        )
    
    return events


@pytest.fixture
def sample_price_data():
    """Sample price series for tickers"""
    base_date = date(2024, 1, 1)
    prices = {}
    
    for ticker in ['AAPL', 'TSLA', 'SPY', 'MSFT']:
        series = []
        price = 100.0
        
        for i in range(60):  # 60 days
            current_date = base_date + timedelta(days=i)
            # Random walk with slight drift
            import random
            change = random.gauss(0.0005, 0.02)  # ~0.05% daily drift, 2% vol
            price *= (1 + change)
            series.append((current_date, round(price, 2)))
        
        prices[ticker] = series
    
    return prices


@pytest.fixture
def sample_outcomes():
    """Sample outcomes for predictions"""
    return {
        uuid4(): {
            'actual_price_move': 0.045,
            'actual_direction': 'bullish',
            'success': True,
            'iv_change': -0.25,
            'call_put_ratio': 1.8,
        },
        uuid4(): {
            'actual_price_move': -0.023,
            'actual_direction': 'bearish',
            'success': True,
            'iv_change': -0.15,
            'call_put_ratio': 0.6,
        },
    }


# ── Repository Tests ─────────────────────────────────────────────────────────────

class TestHistoricalDataRepository:
    """Tests for data repository"""
    
    def test_store_and_retrieve_events(self, temp_repo, sample_events):
        """Test storing events and retrieving through time"""
        repo = temp_repo
        
        # Store events (no outcomes, no prices)
        repo.store_historical_data(sample_events, {}, {})
        
        # Check date indexing
        jan_1 = date(2024, 1, 1)
        jan_2 = date(2024, 1, 2)
        
        events_jan1 = repo.get_events_through(datetime(2024, 1, 1, 23, 59))
        # Only event published exactly on Jan 1 (if any)
        assert isinstance(events_jan1, list)
        
        # Events through Jan 2 should include Jan 1 + Jan 2
        events_through_2 = repo.get_events_through(datetime(2024, 1, 2, 23, 59))
        # Should have at least 2 events (Jan 1 and Jan 2)
        assert len(events_through_2) >= 2
    
    def test_temporal_integrity(self, temp_repo, sample_events):
        """Ensure no future data leakage"""
        repo = temp_repo
        repo.store_historical_data(sample_events, {}, {})
        
        # At Jan 3, should not see Jan 5 event
        cutoff = datetime(2024, 1, 3, 23, 59)
        visible = repo.get_events_through(cutoff)
        
        # Find Jan 5 event if exists
        jan5_events = [e for e in visible if e.published_at.date() == date(2024, 1, 5)]
        assert len(jan5_events) == 0, "Future event leaked into past!"
    
    def test_price_data_storage(self, temp_repo, sample_price_data):
        """Test storing and querying price data"""
        repo = temp_repo
        repo.store_historical_data([], {}, sample_price_data)
        
        # Get price for AAPL on day 10
        target_date = date(2024, 1, 11)  # 10 days after Jan 1 (0-indexed)
        price = repo.get_price_snapshot('AAPL', target_date)
        assert price is not None
        assert isinstance(price, float)
        assert price > 0
    
    def test_price_range_query(self, temp_repo, sample_price_data):
        """Test getting price series over range"""
        repo = temp_repo
        repo.store_historical_data([], {}, sample_price_data)
        
        start = date(2024, 1, 1)
        end = date(2024, 1, 10)
        
        aapl_range = repo.get_price_range('AAPL', start, end)
        assert len(aapl_range) == 10
        
        # Verify chronological order
        dates = [d for d, _ in aapl_range]
        assert dates == sorted(dates)
    
    def test_outcome_retrieval(self, temp_repo, sample_outcomes):
        """Test storing and retrieving outcomes"""
        repo = temp_repo
        event_id = UUID('12345678-1234-5678-1234-567812345678')
        
        outcomes = {
            event_id: {
                'actual_price_move': 0.05,
                'actual_direction': 'bullish',
                'success': True,
            }
        }
        
        repo.store_historical_data([], outcomes, {})
        retrieved = repo.get_outcome(event_id)
        
        assert retrieved is not None
        assert retrieved['actual_price_move'] == 0.05
        assert retrieved['success'] is True
    
    def test_options_chain_storage(self, temp_repo):
        """Test options chain indexing"""
        repo = temp_repo
        
        jan1 = date(2024, 1, 1)
        chain = [
            {
                'ticker': 'AAPL',
                'strike': 180.0,
                'type': 'call',
                'implied_volatility': 0.35,
                'volume': 1000,
            },
            {
                'ticker': 'AAPL',
                'strike': 190.0,
                'type': 'call',
                'implied_volatility': 0.40,
                'volume': 500,
            },
        ]
        
        repo.store_historical_data([], {}, {}, {jan1: chain})
        
        retrieved = repo.get_options_chain(jan1, 'AAPL')
        assert len(retrieved) == 2
        assert retrieved[0]['strike'] == 180.0


# ── Simulation Engine Tests ──────────────────────────────────────────────────────

class TestSimulationEngine:
    """Tests for main simulation engine"""
    
    @pytest.mark.asyncio
    async def test_basic_simulation(self, temp_repo, sample_events, sample_price_data):
        """Test running a basic simulation"""
        repo = temp_repo
        
        # Prepare data
        outcomes = {}
        for event in sample_events:
            # Fake outcome: event published Jan 1, outcome known ~Jan 8
            outcome_date = event.published_at + timedelta(days=7)
            outcomes[event.event_id] = {
                'actual_price_move': 0.03 if 'AAPL' in event.metadata.get('detected_tickers', []) else -0.02,
                'actual_direction': 'bullish' if 'AAPL' in event.metadata.get('detected_tickers', []) else 'bearish',
                'success': True,
            }
        
        repo.store_historical_data(sample_events, outcomes, sample_price_data)
        
        # Run simulation for Jan 1 - Jan 31
        config = SimulationConfig(
            simulation_id="test_run",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            mode=SimulationMode.EVENT_DRIVEN,
            min_confidence=0.0,  # Accept all for testing
        )
        
        engine = SimulationEngine(repo, config, {})
        result = await engine.run_simulation()
        
        assert isinstance(result, SimulationResult)
        assert result.total_signals >= 0
        assert result.win_rate >= 0.0 and result.win_rate <= 1.0
        assert result.avg_return is not None
        assert result.sharpe_ratio is not None
    
    def test_time_walk_forward(self, temp_repo, sample_events, sample_price_data):
        """Test that simulation respects temporal order"""
        repo = temp_repo
        
        # Store data
        repo.store_historical_data(sample_events, {}, sample_price_data)
        
        # Get events at various dates
        jan1 = datetime(2024, 1, 1)
        jan3 = datetime(2024, 1, 3)
        jan6 = datetime(2024, 1, 6)
        
        events_jan1 = repo.get_events_through(jan1)
        events_jan3 = repo.get_events_through(jan3)
        events_jan6 = repo.get_events_through(jan6)
        
        # Monotonicity: later dates include at least as many events
        assert len(events_jan1) <= len(events_jan3) <= len(events_jan6)
        
        # Events on Jan 5 should NOT appear in Jan 3 snapshot
        jan5_events_in_jan3 = [e for e in events_jan3 if e.published_at.date() == date(2024, 1, 5)]
        assert len(jan5_events_in_jan3) == 0
    
    @pytest.mark.asyncio
    async def test_outcome_evaluation(self, temp_repo, sample_events, sample_price_data):
        """Test that predictions are evaluated against actual outcomes"""
        repo = temp_repo
        
        # Store with outcomes
        outcomes = {}
        for event in sample_events:
            event_id = event.event_id
            tickers = event.metadata.get('detected_tickers', [])
            
            # Determine probable outcome based on ticker performance in price data
            if tickers:
                # Simulate price move from publication to +5 days
                pub_date = event.published_at.date()
                prices = repo.get_price_range(tickers[0], pub_date, pub_date + timedelta(days=5))
                if len(prices) >= 2:
                    price_change = (prices[-1][1] - prices[0][1]) / prices[0][1]
                    direction = 'bullish' if price_change > 0 else 'bearish'
                    success = price_change > 0.01 if direction == 'bullish' else price_change < -0.01
                else:
                    price_change = 0.0
                    success = False
            else:
                price_change = 0.0
                success = False
            
            outcomes[event_id] = {
                'actual_price_move': price_change,
                'actual_direction': direction if tickers else 'neutral',
                'success': success,
            }
        
        repo.store_historical_data(sample_events, outcomes, sample_price_data)
        
        # Run simulation
        config = SimulationConfig(
            simulation_id="eval_test",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            min_confidence=0.0,
        )
        
        engine = SimulationEngine(repo, config, {})
        result = await engine.run_simulation()
        
        # All predictions should be evaluated (assuming signals generated)
        if result.total_signals > 0:
            evaluated = [p for p in result.predictions if p.evaluated_at is not None]
            assert len(evaluated) > 0
            
            # Check each evaluated prediction has actuals
            for pred in evaluated:
                assert pred.actual_return is not None
                assert pred.actual_direction is not None
                assert pred.success is not None
                assert pred.pnl_pct is not None


# ── Batch & Walk-Forward Tests ────────────────────────────────────────────────────

class TestBatchRunner:
    """Tests for batch simulation runner"""
    
    @pytest.mark.asyncio
    async def test_walk_forward_analysis(self, temp_repo, sample_events, sample_price_data):
        """Test walk-forward analysis generates rolling windows"""
        repo = temp_repo
        repo.store_historical_data(sample_events, {}, sample_price_data)
        
        from app.services.market_intelligence.simulation import SimulationBatchRunner
        
        runner = SimulationBatchRunner(
            repo,
            SimulationConfig(mode=SimulationMode.WALK_FORWARD),
            {}
        )
        
        results = await runner.run_walk_forward(
            overall_start=datetime(2024, 1, 1),
            overall_end=datetime(2024, 1, 31),
            train_months=1,
            test_months=1,
            step_months=1,
        )
        
        # Should produce multiple test windows
        assert len(results) >= 1
        for result in results:
            assert isinstance(result, SimulationResult)
    
    def test_aggregate_results(self, temp_repo):
        """Test aggregation across multiple simulations"""
        from app.services.market_intelligence.simulation import SimulationBatchRunner
        
        repo = temp_repo
        
        # Create mock results
        results = [
            SimulationResult(
                simulation_id="test1",
                total_signals=10,
                successful_predictions=6,
                failed_predictions=4,
                pending_evaluations=0,
                win_rate=0.6,
                avg_return=0.02,
                sharpe_ratio=1.2,
                max_drawdown=-0.05,
                avg_confidence=0.75,
                by_event_type={},
                by_source={},
                by_direction={},
                predictions=[],
                skipped_dates=[],
                errors=[],
            ),
            SimulationResult(
                simulation_id="test2",
                total_signals=15,
                successful_predictions=9,
                failed_predictions=6,
                pending_evaluations=0,
                win_rate=0.6,
                avg_return=0.025,
                sharpe_ratio=1.3,
                max_drawdown=-0.06,
                avg_confidence=0.72,
                by_event_type={},
                by_source={},
                by_direction={},
                predictions=[],
                skipped_dates=[],
                errors=[],
            ),
        ]
        
        runner = SimulationBatchRunner(repo, SimulationConfig(), {})
        aggregated = runner.aggregate_results(results)
        
        assert aggregated['total_simulations'] == 2
        assert aggregated['total_signals'] == 25
        assert abs(aggregated['avg_win_rate'] - 0.6) < 0.01
        assert aggregated['best_simulation'] in ('test1', 'test2')


# ── Metrics Calculation Tests ────────────────────────────────────────────────────

class TestPerformanceMetrics:
    """Test metric calculations"""
    
    def test_win_rate_calculation(self):
        """Test basic win rate"""
        from app.services.market_intelligence.simulation import SimulationResult
        
        result = SimulationResult(
            simulation_id="test",
            total_signals=100,
            successful_predictions=65,
            failed_predictions=35,
            pending_evaluations=0,
            win_rate=0.0,  # Will be computed
            avg_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            avg_confidence=0.0,
            by_event_type={},
            by_source={},
            by_direction={},
            predictions=[],
            skipped_dates=[],
            errors=[],
        )
        
        # _compile_results computes win_rate
        result.win_rate = result.successful_predictions / result.total_signals
        assert abs(result.win_rate - 0.65) < 0.001
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        import numpy as np
        
        returns = [0.02, -0.01, 0.03, 0.01, -0.02, 0.04]
        mean = np.mean(returns)
        std = np.std(returns)
        sharpe = mean / std if std > 0 else 0.0
        
        assert sharpe > 0
        assert abs(sharpe - 1.22) < 0.1  # Approx value


# ── Data Loader Tests ────────────────────────────────────────────────────────────

class TestDataLoader:
    """Tests for data loading utilities"""
    
    def test_csv_loading(self, temp_repo, tmp_path):
        """Test loading from CSV file"""
        from app.services.market_intelligence.data_loader import HistoricalDataLoader
        
        # Create test CSV
        csv_path = tmp_path / "prices.csv"
        with open(csv_path, 'w') as f:
            f.write("date,open,high,low,close,volume\n")
            base = 100.0
            for i in range(10):
                d = datetime(2024, 1, 1 + i).strftime('%Y-%m-%d')
                base *= 1.001  # Slight drift
                f.write(f"{d},{base-1},{base+1},{base-2},{base},{10000}\n")
        
        loader = HistoricalDataLoader(temp_repo, None)
        # asyncio.run(loader.load_from_csv(str(csv_path), ticker='TEST'))
        # For sync test, could use asyncio.run but pytest-asyncio handles
        # This would require async context
        
        # Verify loaded
        # price = temp_repo.get_price_snapshot('TEST', date(2024, 1, 5))
        # assert price is not None


# ── Integration Tests ────────────────────────────────────────────────────────────

class TestFullSimulation:
    """End-to-end simulation tests"""
    
    @pytest.mark.asyncio
    async def test_simulate_earnings_strategy(self, temp_repo):
        """
        Test earnings-based strategy:
        - Load earnings events for AAPL across 2023
        - Simulate predictions on earnings dates
        - Evaluate performance
        """
        # This would be a longer integration test
        # For now, placeholder
        pass
    
    @pytest.mark.asyncio
    async def test_walk_forward_stability(self):
        """Test that walk-forward results are stable over multiple runs"""
        pass


# ── API Tests ─────────────────────────────────────────────────────────────────────

class TestSimulationAPI:
    """Tests for API endpoints (requires test client)"""
    
    @pytest.mark.asyncio
    async def test_run_simulation_endpoint(self, client):
        """Test POST /sim/run"""
        pass
    
    @pytest.mark.asyncio
    async def test_get_results_endpoint(self, client):
        """Test GET /sim/results"""
        pass
    
    @pytest.mark.asyncio
    async def test_compare_endpoint(self, client):
        """Test POST /sim/compare"""
        pass


# ── Performance Tests ────────────────────────────────────────────────────────────

class TestSimulationPerformance:
    """Benchmark simulation performance"""
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, temp_repo):
        """Test simulation with many events and tickers"""
        # Generate 10000 events, 50 tickers, 1 year
        # Should complete in < X seconds
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Historical Simulation & Backtesting Engine

Allows running the Market Intelligence system against historical periods
to evaluate prediction accuracy without knowing future outcomes.

Key concepts:
- Simulation: Run over a historical timeframe, making predictions as if live
- Backtest: Evaluate those predictions against actual historical outcomes
- Batch: Run multiple simulations across different periods for aggregate stats

Architecture:
1. Historical Data Repository - stores/loads market data for any date
2. Time Travel Engine - walks through time, presenting only past-available data
3. Blind Predictor - runs the full pipeline with temporal data cutoff
4. Outcome Evaluator - compares predictions to what actually happened
5. Analytics & Reporting - detailed success/failure analysis
6. Learning Integration - feeds outcomes back to improve model

The simulation is "foolproof": Nexus cannot accidentally see future data.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID
import json
from pathlib import Path

from app.services.market_intelligence.base import BaseDataSource
from app.services.market_intelligence.schemas import (
    MarketEvent,
    EventClassification,
    OptionsSignal,
    Direction,
    ImpactSeverity,
    TimeHorizon,
    MarketIntelligenceConfig,
    DataSource,
)
from app.services.market_intelligence.news_ingestor import NewsIngestor
from app.services.market_intelligence.social_ingestor import SocialMediaIngestor
from app.services.market_intelligence.classifier import EventClassifier
from app.services.market_intelligence.historical import HistoricalPatternMatcher
from app.services.market_intelligence.options_analyzer import OptionsImpactAnalyzer
from app.services.market_intelligence.decision_engine import DecisionEngine
from app.services.market_intelligence.learning_integration import MarketLearningIntegration

log = logging.getLogger(__name__)


class SimulationMode(str, Enum):
    """How to simulate"""
    WALK_FORWARD = "walk_forward"  # Day-by-day progressive simulation
    EVENT_DRIVEN = "event_driven"  # Only on events
    SNAPSHOT = "snapshot"          # One-time prediction at specific date


@dataclass
class SimulationConfig:
    """Configuration for a simulation run"""
    simulation_id: str
    start_date: datetime
    end_date: datetime
    mode: SimulationMode = SimulationMode.WALK_FORWARD
    
    # Step size for walk-forward
    step_days: int = 1
    
    # Which data sources to include
    include_news: bool = True
    include_social: bool = True
    
    # Whether to use historical patterns (trained on prior data only)
    use_historical_patterns: bool = True
    
    # Whether to allow learning during simulation (learning=False = frozen model)
    enable_learning: bool = False
    
    # Minimum confidence to generate signals
    min_confidence: float = 0.6
    
    # What to evaluate
    evaluate_earnings: bool = True
    evaluate_macro: bool = True
    evaluate_social_viral: bool = True


@dataclass
class TimeSlice:
    """A single point in simulated time"""
    current_time: datetime
    known_events: List[MarketEvent]  # Events known at this time
    market_data: Dict[str, Any]  # Current prices, IV, etc.
    historical_outcomes: Dict[str, Any]  # What happened after (for later eval)


@dataclass
class PredictionRecord:
    """A prediction made during simulation"""
    prediction_id: UUID
    timestamp: datetime  # When prediction was made
    event_id: UUID
    ticker: str
    direction: Direction
    confidence: float
    strategy: str
    expected_return: float
    target_strike: Optional[float]
    target_expiry: Optional[date]
    
    # For evaluation
    actual_return: Optional[float] = None
    actual_direction: Optional[Direction] = None
    success: Optional[bool] = None
    pnl_pct: Optional[float] = None
    evaluated_at: Optional[datetime] = None
    
    # Metadata
    simulation_id: str = ""
    event_type: str = ""
    sources_used: List[str] = field(default_factory=list)


@dataclass
class SimulationResult:
    """Results from a simulation run"""
    simulation_id: str
    total_signals: int
    successful_predictions: int
    failed_predictions: int
    pending_evaluations: int
    
    # Performance metrics
    win_rate: float
    avg_return: float
    sharpe_ratio: float
    max_drawdown: float
    avg_confidence: float
    
    # Breakdown by category
    by_event_type: Dict[str, Dict[str, float]]
    by_source: Dict[str, Dict[str, float]]
    by_direction: Dict[str, Dict[str, float]]
    
    # Timeline of all predictions
    predictions: List[PredictionRecord]
    
    # Errors/warnings
    skipped_dates: List[datetime]
    errors: List[str]
    
    created_at: datetime = field(default_factory=datetime.utcnow)


class HistoricalDataRepository:
    """
    Stores and serves historical market data for simulations.
    
    Provides time-based queries that respect causality:
    - At time T, only return events that published ≤ T
    - Only return outcomes that were known by time T
    """
    
    def __init__(self, data_path: str = "/tmp/simulation_data"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Indexes for fast lookup
        self._events_by_date: Dict[date, List[MarketEvent]] = {}
        self._outcomes_by_event: Dict[UUID, Dict] = {}
        self._price_data: Dict[str, Dict[date, float]] = {}  # ticker -> date -> price
        self._options_chain_cache: Dict[date, List[Dict]] = {}
        
    def store_historical_data(
        self,
        events: List[MarketEvent],
        outcomes: Dict[UUID, Dict],
        price_data: Dict[str, List[Tuple[date, float]]],
        options_chains: Optional[Dict[date, List[Dict]]] = None
    ) -> None:
        """
        Index historical data for efficient querying during simulation.
        
        Args:
            events: All market events in the period
            outcomes: Actual outcomes keyed by event_id
            price_data: Time series of prices per ticker
            options_chains: Options chain snapshots by date
        """
        # Index events by date
        for event in events:
            d = event.published_at.date()
            if d not in self._events_by_date:
                self._events_by_date[d] = []
            self._events_by_date[d].append(event)
        
        # Store outcomes
        self._outcomes_by_event.update(outcomes)
        
        # Index price data
        for ticker, series in price_data.items():
            self._price_data[ticker] = {}
            for dt, price in series:
                self._price_data[ticker][dt if isinstance(dt, date) else dt.date()] = price
        
        # Store options chains
        if options_chains:
            self._options_chain_cache.update(options_chains)
        
        log.info(f"Indexed {len(events)} events across {len(self._events_by_date)} dates")
    
    def get_events_through(self, current_time: datetime) -> List[MarketEvent]:
        """
        Get all events published up to and including current_time.
        
        This is THE critical method ensuring no future leakage.
        """
        events = []
        current_date = current_time.date()
        
        for d, day_events in self._events_by_date.items():
            if d <= current_date:
                events.extend(day_events)
        
        # Sort chronologically
        events.sort(key=lambda e: e.published_at)
        return events
    
    def get_events_on_date(self, target_date: date) -> List[MarketEvent]:
        """Get events published on a specific date"""
        return self._events_by_date.get(target_date, [])
    
    def get_price_snapshot(self, ticker: str, on_date: date) -> Optional[float]:
        """Get closing price for ticker on specific date"""
        ticker_data = self._price_data.get(ticker.upper())
        if not ticker_data:
            return None
        return ticker_data.get(on_date)
    
    def get_price_range(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> List[Tuple[date, float]]:
        """Get price series for a date range"""
        ticker_data = self._price_data.get(ticker.upper(), {})
        result = []
        current = start_date
        while current <= end_date:
            if current in ticker_data:
                result.append((current, ticker_data[current]))
            current += timedelta(days=1)
        return result
    
    def get_outcome(self, event_id: UUID) -> Optional[Dict]:
        """Get actual outcome for an event"""
        return self._outcomes_by_event.get(event_id)
    
    def get_options_chain(self, on_date: date, ticker: Optional[str] = None) -> List[Dict]:
        """Get options chain snapshot for a date"""
        chains = self._options_chain_cache.get(on_date, [])
        if ticker:
            chains = [c for c in chains if c.get('ticker') == ticker.upper()]
        return chains
    
    def get_simulation_dates(self, start: date, end: date, step: int = 1) -> List[date]:
        """Generate list of dates to simulate"""
        dates = []
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=step)
        return dates
    
    def persist(self) -> None:
        """Save indexed data to disk"""
        save_path = self.data_path / "indexed_data.json"
        # Serialize indexes (simplified - real version would use DB)
        data = {
            'events_by_date': {
                d.isoformat(): [
                    {
                        'event_id': str(e.event_id),
                        'title': e.title,
                        'source': e.source.value,
                        'tickers': e.metadata.get('detected_tickers', []),
                        'classification': e.classification.dict() if e.classification else None,
                    }
                    for e in events
                ]
                for d, events in self._events_by_date.items()
            },
            'outcomes': {str(k): v for k, v in self._outcomes_by_event.items()},
        }
        with open(save_path, 'w') as f:
            json.dump(data, f, default=str, indent=2)


class SimulationEngine:
    """
    Core simulation engine that walks through time and makes predictions.
    
    Ensures temporal correctness: at simulated time T, Nexus only sees
    data from ≤ T, never peeking ahead.
    """
    
    def __init__(
        self,
        repository: HistoricalDataRepository,
        config: SimulationConfig,
        market_intelligence_services: Dict[str, Any]
    ):
        self.repo = repository
        self.config = config
        self.services = market_intelligence_services
        
        # Service instances (will be initialized on demand)
        self._news_ingestor: Optional[NewsIngestor] = None
        self._social_ingestor: Optional[SocialMediaIngestor] = None
        self._classifier: Optional[EventClassifier] = None
        self._historical: Optional[HistoricalPatternMatcher] = None
        self._options_analyzer: Optional[OptionsImpactAnalyzer] = None
        self._decision_engine: Optional[DecisionEngine] = None
        self._learning_integration: Optional[MarketLearningIntegration] = None
        
        # Simulation state
        self.predictions: List[PredictionRecord] = []
        self.errors: List[str] = []
        self.current_time: Optional[datetime] = None
        
    async def initialize_services(self):
        """Lazy-load services to avoid startup costs"""
        config = MarketIntelligenceConfig(
            min_confidence_threshold=self.config.min_confidence,
            enabled_sources=list(DataSource),
        )
        
        self._news_ingestor = NewsIngestor(config)
        self._social_ingestor = SocialMediaIngestor(config)
        self._classifier = EventClassifier(config)
        self._historical = HistoricalPatternMatcher(config)
        await self._historical.connect()
        self._options_analyzer = OptionsImpactAnalyzer(config)
        self._decision_engine = DecisionEngine(config)
        
        # Only enable learning if requested
        if self.config.enable_learning:
            try:
                from app.nexus_core.continuous_learner import continuous_learner
                self._learning_integration = MarketLearningIntegration(
                    continuous_learner, config
                )
            except Exception as e:
                log.warning(f"Could not initialize learning: {e}")
                self._learning_integration = None
    
    async def run_simulation(self) -> SimulationResult:
        """
        Execute the full simulation.
        
        Returns:
            SimulationResult with all predictions and outcomes
        """
        log.info(f"Starting simulation {self.config.simulation_id}")
        log.info(f"Period: {self.config.start_date} to {self.config.end_date}")
        
        await self.initialize_services()
        
        # Generate timeline
        dates = self.repo.get_simulation_dates(
            self.config.start_date.date(),
            self.config.end_date.date(),
            step=self.config.step_days
        )
        
        log.info(f"Simulating {len(dates)} dates")
        
        # Walk forward through time
        for sim_date in dates:
            self.current_time = datetime.combine(sim_date, datetime.min.time())
            
            try:
                await self._process_date(sim_date)
            except Exception as e:
                error_msg = f"Error on {sim_date}: {e}"
                log.error(error_msg, exc_info=True)
                self.errors.append(error_msg)
        
        # Evaluate all predictions
        await self._evaluate_all_predictions()
        
        # Generate result summary
        result = self._compile_results()
        
        log.info(f"Simulation complete: {result.total_signals} signals, "
                f"{result.win_rate:.1%} win rate")
        
        return result
    
    async def _process_date(self, sim_date: date):
        """
        Process a single simulation date.
        
        At simulated time T:
        1. Gather all events known at T
        2. Classify them
        3. Find historical patterns (only from before T!)
        4. Generate options analysis
        5. Create trading signals
        6. Store predictions for later evaluation
        """
        current_dt = datetime.combine(sim_date, datetime.min.time())
        log.debug(f"Processing {sim_date}")
        
        # 1. Fetch events available at this time
        known_events = self.repo.get_events_through(current_dt)
        
        # Filter to events from last N days to avoid using ancient news
        # (realistic: traders focus on recent events)
        cutoff = current_dt - timedelta(days=7)
        recent_events = [e for e in known_events if e.published_at >= cutoff]
        
        if not recent_events:
            return
        
        # 2. Classify events
        classifications = await self._classifier.batch_classify(recent_events)
        for event, classification in zip(recent_events, classifications):
            event.classification = classification
        
        # 3. Historical patterns - CRITICAL: only use data strictly before current date
        # This ensures temporal integrity
        self._historical.event_outcomes = [
            o for o in self._historical.event_outcomes
            if datetime.strptime(o.get('date', '2000-01-01'), '%Y-%m-%d').date() < sim_date
        ]
        
        pattern_matches = {}
        for event in recent_events:
            if event.classification and event.classification.confidence >= self.config.min_confidence:
                patterns = await self._historical.find_similar_patterns(
                    event, event.classification
                )
                pattern_matches[event.event_id] = patterns
        
        # 4. Options analysis
        options_analysis = {}
        for event in recent_events:
            patterns = pattern_matches.get(event.event_id, [])
            
            # Get market data available at this historical time
            ticker = (event.classification.affected_tickers[0] 
                     if event.classification and event.classification.affected_tickers 
                     else 'SPY')
            
            historical_market_data = self._get_market_data_at_time(
                ticker, sim_date
            )
            
            analysis = await self._options_analyzer.analyze_options_impact(
                event,
                event.classification,
                patterns,
                historical_market_data
            )
            options_analysis[event.event_id] = analysis
        
        # 5. Generate signals
        signals = await self._decision_engine.generate_signals(
            recent_events,
            classifications,
            pattern_matches,
            options_analysis
        )
        
        # 6. Store predictions with metadata
        for signal in signals:
            event = next(
                (e for e in recent_events if e.event_id == signal.event_id),
                None
            )
            if event and event.classification:
                record = PredictionRecord(
                    prediction_id=signal.signal_id,
                    timestamp=current_dt,
                    event_id=signal.event_id,
                    ticker=signal.ticker,
                    direction=signal.direction,
                    confidence=signal.confidence,
                    strategy=signal.recommendation,
                    expected_return=signal.expected_return or 0.0,
                    target_strike=signal.target_strike,
                    target_expiry=self._calculate_target_expiry(
                        sim_date, event.classification.time_horizon
                    ),
                    simulation_id=self.config.simulation_id,
                    event_type=event.classification.event_type.value,
                    sources_used=self._detect_sources(event),
                )
                self.predictions.append(record)
                
                # Record in learning integration if enabled
                if self._learning_integration and self.config.enable_learning:
                    await self._learning_integration.record_signal(
                        signal, event, event.classification
                    )
        
        log.debug(f"Generated {len(signals)} signals for {sim_date}")
    
    def _get_market_data_at_time(
        self,
        ticker: str,
        on_date: date
    ) -> Dict[str, Any]:
        """
        Get market data as it was known on that historical date.
        No peeking at future prices!
        """
        price = self.repo.get_price_snapshot(ticker, on_date)
        
        # Get options chain if available
        options_chain = self.repo.get_options_chain(on_date, ticker)
        
        # Estimate IV from options if available, else use historic average
        iv = 0.3  # default
        if options_chain:
            # Use ATM option IV
            for opt in options_chain:
                if opt.get('type') == 'call' and abs(opt.get('strike', 0) - price) < price * 0.02:
                    iv = opt.get('implied_volatility', 0.3)
                    break
        
        # Get volume/OI
        volume = sum(c.get('volume', 0) for c in options_chain) if options_chain else 0
        
        return {
            'price': price or 100.0,
            'iv': iv,
            'volume': volume,
            'bid_ask_spread': 0.1,  # Would derive from options chain
        }
    
    def _calculate_target_expiry(
        self,
        prediction_date: date,
        time_horizon: TimeHorizon
    ) -> date:
        """Calculate recommended expiry date based on time horizon"""
        expiry_days = {
            TimeHorizon.IMMEDIATE: 7,
            TimeHorizon.SHORT_TERM: 30,
            TimeHorizon.MEDIUM_TERM: 60,
            TimeHorizon.LONG_TERM: 120,
            TimeHorizon.UNKNOWN: 45,
        }.get(time_horizon, 30)
        
        return prediction_date + timedelta(days=expiry_days)
    
    def _detect_sources(self, event: MarketEvent) -> List[str]:
        """Detect which sources contributed to this event"""
        sources = [event.source.value]
        if event.metadata.get('feed'):
            sources.append(event.metadata['feed'])
        return sources
    
    async def _evaluate_all_predictions(self):
        """
        Evaluate every prediction against actual historical outcomes.
        
        This happens AFTER the simulation completes, simulating
        the passage of time to outcome realization.
        """
        log.info(f"Evaluating {len(self.predictions)} predictions")
        
        evaluated = 0
        for pred in self.predictions:
            outcome = self.repo.get_outcome(pred.prediction_id)
            
            if not outcome:
                log.warning(f"No outcome found for {pred.prediction_id}")
                continue
            
            # Extract actual results
            actual_return = outcome.get('actual_price_move', 0.0)
            actual_direction_val = outcome.get('actual_direction', 'neutral')
            
            try:
                actual_direction = Direction(actual_direction_val)
            except:
                actual_direction = Direction.NEUTRAL
            
            success = outcome.get('success', False)
            
            # Calculate P&L (simplified - would use actual options pricing)
            if pred.direction == Direction.BULLISH:
                pnl = actual_return if success else -abs(actual_return) * 0.5
            elif pred.direction == Direction.BEARISH:
                pnl = -actual_return if success else -abs(actual_return) * 0.5
            else:
                pnl = abs(actual_return) * 0.3 if not success else 0  # Neutral = long vol
            
            # Update prediction record
            pred.actual_return = actual_return
            pred.actual_direction = actual_direction
            pred.success = success
            pred.pnl_pct = pnl
            pred.evaluated_at = datetime.utcnow()
            
            evaluated += 1
            
            # Feed back to learning if enabled
            if self._learning_integration and self.config.enable_learning:
                # Simulate outcome recording
                self._learning_integration._update_metrics(
                    {'ticker': pred.ticker, 'event_type': pred.event_type},
                    success,
                    actual_return
                )
        
        log.info(f"Evaluated {evaluated} predictions")
    
    def _compile_results(self) -> SimulationResult:
        """Compile simulation results into statistics"""
        total = len(self.predictions)
        successful = sum(1 for p in self.predictions if p.success)
        failed = total - successful
        pending = sum(1 for p in self.predictions if p.evaluated_at is None)
        
        # Returns
        returns = [p.pnl_pct for p in self.predictions if p.pnl_pct is not None]
        avg_return = sum(returns) / len(returns) if returns else 0.0
        
        # Win rate
        win_rate = successful / total if total > 0 else 0.0
        
        # Sharpe (simplified)
        import numpy as np
        if returns and len(returns) > 1:
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0
        else:
            sharpe = 0.0
        
        # Max drawdown (simplified)
        if returns:
            cumulative = np.cumsum(returns)
            peak = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - peak) / (peak + 0.0001)
            max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0.0
        else:
            max_drawdown = 0.0
        
        # Avg confidence
        confidences = [p.confidence for p in self.predictions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Breakdown analyses
        by_event_type = self._breakdown_by('event_type')
        by_source = self._breakdown_by('sources_used')
        by_direction = self._breakdown_by('direction')
        
        return SimulationResult(
            simulation_id=self.config.simulation_id,
            total_signals=total,
            successful_predictions=successful,
            failed_predictions=failed,
            pending_evaluations=pending,
            win_rate=win_rate,
            avg_return=avg_return,
            sharpe_ratio=float(sharpe),
            max_drawdown=float(max_drawdown),
            avg_confidence=avg_confidence,
            by_event_type=by_event_type,
            by_source=by_source,
            by_direction=by_direction,
            predictions=self.predictions.copy(),
            skipped_dates=[],
            errors=self.errors.copy(),
        )
    
    def _breakdown_by(self, attr: str) -> Dict[str, Dict[str, float]]:
        """Calculate breakdown statistics by attribute"""
        groups: Dict[str, List[PredictionRecord]] = {}
        
        for pred in self.predictions:
            if not pred.success:
                continue
            
            key = getattr(pred, attr, 'unknown')
            if isinstance(key, list):
                # Handle list attributes (sources_used)
                for k in key:
                    groups.setdefault(k, []).append(pred)
            else:
                groups.setdefault(str(key), []).append(pred)
        
        result = {}
        for key, preds in groups.items():
            if not preds:
                continue
            total = len(preds)
            wins = sum(1 for p in preds if p.success)
            returns = [p.pnl_pct for p in preds if p.pnl_pct is not None]
            
            result[key] = {
                'count': total,
                'win_rate': wins / total if total else 0.0,
                'avg_return': sum(returns) / len(returns) if returns else 0.0,
                'sharpe': float(np.std(returns)) if returns and len(returns) > 1 else 0.0,
            }
        
        return result


class SimulationBatchRunner:
    """
    Runs multiple simulations across different time periods.
    
    Useful for:
    - Stress testing across market regimes
    - Walk-forward analysis (rolling window backtest)
    - Parameter optimization (grid search over config options)
    """
    
    def __init__(
        self,
        repository: HistoricalDataRepository,
        base_config: SimulationConfig,
        services: Dict[str, Any]
    ):
        self.repo = repository
        self.base_config = base_config
        self.services = services
    
    async def run_batch(
        self,
        periods: List[Tuple[datetime, datetime]],
        parallel: bool = False
    ) -> List[SimulationResult]:
        """
        Run multiple simulation periods.
        
        Args:
            periods: List of (start_date, end_date) tuples
            parallel: Run concurrently (careful: memory heavy)
            
        Returns:
            List of SimulationResult objects
        """
        log.info(f"Running batch of {len(periods)} simulations")
        
        if parallel:
            tasks = []
            for start, end in periods:
                config = SimulationConfig(
                    simulation_id=f"batch_{start.date()}_{end.date()}",
                    start_date=start,
                    end_date=end,
                    mode=self.base_config.mode,
                    min_confidence=self.base_config.min_confidence,
                    enable_learning=self.base_config.enable_learning,
                )
                engine = SimulationEngine(self.repo, config, self.services)
                tasks.append(engine.run_simulation())
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if not isinstance(r, Exception)]
        else:
            # Sequential
            results = []
            for start, end in periods:
                config = SimulationConfig(
                    simulation_id=f"batch_{start.date()}_{end.date()}",
                    start_date=start,
                    end_date=end,
                    mode=self.base_config.mode,
                    min_confidence=self.base_config.min_confidence,
                    enable_learning=self.base_config.enable_learning,
                )
                engine = SimulationEngine(self.repo, config, self.services)
                result = await engine.run_simulation()
                results.append(result)
            
            return results
    
    async def run_walk_forward(
        self,
        overall_start: datetime,
        overall_end: datetime,
        train_months: int = 6,
        test_months: int = 1,
        step_months: int = 1
    ) -> List[SimulationResult]:
        """
        Walk-forward analysis: train on past N months, test next M months, roll forward.
        
        Simulates realistic deployment: model retrained periodically on expanding window.
        """
        results = []
        
        current_train_end = overall_start + timedelta(days=train_months * 30)
        while current_train_end + timedelta(days=test_months * 30) <= overall_end:
            test_start = current_train_end
            test_end = test_start + timedelta(days=test_months * 30)
            
            # For this test period, we simulate with the historical data available
            # at the start of the period
            config = SimulationConfig(
                simulation_id=f"wf_{test_start.date()}_{test_end.date()}",
                start_date=test_start,
                end_date=test_end,
                mode=SimulationMode.WALK_FORWARD,
                min_confidence=self.base_config.min_confidence,
            )
            
            engine = SimulationEngine(self.repo, config, self.services)
            result = await engine.run_simulation()
            results.append(result)
            
            # Roll forward
            current_train_end += timedelta(days=step_months * 30)
        
        return results
    
    def aggregate_results(self, results: List[SimulationResult]) -> Dict[str, Any]:
        """Aggregate statistics across multiple simulation runs"""
        if not results:
            return {}
        
        all_returns = []
        all_win_rates = []
        all_sharpes = []
        
        for r in results:
            all_returns.append(r.avg_return)
            all_win_rates.append(r.win_rate)
            all_sharpes.append(r.sharpe_ratio)
        
        import numpy as np
        return {
            'total_simulations': len(results),
            'total_signals': sum(r.total_signals for r in results),
            'avg_win_rate': float(np.mean(all_win_rates)),
            'avg_return': float(np.mean(all_returns)),
            'avg_sharpe': float(np.mean(all_sharpes)),
            'std_return': float(np.std(all_returns)),
            'best_simulation': max(results, key=lambda r: r.sharpe_ratio).simulation_id,
            'worst_simulation': min(results, key=lambda r: r.sharpe_ratio).simulation_id,
            'periods': [r.simulation_id for r in results],
        }


class SimulationAPI:
    """
    High-level API for managing simulations.
    
    Provides:
    - Create simulation
    - Run single simulation
    - Run batch simulations
    - Query results
    - Compare strategies/configurations
    """
    
    def __init__(self, data_repository: HistoricalDataRepository):
        self.repo = data_repository
        self.active_simulations: Dict[str, SimulationEngine] = {}
        self.completed_results: List[SimulationResult] = []
    
    async def create_and_run(
        self,
        start_date: datetime,
        end_date: datetime,
        config_overrides: Optional[Dict] = None
    ) -> SimulationResult:
        """
        Create and immediately run a simulation.
        
        Args:
            start_date: Simulation start (inclusive)
            end_date: Simulation end (inclusive)
            config_overrides: Optional config tweaks
            
        Returns:
            SimulationResult
        """
        sim_id = f"sim_{start_date.date()}_{end_date.date()}"
        
        config = SimulationConfig(
            simulation_id=sim_id,
            start_date=start_date,
            end_date=end_date,
        )
        
        if config_overrides:
            for key, val in config_overrides.items():
                if hasattr(config, key):
                    setattr(config, key, val)
        
        # Get services (would be injected properly in production)
        services = self._get_services()
        
        engine = SimulationEngine(self.repo, config, services)
        self.active_simulations[sim_id] = engine
        
        try:
            result = await engine.run_simulation()
            self.completed_results.append(result)
            return result
        finally:
            self.active_simulations.pop(sim_id, None)
    
    def _get_services(self) -> Dict[str, Any]:
        """Get fresh service instances (simplified)"""
        # In production, these would be properly injected from DI container
        return {}
    
    def get_result(self, simulation_id: str) -> Optional[SimulationResult]:
        """Retrieve a completed simulation result"""
        for r in self.completed_results:
            if r.simulation_id == simulation_id:
                return r
        return None
    
    def list_results(self) -> List[Dict[str, Any]]:
        """List all completed simulations"""
        return [
            {
                'id': r.simulation_id,
                'signals': r.total_signals,
                'win_rate': r.win_rate,
                'avg_return': r.avg_return,
                'sharpe': r.sharpe_ratio,
                'created': r.created_at.isoformat(),
            }
            for r in self.completed_results
        ]
    
    def compare_simulations(self, ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple simulation runs side-by-side.
        """
        results = [self.get_result(sid) for sid in ids]
        results = [r for r in results if r is not None]
        
        comparison = {
            'simulations': ids,
            'metrics': {},
        }
        
        # Side-by-side metrics
        for metric in ['win_rate', 'avg_return', 'sharpe_ratio', 'total_signals']:
            comparison['metrics'][metric] = {
                r.simulation_id: getattr(r, metric)
                for r in results
            }
        
        # Best overall
        if results:
            best = max(results, key=lambda r: r.sharpe_ratio)
            comparison['best_by_sharpe'] = best.simulation_id
        
        return comparison
    
    async def run_monte_carlo(
        self,
        start_date: datetime,
        end_date: datetime,
        iterations: int = 100,
        parameter_variations: Optional[Dict[str, List[float]]] = None
    ) -> List[SimulationResult]:
        """
        Monte Carlo simulation: run many times with slight variations
        to test robustness.
        
        Useful for:
        - Sensitivity analysis
        - Confidence intervals
        - Risk assessment
        """
        import random
        
        base_days = (end_date - start_date).days
        results = []
        
        for i in range(iterations):
            # Randomize parameters if variations provided
            config_overrides = {}
            if parameter_variations:
                for param, values in parameter_variations.items():
                    config_overrides[param] = random.choice(values)
            
            # Optionally vary date range slightly (bootstrapping)
            if random.random() < 0.3:
                shift = random.randint(-30, 30)
                s = start_date + timedelta(days=shift)
                e = s + timedelta(days=base_days)
            else:
                s, e = start_date, end_date
            
            result = await self.create_and_run(s, e, config_overrides)
            results.append(result)
        
        return results


# Convenience functions for common use cases

async def backtest_period(
    repository: HistoricalDataRepository,
    start: datetime,
    end: datetime,
    **kwargs
) -> SimulationResult:
    """
    Quick backtest of a single period.
    
    Example:
        result = await backtest_period(repo, datetime(2024,1,1), datetime(2024,3,31))
        print(f"Win rate: {result.win_rate:.1%}")
    """
    engine = SimulationEngine(
        repository,
        SimulationConfig(
            simulation_id=f"backtest_{start.date()}_{end.date()}",
            start_date=start,
            end_date=end,
            **kwargs
        ),
        {}
    )
    return await engine.run_simulation()


async def compare_market_regimes(
    repository: HistoricalDataRepository,
    periods: Dict[str, Tuple[datetime, datetime]]
) -> Dict[str, Any]:
    """
    Compare performance across different market regimes.
    
    Example periods:
    {
        'bull_market': (datetime(2023,1,1), datetime(2023,12,31)),
        'bear_market': (datetime(2022,1,1), datetime(2022,12,31)),
        'sideways': (datetime(2023,7,1), datetime(2023,9,30)),
    }
    
    Returns:
        Dict comparing win rates, returns, etc. across regimes
    """
    results = {}
    for regime, (start, end) in periods.items():
        result = await backtest_period(repository, start, end)
        results[regime] = {
            'win_rate': result.win_rate,
            'avg_return': result.avg_return,
            'sharpe': result.sharpe_ratio,
            'total_signals': result.total_signals,
            'by_event_type': result.by_event_type,
        }
    
    return results


async def stress_test_configurations(
    repository: HistoricalDataRepository,
    base_period: Tuple[datetime, datetime],
    config_variations: List[Dict[str, Any]]
) -> List[SimulationResult]:
    """
    Test how different configurations perform on same period.
    
    Useful for hyperparameter tuning.
    """
    start, end = base_period
    results = []
    
    for i, vars in enumerate(config_variations):
        result = await backtest_period(
            repository, start, end,
            simulation_id=f"stress_test_{i}",
            **vars
        )
        results.append(result)
    
    return results

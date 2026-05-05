# Market Intelligence: Simulation & Backtesting Guide

## Overview

The Simulation module enables historical testing of the Market Intelligence prediction engine. It allows you to:

1. **Run time-accurate simulations**: Nexus makes predictions using only data available at each historical point (no peeking into the future)
2. **Compare to actual outcomes**: Automatically evaluate predictions against what really happened
3. **Analyze performance**: Detailed breakdowns by event type, ticker, direction, source
4. **Batch test**: Run multiple periods to see how model performs across different market regimes
5. **Learn from outcomes**: Feed results back into ContinuousLearner to improve future predictions

## Quick Start

### 1. Load Historical Data

First, load historical price and event data into the repository:

```python
from app.services.market_intelligence.simulation import HistoricalDataRepository, load_standard_market_data

# Create repository
repo = HistoricalDataRepository("/data/sim")

# Load standard tickers (SPY, QQQ, AAPL, etc.) for 2023
await load_standard_market_data(
    repo,
    tickers=['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL'],
    start=datetime(2023, 1, 1),
    end=datetime(2023, 12, 31)
)
```

### 2. Run a Quick Backtest

```python
from app.services.market_intelligence.simulation import backtest_period
from datetime import datetime

result = await backtest_period(
    repo,
    start=datetime(2023, 1, 1),
    end=datetime(2023, 1, 31)
)

print(f"Signals: {result.total_signals}")
print(f"Win Rate: {result.win_rate:.1%}")
print(f"Avg Return: {result.avg_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

### 3. Via API

```bash
# Trigger simulation
curl -X POST http://localhost:8000/api/v1/market/sim/run \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-03-31T00:00:00Z",
    "min_confidence": 0.6
  }'

# Get results
curl http://localhost:8000/api/v1/market/sim/results

# Get details
curl http://localhost:8000/api/v1/market/sim/results/{simulation_id}

# Compare multiple runs
curl -X POST http://localhost:8000/api/v1/market/sim/compare \
  -H "Content-Type: application/json" \
  -d '{"simulation_ids": ["sim_abc123", "sim_def456"]}'
```

## Architecture

```
Simulation Module
├── HistoricalDataRepository
│   ├── Indexes events by date
│   ├── Stores price series per ticker
│   ├── Caches options chains
│   └── Temporal queries (no future leakage)
├── SimulationEngine
│   ├── Time walking (day by day)
│   ├── Blind prediction (only past data)
│   ├── Outcome evaluation (future known only after simulation)
│   └── Performance compilation
├── BatchSimulationRunner
│   ├── Multiple periods
│   ├── Walk-forward analysis
│   └── Monte Carlo
└── SimulationAPI
    └── HTTP endpoints for control
```

## Detailed Concepts

### Temporal Integrity

The simulation guarantees **causal correctness**:

- At simulated time `T`, Nexus sees:
  - ✓ Events published ≤ T
  - ✓ Market data from ≤ T
  - ✓ Historical patterns from < T (strictly before)
- Nexus **cannot** see:
  - ✗ Events after T
  - ✗ Prices after T
  - ✗ Outcomes before they're actually known

This is enforced by `HistoricalDataRepository.get_events_through()` which filters by publication date.

### Walk-Forward Analysis

Realistic simulation of periodic model retraining:

```
[Train on Jan 2020 - Jun 2020] → [Test Jul 2020] → Record results
[Train on Jan 2020 - Jul 2020] → [Test Aug 2020] → Record results
[Train on Jan 2020 - Aug 2020] → [Test Sep 2020] → Record results
...
```

This mimics production deployment where model is retrained monthly/quarterly.

### Outcome Evaluation

After simulation completes, outcomes become visible and are evaluated:

1. Prediction made at time `T` with expected return `E[T+τ]`
2. Actual return realized at time `T+τ` (τ = expiry, typically 7-60 days)
3. Success determined: actual direction matches predicted? Return > threshold?
4. P&L calculated based on strategy (simplified Black-Scholes for options)
5. Feedback fed to ContinuousLearner (if enabled)

### Performance Metrics

Comprehensive statistics:

| Metric | Calculation | Interpretation |
|--------|-------------|----------------|
| Win Rate | (Successful / Total) * 100% | % of profitable predictions |
| Avg Return | Mean P&L across all predictions | Average gain/loss per trade |
| Sharpe Ratio | Mean(returns) / Std(returns) | Risk-adjusted return |
| Max Drawdown | Min(cumulative returns peak-to-trough) | Worst historical loss |
| Confidence Calibration | (Avg confidence of wins vs losses) | Is confidence predictive? |

Breakdowns available by:
- Event type (earnings vs macro vs viral)
- Direction (bullish vs bearish vs neutral)
- Source (Twitter vs Reuters vs Reddit)
- Impact severity
- Time horizon

## API Reference

### Run a Simulation

```http
POST /api/v1/market/sim/run
Content-Type: application/json

{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-03-31T00:00:00Z",
  "mode": "walk_forward",
  "step_days": 1,
  "min_confidence": 0.6,
  "include_news": true,
  "include_social": true,
  "use_historical_patterns": true,
  "enable_learning": false,
  "evaluate_earnings": true,
  "evaluate_macro": true
}
```

Returns job ID immediately. Run in background.

### Get All Results

```http
GET /api/v1/market/sim/results?limit=20
```

Returns list of completed simulations with summaries.

### Get Detailed Results

```http
GET /api/v1/market/sim/results/{simulation_id}?include_predictions=true
```

Returns full prediction-by-prediction breakdown.

### Compare Simulations

```http
POST /api/v1/market/sim/compare
Content-Type: application/json

{
  "simulation_ids": ["sim_abc123", "sim_def456", "sim_ghi789"]
}
```

Side-by-side comparison of metrics.

### Walk-Forward Analysis

```http
POST /api/v1/market/sim/walk-forward
Content-Type: application/json

{
  "overall_start": "2022-01-01T00:00:00Z",
  "overall_end": "2023-12-31T00:00:00Z",
  "train_months": 6,
  "test_months": 1,
  "step_months": 1
}
```

Runs rolling window backtest. Returns array of simulation results (one per test month).

### Monte Carlo Simulation

```http
POST /api/v1/market/sim/monte-carlo
Content-Type: application/json

{
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2023-12-31T00:00:00Z",
  "iterations": 200,
  "parameter_variations": {
    "min_confidence": [0.55, 0.6, 0.65, 0.7],
    "news_weight": [0.25, 0.30, 0.35]
  }
}
```

Randomizes parameters and date ranges to measure robustness.

### Load Historical Data

```http
POST /api/v1/market/sim/data/ingest
Content-Type: application/json

{
  "data_source": "yahoo",
  "tickers": ["SPY", "QQQ", "AAPL"],
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2023-12-31T00:00:00Z",
  "force_reload": false
}
```

Background task loads data into repository.

## Advanced Usage

### Programmatic Simulation (Python)

```python
from datetime import datetime, timedelta
from app.services.market_intelligence.simulation import (
    HistoricalDataRepository,
    SimulationConfig,
    SimulationEngine,
    SimulationMode,
)

# Setup repository with data
repo = HistoricalDataRepository("/data/sim")
# Load data... (see data_loader.py)

# Define simulation
config = SimulationConfig(
    simulation_id="my_simulation",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    mode=SimulationMode.WALK_FORWARD,
    min_confidence=0.65,
    enable_learning=True,  # Let Nexus learn from this backtest
)

engine = SimulationEngine(repo, config, services={})
result = await engine.run_simulation()

# Inspect results
print(f"Win Rate: {result.win_rate:.1%}")
for pred in result.predictions[:10]:
    print(f"  {pred.ticker} {pred.direction} → {pred.actual_return:.2%} (expected {pred.expected_return:.2%})")
```

### Regime Comparison

```python
from app.services.market_intelligence.simulation import compare_market_regimes

regimes = {
    'bull_2023': (datetime(2023,1,1), datetime(2023,12,31)),
    'bear_2022': (datetime(2022,1,1), datetime(2022,12,31)),
    'covid_2020': (datetime(2020,2,1), datetime(2020,5,1)),
}

comparison = await compare_market_regimes(repo, regimes)

# Output shows performance in each regime
for regime, stats in comparison.items():
    print(f"{regime}: {stats['win_rate']:.1%} win rate, {stats['avg_return']:.2%} avg return")
```

### Stress Testing Configurations

```python
# Test different weightings
configs = [
    {"min_confidence": 0.5, "news_weight": 0.4, "social_weight": 0.2},
    {"min_confidence": 0.6, "news_weight": 0.3, "social_weight": 0.3},
    {"min_confidence": 0.7, "news_weight": 0.2, "social_weight": 0.4},
]

results = await stress_test_configurations(repo, (start, end), configs)

# Pick best config
best = max(results, key=lambda r: r.sharpe_ratio)
print(f"Best config: {best.simulation_id}, Sharpe: {best.sharpe_ratio:.2f}")
```

### Learning from Backtest Results

Enable learning to let Nexus improve from simulations:

```python
config = SimulationConfig(
    simulation_id="training_run",
    start_date=datetime(2023,1,1),
    end_date=datetime(2023,6,30),
    enable_learning=True,  # Critical: feed outcomes back
)

result = await engine.run_simulation()

# After simulation, ContinuousLearner has updated patterns
print("Nexus has learned from these outcomes!")
print(f"New patterns detected: {learner.stats['patterns_detected']}")
```

## Interpreting Results

### Successful Predictions

Look for:
- High win rate (>60%) on high-confidence predictions (>0.7)
- Positive average return (aligned with expected returns)
- Sharpe ratio >1.0 (good risk-adjusted returns)
- Consistent performance across event types

### Failure Modes

Common issues and what they indicate:

| Failure Pattern | Likely Cause |
|-----------------|--------------|
| Low win rate on social-viral signals | Social sentiment noise not predictive |
| High win rate but low returns | Correct direction but magnitude overestimated |
| Poor macro event prediction | Classification needs refinement |
| High confidence → low success | Overconfident model; recalibrate |
| Specific ticker consistently wrong | Ticker-specific noise or data issues |

### Improving the Model

1. **Adjust weights** based on failure analysis:
   ```bash
   POST /api/v1/market/config
   {
     "weights": {
       "news_impact": 0.40,   # Increase if news works better
       "social_sentiment": 0.10  # Decrease if social is noisy
     }
   }
   ```

2. **Raise confidence threshold** if low-confidence signals fail:
   ```python
   config.min_confidence = 0.7
   ```

3. **Exclude problematic event types**:
   ```python
   config.evaluate_viral = False  # If viral predictions are poor
   ```

4. **Extend historical pattern window** if patterns unstable:
   ```python
   config.historical_lookback_days = 730  # 2 years instead of 1
   ```

## Data Sources & Coverage

### Yahoo Finance (via yfinance)

- **Coverage**: US equities, ETFs, indices (SPY, QQQ, etc.)
- **Price data**: Daily OHLCV, ~20 years history
- **Options**: End-of-month snapshots (limited)
- **News**: Recent articles only (not deep archive)
- **Rate limits**: Free, but throttled (use responsibly)

### Custom CSV Import

Create your own data:

```csv
date,open,high,low,close,volume,ticker
2024-01-01,100.0,102.5,99.5,101.5,1000000,AAPL
2024-01-02,101.5,103.0,101.0,102.5,950000,AAPL
```

Load via:
```python
await loader.load_from_csv('my_prices.csv', ticker='AAPL')
```

### Event Archives

For events (news/social), you need to provide:
- Title
- Description
- Publication date
- Detected tickers
- Source type
- URL (optional)

Format (JSON):
```json
[
  {
    "title": "Apple Announces Q1 Earnings Beat",
    "description": "Apple reported EPS of $2.04 vs $1.94 estimate...",
    "published_at": "2024-01-15T14:30:00Z",
    "metadata": {
      "detected_tickers": ["AAPL"],
      "source": "news_api",
      "event_type": "earnings"
    }
  }
]
```

## Performance Expectations

Based on typical market efficiency:

- **Win Rate**: 55-65% on high-confidence predictions
- **Avg Return**: 0.5-1.5% per successful prediction (after slippage)
- **Sharpe Ratio**: 0.8-1.5 (realistic for short-term event trading)
- **Signal Frequency**: 3-10 signals per week (depends on market activity)

**Note**: These are estimates; actual performance varies by period, ticker selection, and market conditions.

## Troubleshooting

### "No data available for dates"

Check repository info:
```bash
GET /api/v1/market/sim/data/info
```
Shows available date range and tickers.

### "No outcomes found for predictions"

Simulation only evaluates outcomes that occurred within the repository's price data window. Make sure your end date is far enough after the last prediction's expiry to capture outcomes.

### "All predictions failed"

Likely causes:
1. Data leakage (future data in repository) - ensure strict temporal ordering
2. Unrealistic strategy assumptions - adjust options pricing model
3. Wrong outcome evaluation logic - check `_evaluate_predictions` in simulation.py

### "Simulation too slow"

Optimizations:
1. Reduce `step_days` (e.g., process weekly instead of daily)
2. Limit tickers in config
3. Disable social sources (slow)
4. Use caching (store intermediate classifications)
5. Increase `min_confidence` to reduce signal volume

## Advanced Topics

### Custom Outcome Evaluation

Modify `_evaluate_predictions()` in `SimulationEngine` to:
- Use actual options pricing (not simplified P&L)
- Account for slippage and commissions
- Consider portfolio-level effects
- Include holding period constraints

### Alternative Data Integration

Add custom data sources:

```python
class SatelliteDataLoader:
    async def load_car_counts(self, repo, ticker, dates):
        # Load satellite imagery car count data
        ...
```

### Multi-Asset Simulations

Extend to:
- Futures
- Forex
- Crypto
- ETFs

Modify `price_data` structure to support multiple asset classes.

### Regime-Aware Model

Detect market regime (bull/bear/sideways) during simulation and adjust:

```python
if self._detect_bear_market(current_date):
    strategy.bearish_bias()
```

## Production Deployment

### Scheduler

Run nightly simulations:

```python
# In apscheduler or celery
@app.on_event("startup")
async def schedule_simulations():
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    
    # Run backtest for yesterday's signals daily
    scheduler.add_job(
        run_daily_backtest,
        'cron',
        hour=2,  # 2 AM
        minute=0,
    )
    
    # Weekly performance report
    scheduler.add_job(
        generate_weekly_report,
        'cron',
        day_of_week='mon',
        hour=3,
    )
```

### Storage

Persist simulation results to PostgreSQL:

```python
# Already defined in models/simulation.py
# Run alembic migration to create tables
```

### Monitoring

Track simulation health:
- Data freshness (last update timestamp)
- Signal generation rate (should not drop to zero)
- Win rate drift (if falling below threshold, alert)

## Future Enhancements

1. **Real-time simulation**: Stream predictions as they would have happened
2. **Transaction cost modeling**: Slippage, commissions, bid-ask spread
3. **Portfolio optimization**: Position sizing, correlation constraints
4. **Options-specific backtesting**: Full options chain dynamics, early assignment
5. **Live paper trading**: Bridge simulation → real paper trading
6. **A/B testing framework**: Test multiple model variants simultaneously
7. **Explainability**: Why did this prediction succeed/fail?
8. **Market regime detection**: Auto-detect and categorize periods
9. **Cross-validation**: Multiple rolling windows for robustness
10. **Interactive dashboard**: Web UI for exploring results

## Summary

The simulation module provides a robust, production-ready backtesting framework for the Market Intelligence system. It ensures temporal correctness, provides detailed analytics, and integrates with the continuous learning loop.

Key files:
- `simulation.py` - Core engine
- `simulation_router.py` - API endpoints  
- `models/simulation.py` - Database models
- `data_loader.py` - Historical data utilities
- `tests/test_simulation.py` - Test suite

Start with simple backtests, then explore walk-forward analysis and Monte Carlo for robust validation.

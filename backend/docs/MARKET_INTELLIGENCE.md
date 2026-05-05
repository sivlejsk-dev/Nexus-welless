# Market Intelligence Module

Comprehensive options trading prediction engine that ingests global news and social media data, classifies market-moving events, analyzes historical patterns, and generates trading signals with continuous learning.

## Architecture

```
Nexus Market Intelligence
├── Data Ingestion
│   ├── News Ingestor (RSS, NewsAPI, 财经新闻)
│   └── Social Media Ingestor (Twitter, Reddit, StockTwits, Sentiment APIs)
├── Event Classification Engine
│   ├── Natural Language Processing (sentiment, keywords)
│   ├── Impact Severity (minimal → extreme)
│   ├── Direction Bias (bullish/bearish/neutral)
│   └── Topic Categorization (earnings, M&A, macro, etc.)
├── Historical Pattern Matcher
│   ├── Event Similarity Engine
│   ├── Outcome Statistics
│   └── Pattern Clustering
├── Options Impact Analyzer
│   ├── IV Prediction & Skew Analysis
│   ├── Strike Selection (delta/probability)
│   └── Strategy Recommendation Engine
├── Decision Engine
│   ├── Weighted Factor Aggregation
│   ├── Confidence Calibration
│   └── Risk-Adjusted Ranking
└── Learning Integration
    ├── ContinuousLearner Integration
    └── Outcome Feedback Loop
```

## Features

### 1. Multi-Source Data Ingestion

**News Sources:**
- RSS feeds (Reuters, Yahoo Finance, MarketWatch, SeekingAlpha, Benzinga)
- NewsAPI (top business headlines)
- Chinese financial news (东方财富, 新浪财经)

**Social Media Sources:**
- Twitter/X (financial tweets via API v2)
- Reddit (wallstreetbets, stocks, investing, options)
- StockTwits (real-time stock sentiment)
- Sentiment APIs (Finnhub social sentiment)

### 2. Event Classification

Automatically determines:
- **Type**: earnings, merger, regulatory, product launch, management change, legal, macroeconomic, geopolitical, viral trend, analyst upgrade, institutional action
- **Impact Severity**: minimal → low → medium → high → critical → extreme
- **Direction**: bullish, bearish, neutral, or mixed
- **Time Horizon**: immediate (hours), short-term (1-7 days), medium-term (1-4 weeks), long-term (1+ months)
- **Affected Sectors & Tickers**: extracted from content
- **Sentiment**: polarity (-1 to +1), subjectivity, emotion detection

### 3. Historical Pattern Matching

Matches current events to similar historical situations:
- Stores event outcomes (actual price moves, options volume changes)
- Computes similarity scores (event type, sectors, sentiment, impact)
- Returns top-N patterns with statistics:
  - Win rate
  - Average return
  - Pattern strength
  - Sample size

### 4. Options Strategy Recommendations

Translates signals into actionable trades:
- **Directional strategies** (long calls/puts, spreads) when direction confident
- **Volatility strategies** (straddles/strangles) when IV expansion expected
- **Income strategies** (credit spreads, iron condors) when neutral
- Recommends:
  - Strike prices (based on delta targets or probability)
  - Expiry dates (aligned with time horizon)
  - Risk metrics (max loss, probability of profit, Greeks)

### 5. Weighted Decision Engine

Aggregates multiple factors with customizable weights:
- News impact (30%)
- Social sentiment (25%)
- Historical patterns (30%)
- Volatility skew (10%)
- Liquidity (5%)

Confidence-adjusted scoring prevents overconfidence.

### 6. Continuous Learning Integration

Feeds outcomes back into Nexus's ContinuousLearner:
- Records prediction success/failure
- Updates pattern win rates
- Tracks source reliability
- Adapts factor weights over time

## Installation & Configuration

### 1. Add API Keys to Environment

```bash
# In .env file or environment variables
NEWSAPI_KEY=your_newsapi_key
TWITTER_BEARER_TOKEN=your_twitter_token
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
FINNHUB_API_KEY=your_finnhub_key
```

### 2. Install Dependencies

Market intelligence requires a few additional packages:

```bash
# Already in requirements.txt:
# - textblob (sentiment analysis)
# - httpx (async HTTP)
# - beautifulsoup4 (web scraping)
pip install textblob beautifulsoup4 lxml
python -m textblob.download_corpora
```

### 3. Add Database Models (Optional for Production)

For persistent storage of events and outcomes:

```python
# In app/models/market.py
from sqlalchemy import Column, String, DateTime, Float, Boolean, JSON, ForeignKey
from app.db.base import Base

class MarketEventDB(Base):
    __tablename__ = "market_events"
    id = Column(UUID, primary_key=True)
    source = Column(String)
    title = Column(String)
    tickers = Column(JSON)  # JSON array of tickers
    event_type = Column(String)
    impact_severity = Column(String)
    direction = Column(String)
    confidence = Column(Float)
    published_at = Column(DateTime)
    # ...

class SignalDB(Base):
    __tablename__ = "trading_signals"
    # ... similar structure
```

### 4. Register Background Jobs

Add to your scheduler (Celery, APScheduler, or cron):

```python
# Run every 15 minutes
@app.on_event("startup")
async def schedule_market_ingest():
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=run_market_cycle,
        trigger="interval",
        minutes=15,
        id="market_ingest"
    )
    scheduler.start()

async def run_market_cycle():
    """Trigger ingestion + analysis + signal generation"""
    from app.routers.market_intelligence import ingest_cycle
    await ingest_cycle()
```

## API Usage

### Trigger Ingestion Cycle

```bash
POST /api/v1/market/ingest
```

```json
{
  "since": "2024-01-15T00:00:00Z"  // optional
}
```

Response:
```json
{
  "job_id": "uuid-here",
  "status": "started",
  "message": "Cycle running in background"
}
```

### Get Latest Signals

```bash
GET /api/v1/market/signals?limit=10&min_confidence=0.7
```

Response:
```json
[
  {
    "signal_id": "...",
    "ticker": "AAPL",
    "direction": "bullish",
    "confidence": 0.82,
    "strategy": "Long Calls",
    "expected_return": 0.15,
    "max_loss": 0.05,
    "target_strike": 175.50,
    "generated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Record Outcome (Manual or Automated)

```bash
POST /api/v1/market/signals/{signal_id}/outcome
```

```json
{
  "actual_return": 0.042,
  "success": true
}
```

### Get Performance Analytics

```bash
GET /api/v1/market/analytics
```

Response:
```json
{
  "overall": {
    "win_rate": 0.68,
    "avg_return": 0.032,
    "sharpe": 1.45
  },
  "by_event_type": { ... },
  "by_source": { ... },
  "pending_signals": 3,
  "completed_signals": 147
}
```

### Health Check

```bash
GET /api/v1/market/health
```

### Configuration Updates

```bash
POST /api/v1/market/config
```

```json
{
  "weights": {
    "news_impact": 0.40,
    "social_sentiment": 0.20,
    "historical_patterns": 0.25
  },
  "min_signal_score": 0.5
}
```

## Customization Guide

### Adding a New Data Source

1. Create a class inheriting from `BaseDataSource`:

```python
from app.services.market_intelligence.base import BaseDataSource
from app.services.market_intelligence.schemas import MarketEvent, DataSource

class MyNewSource(BaseDataSource):
    def __init__(self, config):
        super().__init__(config)
        self.source_type = DataSource.UNKNOWN  # Or add new enum value

    async def connect(self):
        # Initialize connection
        return True

    async def fetch_events(self, since=None):
        # Fetch and return List[MarketEvent]
        events = []
        # ... your logic
        return events
```

2. Register in `NewsIngestor` or `SocialMediaIngestor`:

```python
# In _initialize_sources():
self.sources.append(MyNewSource(self.config))
```

### Adjusting Classification Rules

Modify keyword dictionaries in `EventClassifier`:

```python
# Add custom event type keywords
EVENT_KEYWORDS[EventType.MY_NEW_TYPE] = {'keyword1', 'keyword2', 'keyword3'}

# Add sector keywords
SECTOR_KEYWORDS['crypto'] = {'bitcoin', 'ethereum', 'blockchain'}
```

### Custom Strategy Logic

Override `_recommend_strategy` in `OptionsImpactAnalyzer`:

```python
class CustomOptionsAnalyzer(OptionsImpactAnalyzer):
    async def _recommend_strategy(self, ...):
        # Your custom logic
        # Return OptionStrategy object
```

### Changing Decision Weights

Via API:
```bash
curl -X POST /api/v1/market/config \
  -H "Content-Type: application/json" \
  -d '{"weights": {"news_impact": 0.5, "social_sentiment": 0.3}}'
```

Or programmatically:
```python
decision.weights['news_impact'] = 0.5
decision.weights['social_sentiment'] = 0.3
```

## Monitoring & Observability

### Structured Logging

The module uses `structlog` for structured logs:

```json
{
  "event": "market_cycle_complete",
  "events_ingested": 47,
  "signals_generated": 3,
  "duration_seconds": 12.4,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Metrics to Track

- Ingestion throughput (events/minute)
- Classification confidence distribution
- Signal win rate by event type
- Average P&L per signal
- Time to outcome (signal → evaluation)
- Pattern database size & update frequency

### Alerting Considerations

Set alerts for:
- No signals generated in >24h (pipeline stalled)
- Consecutive signal failures >5 (model degradation)
- API rate limit warnings
- Data source failures (health check failures)

## Production Deployment

### 1. Enable Database Persistence

Replace in-memory storage with SQLAlchemy models:

```python
# Modified HistoricalPatternMatcher
async def store_outcome(self, outcome: Dict):
    async with self.db_session() as session:
        session.add(OutcomeModel(**outcome))
        await session.commit()
```

### 2. Use Redis for Caching

Cache frequent queries:
- Recent events
- Historical patterns
- Signal history

### 3. Horizontal Scaling

Services are stateless except for:
- Pattern database (shared Redis or database)
- ContinuousLearner state (Redis with persistence)
- Signal history (PostgreSQL)

Use a queue (e.g., Redis Queue, Celery) for ingestion tasks.

### 4. Rate Limiting & Costs

Monitor API usage:
- Twitter API: free tier ~500k tweets/month (track carefully)
- NewsAPI: free tier 1000 requests/day
- Finnhub: free tier 60 calls/minute

Implement local aggressive caching to minimize costs.

### 5. Disaster Recovery

- Pattern database backups daily
- Event outcome archive (S3/GCS)
- Configuration as code (environment variables in CI/CD)

## Troubleshooting

### No Signals Generated

1. Check ingestion is running: `GET /health` should show source status
2. Lower `min_confidence_threshold` in config
3. Review classification confidence in logs

### Low Win Rate

1. Check analytics: `GET /analytics` to see which segments underperform
2. Adjust weights to de-emphasize poor factors
3. Consider removing consistently wrong sources

### API Rate Limits

1. Spread out calls over time (don't poll rapidly)
2. Implement exponential backoff on 429 errors
3. Cache aggressively

### High Memory Usage

1. Limit historical pattern cache size
2. Prune outcomes older than 90 days
3. Use database queries instead of in-memory lists

## Future Enhancements

- [x] **Historical simulation & backtesting**: Test predictions against past periods without outcome peeking (see `docs/SIMULATION.md`)
- **Real-time WebSocket feed** for immediate signal streaming
- **Options chain analysis** for precise entry/exit prices
- **Portfolio-level optimization** across multiple signals
- **Alternative data**: satellite imagery, credit card transactions, supply chain data
- **ML-based classification** (BERT/FinBERT) instead of keyword matching
- **Regime detection** (bull/bear/sideways) and adaptive strategies
- **Options Greeks live calculations** with live market data
- **Backtesting framework** for strategy validation
- **User preferences** for risk tolerance, ticker allowlist, sector focus
- **Natural language queries**: "What should I trade today?"

## Simulation & Backtesting

The Market Intelligence module includes a comprehensive **simulation engine** ([docs/SIMULATION.md](docs/SIMULATION.md)) for historical testing:

### Features

- **Temporal integrity**: Guaranteed no future data leakage
- **Walk-forward analysis**: Periodic retraining simulation
- **Batch testing**: Multiple periods, regimes, configurations
- **Monte Carlo**: Robustness testing via parameter randomization
- **Learning integration**: Feed backtest outcomes into ContinuousLearner

### Quick Start

```python
# Load historical data
repo = HistoricalDataRepository("/data/sim")
await load_standard_market_data(repo, tickers=['SPY','QQQ'], 
                               start=datetime(2023,1,1), 
                               end=datetime(2023,12,31))

# Run backtest
result = await backtest_period(repo, 
                              datetime(2023,1,1), 
                              datetime(2023,3,31))
print(f"Win Rate: {result.win_rate:.1%}")
```

### API

- `POST /api/v1/market/sim/run` - Start simulation
- `GET /api/v1/market/sim/results` - List completed runs
- `GET /api/v1/market/sim/results/{id}` - Detailed breakdown
- `POST /api/v1/market/sim/compare` - Compare multiple runs
- `POST /api/v1/market/sim/walk-forward` - Rolling window test
- `POST /api/v1/market/sim/monte-carlo` - Stress testing

See **[full simulation documentation](docs/SIMULATION.md)** for details.

## License & Support

Part of Nexus Wellness Platform. See repository for license.

For issues or feature requests, open a GitHub issue or contact the Nexus team.

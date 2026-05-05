# Market Intelligence Module

## Overview

A comprehensive options trading prediction engine integrated into Nexus that continuously ingests global news and social media data, classifies market-moving events, analyzes historical patterns, and generates trading signals with continuous learning.

## Quick Start

### 1. Configure API Keys (`.env`)

```bash
NEWSAPI_KEY=your_key
TWITTER_BEARER_TOKEN=your_token
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
FINNHUB_API_KEY=your_key
```

### 2. Install Dependencies

```bash
pip install textblob beautifulsoup4 lxml
python -m textblob.download_corpora
```

### 3. Start Ingestion

```bash
# Trigger via API
curl -X POST http://localhost:8000/api/v1/market/ingest

# Or include in scheduler (runs every 15 minutes)
```

### 4. Get Signals

```bash
curl http://localhost:8000/api/v1/market/signals?limit=10
```

### 5. Record Outcomes

```bash
curl -X POST http://localhost:8000/api/v1/market/signals/{id}/outcome \
  -H "Content-Type: application/json" \
  -d '{"actual_return": 0.042, "success": true}'
```

## Module Structure

```
backend/app/services/market_intelligence/
├── __init__.py                    # Public API exports
├── schemas.py                     # Pydantic data models
├── base.py                        # Abstract base classes
├── news_ingestor.py               # RSS, NewsAPI, 财经新闻
├── social_ingestor.py             # Twitter, Reddit, StockTwits
├── classifier.py                  # Event classification & sentiment
├── historical.py                  # Pattern matching engine
├── options_analyzer.py            # Options strategy generator
├── decision_engine.py             # Weighted scoring & signals
└── learning_integration.py        # ContinuousLearner bridge

backend/app/routers/
└── market_intelligence.py         # FastAPI endpoints

backend/app/
├── core/config.py                 # Settings (added API keys)
└── main.py                        # Router registration

backend/tests/
└── test_market_intelligence.py    # Comprehensive unit tests

backend/docs/
└── MARKET_INTELLIGENCE.md         # Full documentation
```

## Key Capabilities

### Data Ingestion
- **20+ news RSS feeds**: Reuters, Yahoo Finance, MarketWatch, SeekingAlpha, Benzinga
- **NewsAPI**: Global business headlines
- **Chinese financial news**: Eastmoney, Sina Finance
- **Social media**: Twitter/X, Reddit (WSB, stocks, options, investing), StockTwits
- **Sentiment APIs**: Finnhub social sentiment data

### Event Classification
- **Event types**: 12 categories (earnings, M&A, regulatory, product launch, management, legal, macro, geopolitical, viral, analyst, institutional, sector shift)
- **Impact severity**: 6-level scale (minimal → extreme)
- **Direction**: Bullish, bearish, neutral, mixed
- **Time horizon**: Immediate, short, medium, long term
- **Tickers & sectors**: Automatic extraction

### Historical Analysis
- Stores event outcomes (price moves, IV changes, options volume)
- Similarity-based pattern matching
- Statistical outcome aggregation (win rate, average return, Sharpe ratio)

### Options Strategies
- Directional (long calls/puts, spreads)
- Volatility (straddles, strangles)
- Income (credit spreads, iron condors)
- Risk metrics (expected value, Greeks, max loss)

### Continuous Learning
- Tracks prediction success/failure
- Feeds into Nexus ContinuousLearner
- Adapts weights based on performance
- Pattern database refinement

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/market/health` | Health check of all sources |
| POST | `/api/v1/market/ingest` | Trigger ingestion cycle |
| GET | `/api/v1/market/events` | List recent classified events |
| GET | `/api/v1/market/signals` | Get trading signals |
| POST | `/api/v1/market/signals/{id}/outcome` | Record trade outcome |
| GET | `/api/v1/market/analytics` | Performance statistics |
| GET | `/api/v1/market/patterns` | Historical pattern summaries |
| POST | `/api/v1/market/config` | Update runtime config |

## Configuration

```python
class MarketIntelligenceSettings:
    # Data sources
    enabled_sources: List[DataSource]
    news_refresh_minutes: int = 15
    social_refresh_seconds: int = 60
    
    # Classification
    min_confidence_threshold: float = 0.6  # 0-1
    
    # Historical
    historical_lookback_days: int = 365
    min_pattern_samples: int = 10
    pattern_similarity_threshold: float = 0.7
    
    # Decision weights (must sum to 1.0)
    weights = {
        "news_impact": 0.30,
        "social_sentiment": 0.25,
        "historical_pattern": 0.30,
        "volatility_skew": 0.10,
        "liquidity": 0.05,
    }
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
pytest tests/test_market_intelligence.py -v
```

Key test coverage:
- Sentiment analysis accuracy
- Event classification correctness
- Pattern matching similarity
- Options Greeks calculations
- Decision engine weighting
- API endpoint functionality
- Performance benchmarks (100 events/sec throughput)

## Production Considerations

### Scalability
- All services are stateless; horizontal scale ready
- Redis for pattern caching (optional)
- Database persistence for events/outcomes
- Queue-based async processing (Celery/Redis Queue)

### Cost Management
- Cache aggressively to minimize API calls
- Batch social media fetches
- Respect rate limits with exponential backoff

### Monitoring
- Structured logs (uses structlog)
- Health checks per source
- Performance metrics (latency, throughput, accuracy)

### Risk Management
- Position size limits (`max_position_size_pct`)
- Daily signal caps (`max_daily_signals`)
- Liquidity filters
- Confidence thresholds

## Extending the System

### Adding a Custom Source

```python
class AlphaVantageSource(BaseDataSource):
    source_type = DataSource.ALPHA_VANTAGE
    
    async def fetch_events(self, since=None):
        # Fetch news from Alpha Vantage
        ...
```

### Custom Strategy

```python
class CustomStrategyAnalyzer:
    def recommend(self, event, classification):
        # Return custom OptionStrategy
        ...
```

### ML Classifier Integration

Replace keyword-based classifier with ML model:

```python
class MLClassifier(EventClassifier):
    async def classify(self, event):
        # Load FinBERT model
        # Generate embeddings
        # Predict with trained classifier
        ...
```

## Learning Loop

1. **Signal Generated** → stored with metadata
2. **Outcome Realized** (7 days later by default)
3. **Success Evaluated** (actual vs predicted)
4. **Feedback to Learner**:
   - Reinforces successful patterns
   - Documents failures as error patterns
   - Adjusts factor weights over time
5. **Model Adaptation** → better future predictions

## Example Workflow

```
[Ingest]    Reuters: "Apple beats earnings" → MarketEvent
               ↓
[Classify]  EventType.EARNINGS, Impact.HIGH, Direction.BULLISH, Confidence=0.85
               ↓
[Patterns]  Matched 42 similar earnings beats → avg return +2.3%, win rate 68%
               ↓
[Options]   IV likely to crush 30% → recommend selling premium
               ↓
[Decision]  Score = +0.72 (strong bullish) → signal generated
               ↓
[Store]     Signal recorded + learning pattern created
               ↓
[7 Days]    Automatic outcome check → actual return +1.8% (success!)
               ↓
[Learn]     Feedback to ContinuousLearner: pattern confidence ↑, weight ↑
```

## Support

For questions, issues, or contributions, please refer to the main repository or contact the Nexus Intelligence team.

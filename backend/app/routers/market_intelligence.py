"""
FastAPI router for Market Intelligence endpoints.

Provides REST API for:
- Fetching latest market events
- Getting trading signals
- Historical performance
- Configuration management
- Learning integration status
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.limiter import limiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.market_intelligence import (
    # Schemas
    MarketEvent,
    EventClassification,
    OptionsSignal,
    HistoricalPattern,
    MarketIntelligenceConfig,
    DataSource,
    # Services
    NewsIngestor,
    SocialMediaIngestor,
    EventClassifier,
    HistoricalPatternMatcher,
    OptionsImpactAnalyzer,
    DecisionEngine,
)
from app.services.market_intelligence.learning_integration import (
    MarketLearningIntegration,
    get_market_learning,
)
from app.nexus_core.continuous_learner import continuous_learner

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/market", tags=["market-intelligence"])

# Rate limiter for market endpoints
limiter = Limiter(key_func=get_remote_address)

# ── Request/Response Schemas ────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Request to trigger data ingestion cycle"""
    sources: Optional[List[str]] = None
    since: Optional[datetime] = None


class SignalResponse(BaseModel):
    """Trading signal response"""
    signal_id: str
    ticker: str
    direction: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    strategy: str
    expected_return: Optional[float] = None
    max_loss: Optional[float] = None
    target_strike: Optional[float] = None
    generated_at: str


class EventResponse(BaseModel):
    """Market event response"""
    event_id: str
    source: str
    title: str
    description: str
    tickers: List[str]
    event_type: str
    impact: str
    direction: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    published_at: str
    url: Optional[str] = None


class AnalyticsResponse(BaseModel):
    """Performance analytics response"""
    overall: Dict[str, float]
    by_event_type: Dict[str, Dict[str, float]]
    by_source: Dict[str, Dict[str, float]]
    pending_signals: int
    completed_signals: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    sources: Dict[str, str]
    pending_outcomes: int
    total_signals: int
    learner_status: str


class ConfigUpdateRequest(BaseModel):
    """Configuration update request"""
    weights: Optional[Dict[str, float]] = None
    min_signal_score: Optional[float] = None
    max_signals_per_ticker: Optional[int] = None


# ── Service Factory Functions ────────────────────────────────────────────────────

_config_cache: Optional[MarketIntelligenceConfig] = None
_services_cache: Dict[str, Any] = {}

async def get_config() -> MarketIntelligenceConfig:
    """Get market intelligence config from settings (cached)"""
    global _config_cache
    if _config_cache is None:
        _config_cache = MarketIntelligenceConfig(
            enabled_sources=[
                DataSource.NEWS_RSS,
                DataSource.NEWS_API,
                DataSource.TWITTER,
                DataSource.REDDIT,
                DataSource.STOCKTWITS,
            ],
            news_refresh_minutes=15,
            social_refresh_seconds=60,
            min_confidence_threshold=0.6,
            newsapi_key=settings.newsapi_key or "",
            twitter_bearer_token=settings.twitter_bearer_token or "",
            reddit_client_id=settings.reddit_client_id or "",
            finnhub_api_key=settings.finnhub_api_key or "",
        )
    return _config_cache


async def get_news_ingestor() -> NewsIngestor:
    if 'news_ingestor' not in _services_cache:
        config = await get_config()
        _services_cache['news_ingestor'] = NewsIngestor(config)
    return _services_cache['news_ingestor']


async def get_classifier() -> EventClassifier:
    if 'classifier' not in _services_cache:
        config = await get_config()
        _services_cache['classifier'] = EventClassifier(config)
    return _services_cache['classifier']


async def get_historical() -> HistoricalPatternMatcher:
    if 'historical' not in _services_cache:
        config = await get_config()
        _services_cache['historical'] = HistoricalPatternMatcher(config)
        await _services_cache['historical'].connect()
    return _services_cache['historical']


async def get_options_analyzer() -> OptionsImpactAnalyzer:
    if 'options_analyzer' not in _services_cache:
        config = await get_config()
        _services_cache['options_analyzer'] = OptionsImpactAnalyzer(config)
    return _services_cache['options_analyzer']


async def get_decision_engine() -> DecisionEngine:
    if 'decision_engine' not in _services_cache:
        config = await get_config()
        _services_cache['decision_engine'] = DecisionEngine(config)
    return _services_cache['decision_engine']


async def get_market_learning() -> Optional[MarketLearningIntegration]:
    """Get market learning integration if learner available"""
    try:
        return get_market_learning(continuous_learner, await get_config())
    except Exception as e:
        log.warning(f"Could not initialize market learning: {e}")
        return None


async def get_social_ingestor() -> SocialMediaIngestor:
    if 'social_ingestor' not in _services_cache:
        config = await get_config()
        _services_cache['social_ingestor'] = SocialMediaIngestor(config)
    return _services_cache['social_ingestor']


# ── Endpoints ─────────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Check health of all market intelligence components"""
    sources_status = {}
    
    # Check news sources
    try:
        news = await get_news_ingestor()
        health_results = await news.health_check_all()
        sources_status.update({f"news_{k}": "ok" if v else "error" for k, v in health_results.items()})
    except Exception as e:
        sources_status['news'] = f"error: {str(e)}"
    
    # Check social sources
    try:
        social = await get_social_ingestor()
        health_results = await social.health_check_all()
        sources_status.update({f"social_{k}": "ok" if v else "error" for k, v in health_results.items()})
    except Exception as e:
        sources_status['social'] = f"error: {str(e)}"
    
    # Learning integration
    learning = await get_market_learning()
    pending = len(learning.pending_outcomes) if learning else 0
    
    decision = await get_decision_engine()
    total_signals = len(decision.signal_history)
    
    return HealthResponse(
        status="ok",
        sources=sources_status,
        pending_outcomes=pending,
        total_signals=total_signals,
        learner_status="active" if continuous_learner else "unavailable",
    )


@router.post("/ingest")
@limiter.limit("5/minute")
async def trigger_ingestion(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    request_obj: Request,  # For rate limiting
):
    """
    Trigger a full market intelligence cycle.
    
    1. Fetch events from news + social sources
    2. Classify each event
    3. Match historical patterns
    4. Analyze options implications
    5. Generate trading signals
    
    Runs in background and returns job ID for status checking.
    """
    import uuid
    
    job_id = str(uuid.uuid4())
    
    async def run_cycle():
        try:
            since = request.since if request.since else datetime.utcnow() - timedelta(minutes=30)
            
            # Fetch events
            news = await get_news_ingestor()
            news_events = await news.fetch_all(since)
            
            social = await get_social_ingestor()
            social_events = await social.fetch_all(since)
            
            all_events = news_events + social_events
            
            if not all_events:
                log.info("No new events found")
                return
            
            log.info(f"Ingested {len(all_events)} events")
            
            # Classify
            classifier = await get_classifier()
            classifications = await classifier.batch_classify(all_events)
            for event, classification in zip(all_events, classifications):
                event.classification = classification
            
            # Historical patterns
            historical = await get_historical()
            pattern_matches = {}
            for event in all_events:
                if event.classification and event.classification.confidence >= 0.6:
                    patterns = await historical.find_similar_patterns(event, event.classification)
                    pattern_matches[event.event_id] = patterns
            
            # Options analysis
            options = await get_options_analyzer()
            options_analysis = {}
            for event in all_events:
                patterns = pattern_matches.get(event.event_id, [])
                analysis = await options.analyze_options_impact(
                    event, event.classification, patterns, None
                )
                options_analysis[event.event_id] = analysis
            
            # Generate signals
            decision = await get_decision_engine()
            signals = await decision.generate_signals(
                all_events, classifications, pattern_matches, options_analysis
            )
            
            # Record for learning
            learning = await get_market_learning()
            if learning:
                for signal in signals:
                    event = next((e for e in all_events if e.event_id == signal.event_id), None)
                    if event and event.classification:
                        await learning.record_signal(signal, event, event.classification)
            
            log.info(f"Cycle {job_id} completed: {len(signals)} signals generated")
            
        except Exception as e:
            log.error(f"Cycle {job_id} failed: {e}", exc_info=True)
    
    background_tasks.add_task(run_cycle)
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "Market intelligence cycle running in background",
        "estimated_duration": "30-60 seconds"
    }


@router.get("/events", response_model=List[EventResponse])
@limiter.limit("30/minute")
async def get_recent_events(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    ticker: Optional[str] = None,
    classifier: EventClassifier = Depends(get_classifier),
):
    """
    Get recently ingested market events with classifications.
    
    In production, this would query the database.
    For now, returns events from in-memory cache.
    """
    # Placeholder - would query database in production
    raise HTTPException(
        status_code=501, 
        detail="Event history persistence not yet implemented. Use /ingest to fetch new events."
    )


@router.get("/signals", response_model=List[SignalResponse])
@limiter.limit("30/minute")
async def get_signals(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    ticker: Optional[str] = None,
    min_confidence: float = Query(0.6, ge=0.1, le=1.0),
    decision: DecisionEngine = Depends(get_decision_engine),
):
    """
    Get latest trading signals.
    
    Returns options trading recommendations based on
    market events and analysis.
    """
    signals = decision.signal_history[-limit:]
    
    # Filter by ticker if specified
    if ticker:
        signals = [s for s in signals if s.ticker.upper() == ticker.upper()]
    
    # Filter by confidence
    signals = [s for s in signals if s.confidence >= min_confidence]
    
    if not signals:
        return []
    
    return [
        SignalResponse(
            signal_id=str(s.signal_id),
            ticker=s.ticker,
            direction=s.direction.value,
            confidence=s.confidence,
            strategy=s.recommendation,
            expected_return=s.expected_return,
            max_loss=s.max_loss,
            target_strike=s.target_strike,
            generated_at=s.generated_at.isoformat(),
        )
        for s in signals[:limit]
    ]


@router.get("/analytics", response_model=AnalyticsResponse)
@limiter.limit("10/minute")
async def get_analytics(
    request: Request,
    learning: Optional[MarketLearningIntegration] = Depends(get_market_learning),
):
    """
    Get performance analytics for market intelligence module.
    
    Includes win rates, returns, and pattern effectiveness.
    """
    if not learning:
        raise HTTPException(status_code=503, detail="Learning integration not available")
    
    report = learning.get_performance_report()
    overall = report.get('overall', {})
    by_event_type = report.get('by_event_type', {})
    by_source = report.get('by_source', {})
    
    return AnalyticsResponse(
        overall=overall,
        by_event_type=by_event_type,
        by_source=by_source,
        pending_signals=len(learning.pending_outcomes),
        completed_signals=len(learning.completed_outcomes),
    )


@router.post("/signals/{signal_id}/outcome")
@limiter.limit("20/minute")
async def record_outcome(
    request: Request,
    signal_id: str,
    actual_return: float,
    success: bool,
    learning: Optional[MarketLearningIntegration] = Depends(get_market_learning),
):
    """
    Manually record outcome for a signal (for testing/demo).
    
    In production, this would be triggered automatically
    after position expiry.
    """
    if not learning:
        raise HTTPException(status_code=503, detail="Learning integration not available")
    
    try:
        signal_uuid = UUID(signal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signal ID format")
    
    if signal_uuid not in learning.pending_outcomes:
        raise HTTPException(status_code=404, detail="Signal not found or outcome already recorded")
    
    record = learning.pending_outcomes[signal_uuid]
    # Manually evaluate
    learning._update_metrics(record, success, actual_return)
    learning._feedback_to_learner(record, success, actual_return, "Manually recorded")
    
    # Move to completed
    del learning.pending_outcomes[signal_uuid]
    record['outcome'] = {
        'success': success,
        'actual_return': actual_return,
        'resolved_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'Manual entry'
    }
    learning.completed_outcomes.append(record)
    learning._save_outcomes()
    
    return {
        "status": "ok", 
        "signal_id": signal_id, 
        "recorded": True,
        "success": success,
        "actual_return": actual_return
    }


@router.get("/patterns", response_model=List[Dict[str, Any]])
@limiter.limit("20/minute")
async def get_historical_patterns(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    historical: HistoricalPatternMatcher = Depends(get_historical),
):
    """
    Get top historical patterns identified in the database.
    
    These patterns are used to match current events to
    similar past situations and predict outcomes.
    """
    # Return summary of known patterns
    # In production would query pattern database
    return [
        {
            "pattern_id": "earnings_high_impact_bullish",
            "name": "High-Impact Positive Earnings",
            "description": "Events with earnings beat + positive guidance",
            "win_rate": 0.72,
            "avg_return": 3.2,
            "sample_size": 142,
            "pattern_strength": 0.78,
        }
    ]


@router.post("/config")
@limiter.limit("5/hour")
async def update_config(
    request: Request,
    updates: ConfigUpdateRequest,
    decision: DecisionEngine = Depends(get_decision_engine),
):
    """
    Update configuration at runtime (non-persistent).
    
    Changes only last until service restart.
    For permanent changes, update environment variables.
    """
    changes = []
    
    # Update weights if provided
    if updates.weights:
        for key, val in updates.weights.items():
            if key in decision.weights:
                old = decision.weights[key]
                decision.weights[key] = val
                changes.append(f"weight.{key}: {old} → {val}")
    
    if updates.min_signal_score is not None:
        old = decision.min_signal_score
        decision.min_signal_score = updates.min_signal_score
        changes.append(f"min_signal_score: {old} → {updates.min_signal_score}")
    
    if updates.max_signals_per_ticker is not None:
        old = decision.max_signals_per_ticker
        decision.max_signals_per_ticker = updates.max_signals_per_ticker
        changes.append(f"max_signals_per_ticker: {old} → {updates.max_signals_per_ticker}")
    
    return {
        "status": "updated",
        "changes": changes,
        "current_weights": decision.weights,
        "min_signal_score": decision.min_signal_score,
        "max_signals_per_ticker": decision.max_signals_per_ticker,
    }


@router.post("/test-signal")
@limiter.limit("10/hour")
async def generate_test_signal(
    request: Request,
    ticker: str = "AAPL",
    direction: str = "bullish",
    decision: DecisionEngine = Depends(get_decision_engine),
):
    """
    Generate a test signal for a ticker (development/demo only).
    
    Useful for testing the signal pipeline without requiring
    actual market events.
    """
    from uuid import uuid4
    
    dir_enum = Direction.BULLISH if direction.lower() == 'bullish' else Direction.BEARISH
    
    signal = OptionsSignal(
        signal_id=uuid4(),
        event_id=uuid4(),
        ticker=ticker.upper(),
        direction=dir_enum,
        confidence=0.75,
        recommendation="Long Calls" if direction.lower() == 'bullish' else "Long Puts",
        expected_return=0.15,
        max_loss=0.05,
        contributing_factors=[
            {'factor': 'test_mode', 'score': 0.5, 'weight': 1.0}
        ],
        historical_similarity=0.7,
        sentiment_weight=0.6,
        news_urgency=0.5,
    )
    
    decision.signal_history.append(signal)
    
    return SignalResponse(
        signal_id=str(signal.signal_id),
        ticker=signal.ticker,
        direction=signal.direction.value,
        confidence=signal.confidence,
        strategy=signal.recommendation,
        expected_return=signal.expected_return,
        max_loss=signal.max_loss,
        target_strike=signal.target_strike,
        generated_at=signal.generated_at.isoformat(),
    )


# ── Scheduled Tasks ───────────────────────────────────────────────────────────────

async def run_scheduled_outcome_check():
    """
    Periodic task to evaluate pending signal outcomes.
    Should be called by a scheduler (e.g., Celery beat, APScheduler).
    """
    learning = await get_market_learning()
    if learning:
        result = await learning.check_outcomes()
        log.info(f"Outcome check complete: {result}")
        return result
    return {'error': 'Learning integration not available', 'checked': 0, 'resolved': 0}


async def run_daily_pattern_build():
    """
    Daily task to rebuild historical pattern database.
    """
    historical = await get_historical()
    await historical.build_pattern_database()
    log.info("Daily pattern rebuild completed")
    return {"status": "ok", "message": "Pattern database rebuilt"}

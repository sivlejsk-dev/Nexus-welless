"""
Pydantic schemas for Market Intelligence data structures.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class DataSource(str, Enum):
    """Supported data source types"""
    NEWS_RSS = "news_rss"
    NEWS_API = "news_api"
    NEWS_财经 = "news_financial_cn"
    TWITTER = "twitter"
    REDDIT = "reddit"
    STOCKTWITS = "stocktwits"
    SENTIMENT_API = "sentiment_api"
    UNKNOWN = "unknown"


class EventType(str, Enum):
    """Types of market-moving events"""
    EARNINGS = "earnings"                    # Earnings reports
    MERGER_ACQUISITION = "ma"                # M&A activity
    REGULATORY = "regulatory"                # Regulatory changes
    PRODUCT_LAUNCH = "product_launch"        # New product announcements
    MANAGEMENT_CHANGE = "management_change"  # Executive changes
    LEGAL = "legal"                          # Legal issues/lawsuits
    MACROECONOMIC = "macro"                  # Economic data (CPI, Fed, etc.)
    GEOPOLITICAL = "geopolitical"            # Wars, treaties, sanctions
    NATURAL_DISASTER = "disaster"            # Natural disasters
    VIRAL_TREND = "viral"                    # Social media viral trends
    ANALYST_UPGRADE = "analyst_upgrade"      # Analyst rating changes
    INSTITUTIONAL_ACTION = "institutional"   # Large fund movements
    SECTOR_SHIFT = "sector_shift"            # Sector rotation
    CYBERSECURITY = "cybersecurity"          # Security breaches
    TECHNICAL_BREAKOUT = "technical"         # Technical pattern breaks
    UNKNOWN = "unknown"


class ImpactSeverity(str, Enum):
    """Severity of market impact expected"""
    MINIMAL = "minimal"      # <0.5% price move expected
    LOW = "low"              # 0.5-1% price move
    MEDIUM = "medium"        # 1-3% price move
    HIGH = "high"            # 3-5% price move
    CRITICAL = "critical"    # >5% price move
    EXTREME = "extreme"      # >10% price move, potential circuit breaker


class Direction(str, Enum):
    """Predicted direction of price movement"""
    BULLISH = "bullish"       # Expecting upward movement
    BEARISH = "bearish"       # Expecting downward movement
    NEUTRAL = "neutral"       # Expecting sideways/choppy action
    MIXED = "mixed"           # Conflicting signals


class TimeHorizon(str, Enum):
    """Expected time horizon for the impact"""
    IMMEDIATE = "immediate"    # Within hours
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"    # 1+ months
    UNKNOWN = "unknown"


class SentimentAnalysis(BaseModel):
    """Sentiment extracted from text"""
    model_config = ConfigDict(frozen=True)

    polarity: float = Field(..., ge=-1.0, le=1.0, description="Sentiment polarity (-1 to +1)")
    subjectivity: float = Field(..., ge=0.0, le=1.0, description="Subjectivity score (0=objective, 1=subjective)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in sentiment analysis")
    emotion_labels: List[str] = Field(default_factory=list, description="Emotion tags (fear, greed, excitement, panic)")
    key_phrases: List[str] = Field(default_factory=list, description="Phrases driving sentiment")

    def is_positive(self, threshold: float = 0.1) -> bool:
        return self.polarity > threshold

    def is_negative(self, threshold: float = -0.1) -> bool:
        return self.polarity < threshold

    def is_neutral(self, threshold: float = 0.1) -> bool:
        return abs(self.polarity) <= threshold


class EventClassification(BaseModel):
    """Full classification of a market event"""
    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    impact_severity: ImpactSeverity
    direction_bias: Direction
    time_horizon: TimeHorizon
    affected_sectors: List[str] = Field(default_factory=list, description="Sectors likely impacted")
    affected_tickers: List[str] = Field(default_factory=list, description="Specific stock symbols")
    keywords: List[str] = Field(default_factory=list, description="Key terms for matching")
    confidence: float = Field(..., ge=0.0, le=1.0)
    classification_notes: Optional[str] = None

    # Sub-classifications
    sentiment: SentimentAnalysis
    news_category: Optional[str] = None
    is_breaking: bool = False
    is_viral: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)


class MarketEvent(BaseModel):
    """Raw ingested event from a data source"""
    model_config = ConfigDict(from_attributes=True, frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    source: DataSource
    source_id: str = Field(..., description="Original ID from source")
    title: str
    description: str
    url: Optional[str] = None
    author: Optional[str] = None

    # Timestamps
    published_at: datetime
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

    # Raw content
    raw_content: str
    cleaned_content: Optional[str] = None

    # Metadata
    language: str = "en"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Classification (filled by classifier)
    classification: Optional[EventClassification] = None

    def get_text_for_analysis(self) -> str:
        """Get combined text for NLP analysis"""
        return f"{self.title} {self.description}"


class HistoricalPattern(BaseModel):
    """A pattern from historical data that matches current events"""
    model_config = ConfigDict(frozen=True)

    pattern_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str

    # Event signature to match against
    event_signature: Dict[str, Any] = Field(..., description="Event characteristics to match")

    # Historical outcomes
    matching_events: List[Dict[str, Any]] = Field(default_factory=list, description="Past similar events")
    avg_price_move: float = Field(..., description="Average % price move following similar events")
    avg_iv_change: float = Field(0.0, description="Average IV change")
    call_put_ratio: float = Field(..., description="Ratio of call to put volume change")
    typical_time_horizon: TimeHorizon

    # Statistics
    sample_size: int = Field(..., gt=0, description="Number of historical matches")
    win_rate: float = Field(..., ge=0.0, le=1.0, description="Proportion where prediction was correct")
    avg_return: float = Field(..., description="Average return from following signal")
    max_drawdown: float = Field(..., description="Worst-case loss in sample")

    # Confidence metrics
    pattern_strength: float = Field(..., ge=0.0, le=1.0, description="How strongly pattern predicts outcome")
    recency_weight: float = Field(..., ge=0.0, le=1.0, description="Weight given to recent vs old patterns")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def score_match(self, event: MarketEvent) -> float:
        """Calculate how well this pattern matches an event (0-1)"""
        # Implement matching logic based on event_signature
        score = 0.0
        signature = self.event_signature

        if 'event_type' in signature and event.classification.event_type == signature['event_type']:
            score += 0.3

        if 'sectors' in signature:
            event_sectors = set(event.classification.affected_sectors)
            pattern_sectors = set(signature['sectors'])
            overlap = len(event_sectors & pattern_sectors) / len(pattern_sectors) if pattern_sectors else 0
            score += 0.2 * overlap

        if 'sentiment_range' in signature:
            sent = event.classification.sentiment.polarity
            low, high = signature['sentiment_range']
            if low <= sent <= high:
                score += 0.2

        if 'impact_range' in signature:
            severity = event.classification.impact_severity.value
            allowed = signature['impact_range']
            if severity in allowed:
                score += 0.2

        return min(1.0, score)


class OptionsSignal(BaseModel):
    """Trading signal for options"""
    model_config = ConfigDict(frozen=True)

    signal_id: UUID = Field(default_factory=uuid4)
    event_id: UUID
    ticker: str
    direction: Direction
    confidence: float = Field(..., ge=0.0, le=1.0)

    # Options specifics
    recommendation: str = Field(..., description="Action: buy calls/puts, sell spreads, etc.")
    target_strike: Optional[float] = None
    target_expiry: Optional[str] = None  # YYYY-MM-DD
    estimated_premium: Optional[float] = None
    max_loss: Optional[float] = None
    expected_return: Optional[float] = None

    # Reasoning
    contributing_factors: List[Dict[str, Any]] = Field(default_factory=list)
    historical_similarity: float = Field(..., description="Similarity to historical patterns")
    sentiment_weight: float = Field(..., description="Weight from sentiment analysis")
    news_urgency: float = Field(..., description="Urgency from news source")

    # Risk metrics
    implied_volatility_impact: float = Field(0.0, description="Expected IV change")
    time_decay_risk: float = Field(0.0, description="Theta risk factor")
    liquidity_risk: float = Field(0.0, description="Bid-ask spread risk")

    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    def to_trading_advice(self) -> str:
        """Convert signal to human-readable trading advice"""
        parts = [
            f"Options signal for {self.ticker}:",
            f"Direction: {self.direction.value.upper()}",
            f"Action: {self.recommendation}",
            f"Confidence: {self.confidence:.1%}",
        ]
        if self.target_strike:
            parts.append(f"Strike: ${self.target_strike:.2f}")
        if self.expected_return:
            parts.append(f"Expected return: {self.expected_return:.1%}")
        if self.max_loss:
            parts.append(f"Max loss: {self.max_loss:.1%}")
        return "\n".join(parts)


class MarketIntelligenceConfig(BaseModel):
    """Configuration for market intelligence module"""
    model_config = ConfigDict(frozen=True)

    # Data source settings
    enabled_sources: List[DataSource] = Field(default_factory=lambda: list(DataSource))
    news_refresh_minutes: int = Field(15, ge=5, le=1440)
    social_refresh_seconds: int = Field(60, ge=30, le=3600)

    # Classification thresholds
    min_confidence_threshold: float = Field(0.6, ge=0.1, le=1.0)
    min_impact_threshold: ImpactSeverity = Field(ImpactSeverity.LOW)

    # Historical analysis
    historical_lookback_days: int = Field(365, ge=30, le=3650)
    min_pattern_samples: int = Field(10, ge=5, le=100)
    pattern_similarity_threshold: float = Field(0.7, ge=0.5, le=1.0)

    # Decision engine
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "news_impact": 0.30,
            "social_sentiment": 0.25,
            "historical_pattern": 0.30,
            "volatility_skew": 0.10,
            "liquidity": 0.05,
        }
    )
    confidence_adjustment_factor: float = Field(0.8, ge=0.5, le=1.0)

    # Risk limits
    max_position_size_pct: float = Field(0.05, ge=0.01, le=0.20)
    max_daily_signals: int = Field(10, ge=1, le=50)

    # Learning settings
    enable_continuous_learning: bool = True
    feedback_retention_days: int = Field(90, ge=30, le=365)

    # API credentials (populated from env vars)
    newsapi_key: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    reddit_client_id: Optional[str] = None
    finnhub_api_key: Optional[str] = None
    alphavantage_key: Optional[str] = None

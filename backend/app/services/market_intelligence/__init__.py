"""
Market Intelligence Module — options trading predictions from news & social sentiment

This module ingests global news and social media data, classifies market-moving events,
analyzes historical patterns, and provides options trading signals with continuous learning.

Architecture:
├── Data Ingestion Layer (news, social media, APIs)
├── Event Classification Engine (impact, topic, sentiment)
├── Historical Pattern Matcher (similarity to past events)
├── Options Impact Analyzer (call/put influence modeling)
├── Decision Engine (weighted factor aggregation)
└── Learning Integration (outcome tracking & model refinement)

Integrates with Nexus ContinuousLearner for adaptive improvement.
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Nexus Intelligence"

# Core components
from app.services.market_intelligence.schemas import (
    MarketEvent,
    EventClassification,
    SentimentAnalysis,
    HistoricalPattern,
    OptionsSignal,
    MarketIntelligenceConfig,
    DataSource,
    EventType,
    ImpactSeverity,
    Direction,
)

from app.services.market_intelligence.base import (
    BaseDataSource,
    BaseEventClassifier,
    BaseHistoricalAnalyzer,
    BaseOptionsAnalyzer,
    EventPipeline,
)

from app.services.market_intelligence.news_ingestor import (
    NewsIngestor,
    RSSNewsSource,
    NewsAPISource,
   财经新闻Source,
)

from app.services.market_intelligence.social_ingestor import (
    SocialMediaIngestor,
    TwitterSource,
    RedditSource,
    StockTwitsSource,
    SentimentAPISource,
)

from app.services.market_intelligence.classifier import (
    EventClassifier,
    ImpactAnalyzer,
    SentimentAnalyzer,
    TopicCategorizer,
)

from app.services.market_intelligence.historical import (
    HistoricalPatternMatcher,
    SimilarityEngine,
    OutcomeAnalyzer,
)

from app.services.market_intelligence.options_analyzer import (
    OptionsImpactAnalyzer,
    CallPutAnalyzer,
    VolatilityPredictor,
    StrikeSelector,
)

from app.services.market_intelligence.decision_engine import (
    DecisionEngine,
)

from app.services.market_intelligence.learning_integration import (
    MarketLearningIntegration,
    get_market_learning,
)

# Simulation & backtesting
from app.services.market_intelligence.simulation import (
    SimulationEngine,
    SimulationConfig,
    SimulationResult,
    SimulationMode,
    HistoricalDataRepository,
    SimulationAPI,
    backtest_period,
    compare_market_regimes,
)
from app.services.market_intelligence.data_loader import (
    HistoricalDataLoader,
    load_standard_market_data,
)

# Re-export commonly used classes
__all__ = [
    # Schemas
    "MarketEvent",
    "EventClassification",
    "SentimentAnalysis",
    "HistoricalPattern",
    "OptionsSignal",
    "MarketIntelligenceConfig",
    # Base classes
    "BaseDataSource",
    "BaseEventClassifier",
    "BaseHistoricalAnalyzer",
    "BaseOptionsAnalyzer",
    "EventPipeline",
    # Implementations
    "NewsIngestor",
    "SocialMediaIngestor",
    "EventClassifier",
    "HistoricalPatternMatcher",
    "OptionsImpactAnalyzer",
    "DecisionEngine",
    "MarketLearningIntegration",
    # Simulation
    "SimulationEngine",
    "SimulationConfig",
    "SimulationResult",
    "HistoricalDataRepository",
    "SimulationAPI",
    "HistoricalDataLoader",
    "backtest_period",
    "compare_market_regimes",
]

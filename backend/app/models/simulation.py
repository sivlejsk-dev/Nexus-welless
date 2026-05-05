"""
Database models for storing simulation results and outcomes.

Allows:
- Persisting simulation runs
- Querying historical backtest performance
- Comparing configurations over time
- Auditing prediction accuracy
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SimulationRun(Base):
    """A completed simulation/backtest run"""
    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    simulation_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    
    # Time period
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Configuration snapshot
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Status
    status: Mapped[str] = mapped_column(String(32), default="running")  # running, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Results summary
    total_signals: Mapped[int] = mapped_column(Integer, default=0)
    total_evaluated: Mapped[int] = mapped_column(Integer, default=0)
    successful_predictions: Mapped[int] = mapped_column(Integer, default=0)
    failed_predictions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance metrics
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_return: Mapped[float] = mapped_column(Float, default=0.0)
    sharpe_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    max_drawdown: Mapped[float] = mapped_column(Float, default=0.0)
    avg_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Breakdowns (JSON blobs)
    by_event_type: Mapped[Optional[dict]] = mapped_column(JSON)
    by_direction: Mapped[Optional[dict]] = mapped_column(JSON)
    by_source: Mapped[Optional[dict]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationship
    predictions: Mapped[list["SimulationPrediction"]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )


class SimulationPrediction(Base):
    """A single prediction made during a simulation"""
    __tablename__ = "simulation_predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    simulation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Identification
    event_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    ticker: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # bullish, bearish, neutral
    
    # Prediction details
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    strategy: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_return: Mapped[float] = mapped_column(Float, default=0.0)
    target_strike: Mapped[Optional[float]] = mapped_column(Float)
    target_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Actual outcome (filled after evaluation)
    actual_return: Mapped[Optional[float]] = mapped_column(Float)
    actual_direction: Mapped[Optional[str]] = mapped_column(String(16))
    success: Mapped[Optional[bool]] = mapped_column(Boolean)
    pnl_pct: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timing
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Context
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    sources_used: Mapped[list] = mapped_column(JSON, default=list)
    simulation_run_id: Mapped[str] = mapped_column(String(64), index=True)  # Links back to SimulationRun.simulation_id
    
    # Relationship
    simulation: Mapped[SimulationRun] = relationship(back_populates="predictions")


class SimulationOutcomeRecord(Base):
    """
    Tracks prediction outcomes for learning and analytics.
    
    Separate from SimulationPrediction for flexible querying.
    Supports:
    - Learning feedback loops
    - Performance analytics
    - Model improvement tracking
    """
    __tablename__ = "simulation_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Link to prediction
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_predictions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Outcome details
    event_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    ticker: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    
    # Prediction vs actual
    predicted_direction: Mapped[str] = mapped_column(String(16), nullable=False)
    actual_direction: Mapped[str] = mapped_column(String(16), nullable=False)
    predicted_return: Mapped[float] = mapped_column(Float, nullable=False)
    actual_return: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Success metrics
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pnl_pct: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Context for learning
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    source_credibility: Mapped[float] = mapped_column(Float, default=0.5)
    pattern_strength: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Outcome recorded
    outcome_available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SimulationParameterSweep(Base):
    """
    Track parameter sweep experiments.
    
    When trying different config variations (grid search),
    record parameters → results mapping for analysis.
    """
    __tablename__ = "simulation_parameter_sweeps"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sweep_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    
    # Parameters tried
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False)  # {"news_weight": 0.4, "social_weight": 0.3}
    
    # Result references
    simulation_run_ids: Mapped[list] = mapped_column(JSON, default=list)
    
    # Aggregate performance
    avg_win_rate: Mapped[float] = mapped_column(Float)
    avg_return: Mapped[float] = mapped_column(Float)
    avg_sharpe: Mapped[float] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    notes: Mapped[Optional[str]] = mapped_column(Text)

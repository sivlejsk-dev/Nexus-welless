"""
FastAPI router for Market Intelligence Simulation endpoints.

Provides:
- Create simulation runs
- Execute simulations
- Query results
- Compare across periods
- Access simulation data
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.market_intelligence.simulation import (
    SimulationEngine,
    SimulationConfig,
    SimulationResult,
    SimulationMode,
    HistoricalDataRepository,
    backtest_period,
    compare_market_regimes,
)
from app.services.market_intelligence import MarketIntelligenceConfig, DataSource

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/market/sim", tags=["market-simulation"])

# Global simulation manager
_simulation_repo: Optional[HistoricalDataRepository] = None
_simulation_api: Optional[Any] = None


# ── Request/Response Schemas ────────────────────────────────────────────────────

class SimulationRequest(BaseModel):
    """Request to create/run a simulation"""
    start_date: datetime
    end_date: datetime
    mode: str = "walk_forward"  # walk_forward, event_driven, snapshot
    step_days: int = Field(1, ge=1, le=30)
    min_confidence: float = Field(0.6, ge=0.1, le=1.0)
    include_news: bool = True
    include_social: bool = True
    use_historical_patterns: bool = True
    enable_learning: bool = False
    evaluate_earnings: bool = True
    evaluate_macro: bool = True


class SimulationListItem(BaseModel):
    """Summary of a simulation result"""
    simulation_id: str
    start_date: str
    end_date: str
    total_signals: int
    win_rate: float
    avg_return: float
    sharpe_ratio: float
    status: str  # 'running', 'completed', 'failed'


class SimulationDetailResponse(BaseModel):
    """Full simulation result"""
    simulation_id: str
    total_signals: int
    successful_predictions: int
    failed_predictions: int
    win_rate: float
    avg_return: float
    sharpe_ratio: float
    max_drawdown: float
    avg_confidence: float
    by_event_type: Dict[str, Dict[str, float]]
    by_direction: Dict[str, Dict[str, float]]
    predictions: List[Dict[str, Any]]
    errors: List[str]
    created_at: str


class BatchSimulationRequest(BaseModel):
    """Request to run multiple simulations"""
    periods: List[Dict[str, str]]  # [{"name": "period1", "start": "...", "end": "..."}]
    parallel: bool = False
    base_config: Optional[SimulationRequest] = None


class ComparisonRequest(BaseModel):
    """Request to compare simulation results"""
    simulation_ids: List[str]


class WalkForwardRequest(BaseModel):
    """Request walk-forward analysis"""
    overall_start: datetime
    overall_end: datetime
    train_months: int = Field(6, ge=1, le=24)
    test_months: int = Field(1, ge=1, le=6)
    step_months: int = Field(1, ge=1, le=3)


class MonteCarloRequest(BaseModel):
    """Request Monte Carlo simulation"""
    start_date: datetime
    end_date: datetime
    iterations: int = Field(100, ge=10, le=1000)
    parameter_variations: Optional[Dict[str, List[Any]]] = None


class DataIngestRequest(BaseModel):
    """Request to load historical data into repository"""
    data_source: str  # 'yahoo', 'local_file', 'database'
    tickers: List[str]
    start_date: datetime
    end_date: datetime
    force_reload: bool = False


# ── Dependency Injection ─────────────────────────────────────────────────────────

async def get_repository() -> HistoricalDataRepository:
    """Get or create historical data repository"""
    global _simulation_repo
    if _simulation_repo is None:
        _simulation_repo = HistoricalDataRepository("/tmp/simulation_data")
    return _simulation_repo


async def get_simulation_api() -> Any:
    """Get simulation API instance"""
    global _simulation_api
    if _simulation_api is None:
        repo = await get_repository()
        _simulation_api = SimulationAPI(repo)
    return _simulation_api


# ── Simulation Control Endpoints ─────────────────────────────────────────────────

@router.post("/run", response_model=SimulationListItem)
async def run_simulation(
    request: SimulationRequest,
    background_tasks: BackgroundTasks,
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """
    Create and run a historical simulation.
    
    The simulation will walk through the specified period day-by-day,
    making predictions using only data available at each point in time.
    No future data leakage occurs.
    
    Returns immediately with job ID; results available via GET /sim/{id}
    """
    import uuid
    
    sim_id = f"sim_{uuid.uuid4().hex[:8]}_{request.start_date.date()}"
    
    config = SimulationConfig(
        simulation_id=sim_id,
        start_date=request.start_date,
        end_date=request.end_date,
        mode=SimulationMode(request.mode),
        step_days=request.step_days,
        include_news=request.include_news,
        include_social=request.include_social,
        use_historical_patterns=request.use_historical_patterns,
        enable_learning=request.enable_learning,
        min_confidence=request.min_confidence,
    )
    
    # Create engine (store in memory for status tracking)
    engine = SimulationEngine(repo, config, {})
    
    async def run_in_background():
        try:
            result = await engine.run_simulation()
            # Store result
            api = await get_simulation_api()
            api.completed_results.append(result)
        except Exception as e:
            log.error(f"Simulation {sim_id} failed: {e}", exc_info=True)
    
    background_tasks.add_task(run_in_background)
    
    return SimulationListItem(
        simulation_id=sim_id,
        start_date=request.start_date.isoformat(),
        end_date=request.end_date.isoformat(),
        total_signals=0,
        win_rate=0.0,
        avg_return=0.0,
        sharpe_ratio=0.0,
        status="running"
    )


@router.get("/results", response_model=List[SimulationListItem])
async def list_simulations(
    limit: int = Query(20, ge=1, le=100),
    api: SimulationAPI = Depends(get_simulation_api),
):
    """List all completed simulations"""
    results = api.list_results()[:limit]
    return [
        SimulationListItem(
            simulation_id=r['id'],
            start_date=r.get('start_date', ''),
            end_date=r.get('end_date', ''),
            total_signals=r.get('total_signals', 0),
            win_rate=r.get('win_rate', 0.0),
            avg_return=r.get('avg_return', 0.0),
            sharpe_ratio=r.get('sharpe', 0.0),
            status="completed"
        )
        for r in results
    ]


@router.get("/results/{simulation_id}", response_model=SimulationDetailResponse)
async def get_simulation_result(
    simulation_id: str,
    include_predictions: bool = Query(True),
    api: SimulationAPI = Depends(get_simulation_api),
):
    """
    Get detailed results of a completed simulation.
    
    Includes:
    - All predictions (ticker, direction, confidence, expected vs actual)
    - Performance breakdowns by event type, direction, source
    - Error logs
    """
    result = api.get_result(simulation_id)
    if not result:
        raise HTTPException(404, f"Simulation {simulation_id} not found")
    
    response = SimulationDetailResponse(
        simulation_id=result.simulation_id,
        total_signals=result.total_signals,
        successful_predictions=result.successful_predictions,
        failed_predictions=result.failed_predictions,
        win_rate=result.win_rate,
        avg_return=result.avg_return,
        sharpe_ratio=result.sharpe_ratio,
        max_drawdown=result.max_drawdown,
        avg_confidence=result.avg_confidence,
        by_event_type=result.by_event_type,
        by_direction=result.by_direction,
        predictions=[
            {
                'prediction_id': str(p.prediction_id),
                'timestamp': p.timestamp.isoformat(),
                'ticker': p.ticker,
                'direction': p.direction.value,
                'confidence': p.confidence,
                'strategy': p.strategy,
                'expected_return': p.expected_return,
                'actual_return': p.actual_return,
                'success': p.success,
                'pnl_pct': p.pnl_pct,
                'event_type': p.event_type,
                'sources_used': p.sources_used,
            }
            for p in (result.predictions if include_predictions else result.predictions[:0])
        ],
        errors=result.errors,
        created_at=result.created_at.isoformat(),
    )
    
    return response


@router.post("/compare")
async def compare_simulations(
    request: ComparisonRequest,
    api: SimulationAPI = Depends(get_simulation_api),
):
    """
    Compare multiple simulation runs side-by-side.
    
    Useful for:
    - Comparing different config parameters
    - Evaluating performance across time periods
    - A/B testing strategy changes
    """
    comparison = api.compare_simulations(request.simulation_ids)
    return comparison


@router.post("/batch", response_model=List[SimulationListItem])
async def run_batch_simulations(
    request: BatchSimulationRequest,
    background_tasks: BackgroundTasks,
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """
    Run multiple simulations across different periods.
    
    Submit a list of date ranges; each runs as separate simulation.
    Results can be compared afterward.
    """
    # Convert periods
    periods = []
    for p in request.periods:
        start = datetime.fromisoformat(p['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(p['end'].replace('Z', '+00:00'))
        periods.append((start, end))
    
    # Get services
    services = {}  # Would get from DI
    
    # Create batch runner
    from app.services.market_intelligence.simulation import SimulationBatchRunner
    runner = SimulationBatchRunner(repo, SimulationConfig(**request.base_config.dict()) if request.base_config else SimulationConfig(simulation_id="batch"), services)
    
    async def run_batch_in_background():
        try:
            results = await runner.run_batch(periods, parallel=request.parallel)
            # Store results
            api = await get_simulation_api()
            api.completed_results.extend(results)
        except Exception as e:
            log.error(f"Batch simulation failed: {e}", exc_info=True)
    
    background_tasks.add_task(run_batch_in_background)
    
    return [
        SimulationListItem(
            simulation_id=f"batch_{i}",
            start_date=p[0].isoformat(),
            end_date=p[1].isoformat(),
            total_signals=0,
            win_rate=0.0,
            avg_return=0.0,
            sharpe_ratio=0.0,
            status="running"
        )
        for i, p in enumerate(periods)
    ]


@router.post("/walk-forward", response_model=List[SimulationListItem])
async def run_walk_forward_analysis(
    request: WalkForwardRequest,
    background_tasks: BackgroundTasks,
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """
    Perform walk-forward analysis.
    
    Trains on data from months 0-N, tests on month N+1, then rolls forward.
    Simulates realistic periodic model retraining.
    
    Returns list of simulation results (one per test window).
    """
    services = {}
    
    async def run_wf_in_background():
        try:
            runner = SimulationBatchRunner(
                repo,
                SimulationConfig(mode=SimulationMode.WALK_FORWARD),
                services
            )
            results = await runner.run_walk_forward(
                start=request.overall_start,
                end=request.overall_end,
                train_months=request.train_months,
                test_months=request.test_months,
                step_months=request.step_months,
            )
            api = await get_simulation_api()
            api.completed_results.extend(results)
            log.info(f"Walk-forward analysis complete: {len(results)} periods tested")
            
        except Exception as e:
            log.error(f"Walk-forward failed: {e}", exc_info=True)
    
    background_tasks.add_task(run_wf_in_background)
    
    # Estimate number of periods
    total_days = (request.overall_end - request.overall_start).days
    est_periods = max(1, total_days // (request.step_months * 30))
    
    return [
        SimulationListItem(
            simulation_id=f"wf_{i}",
            start_date=request.overall_start.isoformat(),
            end_date=request.overall_end.isoformat(),
            total_signals=0,
            win_rate=0.0,
            avg_return=0.0,
            sharpe_ratio=0.0,
            status="running"
        )
        for i in range(est_periods)
    ]


@router.post("/monte-carlo", response_model=Dict[str, Any])
async def run_monte_carlo_simulation(
    request: MonteCarloRequest,
    background_tasks: BackgroundTasks,
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """
    Run Monte Carlo simulation with random variations.
    
    Useful for:
    - Confidence intervals on performance
    - Sensitivity to parameter changes
    - Risk assessment
    """
    services = {}
    
    async def run_mc_in_background():
        try:
            runner = SimulationBatchRunner(repo, SimulationConfig(), services)
            results = await runner.run_monte_carlo(
                start=request.start_date,
                end=request.end_date,
                iterations=request.iterations,
                parameter_variations=request.parameter_variations,
            )
            
            # Aggregate statistics
            import numpy as np
            returns = [r.avg_return for r in results]
            win_rates = [r.win_rate for r in results]
            sharpes = [r.sharpe_ratio for r in results]
            
            summary = {
                'iterations': len(results),
                'return': {
                    'mean': float(np.mean(returns)),
                    'std': float(np.std(returns)),
                    'p5': float(np.percentile(returns, 5)),
                    'p95': float(np.percentile(returns, 95)),
                },
                'win_rate': {
                    'mean': float(np.mean(win_rates)),
                    'std': float(np.std(win_rates)),
                    'p5': float(np.percentile(win_rates, 5)),
                    'p95': float(np.percentile(win_rates, 95)),
                },
                'sharpe': {
                    'mean': float(np.mean(sharpes)),
                    'std': float(np.std(sharpes)),
                },
            }
            
            # Store results
            api = await get_simulation_api()
            api.completed_results.extend(results)
            log.info(f"Monte Carlo complete: {summary}")
            
        except Exception as e:
            log.error(f"Monte Carlo failed: {e}", exc_info=True)
    
    background_tasks.add_task(run_mc_in_background)
    
    return {
        "status": "started",
        "iterations": request.iterations,
        "message": "Monte Carlo simulation running in background"
    }


@router.get("/compare/{simulation_ids}")
async def compare_multiple_simulations(
    simulation_ids: str,  # comma-separated
    api: SimulationAPI = Depends(get_simulation_api),
):
    """
    Compare multiple simulation results.
    
    Example:
        GET /api/v1/market/sim/compare/sim_20240101_20240331,sim_20240701_20240930
    
    Returns side-by-side metrics and identifies best/worst performers.
    """
    ids = simulation_ids.split(',')
    comparison = api.compare_simulations(ids)
    return comparison


@router.post("/quick-backtest")
async def quick_backtest(
    start_date: datetime = Body(...),
    end_date: datetime = Body(...),
    ticker: str = Body("SPY"),
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """
    Quick one-off backtest of a specific period.
    
    Simpler than full /run endpoint; returns immediate result.
    Useful for quick analysis without persistence.
    """
    try:
        result = await backtest_period(repo, start_date, end_date)
        
        return {
            "period": f"{start_date.date()} to {end_date.date()}",
            "signals_generated": result.total_signals,
            "win_rate": result.win_rate,
            "avg_return_per_signal": result.avg_return,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown": result.max_drawdown,
            "by_event_type": result.by_event_type,
            "top_predictions": sorted(
                result.predictions,
                key=lambda p: p.pnl_pct or 0,
                reverse=True
            )[:5],
        }
    except Exception as e:
        log.error(f"Quick backtest failed: {e}", exc_info=True)
        raise HTTPException(500, f"Backtest failed: {str(e)}")


@router.post("/regime-comparison")
async def compare_regimes(
    regimes: Dict[str, str] = Body(...),
    # Format: {"bull": "2023-01-01,2023-12-31", "bear": "2022-01-01,2022-12-31"}
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """
    Compare simulation performance across different market regimes.
    
    Submit dict of regime_name -> "start_date,end_date"
    Returns win/return stats by regime.
    """
    periods = {}
    for regime, date_range in regimes.items():
        start_str, end_str = date_range.split(',')
        start = datetime.fromisoformat(start_str)
        end = datetime.fromisoformat(end_str)
        periods[regime] = (start, end)
    
    comparison = await compare_market_regimes(repo, periods)
    return comparison


# ── Data Management Endpoints ────────────────────────────────────────────────────

@router.post("/data/ingest")
async def ingest_historical_data(
    request: DataIngestRequest,
    background_tasks: BackgroundTasks,
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """
    Load historical market data into the simulation repository.
    
    This data will be used for future simulations.
    
    Sources:
    - yahoo: Download from Yahoo Finance (yfinance)
    - local_file: Load from JSON/CSV file
    - database: Query internal database
    """
    async def load_data():
        if request.data_source == 'yahoo':
            await _ingest_from_yahoo(repo, request.tickers, request.start_date, request.end_date)
        elif request.data_source == 'local_file':
            await _ingest_from_file(repo, request.tickers, request.start_date, request.end_date)
        else:
            raise ValueError(f"Unknown data source: {request.data_source}")
    
    background_tasks.add_task(load_data)
    
    return {
        "status": "started",
        "message": f"Loading {request.data_source} data for {len(request.tickers)} tickers"
    }


@router.get("/data/sources")
async def list_data_sources():
    """List available historical data sources"""
    return {
        "sources": [
            {
                "name": "yahoo",
                "description": "Yahoo Finance historical data (free, delayed)",
                "tickers_available": "All major equities/ETFs",
                "date_range": "Daily, max ~20 years",
            },
            {
                "name": "local_file",
                "description": "Custom CSV/JSON files uploaded by user",
                "tickers_available": "User-defined",
                "date_range": "User-defined",
            },
            {
                "name": "database",
                "description": "Internal Nexus database (if populated)",
                "tickers_available": "All tracked tickers",
                "date_range": "Since Nexus deployment",
            },
        ]
    }


@router.get("/data/info")
async def get_repository_info(
    repo: HistoricalDataRepository = Depends(get_repository),
):
    """Get info about loaded historical data"""
    return {
        "indexed_dates": len(repo._events_by_date),
        "earliest_date": min(repo._events_by_date.keys()) if repo._events_by_date else None,
        "latest_date": max(repo._events_by_date.keys()) if repo._events_by_date else None,
        "total_events": sum(len(v) for v in repo._events_by_date.values()),
        "tickers_with_prices": list(repo._price_data.keys()),
    }


# ── Utilities ────────────────────────────────────────────────────────────────────

async def _ingest_from_yahoo(
    repo: HistoricalDataRepository,
    tickers: List[str],
    start: datetime,
    end: datetime,
):
    """Download historical data from Yahoo Finance"""
    try:
        import yfinance as yf
        import pandas as pd
        
        price_data = {}
        for ticker in tickers:
            log.info(f"Fetching {ticker} from Yahoo Finance")
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start, end=end)
            
            if hist.empty:
                log.warning(f"No data for {ticker}")
                continue
            
            series = []
            for dt, row in hist.iterrows():
                series.append((dt.date(), float(row['Close'])))
            price_data[ticker] = series
        
        # Also fetch news (would use yfinance news)
        events = []  # Would populate from Yahoo News RSS
        
        repo.store_historical_data(events, {}, price_data)
        log.info(f"Yahoo ingestion complete for {len(tickers)} tickers")
        
    except ImportError:
        log.error("yfinance not installed. pip install yfinance")


async def _ingest_from_file(
    repo: HistoricalDataRepository,
    tickers: List[str],
    start: datetime,
    end: datetime,
):
    """Load data from local file"""
    # Would implement CSV/JSON file loader
    pass

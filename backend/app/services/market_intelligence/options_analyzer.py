"""
Options Impact Analyzer - translates event analysis into concrete options strategies.

Determines:
- Implied volatility (IV) crush/expansion expectations
- Skew shifts (put/call volatility spread)
- Optimal strike selection (delta targets, probability ITM)
- Expiry horizon (DTE)
- Strategy type (directional, volatility, income, hedge)
- Greeks exposure (delta, theta, vega, gamma)
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import numpy as np

from .base import BaseOptionsAnalyzer
from .schemas import (
    OptionsSignal,
    Direction,
    TimeHorizon,
    EventClassification,
    MarketEvent,
    HistoricalPattern,
    EventType,
    ImpactSeverity,
)

log = logging.getLogger(__name__)


@dataclass
class OptionStrategy:
    """Concrete options strategy recommendation"""
    strategy_name: str
    description: str
    ticker: str
    legs: List[Dict]
    max_risk: float
    max_reward: float
    probability_profit: float
    expected_value: float
    greeks: Dict[str, float]
    suitable_for: str  # 'beginner', 'intermediate', 'advanced'
    risk_level: int   # 1-5
    capital_required: float


class OptionsImpactAnalyzer(BaseOptionsAnalyzer):
    """
    Analyzes how market events affect options pricing and identifies trading opportunities.
    
    Key analyses:
    1. IV impact - will IV expand or contract?
    2. Skew shift - will OTM puts/calls be relatively more/less expensive?
    3. Time decay - how quickly will theta erode value?
    4. Liquidity assessment - bid-ask spreads for recommended strikes
    """
    
    # IV change estimates by event type (historical averages)
    EVENT_IV_MULTIPLIERS = {
        EventType.EARNINGS: 1.3,  # IV crush post-earnings common
        EventType.MERGER_ACQUISITION: 1.5,
        EventType.REGULATORY: 1.4,
        EventType.PRODUCT_LAUNCH: 1.2,
        EventType.MACROECONOMIC: 1.3,
        EventType.VIRAL_TREND: 1.4,
        EventType.ANALYST_UPGRADE: 1.1,
    }
    
    # Default IV crush percentages after event resolution
    IV_CRUSH_RATES = {
        EventType.EARNINGS: 0.4,  # IV drops ~40% post-earnings
        EventType.MERGER_ACQUISITION: 0.3,
    }
    
    # Skew impact - which side gets more IV?
    # Positive = calls get higher IV, Negative = puts get higher IV
    SKEW_IMPACT = {
        EventType.EARNINGS: 0.0,  # symmetric
        EventType.MERGER_ACQUISITION: 0.2,  # slightly call-bullish
        EventType.REGULATORY: -0.3,  # put-heavy (risk aversion)
        EventType.PRODUCT_LAUNCH: 0.4,  # call optimism
        EventType.MACROECONOMIC: -0.2,  # puts favored
        EventType.VIRAL_TREND: 0.5,  # extreme call skew (meme dynamics)
        EventType.ANALYST_UPGRADE: 0.3,  # bullish
    }

    def __init__(self, config):
        super().__init__(config)
        self.call_put_analyzer = CallPutAnalyzer()
        self.volatility_predictor = VolatilityPredictor()
        self.strike_selector = StrikeSelector(config)

    async def analyze_options_impact(
        self,
        event: MarketEvent,
        classification: EventClassification,
        historical_patterns: List[HistoricalPattern],
        current_market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Full options impact analysis.
        
        Returns structured dict with all analysis results.
        """
        ticker = classification.affected_tickers[0] if classification.affected_tickers else 'SPY'
        
        # 1. Predict IV change
        iv_impact = await self._predict_iv_change(classification, historical_patterns)
        
        # 2. Predict skew shift (calls vs puts IV differential)
        skew_shift = self._predict_skew_shift(classification.event_type, historical_patterns)
        
        # 3. Recommend strategy
        strategy = await self._recommend_strategy(
            classification, iv_impact, skew_shift, current_market_data
        )
        
        # 4. Select specific strikes
        strikes = self._select_strikes(
            ticker,
            classification.direction_bias,
            strategy,
            current_market_data
        )
        
        # 5. Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(
            strategy, strikes, classification, iv_impact
        )
        
        return {
            'ticker': ticker,
            'iv_impact': iv_impact,
            'skew_shift': skew_shift,
            'recommended_strategy': strategy.strategy_name,
            'strategy_details': strategy,
            'optimal_strikes': strikes,
            'expiry_horizon': self._recommend_expiry(classification.time_horizon),
            'risk_metrics': risk_metrics,
            'confidence': classification.confidence,
        }

    async def _predict_iv_change(
        self, 
        classification: EventClassification,
        patterns: List[HistoricalPattern]
    ) -> float:
        """
        Predict net IV change (%) following this event.
        
        IV typically:
        - Rises before known events (awaiting resolution)
        - Crushes after event resolution (if no surprise)
        - Stays elevated for ongoing uncertainty
        """
        base_iv_change = 0.0
        
        # Lookup event-type multiplier
        multiplier = self.EVENT_IV_MULTIPLIERS.get(
            classification.event_type, 
            1.1  # modest expansion for unknown events
        )
        
        # Severity modifier
        severity_mult = {
            ImpactSeverity.EXTREME: 2.0,
            ImpactSeverity.CRITICAL: 1.7,
            ImpactSeverity.HIGH: 1.4,
            ImpactSeverity.MEDIUM: 1.2,
            ImpactSeverity.LOW: 1.0,
            ImpactSeverity.MINIMAL: 0.9,
        }[classification.impact_severity]
        
        # Base IV bump estimate
        base_iv_change = 0.15 * multiplier * severity_mult  # ~15% baseline bump
        
        # If breaking news, IV spikes more
        if classification.is_breaking:
            base_iv_change *= 1.5
        
        # If viral social, IV may spike disproportionately
        if classification.is_viral:
            base_iv_change *= 1.3
        
        # Historical pattern adjustment
        if patterns:
            avg_iv_change = np.mean([p.avg_iv_change for p in patterns])
            base_iv_change = 0.7 * base_iv_change + 0.3 * avg_iv_change
        
        # Cap at reasonable bounds
        return max(0.05, min(2.0, base_iv_change))  # 5% to 200%

    def _predict_skew_shift(
        self,
        event_type: EventType,
        patterns: List[HistoricalPattern]
    ) -> float:
        """
        Predict relative call vs put IV skew change.
        
        Returns:
            Positive = calls get more expensive vs puts (bullish skew)
            Negative = puts more expensive (bearish/fear skew)
        """
        base_skew = self.SKEW_IMPACT.get(event_type, 0.0)
        
        # Adjust based on patterns
        if patterns:
            pattern_skew = np.mean([getattr(p, 'skew_shift', 0) for p in patterns])
            base_skew = 0.6 * base_skew + 0.4 * pattern_skew
        
        return max(-1.0, min(1.0, base_skew))

    async def _recommend_strategy(
        self,
        classification: EventClassification,
        iv_impact: float,
        skew_shift: float,
        market_data: Optional[Dict]
    ) -> OptionStrategy:
        """
        Recommend an options strategy based on analysis.
        
        Strategies by scenario:
        - Bullish + High IV → Credit spreads (sell premium)
        - Bullish + Low IV → Debit spreads (buy directional)
        - Bearish + High IV → Put credit spreads
        - Bearish + Low IV → Put debit spreads / long puts
        - Neutral + High IV → Iron Condor (sell strangle)
        - Extreme impact + uncertainty → Straddle/strangle (buy volatility)
        """
        ticker = classification.affected_tickers[0] if classification.affected_tickers else 'SPY'
        direction = classification.direction_bias
        severity = classification.impact_severity
        is_high_iv = iv_impact > 0.3
        
        strategy_name = ""
        description = ""
        legs = []
        max_risk = 0
        max_reward = 0
        prob = 0.5
        expected_val = 0
        greeks = {'delta': 0, 'vega': 0, 'theta': 0, 'gamma': 0}
        risk_level = 3
        capital = 1000
        suitable = 'intermediate'
        
        # Decision logic
        if direction == Direction.BULLISH:
            if is_high_iv:
                # Sell premium - credit call spread
                strategy_name = "Bull Call Credit Spread"
                description = f"Sell OTM call, buy further OTM call. Profit from IV crush + directional bullish view."
                legs = [
                    {'action': 'sell', 'type': 'call', 'otm_pct': 0.05},
                    {'action': 'buy', 'type': 'call', 'otm_pct': 0.15},
                ]
                max_risk = 500  # per contract approx
                max_reward = 200
                prob = 0.65
                risk_level = 3
                suitable = 'beginner'
                capital = 500
                greeks = {'delta': -0.2, 'vega': -0.3, 'theta': 0.1, 'gamma': 0.1}
            else:
                # Buy directional - debit call spread or naked calls
                if severity in (ImpactSeverity.HIGH, ImpactSeverity.CRITICAL, ImpactSeverity.EXTREME):
                    strategy_name = "Long Calls (Directional)"
                    description = f"Buy OTM calls. Pure bullish play expecting big move with IV expansion."
                    legs = [{'action': 'buy', 'type': 'call', 'otm_pct': 0.10}]
                    max_risk = 1000
                    max_reward = 5000
                    prob = 0.45
                    risk_level = 4
                    suitable = 'advanced'
                    capital = 1000
                    greeks = {'delta': 0.6, 'vega': 0.5, 'theta': -0.2, 'gamma': 0.8}
                else:
                    strategy_name = "Bull Call Debit Spread"
                    description = f"Buy ITM/ATM call, sell OTM call. Lower cost, defined risk."
                    legs = [
                        {'action': 'buy', 'type': 'call', 'moneyness': 'atm'},
                        {'action': 'sell', 'type': 'call', 'otm_pct': 0.10},
                    ]
                    max_risk = 800
                    max_reward = 400
                    prob = 0.6
                    risk_level = 2
                    suitable = 'beginner'
                    capital = 800
        
        elif direction == Direction.BEARISH:
            if is_high_iv:
                strategy_name = "Bear Put Credit Spread"
                description = f"Sell OTM put, buy further OTM put. Short premium with bearish hedge."
                legs = [
                    {'action': 'sell', 'type': 'put', 'otm_pct': 0.05},
                    {'action': 'buy', 'type': 'put', 'otm_pct': 0.15},
                ]
                max_risk = 500
                max_reward = 200
                prob = 0.65
                risk_level = 3
                suitable = 'beginner'
                capital = 500
                greeks = {'delta': 0.2, 'vega': -0.3, 'theta': 0.1, 'gamma': 0.1}
            else:
                strategy_name = "Long Puts (Directional)"
                description = f"Buy OTM puts. Bearish play expecting decline with IV expansion."
                legs = [{'action': 'buy', 'type': 'put', 'otm_pct': 0.10}]
                max_risk = 1000
                max_reward = 5000
                prob = 0.45
                risk_level = 4
                suitable = 'advanced'
                capital = 1000
                greeks = {'delta': -0.6, 'vega': 0.5, 'theta': -0.2, 'gamma': 0.8}
        
        else:  # NEUTRAL or MIXED
            if iv_impact > 0.4:
                # Volatility expansion expected → buy straddle/strangle
                strategy_name = "Long Straddle"
                description = f"Buy ATM call + ATM put. Profit from big move in either direction."
                legs = [
                    {'action': 'buy', 'type': 'call', 'moneyness': 'atm'},
                    {'action': 'buy', 'type': 'put', 'moneyness': 'atm'},
                ]
                max_risk = 2000
                max_reward = 'unlimited'
                prob = 0.45
                risk_level = 5
                suitable = 'advanced'
                capital = 2000
                greeks = {'delta': 0.0, 'vega': 1.0, 'theta': -0.3, 'gamma': 0.9}
            else:
                # Neutral + low IV → income strategies
                strategy_name = "Iron Condor"
                description = f"Sell OTM call spread + OTM put spread. Profit from time decay and low vol."
                legs = [
                    {'action': 'sell', 'type': 'call', 'otm_pct': 0.10},
                    {'action': 'buy', 'type': 'call', 'otm_pct': 0.20},
                    {'action': 'sell', 'type': 'put', 'otm_pct': 0.10},
                    {'action': 'buy', 'type': 'put', 'otm_pct': 0.20},
                ]
                max_risk = 500
                max_reward = 300
                prob = 0.70
                risk_level = 3
                suitable = 'intermediate'
                capital = 500
                greeks = {'delta': 0.0, 'vega': -0.5, 'theta': 0.2, 'gamma': -0.2}
        
        expected_val = (max_reward * prob) - (max_risk * (1 - prob)) if isinstance(max_reward, (int, float)) else 0
        
        return OptionStrategy(
            strategy_name=strategy_name,
            description=description,
            ticker=ticker,
            legs=legs,
            max_risk=max_risk,
            max_reward=max_reward if isinstance(max_reward, (int, float)) else 0,
            probability_profit=prob,
            expected_value=expected_val,
            greeks=greeks,
            suitable_for=suitable,
            risk_level=risk_level,
            capital_required=capital,
        )

    def _select_strikes(
        self,
        ticker: str,
        direction: Direction,
        strategy: OptionStrategy,
        market_data: Optional[Dict] = None
    ) -> List[float]:
        """
        Select concrete strike prices for the strategy.
        
        Uses:
        - Current stock price (from market data)
        - Implied volatility
        - Desired delta exposure (for directional trades)
        - Liquidity (open interest, volume)
        """
        current_price = market_data.get('price', 100.0) if market_data else 100.0
        iv = market_data.get('iv', 0.3) if market_data else 0.3
        
        strikes = []
        
        for leg in strategy.legs:
            action = leg['action']
            option_type = leg['type']
            
            if 'moneyness' in leg and leg['moneyness'] == 'atm':
                strike = current_price
            elif 'otm_pct' in leg:
                # OTM by x%
                otm_pct = leg['otm_pct']
                if option_type == 'call':
                    strike = current_price * (1 + otm_pct)
                else:  # put
                    strike = current_price * (1 - otm_pct)
                # Round to nearest $0.50 or $1.00 increment
                if current_price < 50:
                    strike = round(strike * 2) / 2
                else:
                    strike = round(strike)
            else:
                # Default to slight OTM
                strike = current_price * 1.05 if option_type == 'call' else current_price * 0.95
            
            strikes.append(round(strike, 2))
        
        return strikes

    def _recommend_expiry(self, time_horizon: TimeHorizon) -> int:
        """
        Recommend days to expiration (DTE).
        
        Short-term: 7-30 DTE
        Medium-term: 30-90 DTE
        Long-term: 90+ DTE
        """
        expiry_map = {
            TimeHorizon.IMMEDIATE: 14,    # 2 weeks
            TimeHorizon.SHORT_TERM: 30,    # 1 month
            TimeHorizon.MEDIUM_TERM: 60,   # 2 months
            TimeHorizon.LONG_TERM: 120,    # 4 months
            TimeHorizon.UNKNOWN: 45,       # ~1.5 months default
        }
        return expiry_map.get(time_horizon, 30)

    def _calculate_risk_metrics(
        self,
        strategy: OptionStrategy,
        strikes: List[float],
        classification: EventClassification,
        iv_impact: float
    ) -> Dict[str, float]:
        """
        Calculate risk-adjusted metrics for the recommendation.
        """
        # Simplified Greeks aggregation
        greeks = strategy.greeks.copy()
        
        # Adjust Greeks for IV change
        greeks['vega'] = greeks.get('vega', 0) * iv_impact
        
        # Adjust for time horizon (theta decay)
        days_to_expiry = self._recommend_expiry(classification.time_horizon)
        greeks['theta'] = greeks.get('theta', 0) * (days_to_expiry / 30)
        
        return {
            'max_loss_pct': strategy.max_risk / strategy.capital_required if strategy.capital_required else 0,
            'risk_level': strategy.risk_level,
            'probability_profit': strategy.probability_profit,
            'expected_value_pct': (strategy.expected_value / strategy.capital_required) * 100 if strategy.capital_required else 0,
            'greeks': greeks,
            'capital_required': strategy.capital_required,
        }


class CallPutAnalyzer:
    """
    Specialized analyzer for call vs put volume/interest dynamics.
    
    Tracks:
    - Call/Put open interest ratio
    - Volume skew (more calls or puts traded?)
    - Institutional flow patterns
    - Retail sentiment (options lottery tickets)
    """
    
    def analyze_flow(self, ticker: str, market_data: Dict) -> Dict[str, Any]:
        """Analyze call/put flow and identify anomalies"""
        call_volume = market_data.get('call_volume', 0)
        put_volume = market_data.get('put_volume', 0)
        
        if put_volume == 0:
            ratio = float('inf')
        else:
            ratio = call_volume / put_volume
        
        sentiment = 'bullish' if ratio > 1.0 else 'bearish'
        
        # Detect unusual activity
        is_unusual = (
            (ratio > 2.0 and ratio < 5.0) or    # unusually high call buying
            (ratio < 0.5 and ratio > 0.2) or    # unusually high put buying
            (call_volume > 10000 or put_volume > 10000)  # high absolute volume
        )
        
        return {
            'ticker': ticker,
            'call_volume': call_volume,
            'put_volume': put_volume,
            'call_put_ratio': ratio,
            'sentiment': sentiment,
            'is_unusual_activity': is_unusual,
            'total_volume': call_volume + put_volume,
        }


class VolatilityPredictor:
    """
    Predicts implied volatility changes post-event.
    
    Uses:
    - Historical IV behavior around similar events
    - Current IV percentile
    - Event magnitude
    - Time to expiry
    """
    
    def predict_iv_change(
        self,
        event_type: EventType,
        current_iv: float,
        iv_percentile: float,
        days_to_expiry: int
    ) -> Tuple[float, float]:
        """
        Predict IV change and post-event IV level.
        
        Returns:
            (iv_change_pct, post_event_iv)
        """
        # Baseline crush based on event type
        base_crush = {
            EventType.EARNINGS: 0.30,  # 30% drop post-earnings
            EventType.MERGER_ACQUISITION: 0.20,
            EventType.REGULATORY: 0.25,
        }.get(event_type, 0.10)  # Default small crush
        
        # Adjust by current IV percentile
        # If IV already high (90th percentile), bigger absolute drop but similar % drop
        percentile_factor = 0.8 + (iv_percentile * 0.4)
        
        iv_change = -base_crush * percentile_factor  # Negative = crush
        
        # Pre-event IV expansion (already occurred)
        # For prediction, focus on post-event IV
        post_event_iv = current_iv * (1 + iv_change)
        
        return iv_change, max(0.1, post_event_iv)


class StrikeSelector:
    """
    Selects optimal strike prices based on multiple criteria.
    """
    
    def __init__(self, config):
        self.config = config
        
    def select_by_delta(
        self,
        delta: float,  # Target delta (0.3-0.7 for directional trades)
        option_type: str,
        current_price: float,
        iv: float,
        dte: int
    ) -> float:
        """
        Solve Black-Scholes for strike achieving target delta.
        Simplified approximation - production uses option pricing engine.
        """
        if option_type == 'call':
            strike = current_price / (1 + delta) if delta > 0 else current_price * 1.1
        else:
            strike = current_price * (1 + delta) if delta < 0 else current_price * 0.9
        
        return round(strike, 2)
    
    def select_by_probability(
        self,
        target_prob_itm: float,
        option_type: str,
        current_price: float,
        iv: float,
        dte: int
    ) -> float:
        """
        Select strike with desired probability of expiring ITM.
        Uses normal approximation (Black-Scholes simplified).
        """
        if option_type == 'call':
            target_delta = target_prob_itm  # Rough approximation
            return self.select_by_delta(target_delta, 'call', current_price, iv, dte)
        else:
            target_delta = 1.0 - target_prob_itm  # Put delta = -(1 - prob)
            return self.select_by_delta(-target_delta, 'put', current_price, iv, dte)
    
    def liquid_strikes(self, ticker: str, candidate_strikes: List[float]) -> List[float]:
        """
        Filter strikes by minimum liquidity (open interest, volume).
        Would query market data provider - returns all for now.
        """
        # In production: filter by open_interest > 100, volume > 50
        return candidate_strikes

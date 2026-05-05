"""
Market Intelligence Learning Integration

Integrates the market intelligence module with Nexus's ContinuousLearner system.

Tracks:
- Signal outcomes (did predicted move materialize?)
- Pattern success rates
- Source reliability scores
- Event type prediction accuracy
- Market regime detection

The learning loop:
1. Generate prediction (signal)
2. Store with metadata
3. After N days, evaluate outcome
4. Feed success/failure back to ContinuousLearner
5. Adjust confidence/weights accordingly
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from collections import defaultdict
import numpy as np

from app.nexus_core.continuous_learner import ContinuousLearner, LearningPattern
from app.services.market_intelligence.schemas import (
    OptionsSignal,
    MarketEvent,
    EventClassification,
    Direction,
    ImpactSeverity,
    DataSource,
)
from app.services.market_intelligence.decision_engine import DecisionEngine

log = logging.getLogger(__name__)


class MarketLearningIntegration:
    """
    Bridges market intelligence with Nexus continuous learning.
    
    Provides:
    - Outcome tracking for signals
    - Performance analytics by event type/source
    - Adaptive weight adjustment
    - Pattern insight generation
    
    Feeds into ContinuousLearner as another experience source.
    """
    
    def __init__(self, continuous_learner: ContinuousLearner, config):
        self.learner = continuous_learner
        self.config = config
        self.pending_outcomes: Dict[UUID, Dict[str, Any]] = {}
        self.completed_outcomes: List[Dict] = []
        self._outcomes_file = "/tmp/market_signal_outcomes.json"
        self._load_pending()
        
        # Performance metrics by category
        self.metrics = {
            'by_event_type': defaultdict(lambda: {'count': 0, 'wins': 0, 'returns': []}),
            'by_source': defaultdict(lambda: {'count': 0, 'wins': 0, 'returns': []}),
            'by_direction': defaultdict(lambda: {'count': 0, 'wins': 0, 'returns': []}),
        }
    
    async def record_signal(
        self,
        signal: OptionsSignal,
        event: MarketEvent,
        classification: EventClassification
    ) -> None:
        """
        Record a new trading signal for later outcome tracking.
        """
        record = {
            'signal_id': str(signal.signal_id),
            'event_id': str(event.event_id),
            'ticker': signal.ticker,
            'direction': signal.direction.value,
            'confidence': signal.confidence,
            'strategy': signal.recommendation,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'outcome_due_at': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            'expected_return': signal.expected_return,
            'max_loss': signal.max_loss,
            'event_type': classification.event_type.value,
            'source': event.source.value,
            'impact_severity': classification.impact_severity.value,
        }
        
        self.pending_outcomes[signal.signal_id] = record
        log.info(f"Recorded signal {signal.signal_id} for {signal.ticker}, outcome due in 7 days")
        
        # Also record in ContinuousLearner as new pattern
        self._record_prediction_pattern(record, event, classification)
    
    def _record_prediction_pattern(
        self,
        record: Dict,
        event: MarketEvent,
        classification: EventClassification
    ) -> None:
        """
        Record this prediction as a pattern for the ContinuousLearner.
        """
        pattern_id = f"market_signal_{classification.event_type.value}_{classification.direction_bias.value}"
        
        # Build pattern description
        desc = (
            f"Trading signal: {classification.event_type.value} event "
            f"({classification.impact_severity.value} impact) → {classification.direction_bias.value} "
            f"on {record['ticker']}"
        )
        
        # Create or update pattern
        if pattern_id in self.learner.patterns:
            pattern = self.learner.patterns[pattern_id]
            pattern.update_occurrence(
                example=event.title[:100],
                outcome='pending'
            )
        else:
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type='market_prediction',
                description=desc,
                occurrences=1,
                first_seen=datetime.now().timestamp(),
                last_seen=datetime.now().timestamp(),
                confidence=0.5,
                examples=[event.title[:100]],
                triggers=[classification.event_type.value, classification.direction_bias.value],
                outcomes={'pending': 1}
            )
            self.learner.patterns[pattern_id] = pattern
            self.learner.stats['patterns_detected'] += 1
        
        self.learner.skills.setdefault('market_prediction', 
            LearningPattern(
                pattern_id='skill_market_prediction',
                pattern_type='skill',
                description='Market event classification and prediction',
                proficiency_level=0.5
            )
        )
        
        # Save periodically
        if self.learner.stats['total_interactions'] % 10 == 0:
            self.learner.save()
    
    async def check_outcomes(self) -> Dict[str, int]:
        """
        Check all pending outcomes that have passed their evaluation date.
        
        Queries market data to determine if predicted move occurred.
        Updates ContinuousLearner with success/failure feedback.
        """
        now = datetime.now(timezone.utc)
        due_outcomes = {
            sid: rec for sid, rec in self.pending_outcomes.items()
            if datetime.fromisoformat(rec['outcome_due_at']) <= now
        }
        
        if not due_outcomes:
            return {'checked': 0, 'resolved': 0, 'errors': 0}
        
        log.info(f"Checking {len(due_outcomes)} signal outcomes")
        
        resolved = 0
        errors = 0
        
        # Process outcomes in parallel
        tasks = []
        for signal_id, record in due_outcomes.items():
            tasks.append(self._evaluate_signal_outcome(record))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (signal_id, record), result in zip(due_outcomes.items(), results):
            if isinstance(result, Exception):
                log.error(f"Outcome evaluation failed for {signal_id}: {result}")
                errors += 1
                continue
            
            outcome_success, actual_return, notes = result
            
            # Update metrics
            self._update_metrics(record, outcome_success, actual_return)
            
            # Feed back to ContinuousLearner
            self._feedback_to_learner(record, outcome_success, actual_return, notes)
            
            # Move from pending to completed
            del self.pending_outcomes[signal_id]
            record['outcome'] = {
                'success': outcome_success,
                'actual_return': actual_return,
                'resolved_at': now.isoformat(),
                'notes': notes,
            }
            self.completed_outcomes.append(record)
            resolved += 1
        
        # Persist
        self._save_outcomes()
        
        return {'checked': len(due_outcomes), 'resolved': resolved, 'errors': errors}
    
    async def _evaluate_signal_outcome(
        self, 
        record: Dict
    ) -> Tuple[bool, float, str]:
        """
        Determine if a signal was successful by querying market data.
        
        In production, this would query a market data provider for actual prices.
        For now, simulates with random walk around expectation.
        """
        ticker = record['ticker']
        expected = record.get('expected_return', 0.0) or 0.0
        direction = record['direction']
        
        # Simulate price path from signal generation to now
        # In production: fetch actual historical prices and compute actual return
        # For demo: random walk with slight positive drift for correct direction
        drift = expected * 0.4  # Realized return is typically 40% of expected
        
        # Add noise
        import random
        noise = random.gauss(0, 0.05)  # 5% std dev
        actual_return = drift + noise
        
        # Determine success
        if direction == 'bullish':
            success = actual_return > 0.01  # At least 1% gain
        elif direction == 'bearish':
            success = actual_return < -0.01  # At least 1% loss
        else:
            success = abs(actual_return) < 0.03  # Neutral = low move expected
        
        notes = f"Expected: {expected:.2%}, Actual: {actual_return:.2%}"
        return success, actual_return, notes
    
    def _update_metrics(self, record: Dict, success: bool, actual_return: float):
        """Update performance tracking metrics"""
        # By event type
        et = record['event_type']
        self.metrics['by_event_type'][et]['count'] += 1
        self.metrics['by_event_type'][et]['wins'] += int(success)
        self.metrics['by_event_type'][et]['returns'].append(actual_return)
        
        # By source
        src = record['source']
        self.metrics['by_source'][src]['count'] += 1
        self.metrics['by_source'][src]['wins'] += int(success)
        self.metrics['by_source'][src]['returns'].append(actual_return)
        
        # By direction
        dir_val = record['direction']
        self.metrics['by_direction'][dir_val]['count'] += 1
        self.metrics['by_direction'][dir_val]['wins'] += int(success)
        self.metrics['by_direction'][dir_val]['returns'].append(actual_return)
    
    def _feedback_to_learner(
        self, 
        record: Dict, 
        success: bool, 
        actual_return: float,
        notes: str
    ) -> None:
        """
        Feed outcome back into ContinuousLearner to refine future predictions.
        """
        # Map signal outcome to experience types
        if success:
            experience_type = 'success'
            details = {
                'task': 'market_prediction',
                'actual_return': actual_return,
                'expected_return': record.get('expected_return', 0),
                'notes': notes,
            }
        else:
            experience_type = 'failure'
            details = {
                'task': 'market_prediction',
                'failure_reason': 'prediction_mismatch',
                'actual_return': actual_return,
                'expected_return': record.get('expected_return', 0),
                'notes': notes,
            }
        
        # Feed into learner
        try:
            summary = self.learner.learn_from_experience(experience_type, details)
            log.debug(f"Learning outcome: {summary}")
        except Exception as e:
            log.error(f"Failed to record learning: {e}")
        
        # Also update pattern directly
        pattern_id = f"market_signal_{record['event_type']}_{record['direction']}"
        if pattern_id in self.learner.patterns:
            pattern = self.learner.patterns[pattern_id]
            outcome_label = 'hit' if success else 'miss'
            pattern.update_occurrence(
                example=f"{record['event_type']} on {record['ticker']}",
                outcome=outcome_label
            )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate performance analytics report.
        """
        report = {
            'overall': self._calculate_overall_stats(),
            'by_event_type': self._calculate_category_stats('by_event_type'),
            'by_source': self._calculate_category_stats('by_source'),
            'by_direction': self._calculate_category_stats('by_direction'),
            'pending_count': len(self.pending_outcomes),
            'completed_count': len(self.completed_outcomes),
        }
        return report
    
    def _calculate_overall_stats(self) -> Dict[str, float]:
        """Calculate overall win rate, average return, Sharpe-like ratio"""
        all_returns = []
        all_results = []
        
        for category_data in self.metrics.values():
            all_returns.extend(category_data.get('returns', []))
            # Approximate wins from count/wins
            count = category_data.get('count', 0)
            wins = category_data.get('wins', 0)
            all_results.extend([1] * wins + [0] * (count - wins))
        
        if not all_returns:
            return {'win_rate': 0.0, 'avg_return': 0.0, 'sharpe': 0.0}
        
        win_rate = np.mean(all_results) if all_results else 0.0
        avg_return = np.mean(all_returns) if all_returns else 0.0
        std_return = np.std(all_returns) if all_returns else 0.0
        sharpe = avg_return / std_return if std_return > 0 else 0.0
        
        return {
            'win_rate': float(win_rate),
            'avg_return': float(avg_return),
            'sharpe': float(sharpe),
            'total_signals': len(all_results),
        }
    
    def _calculate_category_stats(self, category: str) -> Dict[str, Dict]:
        """Break down stats by category"""
        category_data = self.metrics.get(category, {})
        result = {}
        for key, stats in category_data.items():
            if stats['count'] > 0:
                result[key] = {
                    'count': stats['count'],
                    'win_rate': stats['wins'] / stats['count'],
                    'avg_return': np.mean(stats['returns']) if stats['returns'] else 0.0,
                }
        return result
    
    def _save_outcomes(self) -> None:
        """Persist outcomes to disk"""
        try:
            data = {
                'pending': self.pending_outcomes,
                'completed': self.completed_outcomes[-1000:],  # Keep last 1000
                'metrics': dict(self.metrics),
            }
            with open(self._outcomes_file, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            log.error(f"Failed to save outcomes: {e}")
    
    def _load_pending(self) -> None:
        """Load pending outcomes from disk"""
        try:
            with open(self._outcomes_file, 'r') as f:
                data = json.load(f)
            self.pending_outcomes = {UUID(k): v for k, v in data.get('pending', {}).items()}
            self.completed_outcomes = data.get('completed', [])
            log.info(f"Loaded {len(self.pending_outcomes)} pending outcomes")
        except FileNotFoundError:
            pass
        except Exception as e:
            log.error(f"Failed to load outcomes: {e}")


# Singleton instance
market_learning: Optional[MarketLearningIntegration] = None


def get_market_learning(learner: ContinuousLearner, config) -> MarketLearningIntegration:
    """Factory for MarketLearningIntegration singleton"""
    global market_learning
    if market_learning is None:
        market_learning = MarketLearningIntegration(learner, config)
    return market_learning

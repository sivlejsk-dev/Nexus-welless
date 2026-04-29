"""
Proactive Intelligence System - Anticipates user needs and suggests actions
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json
import os


class SuggestionType(Enum):
    """Types of proactive suggestions"""
    FOLLOW_UP = "follow_up"           # Natural next step
    RELATED = "related"                # Related action
    OPTIMIZATION = "optimization"      # Better way to do something
    INFORMATION = "information"        # Additional helpful info
    REMINDER = "reminder"              # Based on previous conversations
    COMPLETION = "completion"          # Complete partial task


@dataclass
class ProactiveSuggestion:
    """A proactive suggestion for the user"""
    suggestion_text: str
    suggestion_type: SuggestionType
    relevance_score: float            # 0.0 - 1.0
    context_based_on: str             # What triggered this suggestion
    action_if_accepted: str           # What to do if user says yes
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserPattern:
    """Learned pattern about user behavior"""
    pattern_type: str                 # e.g., "frequent_query", "time_based"
    trigger: str                      # What triggers this pattern
    typical_action: str               # What user typically does
    frequency: int                    # How often this occurs
    last_seen: datetime              # When last observed
    confidence: float                 # 0.0 - 1.0


class ProactiveIntelligence:
    """
    System for anticipating user needs and making proactive suggestions.
    Learns from conversation patterns and suggests relevant actions.
    """
    
    def __init__(self):
        self.learned_patterns: List[UserPattern] = []
        self.conversation_analysis = []
        self.suggestion_history = []
        self._load_learned_patterns()
    
    def _storage_path(self) -> str:
        """Path to store learned patterns"""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "outputs"))
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "proactive_patterns.json")
    
    def _load_learned_patterns(self):
        """Load previously learned patterns"""
        try:
            path = self._storage_path()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for p in data.get('patterns', []):
                        self.learned_patterns.append(UserPattern(
                            pattern_type=p['pattern_type'],
                            trigger=p['trigger'],
                            typical_action=p['typical_action'],
                            frequency=p['frequency'],
                            last_seen=datetime.fromisoformat(p['last_seen']),
                            confidence=p['confidence']
                        ))
        except Exception as e:
            print(f"Proactive patterns load failed: {e}")
    
    def _save_learned_patterns(self):
        """Save learned patterns to disk"""
        try:
            path = self._storage_path()
            data = {
                'patterns': [
                    {
                        'pattern_type': p.pattern_type,
                        'trigger': p.trigger,
                        'typical_action': p.typical_action,
                        'frequency': p.frequency,
                        'last_seen': p.last_seen.isoformat(),
                        'confidence': p.confidence
                    }
                    for p in self.learned_patterns
                ],
                'last_updated': datetime.now().isoformat()
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Proactive patterns save failed: {e}")
    
    def analyze_conversation_flow(self, recent_exchanges: List[Dict[str, Any]]) -> List[ProactiveSuggestion]:
        """
        Analyze recent conversation to generate proactive suggestions.
        Returns suggestions ordered by relevance.
        """
        suggestions = []
        
        if not recent_exchanges:
            return suggestions
        
        # Get last few exchanges
        last_3 = recent_exchanges[-3:] if len(recent_exchanges) >= 3 else recent_exchanges
        
        # Analyze for patterns
        for exchange in last_3:
            user_input = exchange.get('user_input', '').lower()
            ai_response = exchange.get('ai_response', '')
            task_type = exchange.get('task_type', '')
            
            # Generate context-based suggestions
            context_suggestions = self._generate_context_suggestions(user_input, task_type)
            suggestions.extend(context_suggestions)
        
        # Check for incomplete tasks
        incomplete_suggestions = self._suggest_task_completion(last_3)
        suggestions.extend(incomplete_suggestions)
        
        # Check learned patterns
        pattern_suggestions = self._suggest_from_patterns(recent_exchanges)
        suggestions.extend(pattern_suggestions)
        
        # Sort by relevance
        suggestions.sort(key=lambda s: s.relevance_score, reverse=True)
        
        return suggestions[:5]  # Return top 5
    
    def _generate_context_suggestions(self, user_input: str, task_type: str) -> List[ProactiveSuggestion]:
        """Generate suggestions based on current context"""
        suggestions = []
        
        # Stock-related follow-ups
        if 'stock' in task_type or any(word in user_input for word in ['stock', 'ticker', 'share']):
            suggestions.append(ProactiveSuggestion(
                suggestion_text="Would you like to see recent news about this stock?",
                suggestion_type=SuggestionType.FOLLOW_UP,
                relevance_score=0.8,
                context_based_on="stock_query",
                action_if_accepted="fetch_stock_news"
            ))
            
            suggestions.append(ProactiveSuggestion(
                suggestion_text="Should I compare this with similar stocks in the sector?",
                suggestion_type=SuggestionType.RELATED,
                relevance_score=0.7,
                context_based_on="stock_query",
                action_if_accepted="compare_stocks"
            ))
        
        # Code-related follow-ups
        if 'code' in task_type or any(word in user_input for word in ['code', 'function', 'script']):
            suggestions.append(ProactiveSuggestion(
                suggestion_text="Want me to run this code and show you the output?",
                suggestion_type=SuggestionType.FOLLOW_UP,
                relevance_score=0.85,
                context_based_on="code_generation",
                action_if_accepted="execute_code"
            ))
            
            suggestions.append(ProactiveSuggestion(
                suggestion_text="Should I create test cases for this code?",
                suggestion_type=SuggestionType.RELATED,
                relevance_score=0.75,
                context_based_on="code_generation",
                action_if_accepted="generate_tests"
            ))
        
        # Research-related follow-ups
        if 'research' in task_type or any(word in user_input for word in ['what is', 'tell me', 'explain']):
            suggestions.append(ProactiveSuggestion(
                suggestion_text="Want me to explore related topics?",
                suggestion_type=SuggestionType.RELATED,
                relevance_score=0.7,
                context_based_on="research_query",
                action_if_accepted="expand_research"
            ))
        
        return suggestions
    
    def _suggest_task_completion(self, recent_exchanges: List[Dict[str, Any]]) -> List[ProactiveSuggestion]:
        """Suggest completing partially finished tasks"""
        suggestions = []
        
        # Check if user asked multiple questions but only got one answered
        questions_asked = sum(1 for ex in recent_exchanges if '?' in ex.get('user_input', ''))
        
        if questions_asked > 1:
            suggestions.append(ProactiveSuggestion(
                suggestion_text="I noticed you had multiple questions. Want me to address the others?",
                suggestion_type=SuggestionType.COMPLETION,
                relevance_score=0.75,
                context_based_on="multiple_questions",
                action_if_accepted="answer_remaining_questions"
            ))
        
        return suggestions
    
    def _suggest_from_patterns(self, recent_exchanges: List[Dict[str, Any]]) -> List[ProactiveSuggestion]:
        """Generate suggestions based on learned user patterns"""
        suggestions = []
        
        if not recent_exchanges:
            return suggestions
        
        last_exchange = recent_exchanges[-1]
        last_input = last_exchange.get('user_input', '').lower()
        
        # Check if this matches a learned pattern
        for pattern in self.learned_patterns:
            if pattern.confidence > 0.6 and pattern.trigger.lower() in last_input:
                suggestions.append(ProactiveSuggestion(
                    suggestion_text=f"Based on your usual workflow, should I {pattern.typical_action}?",
                    suggestion_type=SuggestionType.REMINDER,
                    relevance_score=pattern.confidence,
                    context_based_on="learned_pattern",
                    action_if_accepted=pattern.typical_action
                ))
        
        return suggestions
    
    def learn_from_interaction(self, user_input: str, task_executed: str, 
                               user_accepted_suggestion: bool, suggestion_type: Optional[str] = None):
        """Learn from user's interaction to improve future suggestions"""
        # Identify potential pattern
        trigger = self._extract_trigger(user_input)
        
        if not trigger:
            return
        
        # Check if we've seen this pattern before
        existing_pattern = None
        for pattern in self.learned_patterns:
            if pattern.trigger.lower() == trigger.lower() and pattern.typical_action == task_executed:
                existing_pattern = pattern
                break
        
        if existing_pattern:
            # Update existing pattern
            existing_pattern.frequency += 1
            existing_pattern.last_seen = datetime.now()
            # Increase confidence
            existing_pattern.confidence = min(0.95, existing_pattern.confidence + 0.05)
        else:
            # Create new pattern
            new_pattern = UserPattern(
                pattern_type="task_sequence",
                trigger=trigger,
                typical_action=task_executed,
                frequency=1,
                last_seen=datetime.now(),
                confidence=0.5
            )
            self.learned_patterns.append(new_pattern)
        
        self._save_learned_patterns()
    
    def _extract_trigger(self, user_input: str) -> Optional[str]:
        """Extract key trigger phrase from user input"""
        # Remove common words
        words = user_input.lower().split()
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 
                      'is', 'are', 'was', 'were', 'can', 'could', 'should', 'would'}
        
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if meaningful_words:
            # Return first 2-3 meaningful words as trigger
            return ' '.join(meaningful_words[:min(3, len(meaningful_words))])
        
        return None
    
    def should_show_suggestion(self, suggestion: ProactiveSuggestion, 
                              conversation_context: Dict[str, Any]) -> bool:
        """Determine if suggestion should be shown now"""
        # Don't be too aggressive with suggestions
        if suggestion.relevance_score < 0.6:
            return False
        
        # Check if we recently showed similar suggestion
        recent_suggestions = [s for s in self.suggestion_history[-5:] 
                             if s.get('type') == suggestion.suggestion_type.value]
        
        if recent_suggestions:
            # Don't repeat same type too often
            return False
        
        return True
    
    def format_suggestion(self, suggestion: ProactiveSuggestion) -> str:
        """Format suggestion in natural, non-intrusive way"""
        # Make it conversational
        if suggestion.suggestion_type == SuggestionType.FOLLOW_UP:
            return f"\n💡 {suggestion.suggestion_text}"
        elif suggestion.suggestion_type == SuggestionType.RELATED:
            return f"\n🔗 {suggestion.suggestion_text}"
        elif suggestion.suggestion_type == SuggestionType.OPTIMIZATION:
            return f"\n⚡ {suggestion.suggestion_text}"
        elif suggestion.suggestion_type == SuggestionType.REMINDER:
            return f"\n📌 {suggestion.suggestion_text}"
        else:
            return f"\n💬 {suggestion.suggestion_text}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns"""
        return {
            'total_patterns': len(self.learned_patterns),
            'high_confidence_patterns': len([p for p in self.learned_patterns if p.confidence > 0.7]),
            'recent_patterns': len([p for p in self.learned_patterns 
                                   if (datetime.now() - p.last_seen).days < 7]),
            'most_frequent_patterns': sorted(
                [(p.trigger, p.frequency) for p in self.learned_patterns],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


# Global instance
proactive_intelligence = ProactiveIntelligence()

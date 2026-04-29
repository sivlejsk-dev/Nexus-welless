"""
Enhanced Conversational Understanding - Natural dialogue and context tracking
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re


@dataclass
class DialogueTurn:
    """Represents a single turn in conversation"""
    speaker: str  # 'user' or 'ai'
    text: str
    timestamp: datetime
    intent: Optional[str] = None
    entities: List[Dict[str, Any]] = field(default_factory=list)
    sentiment: float = 0.0
    topic: Optional[str] = None


@dataclass
class ConversationThread:
    """A thread of related conversation turns"""
    thread_id: str
    topic: str
    turns: List[DialogueTurn] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True


class EnhancedConversationalUnderstanding:
    """
    System for deep conversational understanding including:
    - Pronoun resolution across turns
    - Topic tracking and threading
    - Implicit reference understanding
    - Conversational implicature detection
    """
    
    def __init__(self):
        self.conversation_threads: List[ConversationThread] = []
        self.current_thread: Optional[ConversationThread] = None
        self.discourse_markers = self._load_discourse_markers()
        self.reference_cache = {}  # Cache resolved references
        
    def _load_discourse_markers(self) -> Dict[str, List[str]]:
        """Load discourse markers for understanding conversation flow"""
        return {
            'topic_change': [
                'by the way', 'speaking of', 'changing the subject', 'on another note',
                'anyway', 'moving on', 'different topic', 'new question'
            ],
            'elaboration': [
                'in other words', 'that is', 'specifically', 'more precisely',
                'to clarify', 'what i mean is', 'in particular'
            ],
            'contrast': [
                'but', 'however', 'on the other hand', 'although', 'though',
                'nevertheless', 'yet', 'instead', 'rather'
            ],
            'continuation': [
                'and', 'also', 'furthermore', 'moreover', 'additionally',
                'plus', 'as well', 'in addition'
            ],
            'conclusion': [
                'so', 'therefore', 'thus', 'hence', 'as a result',
                'in conclusion', 'to sum up', 'overall'
            ],
            'clarification_request': [
                'what do you mean', 'can you explain', 'clarify', 'elaborate',
                'what exactly', 'i dont understand', 'confused'
            ]
        }
    
    def process_user_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input with deep understanding of conversational context.
        Returns enriched understanding including resolved references.
        """
        # Detect discourse markers
        discourse_type = self._detect_discourse_marker(user_input)
        
        # Handle topic changes
        if discourse_type == 'topic_change':
            self._start_new_thread(user_input)
        
        # Resolve pronouns and references
        resolved_text = self._resolve_references(user_input, context)
        
        # Detect implicit requests
        implicit_intent = self._detect_implicit_intent(resolved_text, context)
        
        # Handle ellipsis (incomplete sentences that rely on context)
        completed_text = self._complete_ellipsis(resolved_text, context)
        
        # Detect conversational implicature (what user implies but doesn't say)
        implicature = self._detect_implicature(completed_text, context)
        
        return {
            'original_text': user_input,
            'resolved_text': resolved_text,
            'completed_text': completed_text,
            'discourse_type': discourse_type,
            'implicit_intent': implicit_intent,
            'implicature': implicature,
            'needs_clarification': self._needs_clarification(user_input, context)
        }
    
    def _detect_discourse_marker(self, text: str) -> Optional[str]:
        """Detect discourse markers indicating conversation flow"""
        text_lower = text.lower()
        
        for marker_type, markers in self.discourse_markers.items():
            if any(marker in text_lower for marker in markers):
                return marker_type
        
        return None
    
    def _resolve_references(self, text: str, context: Dict[str, Any]) -> str:
        """Resolve pronouns and implicit references"""
        resolved = text
        text_lower = text.lower()
        
        # Pronouns to resolve
        pronouns = {
            'it': self._find_last_entity(context, exclude_person=True),
            'that': self._find_last_mentioned(context),
            'this': self._find_last_mentioned(context),
            'they': self._find_last_entity(context, plural=True),
            'them': self._find_last_entity(context, plural=True),
            'those': self._find_last_entity(context, plural=True),
            'these': self._find_last_entity(context, plural=True),
            'he': self._find_last_person(context, gender='male'),
            'she': self._find_last_person(context, gender='female')
        }
        
        # Replace pronouns with referents
        words = text.split()
        resolved_words = []
        
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?')
            
            if word_lower in pronouns and pronouns[word_lower]:
                # Check if it's actually a pronoun (not part of phrase like \"it's\")
                if i == 0 or words[i-1].lower() not in ['is', 'was', 'does']:
                    resolved_words.append(pronouns[word_lower])
                    # Cache this resolution
                    self.reference_cache[word_lower] = pronouns[word_lower]
                else:
                    resolved_words.append(word)
            else:
                resolved_words.append(word)
        
        resolved = ' '.join(resolved_words)
        
        # Handle phrases like \"the same\", \"similar\", \"another one\"
        if 'the same' in text_lower or 'same thing' in text_lower:
            last_topic = context.get('current_topic')
            if last_topic:
                resolved = resolved.replace('the same', last_topic).replace('same thing', last_topic)
        
        if 'another one' in text_lower or 'similar' in text_lower:
            last_entity = self._find_last_entity(context)
            if last_entity:
                resolved = resolved.replace('another one', f'another {last_entity}')
        
        return resolved
    
    def _find_last_entity(self, context: Dict[str, Any], exclude_person: bool = False, plural: bool = False) -> Optional[str]:
        """Find the last mentioned entity"""
        entities = context.get('recent_entities', [])
        
        if not entities:
            # Try to get from last response
            last_response = context.get('last_ai_response', '')
            if last_response:
                # Extract nouns from last response (simple heuristic)
                words = last_response.split()
                for word in reversed(words):
                    if word[0].isupper() and len(word) > 2:
                        return word
        
        for entity in reversed(entities):
            if exclude_person and entity.get('label') == 'PERSON':
                continue
            return entity.get('text')
        
        return None
    
    def _find_last_mentioned(self, context: Dict[str, Any]) -> Optional[str]:
        """Find the last mentioned concept"""
        last_input = context.get('last_user_input', '')
        
        if last_input:
            # Extract key noun or concept
            words = last_input.split()
            for word in reversed(words):
                if len(word) > 3 and word.lower() not in ['what', 'when', 'where', 'which', 'this', 'that']:
                    return word
        
        return self._find_last_entity(context)
    
    def _find_last_person(self, context: Dict[str, Any], gender: str = None) -> Optional[str]:
        """Find last mentioned person"""
        entities = context.get('recent_entities', [])
        
        for entity in reversed(entities):
            if entity.get('label') == 'PERSON':
                return entity.get('text')
        
        return None
    
    def _detect_implicit_intent(self, text: str, context: Dict[str, Any]) -> Optional[str]:
        """Detect intent that's implied but not explicitly stated"""
        text_lower = text.lower()
        
        # Implicit commands
        implicit_patterns = {
            'want_information': [
                r"i'm curious about", r"wondering about", r"interested in",
                r"would like to know", r"want to learn"
            ],
            'request_action': [
                r"could use", r"would help if", r"it would be great if",
                r"would be nice to", r"hoping you could"
            ],
            'express_confusion': [
                r"not sure", r"don't understand", r"confused about",
                r"unclear", r"doesn't make sense"
            ],
            'request_alternative': [
                r"instead", r"rather", r"different approach",
                r"another way", r"alternative"
            ]
        }
        
        for intent, patterns in implicit_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return None
    
    def _complete_ellipsis(self, text: str, context: Dict[str, Any]) -> str:
        """Complete elliptical constructions using context"""
        text_lower = text.lower().strip()
        
        # Handle single-word or fragment responses
        if len(text.split()) <= 3:
            last_question = context.get('last_user_input', '')
            
            # If previous was a question and this is short, it might be an answer
            if last_question and '?' in last_question:
                # Handle \"also\" or \"too\"
                if text_lower in ['also', 'too', 'same', 'me too', 'same here']:
                    # User wants the same thing as they asked about
                    return f"{last_question.replace('?', '')} also"
                
                # Handle comparative responses
                if text_lower in ['better', 'worse', 'faster', 'slower', 'more', 'less']:
                    return f"that is {text_lower} than before"
        
        # Handle phrases that reference previous context
        if text_lower.startswith(('and ', 'but ', 'or ', 'also ')):
            last_topic = context.get('current_topic', '')
            if last_topic:
                return f"{last_topic} {text}"
        
        return text
    
    def _detect_implicature(self, text: str, context: Dict[str, Any]) -> Optional[str]:
        """Detect conversational implicature (what's implied beyond literal meaning)"""
        text_lower = text.lower()
        
        # Polite requests (indirect speech acts)
        if any(phrase in text_lower for phrase in ['can you', 'could you', 'would you mind']):
            if '?' in text:
                return "polite_request"
        
        # Hedging (uncertainty markers suggesting need for confirmation)
        if any(word in text_lower for word in ['maybe', 'perhaps', 'possibly', 'might', 'could be']):
            return "uncertain_requires_validation"
        
        # Dissatisfaction (subtle complaints)
        if any(phrase in text_lower for phrase in ['i guess', 'i suppose', 'if you say so', 'whatever']):
            return "dissatisfied_with_previous"
        
        # Urgency markers
        if any(word in text_lower for word in ['quickly', 'asap', 'urgent', 'immediately', 'right now', 'hurry']):
            return "high_priority"
        
        return None
    
    def _needs_clarification(self, text: str, context: Dict[str, Any]) -> bool:
        """Determine if AI should ask for clarification"""
        text_lower = text.lower()
        
        # Very short or vague input
        if len(text.split()) <= 2 and not any(word in text_lower for word in ['yes', 'no', 'ok', 'sure']):
            return True
        
        # Multiple pronouns without clear referents
        pronoun_count = sum(1 for word in text_lower.split() if word in ['it', 'that', 'this', 'they', 'them'])
        if pronoun_count > 2:
            return True
        
        # Contradictory discourse markers
        if 'but' in text_lower and 'also' in text_lower:
            return True
        
        return False
    
    def _start_new_thread(self, user_input: str):
        """Start a new conversation thread"""
        if self.current_thread:
            self.current_thread.is_active = False
        
        thread_id = f"thread_{len(self.conversation_threads) + 1}"
        topic = self._extract_topic(user_input)
        
        self.current_thread = ConversationThread(
            thread_id=thread_id,
            topic=topic
        )
        self.conversation_threads.append(self.current_thread)
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text"""
        # Simple extraction: get first meaningful noun phrase
        words = text.split()
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
        
        meaningful = [w for w in words if w.lower() not in stop_words and len(w) > 3]
        
        if meaningful:
            return ' '.join(meaningful[:3])
        
        return 'general_conversation'
    
    def add_turn(self, speaker: str, text: str, intent: Optional[str] = None, 
                 entities: List[Dict[str, Any]] = None):
        """Add a turn to current conversation thread"""
        if not self.current_thread:
            self._start_new_thread(text)
        
        turn = DialogueTurn(
            speaker=speaker,
            text=text,
            timestamp=datetime.now(),
            intent=intent,
            entities=entities or []
        )
        
        self.current_thread.turns.append(turn)
        self.current_thread.last_updated = datetime.now()
    
    def get_conversation_context(self, window: int = 5) -> List[DialogueTurn]:
        """Get recent conversation turns for context"""
        if not self.current_thread:
            return []
        
        return self.current_thread.turns[-window:]
    
    def format_natural_acknowledgment(self, understood: Dict[str, Any]) -> str:
        """Format natural acknowledgment of what was understood"""
        if understood.get('discourse_type') == 'clarification_request':
            return "Let me clarify that for you."
        
        if understood.get('implicit_intent') == 'express_confusion':
            return "I see you're unsure. Let me explain better."
        
        if understood.get('implicature') == 'polite_request':
            return "Of course!"
        
        if understood.get('implicature') == 'high_priority':
            return "Right away!"
        
        # Default: acknowledge naturally
        return random.choice([
            "Got it!", "Understood!", "I see.", "Makes sense.", "Okay!"
        ])


# Global instance
enhanced_understanding = EnhancedConversationalUnderstanding()


# Import random for responses
import random

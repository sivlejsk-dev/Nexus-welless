"""
Phase 4 Ultimate: Advanced Conversational Enhancement Classes

These classes provide sophisticated natural language processing capabilities
for tone matching, flow enhancement, quality validation, and intelligent suggestions.
"""

import re
import random
from typing import Dict, List, Tuple, Optional
from textblob import TextBlob
from collections import defaultdict


class ToneAnalyzer:
    """Analyze user's communication tone and style preferences"""
    
    def __init__(self):
        self.casual_indicators = [
            'yeah', 'yep', 'nah', 'gonna', 'wanna', 'hey', 'yo', 
            'btw', 'tbh', 'kinda', 'sorta', 'dunno', 'sup', 'lol'
        ]
        self.formal_indicators = [
            'please', 'could you', 'would you', 'kindly', 'appreciate', 
            'request', 'grateful', 'thank you', 'sincerely', 'regards'
        ]
        self.technical_indicators = [
            'algorithm', 'implement', 'function', 'method', 'class', 
            'system', 'code', 'debug', 'compile', 'execute', 'optimize',
            'refactor', 'variable', 'parameter', 'return'
        ]
    
    def analyze_tone(self, text: str) -> Dict[str, bool]:
        """
        Analyze the tone and style of user input
        
        Returns dict with tone indicators:
        - is_casual: Uses informal language
        - is_formal: Uses formal/professional language
        - is_brief: Short, concise input
        - is_excited: Enthusiastic with exclamation marks
        - is_technical: Technical/programming vocabulary
        """
        text_lower = text.lower()
        
        # Count indicators
        casual_count = sum(1 for word in self.casual_indicators if word in text_lower)
        formal_count = sum(1 for word in self.formal_indicators if word in text_lower)
        technical_count = sum(1 for word in self.technical_indicators if word in text_lower)
        
        return {
            'is_casual': casual_count > 0 and formal_count == 0,
            'is_formal': formal_count > 0 and casual_count == 0,
            'is_brief': len(text.split()) <= 5,
            'is_excited': text.count('!') > 0 or (text.count('?') > 1 and '?' in text[-5:]),
            'is_technical': technical_count > 0,
            'is_question': text.strip().endswith('?'),
            'word_count': len(text.split()),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?')
        }


class ConversationalFlowEnhancer:
    """Enhance conversational flow to make responses more natural"""
    
    def __init__(self):
        self.mechanical_phrases = [
            ('I can help you with that. ', ''),
            ('Sure, I can do that. ', ''),
            ('Let me help you with that. ', ''),
            ('I understand your request. ', ''),
            ('I will assist you. ', ''),
        ]
        self.echo_threshold = 5  # Min words to check for echo
    
    def enhance_flow(self, response: str, user_input: str, context: Dict) -> str:
        """
        Enhance conversational flow by:
        1. Removing mechanical/robotic phrasing
        2. Preventing echo (repeating user's words)
        3. Adding natural transitions when appropriate
        4. Ensuring proper punctuation and spacing
        """
        if not response or len(response.strip()) < 20:
            return response
        
        enhanced = response
        
        # Remove echoing of user input
        enhanced = self._remove_echo(enhanced, user_input)
        
        # Remove mechanical phrases
        for mechanical, replacement in self.mechanical_phrases:
            if enhanced.startswith(mechanical):
                enhanced = replacement + enhanced[len(mechanical):]
        
        # Clean up spacing and punctuation
        enhanced = self._clean_formatting(enhanced)
        
        # Add natural transitions if switching topics
        if context and self._is_topic_switch(context):
            enhanced = self._add_topic_transition(enhanced, context)
        
        return enhanced.strip()
    
    def _remove_echo(self, response: str, user_input: str) -> str:
        """Remove echoing of user's exact words"""
        user_words = set(user_input.lower().split())
        
        if len(user_words) < self.echo_threshold:
            return response
        
        # Check if response starts by echoing user input
        response_start = ' '.join(response.split()[:min(5, len(response.split()))]).lower()
        user_start = user_input[:min(20, len(user_input))].lower()
        
        if response_start.startswith(user_start):
            sentences = response.split('. ')
            if len(sentences) > 1:
                return '. '.join(sentences[1:])
        
        return response
    
    def _clean_formatting(self, text: str) -> str:
        """Clean up formatting issues"""
        # Remove double periods, spaces, etc.
        text = re.sub(r'\.\.+', '.', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        return text.strip()
    
    def _is_topic_switch(self, context: Dict) -> bool:
        """Check if we're switching topics"""
        if not context:
            return False
        
        last_topic = context.get('last_topic')
        current_topic = context.get('topic')
        
        return last_topic and current_topic and last_topic != current_topic
    
    def _add_topic_transition(self, response: str, context: Dict) -> str:
        """Add natural topic transition phrases"""
        transitions = [
            "Switching gears, ",
            "On a different note, ",
            "Moving on to that, ",
            "Regarding your question, ",
            ""  # Sometimes no transition is best
        ]
        
        # Only add transition 30% of the time to avoid overuse
        if random.random() < 0.3:
            transition = random.choice(transitions)
            return transition + response
        
        return response


class ResponseQualityValidator:
    """Validate and improve response quality"""
    
    def __init__(self):
        self.min_length = 3
        self.generic_responses = [
            "that's interesting", "i see", "okay", "noted", "understood",
            "got it", "sure", "alright", "ok"
        ]
    
    def validate_response(self, response: str, user_input: str, context: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate response quality and suggest improvements
        
        Returns:
            (is_valid, improved_response)
            - is_valid: True if response meets quality standards
            - improved_response: Improved version if needed, None otherwise
        """
        if not response or len(response.strip()) < self.min_length:
            return False, "I'm not sure how to respond to that. Could you rephrase?"
        
        response_lower = response.lower().strip()
        user_lower = user_input.lower().strip()
        
        # Check for overly generic responses to specific questions
        if self._is_specific_question(user_input):
            if response_lower in self.generic_responses:
                return False, self._generate_better_response(user_input, context)
        
        # Check for yes/no question responses
        if self._is_yes_no_question(user_input):
            if not self._has_clear_yes_no(response):
                improved = self._add_clarity_to_yes_no(response)
                return True, improved
        
        # Check for appropriate topic alignment
        if not self._matches_topic(response, user_input, context):
            return False, None
        
        # Check for repetitive content
        if self._is_repetitive(response):
            improved = self._reduce_repetition(response)
            return True, improved
        
        return True, None
    
    def _is_specific_question(self, text: str) -> bool:
        """Check if user asked a specific question"""
        question_words = ['what is', 'how do', 'why does', 'when did', 'where is', 'who is']
        return any(text.lower().startswith(q) for q in question_words)
    
    def _is_yes_no_question(self, text: str) -> bool:
        """Check if it's a yes/no question"""
        yes_no_starters = ['is ', 'are ', 'was ', 'were ', 'will ', 'would ', 
                          'could ', 'should ', 'can ', 'do ', 'does ', 'did ']
        return any(text.lower().startswith(starter) for starter in yes_no_starters)
    
    def _has_clear_yes_no(self, response: str) -> bool:
        """Check if response has clear yes/no answer"""
        response_lower = response.lower()
        clear_answers = ['yes', 'no', 'maybe', "i'm not", "i don't", "i can't"]
        return any(response_lower.startswith(ans) for ans in clear_answers)
    
    def _add_clarity_to_yes_no(self, response: str) -> str:
        """Add clarity to yes/no response"""
        # If response doesn't start with yes/no, add context
        if not self._has_clear_yes_no(response):
            return f"I'm not certain, but {response.lower()}"
        return response
    
    def _matches_topic(self, response: str, user_input: str, context: Dict) -> bool:
        """Check if response is on-topic"""
        if not context or not context.get('topic'):
            return True
        
        topic = context.get('topic', '').lower()
        
        # Financial responses should mention financial terms
        if topic == 'finance':
            finance_terms = ['price', '$', 'stock', 'crypto', 'market', 'invest', 
                           'financial', 'data', 'fund', 'portfolio', 'analysis']
            has_finance_term = any(term in response.lower() for term in finance_terms)
            has_error = 'error' in response.lower()
            return has_finance_term or has_error
        
        return True
    
    def _is_repetitive(self, response: str) -> bool:
        """Check if response has repetitive content"""
        sentences = [s.strip().lower() for s in response.split('. ') if len(s.strip()) > 5]
        
        if len(sentences) < 2:
            return False
        
        unique_sentences = set(sentences)
        repetition_ratio = len(unique_sentences) / len(sentences)
        
        return repetition_ratio < 0.8
    
    def _reduce_repetition(self, response: str) -> str:
        """Remove repetitive sentences"""
        sentences = response.split('. ')
        seen = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence_clean = sentence.strip().lower()
            if sentence_clean and sentence_clean not in seen:
                seen.add(sentence_clean)
                unique_sentences.append(sentence.strip())
        
        return '. '.join(unique_sentences)
    
    def _generate_better_response(self, user_input: str, context: Dict) -> str:
        """Generate a better response for generic replies"""
        return f"Let me think about that. {user_input.strip('?')} is an interesting question."


class TopicTransitionManager:
    """Manage smooth transitions between conversation topics"""
    
    def __init__(self):
        self.transition_templates = {
            'finance_to_tech': [
                "Switching from finance to tech, ",
                "On the technology side, ",
                "Moving to technical matters, "
            ],
            'tech_to_finance': [
                "Back to financial topics, ",
                "Regarding investments, ",
                "On the financial front, "
            ],
            'casual_to_formal': [
                "To be more specific, ",
                "More formally, ",
                "In professional terms, "
            ],
            'formal_to_casual': [
                "Simply put, ",
                "In other words, ",
                "More casually, "
            ],
            'general': [
                "Moving on, ",
                "Regarding that, ",
                "On that topic, ",
                "About your question, ",
                ""  # Sometimes no transition needed
            ]
        }
    
    def add_transition(self, response: str, from_topic: str, to_topic: str) -> str:
        """Add appropriate transition phrase based on topic change"""
        if not from_topic or not to_topic or from_topic == to_topic:
            return response
        
        # Determine transition key
        transition_key = f"{from_topic}_to_{to_topic}"
        
        if transition_key not in self.transition_templates:
            transition_key = 'general'
        
        # Select transition (50% chance to avoid overuse)
        if random.random() < 0.5:
            transitions = self.transition_templates[transition_key]
            transition = random.choice(transitions)
            return transition + response
        
        return response


class ContextualFollowUpGenerator:
    """Generate intelligent contextual follow-up suggestions"""
    
    def __init__(self):
        self.followup_templates = {
            'finance': [
                "Would you like to see more detailed analysis?",
                "Should I check other financial metrics?",
                "Want to compare with other options?",
                "Need historical data as well?"
            ],
            'technology': [
                "Would you like to see implementation details?",
                "Should I explain the technical aspects?",
                "Want to see code examples?",
                "Need more technical depth?"
            ],
            'general': [
                "Would you like more details?",
                "Should I elaborate on any part?",
                "Want to explore related topics?",
                "Need additional clarification?"
            ],
            'code': [
                "Would you like me to add tests?",
                "Should I review the code quality?",
                "Want to see optimization suggestions?",
                "Need documentation added?"
            ]
        }
        
        self.suggestion_cooldown = 3  # Don't suggest too frequently
        self.suggestion_count = 0
    
    def generate_followup(self, context: Dict, topic: str) -> Optional[str]:
        """
        Generate contextual follow-up suggestion
        
        Args:
            context: Conversation context
            topic: Current topic
        
        Returns:
            Follow-up question string or None
        """
        # Cooldown check - don't suggest too often
        self.suggestion_count += 1
        if self.suggestion_count < self.suggestion_cooldown:
            return None
        
        # Reset counter
        self.suggestion_count = 0
        
        # Only suggest 20% of the time to avoid being pushy
        if random.random() > 0.2:
            return None
        
        # Get appropriate suggestions for topic
        suggestions = self.followup_templates.get(topic, self.followup_templates['general'])
        
        # Check context depth - fewer suggestions in deep conversations
        if context and len(context.get('topic_history', [])) > 5:
            return None
        
        return random.choice(suggestions)
    
    def should_suggest(self, response_length: int, conversation_depth: int) -> bool:
        """Determine if we should suggest a follow-up"""
        # Don't suggest if response is already long
        if response_length > 200:
            return False
        
        # Don't suggest in deep conversations
        if conversation_depth > 8:
            return False
        
        return random.random() < 0.15  # 15% chance


# Export all classes
__all__ = [
    'ToneAnalyzer',
    'ConversationalFlowEnhancer',
    'ResponseQualityValidator',
    'TopicTransitionManager',
    'ContextualFollowUpGenerator'
]

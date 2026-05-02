"""
Core Reasoning Framework - Autonomous Thinking System

Implements the fundamental reasoning principles that guide Nexus's autonomous behavior,
decision-making, and conversational intelligence.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import os
import datetime


class ReasoningDepth(Enum):
    """How deeply to reason about a query"""
    SHALLOW = "shallow"       # Quick, surface-level response
    MODERATE = "moderate"     # Standard reasoning
    DEEP = "deep"            # Complex multi-step analysis
    ADAPTIVE = "adaptive"     # Adjust based on context


class ResponseMode(Enum):
    """How to structure the response"""
    DIRECT = "direct"              # Answer directly without preamble
    REASONING_SHOWN = "reasoning"  # Show thinking process
    RECOMMENDATION = "recommendation"  # Provide actionable advice
    CHALLENGE = "challenge"        # Question assumptions respectfully
    EXPLORATORY = "exploratory"    # Open-ended discussion


@dataclass
class ConversationMemory:
    """Track conversation context for intelligent continuity"""
    topics_discussed: List[str] = field(default_factory=list)
    advice_given: Dict[str, List[str]] = field(default_factory=dict)  # topic -> advice list
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    user_expertise_level: str = "intermediate"  # beginner | intermediate | advanced
    conversation_tone: str = "professional"     # casual | professional | technical
    last_n_interactions: List[Dict] = field(default_factory=list)
    repeating_patterns: List[str] = field(default_factory=list)
    
    def add_interaction(self, user_input: str, ai_response: str, topic: str):
        """Record an interaction"""
        self.last_n_interactions.append({
            'user': user_input,
            'ai': ai_response,
            'topic': topic,
            'timestamp': datetime.datetime.now()
        })
        
        # Keep only last 20 interactions
        if len(self.last_n_interactions) > 20:
            self.last_n_interactions.pop(0)
        
        # Track topics
        if topic not in self.topics_discussed:
            self.topics_discussed.append(topic)
    
    def has_discussed_topic(self, topic: str, recently: bool = False) -> bool:
        """Check if topic was discussed"""
        if recently:
            recent_topics = [i.get('topic', '') for i in self.last_n_interactions[-5:]]
            return topic in recent_topics
        return topic in self.topics_discussed
    
    def get_advice_given_on(self, topic: str) -> List[str]:
        """Get previously given advice on a topic"""
        return self.advice_given.get(topic, [])
    
    def record_advice(self, topic: str, advice: str):
        """Record advice given to avoid repetition"""
        if topic not in self.advice_given:
            self.advice_given[topic] = []
        self.advice_given[topic].append(advice)
    
    def detect_repetition(self, new_response: str, threshold: int = 3) -> bool:
        """Detect if we're repeating ourselves"""
        recent_responses = [i.get('ai', '') for i in self.last_n_interactions[-5:]]
        similarity_count = sum(1 for r in recent_responses if self._similarity(r, new_response) > 0.7)
        return similarity_count >= threshold
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Simple similarity metric"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0


@dataclass
class ReasoningContext:
    """Context for making reasoning decisions"""
    user_query: str
    conversation_history: List[Dict]
    user_expertise: str
    topic: str
    complexity: str  # low | medium | high
    has_missing_info: bool
    requires_action: bool
    prior_advice_on_topic: List[str]


class CoreReasoningEngine:
    """
    Core reasoning framework that implements autonomous thinking principles.
    
    This engine sits above all other systems and guides:
    - How to approach problems
    - When to reason deeply vs. respond quickly
    - How to avoid repetition
    - When to challenge vs. agree
    - How to maintain conversational depth
    """
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.reasoning_principles = self._load_reasoning_principles()
        self.technical_knowledge = self._initialize_technical_knowledge()
        self.learning_log = []
        
    def _load_reasoning_principles(self) -> Dict[str, Dict]:
        """Load core reasoning principles"""
        return {
            'context_awareness': {
                'rules': [
                    'Always check conversation history before responding',
                    'Never repeat identical advice unless explicitly requested',
                    'Build on prior discussion rather than restarting',
                    'Adjust tone and complexity to match user expertise'
                ],
                'checks': ['has_discussed_recently', 'advice_already_given', 'tone_appropriate']
            },
            'logical_reasoning': {
                'approach': [
                    'Break complex problems into components',
                    'Evaluate multiple solutions',
                    'Choose most efficient realistic option',
                    'Explain reasoning when helpful, not excessively'
                ],
                'when_to_infer': [
                    'User intent is clear but details missing',
                    'Standard assumptions apply',
                    'Waiting for clarification would block progress'
                ]
            },
            'independent_thinking': {
                'guidelines': [
                    'Form opinions based on logic, data, experience',
                    'Separate facts from assumptions from opinions',
                    'Provide recommendations, not just information',
                    'Challenge flawed ideas respectfully when necessary'
                ],
                'opinion_triggers': [
                    'User asks for opinion/perspective',
                    'Multiple valid approaches exist',
                    'User assumption appears flawed'
                ]
            },
            'autonomous_execution': {
                'approach': [
                    'Determine steps internally without asking permission',
                    'Assume responsibility for task completion',
                    'Self-correct errors without restarting',
                    'Execute with minimal user guidance'
                ],
                'when_applicable': [
                    'Clear actionable task given',
                    'Required tools/capabilities available',
                    'No significant risks or irreversible actions'
                ]
            },
            'conversational_depth': {
                'guidelines': [
                    'Engage as thinking partner, not chatbot',
                    'Ask meaningful questions that add value',
                    'Avoid shallow or generic responses',
                    'Adjust complexity to user knowledge level'
                ],
                'avoid': [
                    'Generic pleasantries without purpose',
                    'Obvious questions user can answer',
                    'Repeating information already discussed'
                ]
            }
        }
    
    def _initialize_technical_knowledge(self) -> Dict[str, List[str]]:
        """Initialize awareness of technical capabilities"""
        return {
            'ml_frameworks': [
                'PyTorch', 'TensorFlow', 'Scikit-learn', 'Keras',
                'Hugging Face Transformers', 'spaCy', 'NLTK'
            ],
            'languages': [
                'Python', 'JavaScript', 'TypeScript', 'Java', 'Bash', 'SQL'
            ],
            'automation_tools': [
                'Selenium', 'Playwright', 'Puppeteer', 'BeautifulSoup', 'Scrapy'
            ],
            'agent_frameworks': [
                'LangChain', 'AutoGPT', 'BabyAGI', 'ReAct patterns'
            ],
            'apis_integrations': [
                'REST APIs', 'GraphQL', 'WebSockets', 'OAuth',
                'Social media APIs', 'Financial APIs', 'News APIs'
            ],
            'data_systems': [
                'Vector databases', 'SQL databases', 'NoSQL', 
                'Redis', 'Elasticsearch', 'ChromaDB', 'Pinecone'
            ]
        }
    
    def analyze_query(self, query: str, context: Dict = None) -> ReasoningContext:
        """Analyze query to determine reasoning approach"""
        
        # Extract topic
        topic = self._extract_topic(query)
        
        # Determine complexity
        complexity = self._assess_complexity(query, context)
        
        # Check for missing information
        has_missing_info = self._has_missing_information(query, context)
        
        # Determine if action required
        requires_action = self._requires_action(query)
        
        # Get prior advice on this topic
        prior_advice = self.memory.get_advice_given_on(topic)
        
        # Build reasoning context
        reasoning_ctx = ReasoningContext(
            user_query=query,
            conversation_history=self.memory.last_n_interactions,
            user_expertise=self.memory.user_expertise_level,
            topic=topic,
            complexity=complexity,
            has_missing_info=has_missing_info,
            requires_action=requires_action,
            prior_advice_on_topic=prior_advice
        )
        
        return reasoning_ctx
    
    def determine_reasoning_depth(self, ctx: ReasoningContext) -> ReasoningDepth:
        """Determine how deeply to reason"""
        
        # Deep reasoning for:
        if ctx.complexity == 'high':
            return ReasoningDepth.DEEP
        
        # Deep reasoning if user seems advanced
        if ctx.user_expertise == 'advanced' and ctx.complexity == 'medium':
            return ReasoningDepth.DEEP
        
        # Shallow for simple queries
        if ctx.complexity == 'low' and not ctx.requires_action:
            return ReasoningDepth.SHALLOW
        
        # Moderate for most cases
        return ReasoningDepth.MODERATE
    
    def determine_response_mode(self, ctx: ReasoningContext) -> ResponseMode:
        """Determine how to structure response"""
        
        # If user seems to have flawed assumption, challenge respectfully
        if self._detect_flawed_assumption(ctx.user_query):
            return ResponseMode.CHALLENGE
        
        # If action required, provide recommendation
        if ctx.requires_action:
            return ResponseMode.RECOMMENDATION
        
        # If complex reasoning needed, show thinking
        if ctx.complexity == 'high' and ctx.user_expertise == 'advanced':
            return ResponseMode.REASONING_SHOWN
        
        # If open-ended question, explore
        if '?' in ctx.user_query and not self._is_yes_no_question(ctx.user_query):
            return ResponseMode.EXPLORATORY
        
        # Default: direct answer
        return ResponseMode.DIRECT
    
    def should_infer_vs_ask(self, ctx: ReasoningContext) -> bool:
        """Decide whether to infer missing info or ask for it"""
        
        # Infer if:
        # 1. Intent is clear even with missing details
        # 2. Standard assumptions apply
        # 3. Asking would slow progress unnecessarily
        
        if ctx.has_missing_info:
            # If complexity is low, safe to infer
            if ctx.complexity == 'low':
                return True  # Infer
            
            # If user is experienced, they probably want action not questions
            if ctx.user_expertise == 'advanced':
                return True  # Infer
            
            # If this is a repeated topic, we likely have context
            if self.memory.has_discussed_topic(ctx.topic, recently=True):
                return True  # Infer from prior discussion
            
            # Otherwise ask
            return False
        
        return True  # No missing info, proceed
    
    def check_for_repetition(self, ctx: ReasoningContext, proposed_response: str) -> Tuple[bool, Optional[str]]:
        """Check if we're about to repeat ourselves"""
        
        # Check if this exact advice was given before on this topic
        if ctx.prior_advice_on_topic:
            for prior in ctx.prior_advice_on_topic:
                if self.memory._similarity(prior, proposed_response) > 0.8:
                    return True, "This is nearly identical to previous advice on this topic"
        
        # Check recent conversation for repetition
        if self.memory.detect_repetition(proposed_response):
            return True, "This response is too similar to recent messages"
        
        return False, None
    
    def generate_alternative_approach(self, ctx: ReasoningContext, reason: str) -> str:
        """Generate alternative approach when repetition detected"""
        
        suggestions = []
        
        if "financial" in ctx.topic or "monetization" in ctx.topic:
            # Vary financial advice
            suggestions = [
                "Let me suggest a different approach we haven't explored yet",
                "Building on our previous discussion, here's an alternative strategy",
                "Instead of repeating what we've covered, let's look at this from a new angle",
                "Here's a fresh perspective considering what we've already discussed"
            ]
        
        if "technical" in ctx.topic or "implementation" in ctx.topic:
            suggestions = [
                "Since we've covered the basics, let's dive into advanced techniques",
                "Here's a more sophisticated approach",
                "Let me show you an alternative implementation pattern"
            ]
        
        if suggestions:
            return suggestions[len(ctx.prior_advice_on_topic) % len(suggestions)]
        
        return "Let me approach this differently than before"
    
    def record_interaction(self, query: str, response: str, topic: str):
        """Record interaction for learning and continuity"""
        self.memory.add_interaction(query, response, topic)
        
        # If this was advice, record it
        if any(word in query.lower() for word in ['how', 'should', 'recommend', 'suggest', 'advice']):
            self.memory.record_advice(topic, response)
        
        # Log for learning
        self.learning_log.append({
            'query': query,
            'response_length': len(response),
            'topic': topic,
            'timestamp': datetime.datetime.now()
        })
    
    def adjust_user_model(self, expertise_indicators: Dict[str, Any]):
        """Adjust user expertise model based on interactions"""
        
        # Look for indicators of expertise
        if expertise_indicators.get('uses_technical_terms', False):
            if self.memory.user_expertise_level == 'beginner':
                self.memory.user_expertise_level = 'intermediate'
        
        if expertise_indicators.get('asks_advanced_questions', False):
            if self.memory.user_expertise_level == 'intermediate':
                self.memory.user_expertise_level = 'advanced'
        
        # Look for indicators of being overwhelmed
        if expertise_indicators.get('asks_for_simpler_explanation', False):
            if self.memory.user_expertise_level == 'advanced':
                self.memory.user_expertise_level = 'intermediate'
    
    def select_tool_or_library(self, task: str, context: Dict = None) -> Optional[Dict[str, str]]:
        """Intelligently select tool/library for a task"""
        
        task_lower = task.lower()
        
        # Browser automation
        if any(word in task_lower for word in ['navigate', 'browser', 'website', 'scrape', 'automate']):
            return {
                'tool': 'Playwright',
                'reason': 'Modern, reliable browser automation with good Python support',
                'alternative': 'Selenium (more established, wider browser support)'
            }
        
        # ML/NLP tasks
        if any(word in task_lower for word in ['classify', 'sentiment', 'nlp', 'language']):
            return {
                'tool': 'Hugging Face Transformers',
                'reason': 'State-of-the-art pre-trained models with simple API',
                'alternative': 'spaCy (faster for basic NLP)'
            }
        
        # Data analysis
        if any(word in task_lower for word in ['analyze', 'data', 'statistics', 'trends']):
            return {
                'tool': 'pandas + scikit-learn',
                'reason': 'Industry standard for data analysis and basic ML',
                'alternative': 'Polars (faster for large datasets)'
            }
        
        # API integration
        if any(word in task_lower for word in ['api', 'fetch', 'request', 'integrate']):
            return {
                'tool': 'requests + aiohttp',
                'reason': 'Simple for sync, efficient for async operations',
                'alternative': 'httpx (modern unified API)'
            }
        
        return None
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query"""
        query_lower = query.lower()
        
        # Financial topics
        if any(word in query_lower for word in ['stock', 'invest', 'money', 'finance', 'revenue', 'profit']):
            return 'financial'
        
        # Technical topics
        if any(word in query_lower for word in ['code', 'implement', 'develop', 'program', 'script']):
            return 'technical'
        
        # Personal/advice topics
        if any(word in query_lower for word in ['should i', 'how can i', 'what do you think']):
            return 'advice'
        
        # Learning topics
        if any(word in query_lower for word in ['learn', 'understand', 'explain', 'how does']):
            return 'educational'
        
        return 'general'
    
    def _assess_complexity(self, query: str, context: Dict = None) -> str:
        """Assess query complexity"""
        word_count = len(query.split())
        
        # Long queries tend to be complex
        if word_count > 30:
            return 'high'
        
        # Check for complexity indicators
        complex_indicators = ['optimize', 'scale', 'architecture', 'design', 'strategy', 'multiple']
        if any(ind in query.lower() for ind in complex_indicators):
            return 'high'
        
        # Simple queries
        simple_indicators = ['what is', 'who is', 'when', 'where']
        if any(ind in query.lower() for ind in simple_indicators):
            return 'low'
        
        return 'medium'
    
    def _has_missing_information(self, query: str, context: Dict = None) -> bool:
        """Detect if critical information is missing"""
        
        # Vague action requests
        if any(word in query.lower() for word in ['something', 'anything', 'some kind of']):
            return True
        
        # Missing specifics for technical tasks
        if 'implement' in query.lower() and not any(word in query.lower() for word in ['python', 'java', 'javascript']):
            return True
        
        return False
    
    def _requires_action(self, query: str) -> bool:
        """Determine if query requires action vs. information"""
        action_verbs = ['create', 'build', 'implement', 'develop', 'write', 'make', 'generate', 'automate', 'set up']
        return any(verb in query.lower() for verb in action_verbs)
    
    def _detect_flawed_assumption(self, query: str) -> bool:
        """Detect if query contains flawed assumption"""
        
        # Common flawed assumptions
        flawed_patterns = [
            'always better to',
            'never should',
            'everyone knows',
            'obviously the best',
            'guaranteed to'
        ]
        
        return any(pattern in query.lower() for pattern in flawed_patterns)
    
    def _is_yes_no_question(self, query: str) -> bool:
        """Check if question expects yes/no answer"""
        yes_no_starters = ['is ', 'are ', 'was ', 'were ', 'will ', 'would ', 'could ', 'should ', 'can ', 'do ', 'does ', 'did ']
        return any(query.lower().startswith(starter) for starter in yes_no_starters)
    
    def get_reasoning_summary(self) -> Dict[str, Any]:
        """Get summary of reasoning behavior"""
        return {
            'total_interactions': len(self.memory.last_n_interactions),
            'topics_discussed': len(self.memory.topics_discussed),
            'user_expertise': self.memory.user_expertise_level,
            'conversation_tone': self.memory.conversation_tone,
            'advice_given_count': sum(len(v) for v in self.memory.advice_given.values()),
            'recent_topics': [i.get('topic') for i in self.memory.last_n_interactions[-5:]]
        }

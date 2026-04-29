"""
Conversational Automation Engine - Natural command understanding and automated task execution
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re
from datetime import datetime


class TaskComplexity(Enum):
    """Complexity level of inferred task"""
    SIMPLE = "simple"           # Single-step action
    MODERATE = "moderate"       # 2-3 steps
    COMPLEX = "complex"         # Multi-step workflow
    COMPOUND = "compound"       # Multiple independent tasks


class IntentConfidence(Enum):
    """How confident we are about user intent"""
    CERTAIN = "certain"         # 90%+
    LIKELY = "likely"           # 70-90%
    POSSIBLE = "possible"       # 50-70%
    UNCLEAR = "unclear"         # <50%


@dataclass
class InferredTask:
    """A task inferred from conversational input"""
    task_type: str              # What to do (e.g., 'stock_lookup', 'code_generation')
    action_sequence: List[str]  # Ordered steps to execute
    parameters: Dict[str, Any]  # Extracted parameters
    confidence: IntentConfidence
    complexity: TaskComplexity
    requires_confirmation: bool
    proactive_suggestions: List[str] = field(default_factory=list)
    missing_info: List[str] = field(default_factory=list)


@dataclass
class ConversationState:
    """Current state of ongoing conversation"""
    active_topic: Optional[str] = None
    pending_tasks: List[InferredTask] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    user_goals: List[str] = field(default_factory=list)
    conversation_flow: List[Dict[str, Any]] = field(default_factory=list)
    last_ai_action: Optional[str] = None
    awaiting_user_input: bool = False
    proactive_mode: bool = True  # AI can suggest actions


class ConversationalAutomationEngine:
    """
    Engine for understanding natural commands and executing tasks automatically.
    Handles conversational fluidity and contextual task execution.
    """
    
    def __init__(self):
        self.conversation_state = ConversationState()
        self.command_patterns = self._load_command_patterns()
        self.task_templates = self._load_task_templates()
        self.conversation_history = []
        
    def _load_command_patterns(self) -> Dict[str, List[str]]:
        """Load natural language patterns for common tasks"""
        return {
            # Information retrieval patterns
            'lookup_info': [
                r"(?:what(?:'s| is)|tell me(?: about)?|find|look up|show me|get(?:ting)?)\s+(?:the\s+)?(.+)",
                r"(?:i want to|i'd like to|can you|could you)\s+(?:know|learn|find out)\s+(?:about\s+)?(.+)",
                r"(?:information|details|data)\s+(?:on|about|for)\s+(.+)"
            ],
            
            # Task execution patterns
            'execute_task': [
                r"(?:can you|could you|please|would you)\s+(.+?)(?:\?|$)",
                r"(?:i need you to|i want you to|you should)\s+(.+)",
                r"(?:go ahead and|just|simply)\s+(.+)"
            ],
            
            # Creation/generation patterns
            'create_something': [
                r"(?:create|make|build|generate|write|produce)\s+(?:a|an|some)?\s*(.+)",
                r"(?:i need|i want|give me)\s+(?:a|an|some)?\s*(.+)"
            ],
            
            # Analysis patterns
            'analyze': [
                r"(?:analyze|examine|evaluate|assess|review|check)\s+(.+)",
                r"(?:what do you think about|your thoughts on|opinion on)\s+(.+)",
                r"(?:should i|is it (?:good|bad|wise) to)\s+(.+)"
            ],
            
            # Comparison patterns
            'compare': [
                r"(?:compare|contrast|difference between)\s+(.+?)\s+(?:and|vs|versus)\s+(.+)",
                r"(?:which is better|what's better)\s+(.+?)\s+(?:or|vs)\s+(.+)",
                r"(.+?)\s+(?:vs|versus|or)\s+(.+?)(?:\?|$)"
            ],
            
            # Multi-task patterns (compound commands)
            'compound': [
                r"(.+?)\s+(?:and then|then|after that|also|plus)\s+(.+)",
                r"(.+?),\s+(.+?),\s+(?:and\s+)?(.+)",  # List of tasks
            ]
        }
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Templates for common task types with automation steps"""
        return {
            'stock_analysis': {
                'steps': ['fetch_stock_data', 'analyze_fundamentals', 'provide_insights'],
                'requires': ['stock_symbol'],
                'optional': ['timeframe', 'comparison_stocks'],
                'proactive_suggestions': [
                    'Would you like to see related news?',
                    'Should I compare with similar stocks?',
                    'Want me to analyze the sector trend?'
                ]
            },
            
            'code_creation': {
                'steps': ['understand_requirements', 'generate_code', 'explain_implementation'],
                'requires': ['language', 'task_description'],
                'optional': ['framework', 'test_cases'],
                'proactive_suggestions': [
                    'Should I create tests for this?',
                    'Would you like documentation?',
                    'Want me to run the code?'
                ]
            },
            
            'research_query': {
                'steps': ['identify_topic', 'search_sources', 'synthesize_findings', 'present_summary'],
                'requires': ['topic'],
                'optional': ['depth', 'sources'],
                'proactive_suggestions': [
                    'Should I dive deeper into any aspect?',
                    'Want related topics explored?',
                    'Need me to verify this information?'
                ]
            },
            
            'problem_solving': {
                'steps': ['understand_problem', 'break_down_components', 'generate_solutions', 'recommend_approach'],
                'requires': ['problem_description'],
                'optional': ['constraints', 'goals'],
                'proactive_suggestions': [
                    'Should I walk through the solution step-by-step?',
                    'Want alternative approaches?',
                    'Need help implementing this?'
                ]
            }
        }
    
    def understand_natural_command(self, user_input: str, context: Dict[str, Any]) -> InferredTask:
        """
        Parse natural language input and infer the task to execute.
        Uses conversational context to fill in missing details.
        """
        # Check for compound commands first
        if self._is_compound_command(user_input):
            return self._handle_compound_command(user_input, context)
        
        # Match against command patterns
        task_type = self._classify_command_type(user_input)
        
        # Extract parameters from input and context
        parameters = self._extract_parameters(user_input, task_type, context)
        
        # Determine complexity
        complexity = self._assess_complexity(task_type, parameters)
        
        # Calculate confidence
        confidence = self._calculate_intent_confidence(user_input, task_type, parameters, context)
        
        # Generate action sequence
        action_sequence = self._generate_action_sequence(task_type, parameters)
        
        # Check if confirmation needed
        requires_confirmation = self._needs_confirmation(complexity, confidence, parameters)
        
        # Generate proactive suggestions
        proactive_suggestions = self._generate_suggestions(task_type, parameters, context)
        
        # Identify missing information
        missing_info = self._identify_missing_info(task_type, parameters)
        
        return InferredTask(
            task_type=task_type,
            action_sequence=action_sequence,
            parameters=parameters,
            confidence=confidence,
            complexity=complexity,
            requires_confirmation=requires_confirmation,
            proactive_suggestions=proactive_suggestions,
            missing_info=missing_info
        )
    
    def _is_compound_command(self, text: str) -> bool:
        """Check if user is requesting multiple tasks"""
        compound_indicators = ['and then', 'then', 'after that', 'also', 'plus', ' and ']
        # Check for comma-separated list
        if text.count(',') >= 2:
            return True
        return any(indicator in text.lower() for indicator in compound_indicators)
    
    def _handle_compound_command(self, text: str, context: Dict[str, Any]) -> InferredTask:
        """Handle commands that involve multiple tasks"""
        # Split into subtasks
        subtasks = self._split_compound_command(text)
        
        # Create action sequence from all subtasks
        all_actions = []
        all_params = {}
        
        for idx, subtask in enumerate(subtasks):
            task_type = self._classify_command_type(subtask)
            params = self._extract_parameters(subtask, task_type, context)
            actions = self._generate_action_sequence(task_type, params)
            
            all_actions.extend(actions)
            all_params[f'subtask_{idx}'] = {'type': task_type, 'params': params}
        
        return InferredTask(
            task_type='compound_task',
            action_sequence=all_actions,
            parameters=all_params,
            confidence=IntentConfidence.LIKELY,
            complexity=TaskComplexity.COMPOUND,
            requires_confirmation=True,
            proactive_suggestions=[f"I'll execute all {len(subtasks)} tasks in sequence"]
        )
    
    def _split_compound_command(self, text: str) -> List[str]:
        """Split compound command into individual tasks"""
        # Try splitting on common separators
        if text.count(',') >= 2:
            parts = [p.strip() for p in text.split(',')]
            # Handle "and" in last part
            if parts and ' and ' in parts[-1]:
                last_parts = parts[-1].split(' and ')
                parts = parts[:-1] + [p.strip() for p in last_parts]
            return [p for p in parts if p]
        
        # Try splitting on "and then", "then", etc.
        for separator in [' and then ', ' then ', ' after that ', ' also ']:
            if separator in text.lower():
                return [p.strip() for p in re.split(separator, text, flags=re.IGNORECASE) if p.strip()]
        
        # Try splitting on " and "
        if ' and ' in text.lower():
            parts = re.split(r'\s+and\s+', text, flags=re.IGNORECASE)
            return [p.strip() for p in parts if p.strip()]
        
        return [text]  # Single task
    
    def _classify_command_type(self, text: str) -> str:
        """Classify the type of command from natural language"""
        text_lower = text.lower()
        
        # Check against patterns
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Further classify based on keywords
                    if cmd_type == 'lookup_info':
                        if any(word in text_lower for word in ['stock', 'price', 'ticker']):
                            return 'stock_lookup'
                        elif any(word in text_lower for word in ['weather', 'temperature', 'forecast']):
                            return 'weather_query'
                        elif any(word in text_lower for word in ['crypto', 'bitcoin', 'ethereum']):
                            return 'crypto_lookup'
                        else:
                            return 'research_query'
                    
                    elif cmd_type == 'create_something':
                        if any(word in text_lower for word in ['code', 'function', 'script', 'program']):
                            return 'code_creation'
                        elif any(word in text_lower for word in ['video', 'content', 'post']):
                            return 'content_creation'
                        else:
                            return 'general_creation'
                    
                    elif cmd_type == 'analyze':
                        if any(word in text_lower for word in ['stock', 'investment', 'portfolio']):
                            return 'stock_analysis'
                        else:
                            return 'general_analysis'
                    
                    return cmd_type
        
        # Default classification based on keywords
        if any(word in text_lower for word in ['stock', 'share', 'ticker', 'equity']):
            return 'stock_lookup'
        elif any(word in text_lower for word in ['code', 'program', 'script', 'function']):
            return 'code_creation'
        elif any(word in text_lower for word in ['why', 'how', 'explain', 'what is']):
            return 'research_query'
        
        return 'general_query'
    
    def _extract_parameters(self, text: str, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from text and context"""
        params = {}
        text_lower = text.lower()
        
        # Get template for this task type
        template = self.task_templates.get(task_type, {})
        
        # Extract based on task type
        if 'stock' in task_type:
            # Extract stock symbols (2-5 uppercase letters)
            symbols = re.findall(r'\b[A-Z]{2,5}\b', text.upper())
            if symbols:
                params['stock_symbol'] = symbols[0]
            else:
                # Try to get from context
                if context.get('last_stock_symbol'):
                    params['stock_symbol'] = context['last_stock_symbol']
        
        if 'code' in task_type:
            # Extract language
            languages = ['python', 'javascript', 'typescript', 'java', 'c++', 'rust', 'go']
            for lang in languages:
                if lang in text_lower:
                    params['language'] = lang
                    break
            
            # Extract task description (everything after "create" or "write")
            for trigger in ['create', 'write', 'make', 'generate']:
                if trigger in text_lower:
                    idx = text_lower.index(trigger) + len(trigger)
                    params['task_description'] = text[idx:].strip()
                    break
        
        if 'research' in task_type or 'query' in task_type:
            # Extract main topic
            for phrase in ['tell me about', 'what is', 'explain', 'find out about']:
                if phrase in text_lower:
                    idx = text_lower.index(phrase) + len(phrase)
                    params['topic'] = text[idx:].strip()
                    break
        
        # Use context to fill missing required parameters
        if template:
            for required in template.get('requires', []):
                if required not in params:
                    # Try to infer from context
                    context_key = f'last_{required}'
                    if context.get(context_key):
                        params[required] = context[context_key]
        
        return params
    
    def _assess_complexity(self, task_type: str, parameters: Dict[str, Any]) -> TaskComplexity:
        """Determine task complexity"""
        if task_type == 'compound_task':
            return TaskComplexity.COMPOUND
        
        template = self.task_templates.get(task_type, {})
        steps = template.get('steps', [])
        
        if len(steps) <= 1:
            return TaskComplexity.SIMPLE
        elif len(steps) <= 3:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.COMPLEX
    
    def _calculate_intent_confidence(self, text: str, task_type: str, 
                                     parameters: Dict[str, Any], context: Dict[str, Any]) -> IntentConfidence:
        """Calculate how confident we are about user's intent"""
        confidence_score = 0.5  # Start at 50%
        
        # Boost confidence for explicit commands
        explicit_indicators = ['please', 'can you', 'would you', 'i want you to', 'i need']
        if any(ind in text.lower() for ind in explicit_indicators):
            confidence_score += 0.2
        
        # Check if we have required parameters
        template = self.task_templates.get(task_type, {})
        required_params = template.get('requires', [])
        
        if required_params:
            found_params = sum(1 for p in required_params if p in parameters)
            param_ratio = found_params / len(required_params)
            confidence_score += param_ratio * 0.3
        
        # Boost if context supports this task
        if context.get('current_topic') == task_type.split('_')[0]:
            confidence_score += 0.1
        
        # Convert to confidence level
        if confidence_score >= 0.9:
            return IntentConfidence.CERTAIN
        elif confidence_score >= 0.7:
            return IntentConfidence.LIKELY
        elif confidence_score >= 0.5:
            return IntentConfidence.POSSIBLE
        else:
            return IntentConfidence.UNCLEAR
    
    def _generate_action_sequence(self, task_type: str, parameters: Dict[str, Any]) -> List[str]:
        """Generate ordered sequence of actions to execute"""
        template = self.task_templates.get(task_type, {})
        
        if template:
            return template.get('steps', [f'execute_{task_type}'])
        
        # Default action sequence
        return [f'execute_{task_type}']
    
    def _needs_confirmation(self, complexity: TaskComplexity, confidence: IntentConfidence, 
                           parameters: Dict[str, Any]) -> bool:
        """Determine if user confirmation is needed before executing"""
        # Always confirm for compound tasks
        if complexity == TaskComplexity.COMPOUND:
            return True
        
        # Confirm if intent is unclear
        if confidence == IntentConfidence.UNCLEAR:
            return True
        
        # Confirm for complex tasks with low confidence
        if complexity == TaskComplexity.COMPLEX and confidence != IntentConfidence.CERTAIN:
            return True
        
        # Confirm if critical parameters are missing
        if not parameters or len(parameters) == 0:
            return True
        
        return False
    
    def _generate_suggestions(self, task_type: str, parameters: Dict[str, Any], 
                             context: Dict[str, Any]) -> List[str]:
        """Generate proactive suggestions for next steps"""
        template = self.task_templates.get(task_type, {})
        
        if template:
            return template.get('proactive_suggestions', [])
        
        return []
    
    def _identify_missing_info(self, task_type: str, parameters: Dict[str, Any]) -> List[str]:
        """Identify what information is missing to complete the task"""
        template = self.task_templates.get(task_type, {})
        
        if not template:
            return []
        
        required = template.get('requires', [])
        missing = [param for param in required if param not in parameters]
        
        return missing
    
    def format_natural_response(self, task: InferredTask, execution_result: Any) -> str:
        """Format AI response in natural, conversational style"""
        responses = []
        
        # Acknowledge understanding
        if task.confidence == IntentConfidence.CERTAIN:
            responses.append(random.choice([
                "Got it!", "Sure thing!", "On it!", "Understood!", "Right away!"
            ]))
        elif task.confidence == IntentConfidence.LIKELY:
            responses.append(random.choice([
                "I think I understand.", "Let me help with that.", "I'll take care of that."
            ]))
        else:
            responses.append("Let me see if I understand correctly.")
        
        # Add main result
        if isinstance(execution_result, str):
            responses.append(execution_result)
        
        # Add proactive suggestions
        if task.proactive_suggestions and self.conversation_state.proactive_mode:
            suggestion = random.choice(task.proactive_suggestions)
            responses.append(f"\n{suggestion}")
        
        return " ".join(responses)
    
    def update_conversation_state(self, user_input: str, task: InferredTask, result: Any):
        """Update conversation state after task execution"""
        # Record conversation turn
        self.conversation_state.conversation_flow.append({
            'timestamp': datetime.now(),
            'user_input': user_input,
            'inferred_task': task.task_type,
            'confidence': task.confidence.value,
            'completed': True
        })
        
        # Update active topic
        self.conversation_state.active_topic = task.task_type.split('_')[0]
        
        # Record completed task
        self.conversation_state.completed_tasks.append(task.task_type)
        
        # Store last action
        self.conversation_state.last_ai_action = task.task_type


# Global instance
conversational_automation = ConversationalAutomationEngine()


# Utility function for other modules
def parse_natural_command(user_input: str, context: Dict[str, Any]) -> InferredTask:
    """Parse natural language command and return inferred task"""
    return conversational_automation.understand_natural_command(user_input, context)


# Import for random responses
import random

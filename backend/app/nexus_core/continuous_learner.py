"""
Continuous Learning Engine

Learns from user interactions, experiences, and new data without manual intervention.
Implements pattern recognition, skill acquisition tracking, and adaptive learning.
"""
from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import re


@dataclass
class LearningPattern:
    """Detected pattern in interactions"""
    pattern_id: str
    pattern_type: str  # 'user_preference', 'common_query', 'error_pattern', 'success_pattern'
    description: str
    occurrences: int = 1
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    confidence: float = 0.5
    examples: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    outcomes: Dict[str, int] = field(default_factory=dict)  # outcome -> count
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LearningPattern:
        return cls(**data)
    
    def update_occurrence(self, example: str, outcome: str = 'success'):
        """Record a new occurrence of this pattern"""
        self.occurrences += 1
        self.last_seen = time.time()
        
        if example not in self.examples:
            self.examples.append(example)
            if len(self.examples) > 10:
                self.examples = self.examples[-10:]  # Keep last 10
        
        # Update confidence based on occurrences
        self.confidence = min(1.0, 0.5 + (self.occurrences / 20))
        
        # Track outcomes
        self.outcomes[outcome] = self.outcomes.get(outcome, 0) + 1


@dataclass
class AcquiredSkill:
    """Skill learned by the AI"""
    skill_id: str
    skill_name: str
    skill_category: str  # 'technical', 'communication', 'problem_solving', 'domain_knowledge'
    description: str
    proficiency_level: float = 0.0  # 0.0 to 1.0
    learning_started: float = field(default_factory=time.time)
    last_practiced: float = field(default_factory=time.time)
    practice_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    knowledge_items: List[str] = field(default_factory=list)  # Related knowledge
    dependencies: List[str] = field(default_factory=list)  # Other skills needed
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AcquiredSkill:
        return cls(**data)
    
    def practice(self, success: bool = True):
        """Record practice of this skill"""
        self.practice_count += 1
        self.last_practiced = time.time()
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # Update proficiency based on success rate
        total_attempts = self.success_count + self.failure_count
        if total_attempts > 0:
            success_rate = self.success_count / total_attempts
            # Proficiency increases with practice and success
            self.proficiency_level = min(1.0, 
                0.3 * (self.practice_count / 50) +  # Practice component
                0.7 * success_rate  # Success component
            )
    
    def get_proficiency_label(self) -> str:
        """Get human-readable proficiency level"""
        if self.proficiency_level < 0.2:
            return "Novice"
        elif self.proficiency_level < 0.4:
            return "Beginner"
        elif self.proficiency_level < 0.6:
            return "Intermediate"
        elif self.proficiency_level < 0.8:
            return "Advanced"
        else:
            return "Expert"


@dataclass
class KnowledgeGraph:
    """Graph of interconnected knowledge"""
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # concept -> metadata
    edges: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))  # concept -> related concepts
    
    def add_concept(self, concept: str, metadata: Dict[str, Any] = None):
        """Add a concept to the knowledge graph"""
        if concept not in self.nodes:
            self.nodes[concept] = metadata or {}
            self.edges[concept] = set()
    
    def connect(self, concept1: str, concept2: str):
        """Create bidirectional connection between concepts"""
        self.add_concept(concept1)
        self.add_concept(concept2)
        self.edges[concept1].add(concept2)
        self.edges[concept2].add(concept1)
    
    def get_related(self, concept: str, depth: int = 1) -> Set[str]:
        """Get related concepts up to specified depth"""
        if concept not in self.edges:
            return set()
        
        related = set(self.edges[concept])
        
        if depth > 1:
            for related_concept in list(related):
                related.update(self.get_related(related_concept, depth - 1))
        
        related.discard(concept)  # Don't include self
        return related
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence"""
        return {
            'nodes': self.nodes,
            'edges': {k: list(v) for k, v in self.edges.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KnowledgeGraph:
        """Load from dictionary"""
        kg = cls()
        kg.nodes = data.get('nodes', {})
        kg.edges = defaultdict(set, {k: set(v) for k, v in data.get('edges', {}).items()})
        return kg


class ContinuousLearner:
    """
    Continuous learning engine that learns from every interaction
    
    Capabilities:
    - Pattern recognition (user preferences, common queries, error patterns)
    - Skill acquisition tracking (proficiency growth over time)
    - Knowledge graph construction (interconnected concepts)
    - Adaptive learning (adjusts based on success/failure)
    - Self-improvement recommendations
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        # Learning data structures
        self.patterns: Dict[str, LearningPattern] = {}
        self.skills: Dict[str, AcquiredSkill] = {}
        self.knowledge_graph = KnowledgeGraph()
        
        # Learning statistics
        self.stats = {
            'total_interactions': 0,
            'patterns_detected': 0,
            'skills_acquired': 0,
            'knowledge_items': 0,
            'learning_sessions': 0,
            'last_learning_session': time.time()
        }
        
        # Storage configuration
        if storage_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "learning"))
            os.makedirs(base_dir, exist_ok=True)
            storage_path = os.path.join(base_dir, "continuous_learning.json")
        
        self.storage_path = storage_path
        
        # Load existing learning data
        self.load()
        
        # Initialize default skills if starting fresh
        if not self.skills:
            self._initialize_default_skills()
    
    def _initialize_default_skills(self):
        """Initialize baseline skills"""
        default_skills = [
            ('conversation', 'Natural Conversation', 'communication', 'Engaging in natural dialogue'),
            ('question_answering', 'Question Answering', 'communication', 'Answering user questions accurately'),
            ('code_generation', 'Code Generation', 'technical', 'Writing code in various languages'),
            ('research', 'Information Research', 'problem_solving', 'Finding and synthesizing information'),
            ('financial_analysis', 'Financial Analysis', 'domain_knowledge', 'Analyzing financial data'),
            ('content_creation', 'Content Creation', 'technical', 'Creating multimedia content'),
            ('project_planning', 'Project Planning', 'problem_solving', 'Planning complex projects'),
            ('pattern_recognition', 'Pattern Recognition', 'problem_solving', 'Identifying patterns in data'),
            ('learning', 'Self-Learning', 'problem_solving', 'Acquiring new knowledge autonomously'),
            ('memory_management', 'Memory Management', 'technical', 'Storing and retrieving information effectively')
        ]
        
        for skill_id, name, category, description in default_skills:
            self.skills[skill_id] = AcquiredSkill(
                skill_id=skill_id,
                skill_name=name,
                skill_category=category,
                description=description,
                proficiency_level=0.5  # Start at intermediate
            )
    
    def learn_from_interaction(self, user_input: str, ai_response: str, 
                              intent: str, success: bool = True,
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Learn from a single interaction
        
        Args:
            user_input: What the user said/typed
            ai_response: AI's response
            intent: Detected intent
            success: Whether the interaction was successful
            context: Additional context
        
        Returns:
            Dictionary of learning insights
        """
        if context is None:
            context = {}
        
        self.stats['total_interactions'] += 1
        learning_insights = {
            'patterns_detected': [],
            'skills_practiced': [],
            'knowledge_added': []
        }
        
        # 1. Detect patterns
        patterns = self._detect_patterns(user_input, ai_response, intent, success, context)
        for pattern in patterns:
            if pattern.pattern_id in self.patterns:
                self.patterns[pattern.pattern_id].update_occurrence(user_input, 'success' if success else 'failure')
            else:
                self.patterns[pattern.pattern_id] = pattern
                self.stats['patterns_detected'] += 1
            learning_insights['patterns_detected'].append(pattern.pattern_id)
        
        # 2. Practice relevant skills
        skills_used = self._identify_skills_used(intent, user_input, ai_response)
        for skill_id in skills_used:
            if skill_id in self.skills:
                self.skills[skill_id].practice(success)
                learning_insights['skills_practiced'].append(skill_id)
        
        # 3. Extract and store knowledge
        knowledge = self._extract_knowledge(user_input, ai_response, intent, context)
        for concept, metadata in knowledge.items():
            self.knowledge_graph.add_concept(concept, metadata)
            learning_insights['knowledge_added'].append(concept)
            self.stats['knowledge_items'] += 1
        
        # 4. Build knowledge connections
        if len(knowledge) > 1:
            concepts = list(knowledge.keys())
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    self.knowledge_graph.connect(concept1, concept2)
        
        # Auto-save periodically
        if self.stats['total_interactions'] % 5 == 0:
            self.save()
        
        return learning_insights
    
    def _detect_patterns(self, user_input: str, ai_response: str, 
                        intent: str, success: bool, context: Dict[str, Any]) -> List[LearningPattern]:
        """Detect patterns in interaction"""
        patterns = []
        
        # Pattern 1: User preference patterns
        if intent in ['stock_info', 'crypto_info'] and success:
            pattern_id = f"preference_{intent}"
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type='user_preference',
                description=f"User frequently asks about {intent}",
                examples=[user_input],
                triggers=[intent]
            )
            patterns.append(pattern)
        
        # Pattern 2: Common query patterns
        query_words = re.findall(r'\b\w+\b', user_input.lower())
        if len(query_words) > 2:
            # Check for repeated word combinations
            for i in range(len(query_words) - 1):
                bigram = f"{query_words[i]}_{query_words[i+1]}"
                pattern_id = f"query_pattern_{bigram}"
                pattern = LearningPattern(
                    pattern_id=pattern_id,
                    pattern_type='common_query',
                    description=f"User commonly uses phrase '{query_words[i]} {query_words[i+1]}'",
                    examples=[user_input],
                    triggers=[bigram]
                )
                patterns.append(pattern)
        
        # Pattern 3: Error patterns (if not successful)
        if not success:
            pattern_id = f"error_{intent}"
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type='error_pattern',
                description=f"Difficulty handling {intent} queries",
                examples=[user_input],
                triggers=[intent, 'error']
            )
            patterns.append(pattern)
        
        # Pattern 4: Success patterns (if successful and complex)
        if success and len(user_input.split()) > 5:
            pattern_id = f"success_{intent}"
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type='success_pattern',
                description=f"Successfully handling {intent} queries",
                examples=[user_input],
                triggers=[intent, 'success']
            )
            patterns.append(pattern)
        
        return patterns
    
    def _identify_skills_used(self, intent: str, user_input: str, ai_response: str) -> List[str]:
        """Identify which skills were used in this interaction"""
        skills_used = []
        
        # Map intents to skills
        intent_skill_map = {
            'greet': ['conversation'],
            'ask_wellbeing': ['conversation'],
            'general_query': ['question_answering', 'research'],
            'calculate': ['question_answering'],
            'code_generation': ['code_generation'],
            'code_generation_enhanced': ['code_generation'],
            'stock_info': ['financial_analysis', 'research'],
            'crypto_info': ['financial_analysis', 'research'],
            'investment_advice': ['financial_analysis', 'question_answering'],
            'financial_planning': ['financial_analysis', 'project_planning'],
            'content_research': ['research', 'content_creation'],
            'project_planning': ['project_planning', 'content_creation'],
            'asset_generation': ['content_creation'],
            'project_execution': ['project_planning', 'content_creation'],
            'advanced_reasoning': ['problem_solving', 'pattern_recognition'],
            'opinion_request': ['problem_solving', 'question_answering'],
            'test_reasoning': ['pattern_recognition', 'learning'],
            'show_reasoning': ['pattern_recognition'],
            'self_assessment': ['learning', 'pattern_recognition'],
            'problem_solving': ['problem_solving', 'pattern_recognition'],
            'task_optimization': ['problem_solving', 'pattern_recognition']
        }
        
        skills_used.extend(intent_skill_map.get(intent, []))
        
        # Always use conversation skill
        if 'conversation' not in skills_used:
            skills_used.append('conversation')
        
        # If AI retrieved from memory, use memory_management skill
        if 'memory' in ai_response.lower() or 'remember' in ai_response.lower():
            skills_used.append('memory_management')
        
        return skills_used
    
    def _extract_knowledge(self, user_input: str, ai_response: str, 
                          intent: str, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract knowledge items from interaction"""
        knowledge = {}
        
        # Extract entities from context
        entities = context.get('entities', [])
        for entity in entities:
            concept = entity.get('text', '').lower()
            if concept and len(concept) > 2:
                knowledge[concept] = {
                    'type': entity.get('label', 'UNKNOWN'),
                    'first_seen': time.time(),
                    'source': 'user_interaction',
                    'context': intent
                }
        
        # Extract key terms from user input (capitalized words, technical terms)
        words = user_input.split()
        for word in words:
            if word[0].isupper() and len(word) > 3 and word.isalpha():
                concept = word.lower()
                if concept not in knowledge:
                    knowledge[concept] = {
                        'type': 'TERM',
                        'first_seen': time.time(),
                        'source': 'user_interaction',
                        'context': intent
                    }
        
        return knowledge
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about what has been learned"""
        # Top patterns
        top_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.occurrences * p.confidence,
            reverse=True
        )[:5]
        
        # Skill proficiencies
        skill_levels = {
            skill_id: {
                'name': skill.skill_name,
                'category': skill.skill_category,
                'proficiency': skill.proficiency_level,
                'proficiency_label': skill.get_proficiency_label(),
                'practice_count': skill.practice_count,
                'success_rate': skill.success_count / max(1, skill.success_count + skill.failure_count)
            }
            for skill_id, skill in self.skills.items()
        }
        
        # Learning velocity (how fast AI is learning)
        recent_patterns = [p for p in self.patterns.values() if time.time() - p.last_seen < 86400]  # Last 24h
        learning_velocity = len(recent_patterns) / max(1, self.stats['total_interactions'] / 100)
        
        return {
            'total_interactions': self.stats['total_interactions'],
            'patterns_detected': len(self.patterns),
            'active_patterns': len(recent_patterns),
            'skills_acquired': len(self.skills),
            'knowledge_concepts': len(self.knowledge_graph.nodes),
            'knowledge_connections': sum(len(edges) for edges in self.knowledge_graph.edges.values()) // 2,
            'learning_velocity': learning_velocity,
            'top_patterns': [
                {
                    'id': p.pattern_id,
                    'type': p.pattern_type,
                    'description': p.description,
                    'occurrences': p.occurrences,
                    'confidence': p.confidence
                }
                for p in top_patterns
            ],
            'skill_proficiencies': skill_levels
        }
    
    def get_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for self-improvement"""
        recommendations = []
        
        # 1. Skills that need practice
        for skill_id, skill in self.skills.items():
            if skill.proficiency_level < 0.7 and skill.practice_count < 50:
                recommendations.append({
                    'type': 'skill_practice',
                    'skill': skill.skill_name,
                    'current_proficiency': skill.get_proficiency_label(),
                    'recommendation': f"Practice {skill.skill_name} more to improve proficiency",
                    'priority': 1.0 - skill.proficiency_level
                })
        
        # 2. Error patterns that need attention
        error_patterns = [p for p in self.patterns.values() if p.pattern_type == 'error_pattern']
        for pattern in error_patterns:
            if pattern.occurrences > 2:
                recommendations.append({
                    'type': 'error_reduction',
                    'pattern': pattern.description,
                    'occurrences': pattern.occurrences,
                    'recommendation': f"Focus on reducing errors in: {pattern.description}",
                    'priority': pattern.occurrences / 10
                })
        
        # 3. Knowledge gaps (concepts with few connections)
        isolated_concepts = [
            concept for concept, edges in self.knowledge_graph.edges.items()
            if len(edges) < 2
        ]
        if isolated_concepts:
            recommendations.append({
                'type': 'knowledge_expansion',
                'concepts': isolated_concepts[:5],
                'recommendation': "Research these concepts to build deeper understanding",
                'priority': 0.6
            })
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.get('priority', 0), reverse=True)
        
        return recommendations
    
    def learn_from_experience(self, experience_type: str, details: Dict[str, Any]) -> Dict[str, str]:
        """
        Learn from a specific experience
        
        Args:
            experience_type: Type of experience ('success', 'failure', 'discovery', 'feedback')
            details: Details about the experience
        
        Returns:
            Learning summary
        """
        summary = {'learned': []}
        
        if experience_type == 'success':
            # Reinforce successful patterns
            task = details.get('task', 'unknown')
            if task in self.skills:
                self.skills[task].practice(success=True)
                summary['learned'].append(f"Reinforced success in {task}")
        
        elif experience_type == 'failure':
            # Learn from failures
            task = details.get('task', 'unknown')
            reason = details.get('reason', 'unknown')
            
            # Create error pattern
            pattern = LearningPattern(
                pattern_id=f"failure_{task}_{int(time.time())}",
                pattern_type='error_pattern',
                description=f"Failed at {task}: {reason}",
                examples=[str(details)]
            )
            self.patterns[pattern.pattern_id] = pattern
            
            if task in self.skills:
                self.skills[task].practice(success=False)
            
            summary['learned'].append(f"Documented failure in {task} to avoid repeating")
        
        elif experience_type == 'discovery':
            # Add new knowledge
            concept = details.get('concept', '')
            information = details.get('information', '')
            
            if concept:
                self.knowledge_graph.add_concept(concept, {
                    'information': information,
                    'discovered': time.time(),
                    'source': 'self_discovery'
                })
                summary['learned'].append(f"Discovered new concept: {concept}")
        
        elif experience_type == 'feedback':
            # Adjust based on feedback
            feedback = details.get('feedback', '')
            rating = details.get('rating', 0)  # 1-5
            
            if rating >= 4:
                # Positive feedback - reinforce
                task = details.get('task', 'conversation')
                if task in self.skills:
                    self.skills[task].practice(success=True)
                summary['learned'].append("Reinforced positive behavior from feedback")
            elif rating <= 2:
                # Negative feedback - adjust
                task = details.get('task', 'conversation')
                if task in self.skills:
                    self.skills[task].practice(success=False)
                summary['learned'].append("Adjusted approach based on negative feedback")
        
        self.stats['learning_sessions'] += 1
        self.stats['last_learning_session'] = time.time()
        
        self.save()
        
        return summary
    
    def save(self):
        """Save learning data to disk"""
        try:
            data = {
                'patterns': {pid: p.to_dict() for pid, p in self.patterns.items()},
                'skills': {sid: s.to_dict() for sid, s in self.skills.items()},
                'knowledge_graph': self.knowledge_graph.to_dict(),
                'stats': self.stats,
                'last_saved': time.time()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Continuous learner save failed: {e}")
    
    def load(self):
        """Load learning data from disk"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load patterns
                if 'patterns' in data:
                    self.patterns = {
                        pid: LearningPattern.from_dict(pdata)
                        for pid, pdata in data['patterns'].items()
                    }
                
                # Load skills
                if 'skills' in data:
                    self.skills = {
                        sid: AcquiredSkill.from_dict(sdata)
                        for sid, sdata in data['skills'].items()
                    }
                
                # Load knowledge graph
                if 'knowledge_graph' in data:
                    self.knowledge_graph = KnowledgeGraph.from_dict(data['knowledge_graph'])
                
                # Load stats
                if 'stats' in data:
                    self.stats.update(data['stats'])
        
        except Exception as e:
            print(f"Continuous learner load failed: {e}")


# Global continuous learner instance
continuous_learner = ContinuousLearner()

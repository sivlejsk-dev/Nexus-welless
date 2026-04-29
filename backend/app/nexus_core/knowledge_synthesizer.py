"""
Knowledge Synthesizer - Intelligent learning, pattern recognition, concept mapping
Maintains and grows knowledge across interactions and domains
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import defaultdict
import json
from datetime import datetime
import hashlib


class KnowledgeType(Enum):
    """Types of knowledge"""
    FACTUAL = "factual"  # Facts and data
    PROCEDURAL = "procedural"  # How-to knowledge
    CONCEPTUAL = "conceptual"  # Understanding concepts
    EXPERIENTIAL = "experiential"  # Learned from experience
    RELATIONAL = "relational"  # Relationships between concepts
    STRATEGIC = "strategic"  # Strategic knowledge


class LearningMode(Enum):
    """Learning mechanisms"""
    DIRECT = "direct"  # Direct instruction
    INFERENCE = "inference"  # Inferred from context
    PATTERN_RECOGNITION = "pattern_recognition"  # Recognized patterns
    ANALOGY = "analogy"  # Learned by analogy
    EXPERIMENTATION = "experimentation"  # Learned by testing


class ConceptMembership(Enum):
    """Strength of concept membership"""
    CORE = "core"  # Central to concept
    TYPICAL = "typical"  # Typical instance
    PERIPHERAL = "peripheral"  # Somewhat related
    BORDERLINE = "borderline"  # Edge case


@dataclass
class Concept:
    """Represents a concept or idea"""
    name: str
    definition: str
    properties: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    counterexamples: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)  # concept_name -> relationship_type
    confidence: float = 0.8
    knowledge_type: KnowledgeType = KnowledgeType.CONCEPTUAL
    learned_from: List[str] = field(default_factory=list)  # Sources/interactions
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0


@dataclass
class ConceptualPattern:
    """Represents a recognized pattern"""
    pattern_name: str
    description: str
    instances: List[str] = field(default_factory=list)
    frequency: int = 0
    consistency: float = 0.8  # How consistently it occurs
    domains: List[str] = field(default_factory=list)  # Which domains this applies to
    exceptions: List[str] = field(default_factory=list)
    discovered_date: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class KnowledgeIntegration:
    """Links concepts across domains"""
    source_concept: str
    target_concept: str
    integration_type: str  # analogy, specialization, generalization
    strength: float = 0.7
    explanation: str = ""
    cross_domain: bool = False


@dataclass
class Learning:
    """Represents a learned fact or relationship"""
    statement: str
    source: str  # Interaction, inference, etc.
    confidence: float = 0.8
    evidence: List[str] = field(default_factory=list)
    reinforced_by: List[str] = field(default_factory=list)
    contradicted_by: List[str] = field(default_factory=list)
    learned_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class KnowledgeSynthesizer:
    """Intelligent learning and knowledge synthesis system"""

    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.patterns: Dict[str, ConceptualPattern] = {}
        self.learnings: List[Learning] = []
        self.integrations: List[KnowledgeIntegration] = []
        self.domain_graph: Dict[str, Set[str]] = defaultdict(set)  # Domain -> concepts
        self.learning_history = []

    def learn_from_interaction(self, user_input: str, ai_response: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract learnings from an interaction"""
        learnings = {
            'new_concepts': [],
            'reinforced_concepts': [],
            'new_patterns': [],
            'integrations': [],
            'confidence_updates': []
        }
        
        # Extract new concepts
        concepts = self._extract_concepts(user_input, ai_response)
        for concept_name, definition in concepts.items():
            if concept_name not in self.concepts:
                self.concepts[concept_name] = Concept(
                    name=concept_name,
                    definition=definition,
                    learned_from=[user_input],
                    knowledge_type=KnowledgeType.CONCEPTUAL
                )
                learnings['new_concepts'].append(concept_name)
            else:
                self.concepts[concept_name].usage_count += 1
                self.concepts[concept_name].learned_from.append(user_input)
                learnings['reinforced_concepts'].append(concept_name)
        
        # Detect patterns
        patterns = self._detect_patterns(user_input)
        for pattern_name, pattern_info in patterns.items():
            if pattern_name not in self.patterns:
                self.patterns[pattern_name] = ConceptualPattern(
                    pattern_name=pattern_name,
                    description=pattern_info['description'],
                    instances=[user_input],
                    frequency=1,
                    domains=pattern_info.get('domains', [])
                )
                learnings['new_patterns'].append(pattern_name)
            else:
                self.patterns[pattern_name].instances.append(user_input)
                self.patterns[pattern_name].frequency += 1
        
        # Find cross-domain integrations
        integrations = self._find_integrations(concepts)
        learnings['integrations'].extend([i.source_concept for i in integrations])
        self.integrations.extend(integrations)
        
        # Update confidence scores
        confidence_updates = self._update_confidence(concepts)
        learnings['confidence_updates'] = confidence_updates
        
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'interaction': user_input[:100],
            'learnings': learnings
        })
        
        return learnings

    def _extract_concepts(self, user_input: str, ai_response: str) -> Dict[str, str]:
        """Extract concepts from interaction"""
        concepts = {}
        
        # Simple heuristic: extract nouns and key terms
        key_terms = [
            ("AI", "Artificial Intelligence - systems designed to perform intelligent tasks"),
            ("learning", "The process of acquiring knowledge and skills"),
            ("problem", "A situation requiring analysis and solution"),
            ("strategy", "A plan of action designed to achieve a goal"),
            ("reasoning", "The process of thinking through problems logically"),
            ("knowledge", "Information and understanding about the world"),
            ("pattern", "A repeated or recurring sequence or structure"),
            ("system", "An organized set of components working together"),
            ("solution", "An answer or method that resolves a problem"),
            ("analysis", "Detailed examination of something")
        ]
        
        input_text = user_input.lower() + " " + ai_response.lower()
        for term, definition in key_terms:
            if term.lower() in input_text:
                concepts[term] = definition
        
        return concepts

    def _detect_patterns(self, interaction: str) -> Dict[str, Dict[str, Any]]:
        """Detect recurring patterns in interactions"""
        patterns = {}
        
        interaction_lower = interaction.lower()
        
        # Pattern detection heuristics
        pattern_signatures = {
            "question_answering": {
                "signature": ["what", "why", "how", "?"],
                "description": "User asking questions expecting explanations",
                "domains": ["learning", "information_seeking"]
            },
            "problem_solving": {
                "signature": ["solve", "problem", "how to", "help with"],
                "description": "User presenting problems for solution",
                "domains": ["problem_solving", "reasoning"]
            },
            "creative_tasks": {
                "signature": ["create", "generate", "write", "design", "make"],
                "description": "User requesting creative generation",
                "domains": ["creativity", "generation"]
            },
            "analytical_tasks": {
                "signature": ["analyze", "evaluate", "compare", "explain"],
                "description": "User requesting analysis and evaluation",
                "domains": ["analysis", "critical_thinking"]
            }
        }
        
        for pattern_name, pattern_info in pattern_signatures.items():
            if any(sig in interaction_lower for sig in pattern_info['signature']):
                patterns[pattern_name] = pattern_info
        
        return patterns

    def _find_integrations(self, concepts: Dict[str, str]) -> List[KnowledgeIntegration]:
        """Find cross-domain integrations"""
        integrations = []
        
        concept_names = list(concepts.keys())
        for i, concept1 in enumerate(concept_names):
            for concept2 in concept_names[i+1:]:
                # Check for relationships between concepts
                integration = KnowledgeIntegration(
                    source_concept=concept1,
                    target_concept=concept2,
                    integration_type=self._determine_relationship(concept1, concept2),
                    strength=0.7,
                    cross_domain=True,
                    explanation=f"{concept1} and {concept2} are related through problem-solving context"
                )
                integrations.append(integration)
        
        return integrations

    def _determine_relationship(self, concept1: str, concept2: str) -> str:
        """Determine type of relationship between concepts"""
        # Simple heuristic
        relationships = {
            ("reasoning", "problem"): "applied_to",
            ("learning", "knowledge"): "produces",
            ("strategy", "solution"): "leads_to",
            ("pattern", "system"): "component_of",
        }
        
        for (c1, c2), rel in relationships.items():
            if (concept1.lower() == c1 and concept2.lower() == c2) or \
               (concept1.lower() == c2 and concept2.lower() == c1):
                return rel
        
        return "related_to"

    def _update_confidence(self, concepts: Dict[str, str]) -> List[str]:
        """Update confidence in concepts based on repeated usage"""
        updates = []
        for concept_name in concepts:
            if concept_name in self.concepts:
                self.concepts[concept_name].confidence = min(0.95, 
                    self.concepts[concept_name].confidence + 0.05)
                updates.append(f"{concept_name}: {self.concepts[concept_name].confidence:.0%}")
        return updates

    def synthesize_knowledge(self, query: str) -> Dict[str, Any]:
        """Synthesize knowledge to answer a query"""
        relevant_concepts = self._find_relevant_concepts(query)
        relevant_patterns = self._find_relevant_patterns(query)
        relevant_integrations = self._find_relevant_integrations(query)
        
        synthesis = {
            'query': query,
            'relevant_concepts': [(c.name, c.definition) for c in relevant_concepts[:3]],
            'relevant_patterns': [(p.pattern_name, p.description) for p in relevant_patterns[:2]],
            'integrations': [(i.source_concept, i.target_concept, i.integration_type) 
                           for i in relevant_integrations[:2]],
            'confidence': self._calculate_synthesis_confidence(relevant_concepts),
            'insights': self._generate_insights(relevant_concepts, relevant_patterns)
        }
        
        return synthesis

    def _find_relevant_concepts(self, query: str) -> List[Concept]:
        """Find concepts relevant to query"""
        query_lower = query.lower()
        relevant = []
        
        for concept in self.concepts.values():
            if (query_lower in concept.name.lower() or 
                any(term in query_lower for term in concept.properties) or
                query_lower in concept.definition.lower()):
                relevant.append(concept)
        
        # Sort by usage and confidence
        return sorted(relevant, key=lambda c: (c.usage_count, c.confidence), reverse=True)

    def _find_relevant_patterns(self, query: str) -> List[ConceptualPattern]:
        """Find patterns relevant to query"""
        query_lower = query.lower()
        relevant = []
        
        for pattern in self.patterns.values():
            if (query_lower in pattern.pattern_name.lower() or
                any(query_lower in instance for instance in pattern.instances) or
                any(d in query_lower for d in pattern.domains)):
                relevant.append(pattern)
        
        return sorted(relevant, key=lambda p: p.frequency, reverse=True)

    def _find_relevant_integrations(self, query: str) -> List[KnowledgeIntegration]:
        """Find integrations relevant to query"""
        query_lower = query.lower()
        relevant = []
        
        for integration in self.integrations:
            if (query_lower in integration.source_concept.lower() or
                query_lower in integration.target_concept.lower()):
                relevant.append(integration)
        
        return relevant

    def _calculate_synthesis_confidence(self, concepts: List[Concept]) -> float:
        """Calculate confidence in synthesis"""
        if not concepts:
            return 0.3
        
        avg_confidence = sum(c.confidence for c in concepts) / len(concepts)
        return min(0.95, avg_confidence)

    def _generate_insights(self, concepts: List[Concept], 
                          patterns: List[ConceptualPattern]) -> List[str]:
        """Generate insights from synthesized knowledge"""
        insights = []
        
        if concepts:
            insights.append(f"Core concepts: {', '.join([c.name for c in concepts[:2]])}")
        
        if patterns:
            insights.append(f"Recognized patterns: {', '.join([p.pattern_name for p in patterns[:2]])}")
        
        if concepts and patterns:
            insights.append(f"Integration: {concepts[0].name} relates to {patterns[0].pattern_name}")
        
        return insights

    def get_knowledge_report(self) -> Dict[str, Any]:
        """Generate comprehensive knowledge report"""
        return {
            'total_concepts': len(self.concepts),
            'total_patterns': len(self.patterns),
            'total_integrations': len(self.integrations),
            'total_learnings': len(self.learnings),
            'top_concepts': [(c.name, c.usage_count) 
                           for c in sorted(self.concepts.values(), 
                                         key=lambda x: x.usage_count, reverse=True)[:5]],
            'active_patterns': [(p.pattern_name, p.frequency) 
                              for p in sorted(self.patterns.values(), 
                                            key=lambda x: x.frequency, reverse=True)[:5]],
            'cross_domain_integrations': len([i for i in self.integrations if i.cross_domain]),
            'average_concept_confidence': (sum(c.confidence for c in self.concepts.values()) / 
                                          len(self.concepts) if self.concepts else 0)
        }


# Global instance
knowledge_synthesizer = KnowledgeSynthesizer()

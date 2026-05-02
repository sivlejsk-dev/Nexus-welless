"""
Advanced Reasoning Engine - Sophisticated Logical Problem-Solving System

Provides:
- Logical reasoning frameworks (deductive, inductive, abductive)
- Problem decomposition and analysis
- Multi-approach solution generation
- Dynamic reasoning path adaptation
- Evidence-based conclusion synthesis
- Insight and innovation extraction
"""

from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from datetime import datetime
import re


class ReasoningFramework(Enum):
    """Available logical reasoning frameworks"""
    DEDUCTIVE = "deductive"          # General → Specific
    INDUCTIVE = "inductive"          # Specific → General
    ABDUCTIVE = "abductive"          # Effect → Cause
    COMPARATIVE = "comparative"      # Compare alternatives
    CAUSAL = "causal"                # Cause-effect chains
    SYSTEMS = "systems"              # Interconnected systems
    PROBABILISTIC = "probabilistic"  # Based on likelihood
    ANALOGICAL = "analogical"        # By analogy/similarity


@dataclass
class ProblemComponent:
    """Represents a component of a decomposed problem"""
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    complexity: int = 1  # 1-10 scale
    priority: int = 5    # 1-10 scale (10 = highest)


@dataclass
class LogicalStep:
    """Represents one step in logical reasoning"""
    framework: ReasoningFramework
    premise: str
    reasoning: str
    conclusion: str
    confidence: float = 0.7
    evidence: List[str] = field(default_factory=list)


@dataclass
class ProblemAnalysis:
    """Complete analysis of a complex problem"""
    problem_statement: str
    key_questions: List[str] = field(default_factory=list)
    components: List[ProblemComponent] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    reasoning_path: str = ""
    overall_complexity: int = 5


@dataclass
class Solution:
    """Proposed solution with reasoning"""
    approach: str
    steps: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    implementation_difficulty: int = 5  # 1-10
    expected_effectiveness: float = 0.7  # 0-1
    requirements: List[str] = field(default_factory=list)
    timeline: str = "Medium-term"
    innovation_level: int = 3  # 1-10 (10 = highly innovative)


@dataclass
class AdvancedReasoningOutput:
    """Complete output from advanced reasoning"""
    original_problem: str
    analysis: ProblemAnalysis
    logical_steps: List[LogicalStep]
    alternative_approaches: List[str]
    proposed_solutions: List[Solution]
    recommended_solution: Optional[Solution]
    insights: List[str]
    key_insights: List[str]
    dialogue_points: List[str]
    adaptation_notes: str
    confidence_level: float
    reasoning_depth: int  # 1-10


class AdvancedReasoningEngine:
    """
    Sophisticated reasoning engine for complex problem-solving
    """
    
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base
        self.reasoning_history = []
        self.problem_cache = {}
        self.frameworks = self._initialize_frameworks()
        self.heuristics = self._initialize_heuristics()
    
    def _initialize_frameworks(self) -> Dict[ReasoningFramework, Dict]:
        """Define characteristics of each reasoning framework"""
        return {
            ReasoningFramework.DEDUCTIVE: {
                "direction": "top-down",
                "approach": "Start with general truths, derive specific conclusions",
                "best_for": ["Logical proofs", "Rule-based problems", "Mathematical problems"],
                "strength": "Certainty when premises are true",
                "weakness": "Requires valid premises"
            },
            ReasoningFramework.INDUCTIVE: {
                "direction": "bottom-up",
                "approach": "Observe specifics, generalize to broader principles",
                "best_for": ["Pattern recognition", "Data analysis", "Scientific hypothesis"],
                "strength": "Discovers new patterns",
                "weakness": "Not guaranteed to be true"
            },
            ReasoningFramework.ABDUCTIVE: {
                "direction": "effect-to-cause",
                "approach": "Observe effect, infer most likely cause",
                "best_for": ["Diagnosis", "Root cause analysis", "Mystery solving"],
                "strength": "Practical problem-solving",
                "weakness": "May miss actual cause"
            },
            ReasoningFramework.CAUSAL: {
                "direction": "bidirectional",
                "approach": "Trace cause-effect chains",
                "best_for": ["System analysis", "Dependency understanding", "Impact prediction"],
                "strength": "Shows interconnections",
                "weakness": "Complex with many variables"
            },
            ReasoningFramework.COMPARATIVE: {
                "direction": "lateral",
                "approach": "Compare alternatives across dimensions",
                "best_for": ["Decision-making", "Option evaluation", "Trade-off analysis"],
                "strength": "Reveals relative strengths",
                "weakness": "Requires pre-existing alternatives"
            },
            ReasoningFramework.SYSTEMS: {
                "direction": "holistic",
                "approach": "Understand problem as interconnected system",
                "best_for": ["Complex systems", "Organizational issues", "Ecosystem problems"],
                "strength": "Sees whole picture",
                "weakness": "Information overload possible"
            },
            ReasoningFramework.PROBABILISTIC: {
                "direction": "risk-based",
                "approach": "Consider likelihood and uncertainty",
                "best_for": ["Risk analysis", "Prediction", "Uncertain decisions"],
                "strength": "Handles uncertainty",
                "weakness": "Requires probability data"
            },
            ReasoningFramework.ANALOGICAL: {
                "direction": "similarity-based",
                "approach": "Apply solutions from similar problems",
                "best_for": ["Novel problems", "Creative solutions", "Precedent-based"],
                "strength": "Leverages existing knowledge",
                "weakness": "Analogies may not hold"
            }
        }
    
    def _initialize_heuristics(self) -> Dict[str, callable]:
        """Heuristics for problem-solving"""
        return {
            "divide_and_conquer": lambda p: self._divide_and_conquer(p),
            "work_backwards": lambda p: self._work_backwards(p),
            "simplify": lambda p: self._simplify_problem(p),
            "identify_constraints": lambda p: self._identify_constraints(p),
            "find_patterns": lambda p: self._find_patterns(p),
        }
    
    def analyze_problem(self, problem_statement: str) -> ProblemAnalysis:
        """
        Comprehensive problem analysis
        
        Breaks down problem into:
        - Key questions
        - Components
        - Constraints
        - Assumptions
        - Knowledge gaps
        """
        analysis = ProblemAnalysis(problem_statement=problem_statement)
        
        # Generate key questions
        analysis.key_questions = self._generate_key_questions(problem_statement)
        
        # Identify components
        analysis.components = self._decompose_problem(problem_statement)
        
        # Extract constraints
        analysis.constraints = self._extract_constraints(problem_statement)
        
        # Identify assumptions
        analysis.assumptions = self._identify_assumptions(problem_statement)
        
        # Find knowledge gaps
        analysis.knowledge_gaps = self._identify_knowledge_gaps(problem_statement)
        
        # Determine complexity
        analysis.overall_complexity = self._assess_complexity(analysis)
        
        # Suggest reasoning path
        analysis.reasoning_path = self._suggest_reasoning_path(analysis)
        
        return analysis
    
    def _generate_key_questions(self, problem: str) -> List[str]:
        """Generate key questions for understanding the problem"""
        questions = []
        
        # Fundamental questions
        questions.append(f"What exactly is the core issue in '{problem}'?")
        questions.append(f"What would success look like for '{problem}'?")
        questions.append(f"What constraints exist for '{problem}'?")
        
        # Causal questions
        questions.append(f"Why does '{problem}' exist?")
        questions.append(f"What causes '{problem}' to persist?")
        
        # Systemic questions
        questions.append(f"How does '{problem}' relate to other issues?")
        questions.append(f"Who is affected by '{problem}'?")
        
        # Future questions
        questions.append(f"What would happen if '{problem}' were solved?")
        questions.append(f"What would happen if '{problem}' worsened?")
        
        return questions[:5]  # Return top 5
    
    def _decompose_problem(self, problem: str) -> List[ProblemComponent]:
        """Break problem into manageable components"""
        components = []
        
        # Extract potential components from problem description
        keywords = self._extract_keywords(problem)
        
        component_patterns = {
            "Technical": ["system", "process", "technology", "tool", "method"],
            "People": ["team", "stakeholder", "person", "group", "organization"],
            "Process": ["workflow", "procedure", "sequence", "step", "phase"],
            "Resource": ["budget", "time", "cost", "investment", "resource"],
            "External": ["market", "competition", "environment", "external", "outside"]
        }
        
        for comp_type, keywords_list in component_patterns.items():
            if any(kw in problem.lower() for kw in keywords_list):
                components.append(ProblemComponent(
                    name=comp_type,
                    description=f"The {comp_type.lower()} aspect of this problem",
                    priority=6
                ))
        
        # Add a general analysis component
        if not components:
            components.append(ProblemComponent(
                name="Core Problem",
                description="Understanding the fundamental issue",
                priority=10
            ))
        
        return components[:5]
    
    def _extract_constraints(self, problem: str) -> List[str]:
        """Extract constraints from problem statement"""
        constraints = []
        
        constraint_keywords = {
            "time": ["deadline", "quickly", "fast", "limited time", "urgent", "weeks", "days"],
            "budget": ["cost", "expensive", "budget", "limited funding", "affordable"],
            "resources": ["limited", "scarce", "availability", "lack of"],
            "regulation": ["rules", "regulations", "compliance", "legal", "laws"],
            "technical": ["complexity", "difficult", "technical", "not possible"]
        }
        
        lower_problem = problem.lower()
        for constraint_type, keywords in constraint_keywords.items():
            if any(kw in lower_problem for kw in keywords):
                constraints.append(f"{constraint_type.title()}: Limited by problem constraints")
        
        if not constraints:
            constraints.append("No explicit constraints identified - ensure feasibility check")
        
        return constraints[:5]
    
    def _identify_assumptions(self, problem: str) -> List[str]:
        """Identify implicit assumptions in the problem"""
        assumptions = []
        
        # Common assumptions
        assumptions.append("That the problem statement is accurate and complete")
        assumptions.append("That relevant stakeholders have been considered")
        assumptions.append("That the proposed scope is appropriate")
        assumptions.append("That existing solutions have been evaluated")
        assumptions.append("That the problem will remain stable during solution")
        
        return assumptions
    
    def _identify_knowledge_gaps(self, problem: str) -> List[str]:
        """Identify areas where more knowledge is needed"""
        gaps = []
        
        gap_patterns = {
            "Historical context": "previous solutions or similar problems",
            "Expert opinion": "what subject matter experts think",
            "Data": "relevant statistics or measurements",
            "Market/Competition": "how others handle similar issues",
            "Technology": "available tools or approaches"
        }
        
        for gap_type, description in gap_patterns.items():
            gaps.append(f"{gap_type}: Understanding of {description}")
        
        return gaps[:5]
    
    def _assess_complexity(self, analysis: ProblemAnalysis) -> int:
        """Assess overall problem complexity (1-10)"""
        complexity = 5  # Start at medium
        
        # Increase by number of components
        complexity += len(analysis.components)
        
        # Increase by constraints
        complexity += len(analysis.constraints) // 2
        
        # Cap at 10
        return min(complexity, 10)
    
    def _suggest_reasoning_path(self, analysis: ProblemAnalysis) -> str:
        """Suggest which reasoning frameworks to use"""
        if analysis.overall_complexity > 8:
            return "Systems thinking + Causal analysis for interconnected complexity"
        elif analysis.overall_complexity > 5:
            return "Deductive reasoning for structure + Inductive for patterns"
        else:
            return "Direct logical analysis + Comparative evaluation"
    
    def reason_through_problem(self, problem: str, analysis: ProblemAnalysis) -> List[LogicalStep]:
        """
        Apply logical reasoning frameworks to problem
        
        Returns sequence of logical steps
        """
        steps = []
        
        # Step 1: Deductive - Start with established principles
        steps.append(self._apply_deductive_reasoning(problem, analysis))
        
        # Step 2: Inductive - Look for patterns
        steps.append(self._apply_inductive_reasoning(problem, analysis))
        
        # Step 3: Abductive - Infer causes
        steps.append(self._apply_abductive_reasoning(problem, analysis))
        
        # Step 4: Causal - Trace relationships
        steps.append(self._apply_causal_reasoning(problem, analysis))
        
        return [s for s in steps if s is not None]
    
    def _apply_deductive_reasoning(self, problem: str, analysis: ProblemAnalysis) -> LogicalStep:
        """Apply deductive reasoning (general to specific)"""
        return LogicalStep(
            framework=ReasoningFramework.DEDUCTIVE,
            premise="General principles that likely apply to this problem type",
            reasoning=f"Based on problem type '{analysis.problem_statement[:50]}...', "
                     f"we can apply established principles in {analysis.components[0].name if analysis.components else 'this domain'}",
            conclusion="These principles should guide our approach",
            confidence=0.85,
            evidence=[f"Component: {c.name}" for c in analysis.components[:3]]
        )
    
    def _apply_inductive_reasoning(self, problem: str, analysis: ProblemAnalysis) -> LogicalStep:
        """Apply inductive reasoning (specific to general)"""
        return LogicalStep(
            framework=ReasoningFramework.INDUCTIVE,
            premise="Specific observations from the problem",
            reasoning=f"Looking at the {len(analysis.constraints)} identified constraints "
                     f"and {len(analysis.components)} components, patterns emerge",
            conclusion="These patterns suggest a broader principle that should guide solutions",
            confidence=0.7,
            evidence=analysis.constraints[:3]
        )
    
    def _apply_abductive_reasoning(self, problem: str, analysis: ProblemAnalysis) -> LogicalStep:
        """Apply abductive reasoning (effect to cause)"""
        return LogicalStep(
            framework=ReasoningFramework.ABDUCTIVE,
            premise="Observed symptoms and effects of the problem",
            reasoning="The most likely explanation for these symptoms is rooted in the "
                     f"{analysis.knowledge_gaps[0] if analysis.knowledge_gaps else 'underlying factors'}",
            conclusion="Addressing root causes will resolve the observed effects",
            confidence=0.65,
            evidence=analysis.key_questions[:2]
        )
    
    def _apply_causal_reasoning(self, problem: str, analysis: ProblemAnalysis) -> LogicalStep:
        """Apply causal reasoning (cause-effect chains)"""
        return LogicalStep(
            framework=ReasoningFramework.CAUSAL,
            premise="Complex cause-effect relationships in the system",
            reasoning=f"With {len(analysis.components)} interconnected components, "
                     f"changes in one affect others through causal chains",
            conclusion="Solutions must account for ripple effects and system interactions",
            confidence=0.75,
            evidence=[f"Component dependency: {c.dependencies}" for c in analysis.components[:2]]
        )
    
    def generate_solutions(self, problem: str, analysis: ProblemAnalysis, 
                          reasoning_steps: List[LogicalStep]) -> List[Solution]:
        """Generate multiple solution approaches"""
        solutions = []
        
        # Approach 1: Direct solution
        solutions.append(self._generate_direct_solution(problem, analysis))
        
        # Approach 2: Systemic solution
        solutions.append(self._generate_systemic_solution(problem, analysis))
        
        # Approach 3: Innovative solution
        solutions.append(self._generate_innovative_solution(problem, analysis))
        
        # Approach 4: Phased solution
        solutions.append(self._generate_phased_solution(problem, analysis))
        
        return solutions
    
    def _generate_direct_solution(self, problem: str, analysis: ProblemAnalysis) -> Solution:
        """Direct, straightforward approach"""
        return Solution(
            approach="Direct Approach - Address the problem head-on",
            steps=[
                f"1. Clearly define the {analysis.components[0].name if analysis.components else 'core'} issue",
                "2. Identify immediate obstacles and constraints",
                "3. Implement targeted solution to core problem",
                "4. Monitor and adjust based on results"
            ],
            pros=["Fast to implement", "Clear and understandable", "Proven approaches"],
            cons=["May miss systemic issues", "Could have unintended consequences"],
            implementation_difficulty=4,
            expected_effectiveness=0.75,
            timeline="Short-term (weeks to months)",
            innovation_level=2
        )
    
    def _generate_systemic_solution(self, problem: str, analysis: ProblemAnalysis) -> Solution:
        """Address the entire system"""
        return Solution(
            approach="Systemic Approach - Address interconnected elements",
            steps=[
                "1. Map all system components and relationships",
                "2. Identify leverage points in the system",
                "3. Implement solutions across multiple components",
                "4. Monitor emergent behaviors and feedback loops"
            ],
            pros=["Addresses root causes", "Prevents problem recurrence", "Improves overall system"],
            cons=["Complex to implement", "Takes longer", "Requires coordination"],
            implementation_difficulty=8,
            expected_effectiveness=0.85,
            timeline="Medium to long-term (months to years)",
            innovation_level=6
        )
    
    def _generate_innovative_solution(self, problem: str, analysis: ProblemAnalysis) -> Solution:
        """Novel, creative approach"""
        return Solution(
            approach="Innovative Approach - Novel and creative solution",
            steps=[
                "1. Challenge fundamental assumptions about the problem",
                "2. Apply analogies from unrelated domains",
                "3. Experiment with non-traditional approaches",
                "4. Iterate based on feedback and learning"
            ],
            pros=["Potentially transformative", "May create competitive advantage", "Inspiring"],
            cons=["High risk", "Uncertain outcomes", "Requires organizational buy-in"],
            implementation_difficulty=9,
            expected_effectiveness=0.70,
            requirements=["Experimentation budget", "Risk tolerance", "Talented team"],
            timeline="Long-term with short iterations (6+ months)",
            innovation_level=9
        )
    
    def _generate_phased_solution(self, problem: str, analysis: ProblemAnalysis) -> Solution:
        """Step-by-step phased approach"""
        return Solution(
            approach="Phased Approach - Implement in manageable phases",
            steps=[
                "1. Phase 1: Quick wins and early validation",
                "2. Phase 2: Build on early success with broader changes",
                "3. Phase 3: Optimize and scale solution",
                "4. Phase 4: Maintain and continuously improve"
            ],
            pros=["Lower risk per phase", "Allows learning and adjustment", "Builds momentum"],
            cons=["Takes longer overall", "Requires sustained effort", "Interim solutions needed"],
            implementation_difficulty=6,
            expected_effectiveness=0.80,
            timeline="Medium-term with progressive phases",
            innovation_level=5
        )
    
    def extract_insights(self, problem: str, analysis: ProblemAnalysis,
                        solutions: List[Solution]) -> Tuple[List[str], List[str]]:
        """
        Extract key insights and dialogue points
        
        Returns:
        - General insights
        - Key dialogue points for meaningful discussion
        """
        insights = []
        dialogue_points = []
        
        # Insight 1: Complexity
        insights.append(
            f"This problem involves {len(analysis.components)} interconnected components "
            f"with complexity level {analysis.overall_complexity}/10, suggesting systemic thinking "
            f"is valuable alongside direct solutions."
        )
        
        # Insight 2: Constraints
        if analysis.constraints:
            insights.append(
                f"The {len(analysis.constraints)} identified constraints will significantly "
                f"impact solution selection, particularly {analysis.constraints[0].lower()} "
                f"and {analysis.constraints[1].lower() if len(analysis.constraints) > 1 else 'other factors'}."
            )
        
        # Insight 3: Knowledge gaps
        if analysis.knowledge_gaps:
            insights.append(
                f"Critical knowledge gaps exist around {analysis.knowledge_gaps[0].lower()}. "
                f"Acquiring this information before implementation could prevent costly mistakes."
            )
        
        # Insight 4: Solution diversity
        effectiveness_range = (
            min(s.expected_effectiveness for s in solutions),
            max(s.expected_effectiveness for s in solutions)
        )
        insights.append(
            f"Solution effectiveness ranges from {effectiveness_range[0]:.0%} to {effectiveness_range[1]:.0%}, "
            f"indicating trade-offs between speed, certainty, and transformative potential."
        )
        
        # Dialogue Point 1: Problem framing
        dialogue_points.append(
            f"How might reframing '{problem}' differently change our approach? "
            f"Are we solving the right problem or just the symptoms?"
        )
        
        # Dialogue Point 2: Stakeholder perspective
        dialogue_points.append(
            "Which stakeholders are most affected? How do their perspectives change "
            "what we should prioritize?"
        )
        
        # Dialogue Point 3: Timeline and resources
        dialogue_points.append(
            "Given your available resources and timeline, which solution approach "
            "offers the best balance of impact and feasibility?"
        )
        
        # Dialogue Point 4: Risk tolerance
        dialogue_points.append(
            "How much risk can you tolerate? This determines whether we should pursue "
            "proven solutions or innovative approaches."
        )
        
        # Dialogue Point 5: Success metrics
        dialogue_points.append(
            "How will you measure success? Clear metrics help track progress and "
            "justify resource allocation."
        )
        
        return insights, dialogue_points
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'be', 'been', 'being', 'have', 'has', 'had'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        return {w for w in words if w not in stop_words and len(w) > 3}
    
    def _divide_and_conquer(self, problem: str) -> List[str]:
        """Break problem into smaller parts"""
        return ["Divide into smaller subproblems", "Solve each independently", "Integrate solutions"]
    
    def _work_backwards(self, problem: str) -> List[str]:
        """Work backwards from desired outcome"""
        return ["Define desired outcome", "Work backwards to current state", "Identify gaps and steps"]
    
    def _simplify_problem(self, problem: str) -> List[str]:
        """Remove non-essential elements"""
        return ["Strip down to core issue", "Solve simplified version", "Add complexity gradually"]
    
    def _identify_constraints(self, problem: str) -> List[str]:
        """Clearly define constraints"""
        return ["List all constraints", "Prioritize by impact", "Find creative solutions within bounds"]
    
    def _find_patterns(self, problem: str) -> List[str]:
        """Look for patterns and similarities"""
        return ["Identify recurring patterns", "Find similar problems", "Apply analogous solutions"]
    
    def generate_comprehensive_reasoning(self, problem: str) -> AdvancedReasoningOutput:
        """
        Complete reasoning process from problem to solution recommendation
        """
        # Step 1: Analyze
        analysis = self.analyze_problem(problem)
        
        # Step 2: Apply reasoning frameworks
        logical_steps = self.reason_through_problem(problem, analysis)
        
        # Step 3: Generate solutions
        solutions = self.generate_solutions(problem, analysis, logical_steps)
        
        # Step 4: Extract insights
        insights, dialogue_points = self.extract_insights(problem, analysis, solutions)
        
        # Step 5: Recommend best solution
        recommended = self._select_best_solution(solutions)
        
        # Step 6: Calculate overall confidence
        confidence = self._calculate_confidence(analysis, logical_steps, solutions)
        
        # Step 7: Determine reasoning depth
        reasoning_depth = min(8, analysis.overall_complexity + 2)
        
        return AdvancedReasoningOutput(
            original_problem=problem,
            analysis=analysis,
            logical_steps=logical_steps,
            alternative_approaches=[s.approach for s in solutions],
            proposed_solutions=solutions,
            recommended_solution=recommended,
            insights=insights,
            key_insights=insights[:3],
            dialogue_points=dialogue_points,
            adaptation_notes="Reasoning adapted based on problem complexity and framework analysis",
            confidence_level=confidence,
            reasoning_depth=reasoning_depth
        )
    
    def _select_best_solution(self, solutions: List[Solution]) -> Solution:
        """Select the best overall solution"""
        if not solutions:
            return None
        
        # Score based on effectiveness, feasibility, and balance
        def solution_score(s: Solution) -> float:
            effectiveness = s.expected_effectiveness
            feasibility = 1 - (s.implementation_difficulty / 10)
            innovation = s.innovation_level / 10
            
            # Weight: 50% effectiveness, 30% feasibility, 20% innovation
            return (effectiveness * 0.5) + (feasibility * 0.3) + (innovation * 0.2)
        
        best = max(solutions, key=solution_score)
        return best
    
    def _calculate_confidence(self, analysis: ProblemAnalysis, 
                            steps: List[LogicalStep], 
                            solutions: List[Solution]) -> float:
        """Calculate overall confidence in the reasoning"""
        avg_step_confidence = sum(s.confidence for s in steps) / len(steps) if steps else 0.7
        
        # Reduce confidence if many knowledge gaps
        gap_penalty = len(analysis.knowledge_gaps) * 0.05
        
        # Increase confidence if problem is well-defined
        clarity_bonus = min(0.1, 0.02 * len(analysis.components))
        
        confidence = avg_step_confidence - gap_penalty + clarity_bonus
        return max(0.5, min(0.95, confidence))  # Constrain to 0.5-0.95
    
    def adapt_reasoning(self, original_problem: str, new_information: str,
                       previous_reasoning: AdvancedReasoningOutput) -> AdvancedReasoningOutput:
        """
        Dynamically adapt reasoning based on new information
        """
        # Re-analyze with new information
        updated_problem = f"{original_problem}\n[New information: {new_information}]"
        
        # Generate new reasoning
        new_reasoning = self.generate_comprehensive_reasoning(updated_problem)
        
        # Note adaptation
        new_reasoning.adaptation_notes = (
            f"Reasoning updated based on new information. "
            f"Previous confidence: {previous_reasoning.confidence_level:.0%}, "
            f"Updated confidence: {new_reasoning.confidence_level:.0%}"
        )
        
        return new_reasoning
    
    def format_reasoning_dialogue(self, reasoning: AdvancedReasoningOutput) -> str:
        """Format reasoning output as natural dialogue"""
        dialogue = []
        
        dialogue.append(f"**Problem Analysis:**")
        dialogue.append(f"You've presented: {reasoning.original_problem}")
        dialogue.append("")
        
        dialogue.append(f"**My Understanding:**")
        dialogue.append(f"This is a {reasoning.reasoning_depth}/10 complexity problem with:")
        dialogue.append(f"- {len(reasoning.analysis.components)} key components to address")
        dialogue.append(f"- {len(reasoning.analysis.constraints)} important constraints")
        dialogue.append(f"- {len(reasoning.analysis.knowledge_gaps)} knowledge gaps to consider")
        dialogue.append("")
        
        dialogue.append(f"**Key Questions to Consider:**")
        for q in reasoning.analysis.key_questions[:3]:
            dialogue.append(f"- {q}")
        dialogue.append("")
        
        dialogue.append(f"**My Reasoning Approach:**")
        for step in reasoning.logical_steps[:2]:
            dialogue.append(f"- {step.framework.value.title()}: {step.reasoning[:100]}...")
        dialogue.append("")
        
        dialogue.append(f"**Solution Approaches:**")
        for sol in reasoning.proposed_solutions[:3]:
            dialogue.append(f"- **{sol.approach}**: {sol.expected_effectiveness:.0%} effective, "
                          f"difficulty {sol.implementation_difficulty}/10")
        dialogue.append("")
        
        dialogue.append(f"**My Recommendation:**")
        if reasoning.recommended_solution:
            dialogue.append(f"I recommend the **{reasoning.recommended_solution.approach}** because it "
                          f"balances effectiveness ({reasoning.recommended_solution.expected_effectiveness:.0%}) "
                          f"with feasibility (difficulty {reasoning.recommended_solution.implementation_difficulty}/10).")
        dialogue.append("")
        
        dialogue.append(f"**Key Insights:**")
        for insight in reasoning.key_insights:
            dialogue.append(f"- {insight}")
        dialogue.append("")
        
        dialogue.append(f"**Let's Explore Together:**")
        for point in reasoning.dialogue_points[:3]:
            dialogue.append(f"- {point}")
        dialogue.append("")
        
        dialogue.append(f"**Confidence Level:** {reasoning.confidence_level:.0%}")
        
        return "\n".join(dialogue)

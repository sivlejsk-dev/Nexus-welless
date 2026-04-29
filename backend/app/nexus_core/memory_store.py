"""
Core Memory Store Interface

Unified interface for all memory types with standardized storage and retrieval.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime
import json


class MemoryType(Enum):
    """Types of memory in the system"""
    EPISODIC = "episodic"  # Conversation history, events
    SEMANTIC = "semantic"  # Knowledge, facts, relationships
    WORKING = "working"    # Active context (5-9 items)
    LONG_TERM = "long_term"  # User preferences, learned patterns


@dataclass
class MemoryItem:
    """Base class for all memory items"""
    id: str
    memory_type: MemoryType
    content: Any
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance: float = 0.5  # 0-1 scale
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'memory_type': self.memory_type.value,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'access_count': self.access_count,
            'importance': self.importance,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryItem:
        """Create from dictionary"""
        return cls(
            id=data['id'],
            memory_type=MemoryType(data['memory_type']),
            content=data['content'],
            created_at=datetime.fromisoformat(data['created_at']),
            accessed_at=datetime.fromisoformat(data['accessed_at']),
            access_count=data['access_count'],
            importance=data['importance'],
            tags=data['tags'],
            metadata=data['metadata']
        )


class MemoryStore:
    """
    Unified memory storage interface
    
    Coordinates all memory types and provides unified API for storage/retrieval.
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self._episodic_memory = None
        self._semantic_memory = None
        self._working_memory = None
        self._preference_store = None
        
        # Statistics
        self.total_stores = 0
        self.total_retrievals = 0
        self.cache_hits = 0
        
    def initialize(self):
        """Initialize all memory subsystems (lazy loading)"""
        from .episodic_memory import EpisodicMemory
        from .semantic_memory import SemanticMemory
        from .working_memory import WorkingMemory
        from .preference_store import PreferenceStore
        
        self._episodic_memory = EpisodicMemory(self.user_id)
        self._semantic_memory = SemanticMemory(self.user_id)
        self._working_memory = WorkingMemory(self.user_id)
        self._preference_store = PreferenceStore(self.user_id)
        
        print(f"✓ Memory system initialized for user: {self.user_id}")
    
    @property
    def episodic(self):
        """Access episodic memory (conversation history)"""
        if self._episodic_memory is None:
            self.initialize()
        return self._episodic_memory
    
    @property
    def semantic(self):
        """Access semantic memory (knowledge graph)"""
        if self._semantic_memory is None:
            self.initialize()
        return self._semantic_memory
    
    @property
    def working(self):
        """Access working memory (active context)"""
        if self._working_memory is None:
            self.initialize()
        return self._working_memory
    
    @property
    def preferences(self):
        """Access preference store (long-term user data)"""
        if self._preference_store is None:
            self.initialize()
        return self._preference_store
    
    def store(self, memory_type: MemoryType, content: Any, 
              importance: float = 0.5, tags: List[str] = None,
              metadata: Dict[str, Any] = None) -> str:
        """
        Store a memory item
        
        Args:
            memory_type: Type of memory to store
            content: Memory content (dict, string, or object)
            importance: Importance score (0-1)
            tags: Optional tags for categorization
            metadata: Optional metadata
            
        Returns:
            Memory item ID
        """
        self.total_stores += 1
        
        if memory_type == MemoryType.EPISODIC:
            return self.episodic.store_event(content, importance, tags, metadata)
        elif memory_type == MemoryType.SEMANTIC:
            return self.semantic.store_knowledge(content, importance, tags, metadata)
        elif memory_type == MemoryType.WORKING:
            return self.working.add_to_context(content, importance, tags, metadata)
        elif memory_type == MemoryType.LONG_TERM:
            return self.preferences.store_preference(content, importance, tags, metadata)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    def retrieve(self, query: str, memory_types: List[MemoryType] = None,
                limit: int = 10, min_relevance: float = 0.5) -> List[MemoryItem]:
        """
        Retrieve memories across all or specified types
        
        Args:
            query: Search query
            memory_types: Types to search (None = all types)
            limit: Maximum results
            min_relevance: Minimum relevance score (0-1)
            
        Returns:
            List of memory items sorted by relevance
        """
        self.total_retrievals += 1
        
        if memory_types is None:
            memory_types = list(MemoryType)
        
        results = []
        
        for mem_type in memory_types:
            if mem_type == MemoryType.EPISODIC:
                results.extend(self.episodic.search(query, limit, min_relevance))
            elif mem_type == MemoryType.SEMANTIC:
                results.extend(self.semantic.search(query, limit, min_relevance))
            elif mem_type == MemoryType.WORKING:
                results.extend(self.working.search(query, limit, min_relevance))
            elif mem_type == MemoryType.LONG_TERM:
                results.extend(self.preferences.search(query, limit, min_relevance))
        
        # Sort by relevance and importance
        results.sort(key=lambda x: (x.importance, x.access_count), reverse=True)
        
        return results[:limit]
    
    def recall_conversation(self, topic: str = None, 
                           time_window_hours: int = 24,
                           limit: int = 10) -> List[Any]:
        """
        Recall recent conversation about a topic
        
        Args:
            topic: Topic to recall (None = all recent)
            time_window_hours: How far back to search
            limit: Maximum results
            
        Returns:
            List of conversation events
        """
        return self.episodic.recall_conversation(topic, time_window_hours, limit)
    
    def get_knowledge(self, entity: str, relationship_type: str = None) -> Dict[str, Any]:
        """
        Get knowledge about an entity and its relationships
        
        Args:
            entity: Entity name
            relationship_type: Optional relationship filter
            
        Returns:
            Knowledge structure with entity and relationships
        """
        return self.semantic.get_knowledge(entity, relationship_type)
    
    def get_active_context(self) -> List[Any]:
        """Get current working memory context (5-9 items)"""
        return self.working.get_context()
    
    def get_user_preferences(self, category: str = None) -> Dict[str, Any]:
        """Get user preferences, optionally filtered by category"""
        return self.preferences.get_preferences(category)
    
    def consolidate_memories(self):
        """
        Consolidate memories across systems
        
        Moves important working memory to episodic/semantic.
        Prunes old low-importance memories.
        """
        # Move important working memory to episodic
        consolidated = self.working.consolidate_to_episodic(self.episodic)
        
        # Prune old low-importance memories
        pruned_episodic = self.episodic.prune_old_memories(days=90, min_importance=0.3)
        pruned_semantic = self.semantic.prune_unused_knowledge(days=180)
        
        return {
            'consolidated': consolidated,
            'pruned_episodic': pruned_episodic,
            'pruned_semantic': pruned_semantic
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            'user_id': self.user_id,
            'total_stores': self.total_stores,
            'total_retrievals': self.total_retrievals,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.cache_hits / max(1, self.total_retrievals),
            'episodic_count': len(self.episodic.events) if self._episodic_memory else 0,
            'semantic_nodes': len(self.semantic.nodes) if self._semantic_memory else 0,
            'working_items': len(self.working.context) if self._working_memory else 0,
            'preferences_count': len(self.preferences.preferences) if self._preference_store else 0
        }

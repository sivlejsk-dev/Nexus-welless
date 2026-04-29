"""
Working Memory: Active Context & Short-Term State

Implements Miller's Law (5±2 items) for active context management.
Auto-consolidates to episodic memory when capacity reached.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .memory_store import MemoryItem, MemoryType
import uuid


@dataclass
class ContextItem:
    """Item in working memory"""
    id: str
    content: Any
    added_at: datetime
    importance: float
    tags: List[str]
    metadata: Dict[str, Any]
    
    def to_memory_item(self) -> MemoryItem:
        """Convert to MemoryItem"""
        return MemoryItem(
            id=self.id,
            memory_type=MemoryType.WORKING,
            content=self.content,
            created_at=self.added_at,
            accessed_at=datetime.now(),
            importance=self.importance,
            tags=self.tags,
            metadata=self.metadata
        )


class WorkingMemory:
    """
    Working memory subsystem
    
    Maintains active context (5-9 items max per Miller's Law).
    Auto-consolidates to episodic memory when full.
    
    Use for: current conversation context, active tasks, immediate goals
    """
    
    def __init__(self, user_id: str, max_items: int = 7):
        """
        Initialize working memory
        
        Args:
            user_id: User identifier
            max_items: Maximum items (5-9 recommended per Miller's Law)
        """
        self.user_id = user_id
        self.max_items = max(5, min(9, max_items))  # Enforce Miller's Law
        self.items: List[ContextItem] = []
        self.item_index: Dict[str, ContextItem] = {}
        self._episodic_memory = None  # Set externally for consolidation
        
    def set_episodic_memory(self, episodic_memory):
        """Set episodic memory for consolidation"""
        self._episodic_memory = episodic_memory
    
    def add_to_context(self, content: Any, importance: float = 0.5,
                      tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """
        Add item to working memory
        
        If full, consolidates least important item to episodic memory.
        """
        item_id = str(uuid.uuid4())
        
        item = ContextItem(
            id=item_id,
            content=content,
            added_at=datetime.now(),
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Check capacity
        if len(self.items) >= self.max_items:
            self._consolidate_least_important()
        
        self.items.append(item)
        self.item_index[item_id] = item
        
        return item_id
    
    def get_context(self) -> List[ContextItem]:
        """Get current context items (ordered by importance)"""
        sorted_items = sorted(self.items, key=lambda x: x.importance, reverse=True)
        return sorted_items
    
    def search(self, query: str, limit: int = 10, min_relevance: float = 0.5) -> List[MemoryItem]:
        """Search working memory"""
        results = []
        query_lower = query.lower()
        
        for item in self.items:
            relevance = 0.0
            
            # Check content
            if isinstance(item.content, str) and query_lower in item.content.lower():
                relevance += 0.6
            elif isinstance(item.content, dict):
                # Search in dictionary values
                for value in item.content.values():
                    if query_lower in str(value).lower():
                        relevance += 0.4
                        break
            
            # Check tags
            if any(query_lower in tag.lower() for tag in item.tags):
                relevance += 0.4
            
            if relevance >= min_relevance:
                memory_item = item.to_memory_item()
                memory_item.importance = relevance
                results.append(memory_item)
        
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    def remove_item(self, item_id: str) -> bool:
        """Remove item from working memory"""
        if item_id in self.item_index:
            item = self.item_index[item_id]
            self.items.remove(item)
            del self.item_index[item_id]
            return True
        return False
    
    def clear_context(self):
        """Clear all working memory (use with caution)"""
        self.items.clear()
        self.item_index.clear()
    
    def _consolidate_least_important(self):
        """Move least important item to episodic memory"""
        if not self.items:
            return
        
        # Find least important item
        least_important = min(self.items, key=lambda x: x.importance)
        
        # Consolidate to episodic memory if available
        if self._episodic_memory:
            # Store in episodic memory
            self._episodic_memory.store_event(
                content=least_important.content,
                importance=least_important.importance,
                tags=least_important.tags,
                metadata={
                    **least_important.metadata,
                    'consolidated_from': 'working_memory',
                    'consolidated_at': datetime.now().isoformat()
                }
            )
        
        # Remove from working memory
        self.remove_item(least_important.id)
    
    def consolidate_to_episodic(self, episodic_memory) -> int:
        """
        Manually consolidate all items to episodic memory
        
        Returns: Number of items consolidated
        """
        count = 0
        for item in list(self.items):
            episodic_memory.store_event(
                content=item.content,
                importance=item.importance,
                tags=item.tags,
                metadata={
                    **item.metadata,
                    'consolidated_from': 'working_memory',
                    'consolidated_at': datetime.now().isoformat()
                }
            )
            count += 1
        
        self.clear_context()
        return count
    
    def prune_old_items(self, hours: int = 24) -> int:
        """Remove items older than threshold"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        before_count = len(self.items)
        
        # Consolidate old items to episodic memory
        old_items = [item for item in self.items if item.added_at < cutoff_time]
        
        if self._episodic_memory:
            for item in old_items:
                self._episodic_memory.store_event(
                    content=item.content,
                    importance=item.importance,
                    tags=item.tags,
                    metadata={
                        **item.metadata,
                        'pruned_from_working': True,
                        'pruned_at': datetime.now().isoformat()
                    }
                )
        
        # Remove old items
        self.items = [item for item in self.items if item.added_at >= cutoff_time]
        self.item_index = {item.id: item for item in self.items}
        
        after_count = len(self.items)
        return before_count - after_count
    
    def get_capacity_status(self) -> Dict[str, Any]:
        """Get working memory capacity status"""
        return {
            'current_items': len(self.items),
            'max_items': self.max_items,
            'capacity_used': len(self.items) / self.max_items,
            'is_full': len(self.items) >= self.max_items,
            'available_slots': self.max_items - len(self.items)
        }

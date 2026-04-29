"""
Preference Store: Long-Term User Preferences & Learned Behaviors

Stores persistent user preferences, learned patterns, and personalization data.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .memory_store import MemoryItem, MemoryType
import uuid


@dataclass
class UserPreference:
    """User preference or learned behavior"""
    id: str
    category: str  # interaction, interface, content, behavior, etc.
    key: str  # preference name
    value: Any  # preference value
    confidence: float  # 0-1 (how confident we are about this preference)
    created_at: datetime
    updated_at: datetime
    access_count: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'category': self.category,
            'key': self.key,
            'value': self.value,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'access_count': self.access_count,
            'metadata': self.metadata
        }
    
    def to_memory_item(self) -> MemoryItem:
        """Convert to MemoryItem"""
        return MemoryItem(
            id=self.id,
            memory_type=MemoryType.LONG_TERM,
            content=self.to_dict(),
            created_at=self.created_at,
            accessed_at=self.updated_at,
            last_accessed_at=self.updated_at,
            access_count=self.access_count,
            importance=self.confidence,
            tags=[self.category, self.key],
            metadata=self.metadata
        )


class PreferenceStore:
    """
    Preference store subsystem
    
    Stores long-term user preferences and learned behaviors.
    Enables personalization and user-specific adaptations.
    
    Categories:
    - interaction: Communication style preferences
    - interface: UI/UX preferences
    - content: Content type preferences
    - behavior: Learned behavior patterns
    - privacy: Privacy and security preferences
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferences: Dict[str, UserPreference] = {}  # key -> preference
        self.category_index: Dict[str, List[str]] = {}  # category -> list of keys
        
    def store_preference(self, content: Any, importance: float = 0.5,
                        tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Store or update a preference"""
        if isinstance(content, dict):
            category = content.get('category', 'general')
            key = content.get('key', str(uuid.uuid4()))
            value = content.get('value')
            confidence = importance
        else:
            # Simple text-based preference
            category = 'general'
            key = str(uuid.uuid4())
            value = str(content)
            confidence = importance
        
        pref_id = f"{category}:{key}"
        
        # Update existing or create new
        if pref_id in self.preferences:
            pref = self.preferences[pref_id]
            pref.value = value
            pref.confidence = max(pref.confidence, confidence)
            pref.updated_at = datetime.now()
            pref.access_count += 1
            if metadata:
                pref.metadata.update(metadata)
        else:
            pref = UserPreference(
                id=pref_id,
                category=category,
                key=key,
                value=value,
                confidence=confidence,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                access_count=1,
                metadata=metadata or {}
            )
            self.preferences[pref_id] = pref
            
            # Update category index
            if category not in self.category_index:
                self.category_index[category] = []
            if key not in self.category_index[category]:
                self.category_index[category].append(key)
        
        return pref_id
    
    def get_preferences(self, category: str = None) -> Dict[str, Any]:
        """Get all preferences (optionally filtered by category)"""
        if category:
            keys = self.category_index.get(category, [])
            return {
                key: self.preferences[f"{category}:{key}"].value
                for key in keys
                if f"{category}:{key}" in self.preferences
            }
        else:
            # Return all preferences organized by category
            result = {}
            for pref in self.preferences.values():
                if pref.category not in result:
                    result[pref.category] = {}
                result[pref.category][pref.key] = pref.value
            return result
    
    def get_preference(self, category: str, key: str) -> Optional[Any]:
        """Get a specific preference value"""
        pref_id = f"{category}:{key}"
        if pref_id in self.preferences:
            pref = self.preferences[pref_id]
            pref.access_count += 1
            return pref.value
        return None
    
    def set_preference(self, category: str, key: str, value: Any, confidence: float = 0.8):
        """Set a specific preference"""
        return self.store_preference(
            content={
                'category': category,
                'key': key,
                'value': value
            },
            importance=confidence
        )
    
    def search(self, query: str, limit: int = 10, min_relevance: float = 0.5) -> List[MemoryItem]:
        """Search preferences"""
        results = []
        query_lower = query.lower()
        
        for pref in self.preferences.values():
            relevance = 0.0
            
            if query_lower in pref.key.lower():
                relevance += 0.5
            if query_lower in pref.category.lower():
                relevance += 0.3
            if query_lower in str(pref.value).lower():
                relevance += 0.2
            
            if relevance >= min_relevance:
                memory_item = pref.to_memory_item()
                memory_item.importance = relevance
                results.append(memory_item)
        
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    def learn_from_behavior(self, behavior_data: Dict[str, Any]) -> int:
        """
        Learn preferences from observed behavior
        
        Args:
            behavior_data: Dict with behavior observations
            
        Returns: Number of preferences learned/updated
        """
        count = 0
        
        # Example: If user frequently asks brief questions, learn brief preference
        if 'response_length_preference' in behavior_data:
            avg_length = behavior_data['response_length_preference']
            if avg_length < 50:
                self.set_preference('interaction', 'response_length', 'brief', confidence=0.7)
                count += 1
            elif avg_length > 200:
                self.set_preference('interaction', 'response_length', 'detailed', confidence=0.7)
                count += 1
        
        # Example: Learn communication style
        if 'formality_level' in behavior_data:
            formality = behavior_data['formality_level']
            if formality > 0.7:
                self.set_preference('interaction', 'communication_style', 'formal', confidence=0.7)
                count += 1
            elif formality < 0.3:
                self.set_preference('interaction', 'communication_style', 'casual', confidence=0.7)
                count += 1
        
        # Example: Learn topic interests
        if 'frequent_topics' in behavior_data:
            topics = behavior_data['frequent_topics']
            for topic, frequency in topics.items():
                if frequency > 5:  # Mentioned more than 5 times
                    self.set_preference('content', f'interest_{topic}', True, confidence=0.6)
                    count += 1
        
        return count
    
    def get_high_confidence_preferences(self, min_confidence: float = 0.8) -> Dict[str, Any]:
        """Get preferences with high confidence"""
        result = {}
        for pref in self.preferences.values():
            if pref.confidence >= min_confidence:
                if pref.category not in result:
                    result[pref.category] = {}
                result[pref.category][pref.key] = {
                    'value': pref.value,
                    'confidence': pref.confidence,
                    'access_count': pref.access_count
                }
        return result
    
    def prune_low_confidence(self, min_confidence: float = 0.2, min_access: int = 1) -> int:
        """Remove low-confidence, rarely accessed preferences"""
        before_count = len(self.preferences)
        
        # Remove preferences with low confidence AND low access
        to_remove = [
            pref_id for pref_id, pref in self.preferences.items()
            if pref.confidence < min_confidence and pref.access_count < min_access
        ]
        
        for pref_id in to_remove:
            pref = self.preferences[pref_id]
            del self.preferences[pref_id]
            
            # Update category index
            if pref.category in self.category_index:
                if pref.key in self.category_index[pref.category]:
                    self.category_index[pref.category].remove(pref.key)
        
        after_count = len(self.preferences)
        return before_count - after_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get preference store statistics"""
        categories = list(self.category_index.keys())
        total_prefs = len(self.preferences)
        
        avg_confidence = sum(p.confidence for p in self.preferences.values()) / total_prefs if total_prefs > 0 else 0
        
        high_confidence_count = sum(1 for p in self.preferences.values() if p.confidence >= 0.8)
        
        most_accessed = sorted(
            self.preferences.values(),
            key=lambda p: p.access_count,
            reverse=True
        )[:5]
        
        return {
            'total_preferences': total_prefs,
            'categories': categories,
            'category_counts': {cat: len(keys) for cat, keys in self.category_index.items()},
            'average_confidence': avg_confidence,
            'high_confidence_count': high_confidence_count,
            'most_accessed': [
                {'category': p.category, 'key': p.key, 'access_count': p.access_count}
                for p in most_accessed
            ]
        }

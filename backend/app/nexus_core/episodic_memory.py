"""
Episodic Memory: Conversation History & Event Timeline

Stores conversation turns, user interactions, and temporal events.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .memory_store import MemoryItem, MemoryType
import uuid


@dataclass
class ConversationEvent:
    """Single conversation turn or event"""
    id: str
    timestamp: datetime
    user_input: str
    ai_response: str
    intent: str
    entities: List[Dict[str, str]]
    sentiment: float
    topic: str
    importance: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_memory_item(self) -> MemoryItem:
        """Convert to MemoryItem for storage"""
        content = {
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'intent': self.intent,
            'entities': self.entities,
            'sentiment': self.sentiment,
            'topic': self.topic
        }
        
        return MemoryItem(
            id=self.id,
            memory_type=MemoryType.EPISODIC,
            content=content,
            created_at=self.timestamp,
            accessed_at=datetime.now(),
            importance=self.importance,
            tags=[self.topic, self.intent],
            metadata=self.metadata
        )


class EpisodicMemory:
    """
    Episodic memory subsystem
    
    Stores conversation history with temporal context.
    Enables "remember when we talked about X?" queries.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.events: List[ConversationEvent] = []
        self.event_index: Dict[str, ConversationEvent] = {}
        
    def store_event(self, content: Any, importance: float = 0.5,
                   tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Store a conversation event"""
        event_id = str(uuid.uuid4())
        
        # Create event from content
        if isinstance(content, dict):
            event = ConversationEvent(
                id=event_id,
                timestamp=datetime.now(),
                user_input=content.get('user_input', ''),
                ai_response=content.get('ai_response', ''),
                intent=content.get('intent', 'unknown'),
                entities=content.get('entities', []),
                sentiment=content.get('sentiment', 0.0),
                topic=content.get('topic', 'general'),
                importance=importance,
                metadata=metadata or {}
            )
        else:
            # Simplified event from string
            event = ConversationEvent(
                id=event_id,
                timestamp=datetime.now(),
                user_input=str(content),
                ai_response='',
                intent='unknown',
                entities=[],
                sentiment=0.0,
                topic='general',
                importance=importance,
                metadata=metadata or {}
            )
        
        self.events.append(event)
        self.event_index[event_id] = event
        
        return event_id
    
    def search(self, query: str, limit: int = 10, min_relevance: float = 0.5) -> List[MemoryItem]:
        """Search episodic memory"""
        results = []
        query_lower = query.lower()
        
        for event in self.events:
            # Simple relevance scoring
            relevance = 0.0
            
            if query_lower in event.user_input.lower():
                relevance += 0.5
            if query_lower in event.ai_response.lower():
                relevance += 0.3
            if query_lower in event.topic.lower():
                relevance += 0.2
            
            if relevance >= min_relevance:
                memory_item = event.to_memory_item()
                memory_item.importance = relevance
                results.append(memory_item)
        
        # Sort by relevance
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    def recall_conversation(self, topic: str = None,
                          time_window_hours: int = 24,
                          limit: int = 10) -> List[ConversationEvent]:
        """Recall recent conversation about a topic"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        relevant_events = []
        for event in self.events:
            if event.timestamp < cutoff_time:
                continue
            
            if topic is None or topic.lower() in event.topic.lower():
                relevant_events.append(event)
        
        # Sort by timestamp (most recent first)
        relevant_events.sort(key=lambda x: x.timestamp, reverse=True)
        return relevant_events[:limit]
    
    def get_conversation_timeline(self, start_time: datetime = None,
                                 end_time: datetime = None) -> List[ConversationEvent]:
        """Get conversation timeline between two times"""
        if start_time is None:
            start_time = datetime.min
        if end_time is None:
            end_time = datetime.max
        
        timeline = [
            event for event in self.events
            if start_time <= event.timestamp <= end_time
        ]
        
        timeline.sort(key=lambda x: x.timestamp)
        return timeline
    
    def prune_old_memories(self, days: int = 90, min_importance: float = 0.3) -> int:
        """Prune old low-importance memories"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        before_count = len(self.events)
        
        self.events = [
            event for event in self.events
            if event.timestamp >= cutoff_time or event.importance >= min_importance
        ]
        
        # Rebuild index
        self.event_index = {event.id: event for event in self.events}
        
        after_count = len(self.events)
        return before_count - after_count

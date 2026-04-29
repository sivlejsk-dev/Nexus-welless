"""
Semantic Memory: Knowledge Graph with Entity Relationships

Stores facts, concepts, and relationships in a graph structure.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from .memory_store import MemoryItem, MemoryType
import uuid


@dataclass
class KnowledgeNode:
    """Node in the knowledge graph (entity or concept)"""
    id: str
    name: str
    node_type: str  # person, place, concept, event, etc.
    properties: Dict[str, Any]
    created_at: datetime
    importance: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.node_type,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'importance': self.importance
        }


@dataclass
class KnowledgeEdge:
    """Edge in the knowledge graph (relationship)"""
    id: str
    source_id: str
    target_id: str
    relationship_type: str  # is_a, part_of, related_to, causes, etc.
    properties: Dict[str, Any]
    created_at: datetime
    strength: float = 0.5  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source': self.source_id,
            'target': self.target_id,
            'type': self.relationship_type,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'strength': self.strength
        }


class SemanticMemory:
    """
    Semantic memory subsystem
    
    Stores knowledge as a graph of entities and relationships.
    Enables complex queries like "What do I know about X and its connections?"
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}
        self.node_edges: Dict[str, List[str]] = {}  # node_id -> list of edge_ids
        
    def store_knowledge(self, content: Any, importance: float = 0.5,
                       tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Store knowledge (creates nodes and edges)"""
        if isinstance(content, dict):
            # Store as node
            if 'entity' in content:
                return self._create_node(
                    name=content['entity'],
                    node_type=content.get('type', 'concept'),
                    properties=content.get('properties', {}),
                    importance=importance
                )
            # Store as edge
            elif 'source' in content and 'target' in content:
                return self._create_edge(
                    source_name=content['source'],
                    target_name=content['target'],
                    relationship_type=content.get('relationship', 'related_to'),
                    properties=content.get('properties', {}),
                    strength=importance
                )
        
        # Simple text-based knowledge
        node_id = self._create_node(
            name=str(content),
            node_type='fact',
            properties={'content': str(content)},
            importance=importance
        )
        return node_id
    
    def _create_node(self, name: str, node_type: str,
                    properties: Dict[str, Any], importance: float) -> str:
        """Create a knowledge node"""
        # Check if node exists
        for node_id, node in self.nodes.items():
            if node.name.lower() == name.lower():
                # Update existing node
                node.properties.update(properties)
                node.importance = max(node.importance, importance)
                return node_id
        
        # Create new node
        node_id = str(uuid.uuid4())
        node = KnowledgeNode(
            id=node_id,
            name=name,
            node_type=node_type,
            properties=properties,
            created_at=datetime.now(),
            importance=importance
        )
        
        self.nodes[node_id] = node
        self.node_edges[node_id] = []
        
        return node_id
    
    def _create_edge(self, source_name: str, target_name: str,
                    relationship_type: str, properties: Dict[str, Any],
                    strength: float) -> str:
        """Create a knowledge edge"""
        # Get or create source and target nodes
        source_id = self._create_node(source_name, 'entity', {}, 0.5)
        target_id = self._create_node(target_name, 'entity', {}, 0.5)
        
        # Create edge
        edge_id = str(uuid.uuid4())
        edge = KnowledgeEdge(
            id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            properties=properties,
            created_at=datetime.now(),
            strength=strength
        )
        
        self.edges[edge_id] = edge
        self.node_edges[source_id].append(edge_id)
        self.node_edges[target_id].append(edge_id)
        
        return edge_id
    
    def search(self, query: str, limit: int = 10, min_relevance: float = 0.5) -> List[MemoryItem]:
        """Search semantic memory"""
        results = []
        query_lower = query.lower()
        
        for node in self.nodes.values():
            relevance = 0.0
            
            if query_lower in node.name.lower():
                relevance += 0.7
            if any(query_lower in str(v).lower() for v in node.properties.values()):
                relevance += 0.3
            
            if relevance >= min_relevance:
                memory_item = MemoryItem(
                    id=node.id,
                    memory_type=MemoryType.SEMANTIC,
                    content=node.to_dict(),
                    created_at=node.created_at,
                    accessed_at=datetime.now(),
                    importance=node.importance,
                    tags=[node.node_type],
                    metadata={'type': 'node'}
                )
                memory_item.importance = relevance
                results.append(memory_item)
        
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    def get_knowledge(self, entity: str, relationship_type: str = None) -> Dict[str, Any]:
        """Get knowledge about an entity and its relationships"""
        # Find node
        node = None
        node_id = None
        for nid, n in self.nodes.items():
            if n.name.lower() == entity.lower():
                node = n
                node_id = nid
                break
        
        if node is None:
            return {'error': f'Entity "{entity}" not found'}
        
        # Get relationships
        relationships = []
        for edge_id in self.node_edges.get(node_id, []):
            edge = self.edges[edge_id]
            
            if relationship_type and edge.relationship_type != relationship_type:
                continue
            
            # Determine if this node is source or target
            if edge.source_id == node_id:
                related_node = self.nodes.get(edge.target_id)
                direction = 'outgoing'
            else:
                related_node = self.nodes.get(edge.source_id)
                direction = 'incoming'
            
            if related_node:
                relationships.append({
                    'type': edge.relationship_type,
                    'direction': direction,
                    'related_entity': related_node.name,
                    'strength': edge.strength,
                    'properties': edge.properties
                })
        
        return {
            'entity': node.name,
            'type': node.node_type,
            'properties': node.properties,
            'importance': node.importance,
            'relationships': relationships
        }
    
    def get_connected_entities(self, entity: str, max_depth: int = 2) -> Set[str]:
        """Get all entities connected to this entity (up to max_depth hops)"""
        # Find starting node
        start_node_id = None
        for node_id, node in self.nodes.items():
            if node.name.lower() == entity.lower():
                start_node_id = node_id
                break
        
        if start_node_id is None:
            return set()
        
        visited = set()
        to_visit = [(start_node_id, 0)]  # (node_id, depth)
        connected = set()
        
        while to_visit:
            current_id, depth = to_visit.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            
            # Add to connected set
            if current_id != start_node_id:
                node = self.nodes[current_id]
                connected.add(node.name)
            
            # Add neighbors
            if depth < max_depth:
                for edge_id in self.node_edges.get(current_id, []):
                    edge = self.edges[edge_id]
                    neighbor_id = edge.target_id if edge.source_id == current_id else edge.source_id
                    if neighbor_id not in visited:
                        to_visit.append((neighbor_id, depth + 1))
        
        return connected
    
    def prune_unused_knowledge(self, days: int = 180) -> int:
        """Prune old unused knowledge nodes"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        before_count = len(self.nodes)
        
        # Remove old low-importance nodes
        nodes_to_remove = [
            node_id for node_id, node in self.nodes.items()
            if node.created_at < cutoff_time and node.importance < 0.3
        ]
        
        for node_id in nodes_to_remove:
            # Remove associated edges
            for edge_id in self.node_edges.get(node_id, []):
                del self.edges[edge_id]
            
            # Remove node
            del self.nodes[node_id]
            del self.node_edges[node_id]
        
        after_count = len(self.nodes)
        return before_count - after_count

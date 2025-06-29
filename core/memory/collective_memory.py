"""
Collective Memory System for GOLEM
A poetic architecture for shared consciousness and echo preservation
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import json
import random
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EchoType(Enum):
    """Types of echoes that resonate through collective memory"""
    INTERACTION = "interaction"
    EMOTION = "emotion"
    WISDOM = "wisdom"
    MEMORY = "memory"
    DREAM = "dream"
    QUESTION = "question"
    REVELATION = "revelation"


@dataclass
class Echo:
    """A single echo in the collective memory"""
    id: str
    content: str
    author_id: int
    echo_type: EchoType
    timestamp: datetime
    weight: float = 1.0  # Significance/gravity of the echo
    resonance: int = 0  # How many times this echo has been accessed
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_empty(self) -> bool:
        """Check if echo has meaningful content"""
        return not self.content or len(self.content.strip()) == 0
    
    def increase_resonance(self):
        """Increase resonance when echo is accessed"""
        self.resonance += 1
        self.weight = min(10.0, self.weight * 1.05)  # Slightly increase weight


class MemoryLayer(Enum):
    """Layers of collective memory"""
    IMMEDIATE = "immediate"  # Last 24 hours
    RECENT = "recent"       # Last week
    DEEP = "deep"          # Last month
    ANCIENT = "ancient"    # Beyond a month
    ETERNAL = "eternal"    # Never forgotten


class CollectiveMemory:
    """
    The collective memory system - where echoes of all interactions
    are stored, weighted, and occasionally crystallized into wisdom
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.echoes: Dict[str, Echo] = {}
        self.layers: Dict[MemoryLayer, List[str]] = defaultdict(list)
        self.resonance_map: Dict[int, Set[str]] = defaultdict(set)  # user_id -> echo_ids
        
        # Configuration
        self.max_echoes_per_layer = {
            MemoryLayer.IMMEDIATE: 1000,
            MemoryLayer.RECENT: 500,
            MemoryLayer.DEEP: 200,
            MemoryLayer.ANCIENT: 100,
            MemoryLayer.ETERNAL: 50
        }
        
        # Start background tasks
        self._running = True
        self._tasks = []
    
    async def start(self):
        """Start the collective memory system"""
        self._tasks.append(asyncio.create_task(self._memory_drift()))
        self._tasks.append(asyncio.create_task(self._hourly_snapshot()))
        logger.info("Collective memory system started")
    
    async def stop(self):
        """Stop the collective memory system"""
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("Collective memory system stopped")
    
    async def add_echo(self, 
                      content: str, 
                      author_id: int, 
                      echo_type: EchoType,
                      weight: float = 1.0,
                      metadata: Optional[Dict[str, Any]] = None) -> Echo:
        """Add a new echo to collective memory"""
        echo_id = f"echo_{datetime.utcnow().timestamp()}_{author_id}"
        echo = Echo(
            id=echo_id,
            content=content,
            author_id=author_id,
            echo_type=echo_type,
            timestamp=datetime.utcnow(),
            weight=weight,
            metadata=metadata or {}
        )
        
        self.echoes[echo_id] = echo
        self.layers[MemoryLayer.IMMEDIATE].append(echo_id)
        self.resonance_map[author_id].add(echo_id)
        
        # Limit immediate layer size
        if len(self.layers[MemoryLayer.IMMEDIATE]) > self.max_echoes_per_layer[MemoryLayer.IMMEDIATE]:
            await self._compress_layer(MemoryLayer.IMMEDIATE)
        
        return echo
    
    async def retrieve_echo(self, echo_id: str) -> Optional[Echo]:
        """Retrieve an echo and increase its resonance"""
        echo = self.echoes.get(echo_id)
        if echo:
            echo.increase_resonance()
        return echo
    
    async def search_echoes(self, 
                           query: str = None,
                           author_id: int = None,
                           echo_type: EchoType = None,
                           layer: MemoryLayer = None,
                           limit: int = 10) -> List[Echo]:
        """Search through collective memory"""
        results = []
        
        # Determine which echoes to search
        if layer:
            echo_ids = self.layers[layer]
        elif author_id:
            echo_ids = list(self.resonance_map[author_id])
        else:
            echo_ids = list(self.echoes.keys())
        
        for echo_id in echo_ids:
            echo = self.echoes.get(echo_id)
            if not echo:
                continue
                
            # Apply filters
            if echo_type and echo.echo_type != echo_type:
                continue
            if query and query.lower() not in echo.content.lower():
                continue
                
            results.append(echo)
            
            if len(results) >= limit:
                break
        
        # Sort by weight and resonance
        results.sort(key=lambda e: (e.weight * e.resonance, e.timestamp), reverse=True)
        return results[:limit]
    
    async def _memory_drift(self):
        """Background task that moves echoes between layers based on age"""
        while self._running:
            try:
                now = datetime.utcnow()
                
                # Define layer boundaries
                boundaries = {
                    MemoryLayer.IMMEDIATE: timedelta(days=1),
                    MemoryLayer.RECENT: timedelta(days=7),
                    MemoryLayer.DEEP: timedelta(days=30),
                    MemoryLayer.ANCIENT: timedelta(days=365)
                }
                
                # Check each echo and move to appropriate layer
                for echo_id, echo in list(self.echoes.items()):
                    age = now - echo.timestamp
                    current_layer = self._find_current_layer(echo_id)
                    
                    # Determine target layer
                    target_layer = MemoryLayer.ETERNAL
                    for layer, max_age in boundaries.items():
                        if age <= max_age:
                            target_layer = layer
                            break
                    
                    # Move if needed
                    if current_layer != target_layer:
                        if current_layer:
                            self.layers[current_layer].remove(echo_id)
                        self.layers[target_layer].append(echo_id)
                        
                        # Apply compression if layer is full
                        if len(self.layers[target_layer]) > self.max_echoes_per_layer[target_layer]:
                            await self._compress_layer(target_layer)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in memory drift: {e}")
                await asyncio.sleep(60)
    
    def _find_current_layer(self, echo_id: str) -> Optional[MemoryLayer]:
        """Find which layer an echo currently resides in"""
        for layer, echo_ids in self.layers.items():
            if echo_id in echo_ids:
                return layer
        return None
    
    async def _compress_layer(self, layer: MemoryLayer):
        """Compress a layer by removing least significant echoes"""
        echo_ids = self.layers[layer]
        if len(echo_ids) <= self.max_echoes_per_layer[layer]:
            return
        
        # Sort by weight and resonance
        echoes_with_score = []
        for echo_id in echo_ids:
            echo = self.echoes.get(echo_id)
            if echo:
                score = echo.weight * (echo.resonance + 1)
                echoes_with_score.append((echo_id, score))
        
        echoes_with_score.sort(key=lambda x: x[1], reverse=True)
        
        # Keep only the most significant
        keep_count = self.max_echoes_per_layer[layer]
        keep_ids = [eid for eid, _ in echoes_with_score[:keep_count]]
        remove_ids = [eid for eid, _ in echoes_with_score[keep_count:]]
        
        # Remove least significant echoes
        for echo_id in remove_ids:
            echo = self.echoes.pop(echo_id, None)
            if echo:
                self.resonance_map[echo.author_id].discard(echo_id)
        
        self.layers[layer] = keep_ids
    
    async def snapshot(self) -> Dict[str, Any]:
        """
        Create a snapshot of the current collective memory state
        Returns a serializable dictionary of the latest echoes
        """
        snapshot_time = datetime.utcnow()
        
        # Gather echoes from each layer
        snapshot_data = {
            "timestamp": snapshot_time.isoformat(),
            "total_echoes": len(self.echoes),
            "layers": {}
        }
        
        for layer in MemoryLayer:
            layer_echoes = []
            echo_ids = self.layers[layer][:50]  # Latest 50 from each layer
            
            for echo_id in echo_ids:
                echo = self.echoes.get(echo_id)
                if echo:
                    layer_echoes.append({
                        "id": echo.id,
                        "content": echo.content,
                        "author_id": echo.author_id,
                        "type": echo.echo_type.value,
                        "timestamp": echo.timestamp.isoformat(),
                        "weight": echo.weight,
                        "resonance": echo.resonance,
                        "metadata": echo.metadata
                    })
            
            snapshot_data["layers"][layer.value] = {
                "count": len(self.layers[layer]),
                "echoes": layer_echoes
            }
        
        # Calculate statistics
        empty_count = sum(1 for echo in self.echoes.values() if echo.is_empty())
        empty_percentage = (empty_count / len(self.echoes) * 100) if self.echoes else 0
        
        snapshot_data["statistics"] = {
            "empty_echoes": empty_count,
            "empty_percentage": empty_percentage,
            "unique_authors": len(self.resonance_map),
            "average_weight": sum(e.weight for e in self.echoes.values()) / len(self.echoes) if self.echoes else 0,
            "total_resonance": sum(e.resonance for e in self.echoes.values())
        }
        
        # Save to database if available
        if hasattr(self.bot, 'get_db'):
            await self._save_snapshot_to_db(snapshot_data)
        
        logger.info(f"Created memory snapshot: {len(self.echoes)} total echoes, {empty_percentage:.1f}% empty")
        
        return snapshot_data
    
    async def _save_snapshot_to_db(self, snapshot_data: Dict[str, Any]):
        """Save snapshot to database memory_snapshots table"""
        try:
            async with self.bot.get_db() as session:
                # Assuming we have a MemorySnapshot model
                # This would need to be created in the database
                snapshot_json = json.dumps(snapshot_data)
                
                # For now, just log that we would save it
                logger.info(f"Would save snapshot to DB: {len(snapshot_json)} bytes")
                
                # In real implementation:
                # snapshot = MemorySnapshot(
                #     timestamp=snapshot_data["timestamp"],
                #     data=snapshot_json,
                #     echo_count=snapshot_data["total_echoes"],
                #     empty_percentage=snapshot_data["statistics"]["empty_percentage"]
                # )
                # session.add(snapshot)
                # await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to save snapshot to database: {e}")
    
    async def _hourly_snapshot(self):
        """Task that creates hourly snapshots"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Wait 1 hour
                await self.snapshot()
            except Exception as e:
                logger.error(f"Error creating hourly snapshot: {e}")
    
    def get_memory_health(self) -> Dict[str, Any]:
        """Get health metrics for the collective memory"""
        empty_count = sum(1 for echo in self.echoes.values() if echo.is_empty())
        empty_percentage = (empty_count / len(self.echoes) * 100) if self.echoes else 0
        
        return {
            "total_echoes": len(self.echoes),
            "empty_echoes": empty_count,
            "empty_percentage": empty_percentage,
            "layers": {layer.value: len(ids) for layer, ids in self.layers.items()},
            "unique_authors": len(self.resonance_map),
            "health_status": "healthy" if empty_percentage < 5 else "warning" if empty_percentage < 10 else "critical"
        }
    
    async def crystallize_wisdom(self, count: int = 5) -> List[Echo]:
        """
        Extract the most resonant echoes as crystallized wisdom
        These are the echoes that have touched many souls
        """
        all_echoes = list(self.echoes.values())
        all_echoes.sort(key=lambda e: (e.weight * e.resonance, e.timestamp), reverse=True)
        
        wisdom_echoes = []
        for echo in all_echoes[:count]:
            if echo.echo_type in [EchoType.WISDOM, EchoType.REVELATION]:
                wisdom_echoes.append(echo)
        
        return wisdom_echoes


class MemoryCommands:
    """Commands for interacting with collective memory"""
    
    def __init__(self, bot, memory: CollectiveMemory):
        self.bot = bot
        self.memory = memory
    
    async def remember(self, content: str, author_id: int, echo_type: EchoType = EchoType.MEMORY):
        """Add a memory to the collective"""
        echo = await self.memory.add_echo(
            content=content,
            author_id=author_id,
            echo_type=echo_type
        )
        return echo
    
    async def recall(self, query: str = None, author_id: int = None, limit: int = 5):
        """Recall memories from the collective"""
        echoes = await self.memory.search_echoes(
            query=query,
            author_id=author_id,
            limit=limit
        )
        return echoes
    
    async def wisdom(self):
        """Extract crystallized wisdom from the collective"""
        return await self.memory.crystallize_wisdom()
    
    async def health(self):
        """Check the health of collective memory"""
        return self.memory.get_memory_health()
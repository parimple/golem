"""
Integration tests for CollectiveMemory system
Tests snapshot functionality and echo preservation
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.memory.collective_memory import (
    CollectiveMemory, Echo, EchoType, MemoryLayer
)


class TestCollectiveMemory:
    """Test suite for collective memory system"""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance"""
        bot = MagicMock()
        bot.get_db = AsyncMock()
        return bot
    
    @pytest.fixture
    def memory_system(self, mock_bot):
        """Create a collective memory instance"""
        memory = CollectiveMemory(mock_bot)
        return memory
    
    @pytest.mark.asyncio
    async def test_add_echo(self, memory_system):
        """Test adding an echo to collective memory"""
        echo = await memory_system.add_echo(
            content="The stars remember everything",
            author_id=123456,
            echo_type=EchoType.WISDOM,
            weight=2.5
        )
        
        assert echo.id.startswith("echo_")
        assert echo.content == "The stars remember everything"
        assert echo.author_id == 123456
        assert echo.echo_type == EchoType.WISDOM
        assert echo.weight == 2.5
        assert echo.resonance == 0
        assert not echo.is_empty()
    
    @pytest.mark.asyncio
    async def test_empty_echo_detection(self, memory_system):
        """Test detection of empty echoes"""
        empty_echo = await memory_system.add_echo(
            content="   ",  # Only whitespace
            author_id=123456,
            echo_type=EchoType.MEMORY
        )
        
        assert empty_echo.is_empty()
        
        valid_echo = await memory_system.add_echo(
            content="This has content",
            author_id=123456,
            echo_type=EchoType.MEMORY
        )
        
        assert not valid_echo.is_empty()
    
    @pytest.mark.asyncio
    async def test_echo_resonance(self, memory_system):
        """Test echo resonance increases on retrieval"""
        echo = await memory_system.add_echo(
            content="A whisper in the void",
            author_id=123456,
            echo_type=EchoType.QUESTION
        )
        
        # Initial state
        assert echo.resonance == 0
        assert echo.weight == 1.0
        
        # Retrieve echo multiple times
        for i in range(3):
            retrieved = await memory_system.retrieve_echo(echo.id)
            assert retrieved is not None
        
        # Check resonance increased
        assert echo.resonance == 3
        assert echo.weight > 1.0  # Weight should have increased
    
    @pytest.mark.asyncio
    async def test_search_echoes(self, memory_system):
        """Test searching through collective memory"""
        # Add various echoes
        await memory_system.add_echo("The moon guides us", 111, EchoType.WISDOM)
        await memory_system.add_echo("Stars shine bright", 222, EchoType.WISDOM)
        await memory_system.add_echo("What is the meaning?", 333, EchoType.QUESTION)
        await memory_system.add_echo("I remember the sun", 111, EchoType.MEMORY)
        
        # Search by query
        moon_echoes = await memory_system.search_echoes(query="moon")
        assert len(moon_echoes) == 1
        assert "moon" in moon_echoes[0].content.lower()
        
        # Search by author
        author_echoes = await memory_system.search_echoes(author_id=111)
        assert len(author_echoes) == 2
        assert all(e.author_id == 111 for e in author_echoes)
        
        # Search by type
        wisdom_echoes = await memory_system.search_echoes(echo_type=EchoType.WISDOM)
        assert len(wisdom_echoes) == 2
        assert all(e.echo_type == EchoType.WISDOM for e in wisdom_echoes)
    
    @pytest.mark.asyncio
    async def test_snapshot_creation(self, memory_system):
        """Test creating a snapshot of collective memory"""
        # Add test data
        echoes_data = [
            ("Memory of dawn", 111, EchoType.MEMORY, 1.0),
            ("Question about existence", 222, EchoType.QUESTION, 1.5),
            ("", 333, EchoType.MEMORY, 1.0),  # Empty echo
            ("   ", 444, EchoType.DREAM, 1.0),  # Empty echo
            ("Wisdom of ages", 555, EchoType.WISDOM, 3.0),
        ]
        
        for content, author_id, echo_type, weight in echoes_data:
            await memory_system.add_echo(content, author_id, echo_type, weight)
        
        # Create snapshot
        snapshot = await memory_system.snapshot()
        
        # Verify snapshot structure
        assert "timestamp" in snapshot
        assert "total_echoes" in snapshot
        assert "layers" in snapshot
        assert "statistics" in snapshot
        
        # Verify statistics
        stats = snapshot["statistics"]
        assert stats["empty_echoes"] == 2  # Two empty echoes
        assert stats["empty_percentage"] == 40.0  # 2/5 = 40%
        assert stats["unique_authors"] == 5
        assert stats["total_resonance"] == 0  # No echoes retrieved yet
        
        # Verify layer data
        immediate_layer = snapshot["layers"][MemoryLayer.IMMEDIATE.value]
        assert immediate_layer["count"] == 5
        assert len(immediate_layer["echoes"]) == 5
        
        # Verify echo data in snapshot
        first_echo = immediate_layer["echoes"][0]
        assert "id" in first_echo
        assert "content" in first_echo
        assert "author_id" in first_echo
        assert "weight" in first_echo
        assert "resonance" in first_echo
    
    @pytest.mark.asyncio
    async def test_snapshot_database_save(self, memory_system, mock_bot):
        """Test that snapshot attempts to save to database"""
        # Add some echoes
        await memory_system.add_echo("Test echo", 123, EchoType.MEMORY)
        
        # Mock database session
        mock_session = AsyncMock()
        mock_bot.get_db.return_value.__aenter__.return_value = mock_session
        
        # Create snapshot
        with patch('core.memory.collective_memory.logger') as mock_logger:
            snapshot = await memory_system.snapshot()
            
            # Verify database interaction was attempted
            mock_bot.get_db.assert_called_once()
            
            # Verify logging
            mock_logger.info.assert_any_call(
                f"Created memory snapshot: 1 total echoes, 0.0% empty"
            )
    
    @pytest.mark.asyncio
    async def test_memory_health(self, memory_system):
        """Test memory health metrics"""
        # Add mix of empty and valid echoes
        await memory_system.add_echo("Valid content", 111, EchoType.MEMORY)
        await memory_system.add_echo("", 222, EchoType.MEMORY)
        await memory_system.add_echo("Another valid", 333, EchoType.WISDOM)
        await memory_system.add_echo("   ", 444, EchoType.DREAM)
        
        health = memory_system.get_memory_health()
        
        assert health["total_echoes"] == 4
        assert health["empty_echoes"] == 2
        assert health["empty_percentage"] == 50.0
        assert health["unique_authors"] == 4
        assert health["health_status"] == "critical"  # >10% empty
    
    @pytest.mark.asyncio
    async def test_crystallize_wisdom(self, memory_system):
        """Test extracting crystallized wisdom"""
        # Add echoes with different resonance
        wisdom1 = await memory_system.add_echo(
            "Ancient wisdom", 111, EchoType.WISDOM, weight=3.0
        )
        wisdom2 = await memory_system.add_echo(
            "Profound revelation", 222, EchoType.REVELATION, weight=2.5
        )
        memory1 = await memory_system.add_echo(
            "Simple memory", 333, EchoType.MEMORY, weight=1.0
        )
        
        # Increase resonance of wisdom1
        for _ in range(5):
            await memory_system.retrieve_echo(wisdom1.id)
        
        # Get crystallized wisdom
        wisdom = await memory_system.crystallize_wisdom(count=2)
        
        # Should prioritize wisdom/revelation types with high resonance
        assert len(wisdom) <= 2
        assert all(e.echo_type in [EchoType.WISDOM, EchoType.REVELATION] for e in wisdom)
        if wisdom:
            assert wisdom[0].id == wisdom1.id  # Should be first due to high resonance
    
    @pytest.mark.asyncio
    async def test_memory_layer_organization(self, memory_system):
        """Test that echoes are organized into layers"""
        # Add echo
        echo = await memory_system.add_echo(
            "Fresh memory", 123, EchoType.MEMORY
        )
        
        # Should be in immediate layer
        assert echo.id in memory_system.layers[MemoryLayer.IMMEDIATE]
        assert echo.id not in memory_system.layers[MemoryLayer.RECENT]
        
        # Check layer finding
        current_layer = memory_system._find_current_layer(echo.id)
        assert current_layer == MemoryLayer.IMMEDIATE
    
    @pytest.mark.asyncio
    async def test_hourly_snapshot_warning(self, memory_system):
        """Test that empty echo percentage triggers warning"""
        # Add mostly empty echoes (>5% threshold)
        for i in range(20):
            if i < 18:  # 90% will be empty
                content = "   "
            else:
                content = f"Valid content {i}"
            await memory_system.add_echo(content, i, EchoType.MEMORY)
        
        snapshot = await memory_system.snapshot()
        
        # Check statistics
        stats = snapshot["statistics"]
        assert stats["empty_percentage"] == 90.0
        
        # Health should be critical
        health = memory_system.get_memory_health()
        assert health["health_status"] == "critical"
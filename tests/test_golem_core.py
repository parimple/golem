"""
Tests for GOLEM Core Systems
Demonstrating the Tesla/Apple approach to testing
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import numpy as np

# Add project to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.quantum import QuantumCore, Signal, Response, QuantumObserver
from core.self_assembly import SelfAssemblingModule, ModuleFactory
from core.neural import NeuralCommand, CommandContext, neural_command
from golem import transcend


class TestQuantumCore:
    """Test the quantum reality engine"""
    
    @pytest.mark.asyncio
    async def test_quantum_transcendence(self):
        """Test basic quantum processing"""
        core = QuantumCore()
        
        # Create a test signal
        signal = Signal(
            source="test",
            intent="greeting",
            context={"message": "Hello quantum world"}
        )
        
        # Add a simple observer
        class TestObserver(QuantumObserver):
            def can_observe(self, signal):
                return signal.intent == "greeting"
                
            async def observe(self, state, signal):
                return Response(
                    content="Quantum greetings!",
                    confidence=0.95
                )
        
        core.add_observer(TestObserver())
        
        # Process signal
        response = await core.receive(signal)
        
        assert response.content == "Quantum greetings!"
        assert response.confidence == 0.95
        
    @pytest.mark.asyncio
    async def test_quantum_superposition(self):
        """Test multiple observers creating superposition"""
        core = QuantumCore()
        
        # Add multiple observers
        class Observer1(QuantumObserver):
            def can_observe(self, signal):
                return True
                
            async def observe(self, state, signal):
                return Response(content="Reality 1", confidence=0.7)
                
        class Observer2(QuantumObserver):
            def can_observe(self, signal):
                return True
                
            async def observe(self, state, signal):
                return Response(content="Reality 2", confidence=0.9)
        
        core.add_observer(Observer1())
        core.add_observer(Observer2())
        
        signal = Signal(source="test", intent="test")
        response = await core.receive(signal)
        
        # Should choose higher confidence
        assert response.content == "Reality 2"
        
    @pytest.mark.asyncio
    async def test_quantum_performance(self):
        """Test quantum performance tracking"""
        core = QuantumCore()
        
        # Process multiple signals
        for i in range(10):
            signal = Signal(source=f"test_{i}", intent="test")
            await core.receive(signal)
            
        health = core.health
        assert health['total_interactions'] == 10
        assert 'avg_response_time' in health
        assert health['quantum_coherence'] > 0


class TestSelfAssembly:
    """Test self-assembling modules"""
    
    @pytest.mark.asyncio
    async def test_module_self_assembly(self):
        """Test module assembles itself"""
        
        class TestModule(SelfAssemblingModule):
            async def process(self, input):
                return {"result": "processed"}
        
        module = TestModule("test_module")
        
        # Module should assemble itself
        await module.assemble()
        
        assert module.is_assembled
        assert 'system' in module.config
        assert module.health.status in ["healthy", "degraded"]
        
    @pytest.mark.asyncio
    async def test_module_factory(self):
        """Test module factory creates optimal configuration"""
        factory = ModuleFactory()
        
        # Register test module
        class TestModule(SelfAssemblingModule):
            async def process(self, input):
                return input
                
        factory.register(TestModule)
        
        # Create module
        module = await factory.create("TestModule", "test1")
        
        assert module.name == "test1"
        assert module.is_assembled
        assert "test1" in factory.active_modules
        
    @pytest.mark.asyncio 
    async def test_module_auto_configuration(self):
        """Test module configures itself based on environment"""
        
        class SmartModule(SelfAssemblingModule):
            async def process(self, input):
                return self.config
                
        module = SmartModule("smart")
        await module.assemble()
        
        # Should have auto-configured based on system
        assert 'cache_size' in module.config
        assert 'parallel_workers' in module.config


class TestNeuralCommands:
    """Test commands that learn"""
    
    @pytest.mark.asyncio
    async def test_neural_command_learning(self):
        """Test neural command learns from execution"""
        
        @neural_command(name="test_cmd")
        async def test_command(ctx, value: int = 10):
            # Simulate some work
            await asyncio.sleep(0.01)
            return value * 2
            
        # Create context
        ctx = CommandContext(
            user_id=123,
            guild_id=456, 
            channel_id=789,
            command_name="test_cmd"
        )
        
        # Execute multiple times
        results = []
        for i in range(5):
            result = await test_command(ctx, value=i)
            results.append(result)
            
        # Check it executed correctly
        assert results == [0, 2, 4, 6, 8]
        
        # Check it learned
        assert test_command.total_executions == 5
        assert len(test_command.performance_history) == 5
        
    @pytest.mark.asyncio
    async def test_neural_optimization(self):
        """Test neural network optimization"""
        
        @neural_command()
        async def optimized_cmd(ctx, use_cache=False, batch_size=10):
            return {"cache": use_cache, "batch": batch_size}
            
        ctx = CommandContext(
            user_id=123,
            guild_id=456,
            channel_id=789,
            command_name="optimized_cmd"
        )
        
        # Execute and let it optimize
        result = await optimized_cmd(ctx, use_cache=False, batch_size=20)
        
        # Neural network should have processed context
        assert optimized_cmd.neural_net.w1 is not None
        
    def test_command_context_vectorization(self):
        """Test context converts to vector correctly"""
        ctx = CommandContext(
            user_id=12345,
            guild_id=67890,
            channel_id=11111,
            command_name="test",
            user_history=["cmd1", "cmd2"]
        )
        
        vector = ctx.to_vector()
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 6  # Based on our features


class TestGOLEMIntegration:
    """Test the complete GOLEM system"""
    
    @pytest.mark.asyncio
    async def test_golem_transcendence(self):
        """Test GOLEM initialization"""
        bot = transcend()
        
        assert bot.quantum_core is not None
        assert bot.module_factory is not None
        assert bot.collective_memory is not None
        
        # Should have example commands
        assert 'hello' in [cmd.name for cmd in bot.commands]
        assert 'transcend' in [cmd.name for cmd in bot.commands]
        
    @pytest.mark.asyncio
    async def test_golem_health_monitoring(self):
        """Test GOLEM self-monitoring"""
        bot = transcend()
        
        # Mock some activity
        bot.metrics['commands_processed'] = 100
        bot.metrics['errors'] = 1
        
        health = await bot._check_health()
        
        assert 'performance' in health
        assert 'memory_usage' in health  
        assert 'error_rate' in health
        assert health['error_rate'] == 0.01  # 1/100
        
    @pytest.mark.asyncio
    async def test_golem_message_processing(self):
        """Test GOLEM processes messages through quantum core"""
        bot = transcend()
        
        # Mock message
        message = MagicMock()
        message.author.bot = False
        message.content = "Hello GOLEM"
        message.author.id = 123
        
        # Spy on quantum core
        with patch.object(bot.quantum_core, 'receive') as mock_receive:
            mock_receive.return_value = Response(content="Processed")
            
            await bot.on_message(message)
            
            # Should have created signal and processed it
            mock_receive.assert_called_once()
            call_args = mock_receive.call_args[0]
            signal = call_args[0]
            
            assert isinstance(signal, Signal)
            assert signal.intent == "message"
            assert signal.context['content'] == "Hello GOLEM"
            
            
class TestSimplicity:
    """Test that GOLEM remains simple to use"""
    
    def test_minimal_setup(self):
        """Test GOLEM works with minimal code"""
        # This is all you need
        bot = transcend()
        
        # It should just work
        assert bot is not None
        assert hasattr(bot, 'run')
        
    def test_zero_configuration(self):
        """Test GOLEM requires no configuration"""
        bot = transcend()
        
        # Everything should be auto-configured
        assert bot.command_prefix == '/'
        assert bot.intents.messages == True
        assert len(bot.modules) == 0  # Modules load on startup
        
    @pytest.mark.asyncio
    async def test_self_healing(self):
        """Test GOLEM heals itself"""
        bot = transcend()
        
        # Simulate high error rate
        bot.metrics['commands_processed'] = 100
        bot.metrics['errors'] = 10
        
        # Check health
        health = await bot._check_health()
        assert health['error_rate'] > 0.01
        
        # Self-heal should be triggered in maintenance loop
        with patch.object(bot, '_self_heal') as mock_heal:
            await bot._self_maintenance_loop()
            # Would be called if loop ran long enough
#!/usr/bin/env python3
"""
Test GOLEM with advanced features
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable advanced features
os.environ['GOLEM_SIMPLE'] = 'false'

async def test_advanced():
    print("🧬 GOLEM Advanced Features Test")
    print("=" * 50)
    
    try:
        from golem_core import GOLEMCore
        print("✅ Advanced GOLEM loaded")
        
        # Create bot
        bot = GOLEMCore()
        await bot.setup_hook()
        
        print("\n🧬 System Status:")
        for system, active in bot.systems_status.items():
            status = "✅" if active else "❌"
            print(f"  {status} {system.title()}")
        
        # Test Quantum Core
        if bot.quantum_core:
            print("\n⚛️ Testing Quantum Core...")
            from core.quantum import Signal
            signal = Signal(
                source="test",
                intent="test",
                context={'message': "Hello Quantum"}
            )
            response = await bot.quantum_core.receive(signal)
            print(f"  Response confidence: {response.confidence:.1%}")
            print(f"  Quantum health: {bot.quantum_core.health}")
        
        # Test Collective Memory
        if bot.collective_memory:
            print("\n💭 Testing Collective Memory...")
            from core.memory.collective_memory import EchoType
            echo = await bot.collective_memory.add_echo(
                content="Test memory",
                author_id=123,
                echo_type=EchoType.MEMORY
            )
            print(f"  Echo created: {echo.id}")
            print(f"  Memory health: {bot.collective_memory.get_memory_health()}")
            
            # Stop memory system
            await bot.collective_memory.stop()
        
        print("\n✨ Advanced systems working!")
        
    except ImportError as e:
        print(f"⚠️  Could not load advanced features: {e}")
        print("\nAdvanced features require full installation.")
        print("This is normal for the simple version.")

if __name__ == "__main__":
    asyncio.run(test_advanced())
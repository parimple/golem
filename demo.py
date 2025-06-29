#!/usr/bin/env python3
"""
GOLEM Demo - Shows bot functionality without Discord connection
"""
import asyncio
import sys
import os
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import GOLEM
from golem_simple import GOLEM


class DemoContext:
    """Mock context for demo"""
    def __init__(self, author_name="Demo User", channel_name="demo-channel"):
        self.author = type('obj', (object,), {
            'name': author_name,
            'mention': f"@{author_name}",
            'id': 123456789
        })
        self.channel = type('obj', (object,), {
            'name': channel_name
        })
        self.message = type('obj', (object,), {
            'content': ""
        })
        
    async def send(self, content=None, embed=None):
        """Mock send method"""
        if embed:
            print(f"\n📨 Bot Response (Embed):")
            print(f"   Title: {embed.title}")
            if embed.description:
                print(f"   Description: {embed.description}")
            for field in embed.fields:
                print(f"   {field.name}: {field.value}")
            if embed.footer:
                print(f"   Footer: {embed.footer.text}")
        else:
            print(f"\n📨 Bot Response: {content}")


async def demo_commands():
    """Demonstrate bot commands"""
    print("🚀 GOLEM Demo Mode")
    print("==================")
    print("This shows how the bot works without Discord connection\n")
    
    # Create bot instance
    bot = GOLEM()
    
    # Add commands
    bot.add_commands()
    
    # Simulate bot being ready
    bot._user = type('obj', (object,), {'name': 'GOLEM Bot'})
    bot._connection = type('obj', (object,), {
        '_guilds': {
            1: type('obj', (object,), {'member_count': 100}),
            2: type('obj', (object,), {'member_count': 250})
        },
        'latency': 0.045
    })
    bot.start_time = datetime.utcnow()
    
    print(f"✅ Bot initialized as: GOLEM Bot")
    print(f"📡 Simulating 2 servers with 350 total users\n")
    
    # Demo each command
    demos = [
        ("help", "Show help menu"),
        ("ping", "Check latency"),
        ("status", "Show bot status"),
        ("hello", "Simple greeting"),
        ("hello GOLEM", "Greeting with name")
    ]
    
    for demo_cmd, description in demos:
        print(f"\n🔹 Testing /{demo_cmd} - {description}")
        print(f"   User input: /{demo_cmd}")
        
        # Parse command
        parts = demo_cmd.split()
        cmd_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Find command
        command = bot.get_command(cmd_name)
        if command:
            # Create mock context
            ctx = DemoContext()
            
            # Execute command
            try:
                if args:
                    await command(ctx, *args)
                else:
                    await command(ctx)
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"   ❌ Command not found: {cmd_name}")
            
        await asyncio.sleep(0.5)  # Small delay for readability
    
    print("\n" + "="*50)
    print("✨ Demo complete!")
    print("\nTo run the real bot:")
    print("1. Add your Discord bot token to .env file")
    print("2. Run: python run.py")
    print("\nTo create a Discord bot:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Create New Application")
    print("3. Go to Bot section")
    print("4. Create a Bot and copy the token")
    print("5. Add the token to .env file")


async def test_advanced_features():
    """Test advanced features if available"""
    print("\n\n🧬 Testing Advanced Features")
    print("============================\n")
    
    # Try to import advanced features
    try:
        from golem_core import GOLEMCore
        bot = GOLEMCore()
        await bot.setup_hook()
        
        print("✅ Advanced systems available:")
        for system, active in bot.systems_status.items():
            status = "✅" if active else "❌"
            print(f"   {status} {system.title()}")
            
        # Test quantum system if available
        if bot.systems_status.get('quantum'):
            print("\n🔹 Testing Quantum Core:")
            from core.quantum import Signal
            signal = Signal(
                source="test",
                intent="greeting", 
                context={'content': "Hello Quantum World"}
            )
            response = await bot.quantum_core.receive(signal)
            print(f"   Quantum Response: {response.content}")
            print(f"   Confidence: {response.confidence:.1%}")
            
        # Test memory system if available
        if bot.systems_status.get('memory'):
            print("\n🔹 Testing Collective Memory:")
            from core.memory.collective_memory import EchoType
            echo = await bot.collective_memory.add_echo(
                content="Demo memory echo",
                author_id=123,
                echo_type=EchoType.MEMORY
            )
            print(f"   Memory stored: {echo.id}")
            
            # Search memory
            echoes = await bot.collective_memory.search_echoes(query="Demo")
            print(f"   Found {len(echoes)} matching echoes")
            
        # Cleanup
        if bot.collective_memory:
            await bot.collective_memory.stop()
            
    except ImportError as e:
        print(f"⚠️  Advanced features not available: {e}")
        print("   Run with GOLEM_SIMPLE=false to enable advanced features")


async def main():
    """Run demo"""
    await demo_commands()
    
    # Test advanced features if user wants
    print("\n" + "="*50)
    response = input("\nTest advanced features? (y/n): ").lower()
    if response == 'y':
        await test_advanced_features()
    
    print("\n🌟 Thanks for trying GOLEM!")


if __name__ == "__main__":
    asyncio.run(main())
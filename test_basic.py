"""
Basic tests for GOLEM bot
"""
import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golem_simple import GOLEM, transcend


def test_bot_creation():
    """Test if bot can be created"""
    bot = transcend()
    assert bot is not None
    assert isinstance(bot, GOLEM)
    print("✅ Bot creation successful")


def test_commands_exist():
    """Test if basic commands are registered"""
    bot = transcend()
    
    # Add commands (normally done in setup_hook)
    bot.add_commands()
    
    command_names = [cmd.name for cmd in bot.commands]
    
    assert 'help' in command_names
    assert 'ping' in command_names
    assert 'status' in command_names
    assert 'hello' in command_names
    
    print("✅ All basic commands registered")


async def test_bot_initialization():
    """Test bot initialization"""
    bot = transcend()
    
    # Simulate setup hook
    await bot.setup_hook()
    
    print("✅ Bot initialization successful")


def main():
    """Run all tests"""
    print("🧪 Running GOLEM basic tests...")
    
    # Test 1: Creation
    test_bot_creation()
    
    # Test 2: Commands
    test_commands_exist()
    
    # Test 3: Initialization
    asyncio.run(test_bot_initialization())
    
    print("\n✨ All tests passed! GOLEM is ready to run.")
    print("\nNext steps:")
    print("1. Copy .env.example to .env")
    print("2. Add your Discord bot token")
    print("3. Run: python run.py")


if __name__ == "__main__":
    main()
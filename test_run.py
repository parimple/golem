#!/usr/bin/env python3
"""
Test run GOLEM without Discord connection
Shows initialization and readiness
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golem_simple import GOLEM

async def test_run():
    print("🚀 GOLEM Test Run (without Discord)")
    print("=" * 50)
    
    # Create bot instance
    bot = GOLEM()
    print("✅ Bot instance created")
    
    # Run setup hook
    await bot.setup_hook()
    print("✅ Setup complete")
    
    # Show commands
    print("\n📝 Registered commands:")
    for command in bot.commands:
        print(f"  /{command.name} - {command.help or 'No description'}")
    
    print("\n🧬 Bot Configuration:")
    print(f"  Prefix: {bot.command_prefix}")
    print(f"  Commands: {len(bot.commands)}")
    
    print("\n✨ GOLEM is ready!")
    print("\nTo connect to Discord:")
    print("1. Add DISCORD_TOKEN to .env")
    print("2. Run: python run.py")
    
    # Test a command locally
    print("\n" + "-" * 50)
    print("Testing command execution locally...")
    
    # Mock context
    class MockContext:
        class Author:
            name = "Test User"
            mention = "@Test User"
            
        author = Author()
        
        async def send(self, content=None, embed=None):
            if embed:
                print(f"\nBot would send embed:")
                print(f"  Title: {embed.title}")
                print(f"  Description: {embed.description}")
            else:
                print(f"\nBot would send: {content}")
    
    # Test help command
    ctx = MockContext()
    help_cmd = bot.get_command('help')
    if help_cmd:
        print("\nExecuting /help command...")
        await help_cmd(ctx)

if __name__ == "__main__":
    asyncio.run(test_run())
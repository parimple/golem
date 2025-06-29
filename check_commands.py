#!/usr/bin/env python3
"""
Check available GOLEM commands
"""
import asyncio
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golem_simple import GOLEM


async def check_commands():
    """List all available commands"""
    print("🔍 Checking GOLEM Commands")
    print("=" * 60)
    
    # Create bot instance
    bot = GOLEM()
    
    # Load cogs
    await bot.setup_hook()
    
    # Group commands by cog
    commands_by_cog = defaultdict(list)
    
    for command in bot.commands:
        cog_name = command.cog.__class__.__name__ if command.cog else "Core"
        commands_by_cog[cog_name].append(command)
    
    # Display commands
    total_commands = 0
    
    for cog_name, commands in sorted(commands_by_cog.items()):
        print(f"\n📦 {cog_name}")
        print("-" * 40)
        
        for cmd in sorted(commands, key=lambda x: x.name):
            aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            print(f"  ,{cmd.name}{aliases}")
            if cmd.help:
                print(f"    → {cmd.help}")
            total_commands += 1
    
    print(f"\n✅ Total commands: {total_commands}")
    print(f"✅ Total cogs: {len(bot.cogs)}")
    
    # Check specific features
    print("\n🔧 Feature Check:")
    print("-" * 40)
    
    features = {
        "Economy": ["balance", "daily", "pay"],
        "Activity": ["level", "leaderboard"],
        "Moderation": ["kick", "ban", "mute"],
        "Voice": ["voice"],
        "Premium": ["premium", "mypremium"],
        "Fun": ["coinflip", "8ball", "roll"],
        "Monitoring": ["performance", "health"]
    }
    
    for feature, commands in features.items():
        available = [cmd for cmd in commands if bot.get_command(cmd)]
        status = "✅" if len(available) == len(commands) else "⚠️"
        print(f"{status} {feature}: {len(available)}/{len(commands)} commands")
    
    await bot.close()


if __name__ == "__main__":
    asyncio.run(check_commands())
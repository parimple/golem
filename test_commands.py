#!/usr/bin/env python3
"""
Test GOLEM commands locally
"""
import asyncio
import discord
from discord.ext import commands
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golem_simple import GOLEM


class MockContext:
    """Mock context for testing commands"""
    def __init__(self, bot, author=None, channel=None):
        self.bot = bot
        self.author = author or MockUser()
        self.channel = channel or MockChannel()
        self.guild = MockGuild()
        self.message = MockMessage()
        self.command = None
        self.invoked_with = None
        self.prefix = ","
        self.sent_messages = []
        
    async def send(self, content=None, *, embed=None, **kwargs):
        """Mock send method"""
        msg_data = {
            'content': content,
            'embed': embed,
            'kwargs': kwargs
        }
        self.sent_messages.append(msg_data)
        
        if embed:
            print(f"\n📨 Embed: {embed.title}")
            if embed.description:
                print(f"   {embed.description}")
            for field in embed.fields:
                print(f"   {field.name}: {field.value}")
        else:
            print(f"\n💬 {content}")
        
        return MockMessage()
    
    async def reply(self, content=None, *, embed=None, **kwargs):
        """Mock reply method"""
        return await self.send(content, embed=embed, **kwargs)
    
    async def defer(self):
        """Mock defer method"""
        print("⏳ Deferring response...")


class MockUser:
    """Mock user object"""
    def __init__(self, id=123456789, name="TestUser"):
        self.id = id
        self.name = name
        self.display_name = name
        self.mention = f"<@{id}>"
        self.bot = False
        self.display_avatar = MockAvatar()
        self.top_role = MockRole(position=10)
        
    def __str__(self):
        return self.name


class MockMember(MockUser):
    """Mock member object"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles = [MockRole(name="Member")]
        self.voice = None
        self.guild = MockGuild()
        self.color = discord.Color.blue()


class MockAvatar:
    """Mock avatar object"""
    @property
    def url(self):
        return "https://example.com/avatar.png"


class MockChannel:
    """Mock channel object"""
    def __init__(self):
        self.id = 987654321
        self.name = "test-channel"
        self.mention = f"<#{self.id}>"
        
    async def send(self, *args, **kwargs):
        print(f"Channel message: {args[0] if args else 'embed'}")


class MockGuild:
    """Mock guild object"""
    def __init__(self):
        self.id = 111222333
        self.name = "Test Guild"
        self.member_count = 100
        self.members = []
        self.voice_channels = []
        self.afk_channel = None


class MockMessage:
    """Mock message object"""
    def __init__(self):
        self.id = 555666777
        self.content = "test message"
        self.author = MockUser()
        
    async def delete(self):
        print("Message deleted")


class MockRole:
    """Mock role object"""
    def __init__(self, name="TestRole", position=1):
        self.name = name
        self.position = position
        
    def __ge__(self, other):
        return self.position >= other.position


async def test_commands():
    """Test various GOLEM commands"""
    print("🧪 Testing GOLEM Commands")
    print("=" * 50)
    
    # Create bot instance
    bot = GOLEM()
    
    # Wait for cogs to load
    await bot.setup_hook()
    
    # Mock some bot properties
    bot._connection = type('obj', (object,), {
        'latency': 0.05,
        '_get_websocket': lambda x: type('obj', (object,), {'latency': 0.05})()
    })()
    
    # Create test context
    ctx = MockContext(bot)
    test_member = MockMember(id=987654321, name="OtherUser")
    
    # Test basic commands
    print("\n📌 Testing Basic Commands:")
    print("-" * 30)
    
    # Help command
    if help_cmd := bot.get_command('help'):
        await help_cmd(ctx)
    
    # Ping command
    if ping_cmd := bot.get_command('ping'):
        await ping_cmd(ctx)
    
    # Status command
    if status_cmd := bot.get_command('status'):
        await status_cmd(ctx)
    
    # Hello command
    if hello_cmd := bot.get_command('hello'):
        await hello_cmd(ctx, name="GOLEM")
    
    print("\n💰 Testing Economy Commands:")
    print("-" * 30)
    
    # Balance command
    if balance_cmd := bot.get_command('balance'):
        await balance_cmd(ctx)
    
    # Daily command
    if daily_cmd := bot.get_command('daily'):
        await daily_cmd(ctx)
    
    # Pay command (should fail - no balance)
    if pay_cmd := bot.get_command('pay'):
        await pay_cmd(ctx, test_member, 50)
    
    print("\n📊 Testing Activity Commands:")
    print("-" * 30)
    
    # Level command
    if level_cmd := bot.get_command('level'):
        await level_cmd(ctx)
    
    # Leaderboard command
    if lb_cmd := bot.get_command('leaderboard'):
        await lb_cmd(ctx)
    
    print("\n🎮 Testing Fun Commands:")
    print("-" * 30)
    
    # Coinflip
    if flip_cmd := bot.get_command('coinflip'):
        await flip_cmd(ctx)
    
    # 8ball
    if ball_cmd := bot.get_command('8ball'):
        await ball_cmd(ctx, question="Will GOLEM become the best bot?")
    
    # Roll dice
    if roll_cmd := bot.get_command('roll'):
        await roll_cmd(ctx, "2d6")
    
    print("\n💎 Testing Premium Commands:")
    print("-" * 30)
    
    # Premium info
    if premium_cmd := bot.get_command('premium'):
        await premium_cmd(ctx)
    
    # My premium
    if mypremium_cmd := bot.get_command('mypremium'):
        await mypremium_cmd(ctx)
    
    print("\n🔧 Testing Monitor Commands:")
    print("-" * 30)
    
    # Health check
    if health_cmd := bot.get_command('health'):
        ctx.author = MockMember()  # Need member with admin perms
        ctx.author.guild_permissions = type('obj', (object,), {'administrator': True})
        await health_cmd(ctx)
    
    print("\n✅ Command testing complete!")
    
    # Close bot
    await bot.close()


if __name__ == "__main__":
    asyncio.run(test_commands())
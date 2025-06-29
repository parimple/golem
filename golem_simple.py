"""
GOLEM - Simplified Version
The simplest possible working bot that can be extended
"""
import asyncio
import logging
import os
from typing import Optional, List
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration if available
try:
    from config.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    logger.warning("Configuration module not available")


class GOLEM(commands.Bot):
    """
    The simplified GOLEM bot - ready to evolve
    """
    
    def __init__(self):
        # Load configuration
        self.config = Config() if CONFIG_AVAILABLE else None
        
        # Get configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.voice_states = True
        
        # Get prefix from config or env
        if self.config:
            prefix = self.config.prefix
        else:
            prefix = os.getenv('COMMAND_PREFIX', ',')
        
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            help_command=None  # We'll make our own
        )
        
        # Basic metrics
        self.ready = False
        self.start_time = None
        self.cogs_loaded = []
        
    async def setup_hook(self):
        """Initialize bot on startup"""
        logger.info("🚀 GOLEM awakening...")
        
        # Add basic commands
        self.add_commands()
        
        # Load cogs
        await self.load_cogs()
        
        logger.info("✨ GOLEM initialized")
        
    async def on_ready(self):
        """Bot is ready"""
        if not self.ready:
            self.ready = True
            self.start_time = discord.utils.utcnow()
            
            logger.info(f"⚡ {self.user} online")
            logger.info(f"📡 Servers: {len(self.guilds)}")
            
            # Set presence
            prefix = self.command_prefix
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"reality unfold | {prefix}help"
                )
            )
    
    def add_commands(self):
        """Add basic commands"""
        
        @self.command(name='help')
        async def help_command(ctx: commands.Context):
            """Show help information"""
            embed = discord.Embed(
                title="🌟 GOLEM Help",
                description="A bot that transcends simplicity",
                color=discord.Color.blue()
            )
            
            prefix = self.command_prefix
            embed.add_field(
                name="Commands",
                value=(
                    f"`{prefix}help` - Show this message\n"
                    f"`{prefix}ping` - Check bot latency\n"
                    f"`{prefix}status` - Bot status\n"
                    f"`{prefix}hello` - Simple greeting"
                ),
                inline=False
            )
            
            embed.set_footer(text="GOLEM - Where complexity dies")
            await ctx.send(embed=embed)
        
        @self.command(name='ping')
        async def ping(ctx: commands.Context):
            """Check bot latency"""
            latency = round(self.latency * 1000)
            
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Latency: {latency}ms",
                color=discord.Color.green() if latency < 100 else discord.Color.orange()
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='status')
        async def status(ctx: commands.Context):
            """Show bot status"""
            embed = discord.Embed(
                title="🤖 GOLEM Status",
                color=discord.Color.green()
            )
            
            # Uptime
            if self.start_time:
                uptime = discord.utils.utcnow() - self.start_time
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours}h {minutes}m {seconds}s"
            else:
                uptime_str = "Unknown"
            
            embed.add_field(name="⏰ Uptime", value=uptime_str, inline=True)
            embed.add_field(name="📡 Servers", value=len(self.guilds), inline=True)
            embed.add_field(name="👥 Users", value=sum(g.member_count for g in self.guilds), inline=True)
            
            # System info
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                embed.add_field(name="💾 Memory", value=f"{memory_mb:.1f} MB", inline=True)
                embed.add_field(name="🖥️ CPU", value=f"{psutil.cpu_percent(interval=1)}%", inline=True)
            except:
                pass
            
            embed.add_field(
                name="🧬 Status",
                value="Ready to evolve",
                inline=False
            )
            
            # Show loaded cogs
            if self.cogs_loaded:
                cogs_list = "\n".join([f"• {cog.split('.')[-1]}" for cog in self.cogs_loaded])
                embed.add_field(
                    name="📦 Loaded Modules",
                    value=cogs_list or "None",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='hello')
        async def hello(ctx: commands.Context, *, name: Optional[str] = None):
            """Simple greeting command"""
            if name:
                greeting = f"Hello, {name}! 👋"
            else:
                greeting = f"Hello, {ctx.author.mention}! 👋"
            
            embed = discord.Embed(
                description=greeting,
                color=discord.Color.blue()
            )
            
            await ctx.send(embed=embed)
    
    async def load_cogs(self):
        """Load all cogs from the cogs directory"""
        cogs_dir = Path("cogs/commands")
        if not cogs_dir.exists():
            logger.warning("No cogs directory found")
            return
        
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
                
            cog_name = f"cogs.commands.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                self.cogs_loaded.append(cog_name)
                logger.info(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog_name}: {e}")
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle command errors gracefully"""
        if isinstance(error, commands.CommandNotFound):
            # Ignore unknown commands
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: {error.param.name}")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send("❌ An error occurred while processing the command")


def transcend():
    """
    Create a GOLEM bot instance
    This is all you need
    """
    return GOLEM()


def neural_command(name=None, memory_size=1000):
    """
    Placeholder for neural command decorator
    In simple version, it just returns the function unchanged
    """
    def decorator(func):
        # In simple version, just return the function as-is
        func.__neural__ = True  # Mark as neural command
        return func
    return decorator


def main():
    """Main entry point"""
    # Check for token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("No DISCORD_TOKEN found in environment variables!")
        logger.info("Please create a .env file with DISCORD_TOKEN=your_token_here")
        return
    
    # Create and run bot
    bot = transcend()
    
    try:
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
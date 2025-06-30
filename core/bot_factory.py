"""
Bot Factory - Creates bot instances based on configuration
"""
import os
import discord
from discord.ext import commands
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import importlib.util
from datetime import datetime

from config.bot_profiles import get_bot_profile

logger = logging.getLogger(__name__)

class ConfigurableBot(commands.Bot):
    """Bot that can be configured to work as different bots"""
    
    def __init__(self, profile_name: str = None):
        # Get profile from environment or parameter
        self.profile_name = profile_name or os.getenv('BOT_PROFILE', 'GOLEM')
        self.profile = get_bot_profile(self.profile_name)
        
        # Set up bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        
        # Get prefix from profile or environment
        prefix = os.getenv('COMMAND_PREFIX', self.profile['prefix'])
        
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            description=self.profile['description']
        )
        
        # Store configuration
        self.config = self.profile
        self.colors = self.profile['colors']
        self.features = self.profile['features']
        
        # Track loaded modules
        self.loaded_modules: List[str] = []
        
        # Track start time for uptime
        self.start_time = datetime.now()
        
        # Remove default help command to use custom one
        self.remove_command('help')
        
        logger.info(f"🤖 Initializing as {self.profile_name} bot")
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        # Load modules based on profile
        await self.load_profile_modules()
        
        # Add basic commands
        self.add_basic_commands()
        
        logger.info(f"✅ {self.profile_name} setup complete")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"⚡ {self.user.name} online as {self.profile_name}")
        logger.info(f"📡 Servers: {len(self.guilds)}")
        
        # Set presence based on profile
        await self.update_presence()
    
    async def update_presence(self):
        """Update bot presence based on profile"""
        presence = self.profile.get('presence', {})
        activity_type = getattr(discord.ActivityType, presence.get('type', 'watching'))
        text = presence.get('text', '{prefix}help').format(prefix=self.command_prefix)
        
        await self.change_presence(
            activity=discord.Activity(
                type=activity_type,
                name=text
            )
        )
    
    async def load_profile_modules(self):
        """Load modules defined in profile"""
        modules = self.profile.get('modules', [])
        
        for module in modules:
            try:
                # Check if module exists
                module_path = module.replace('.', '/')
                if Path(f"{module_path}.py").exists():
                    await self.load_extension(module)
                    self.loaded_modules.append(module)
                    logger.info(f"✅ Loaded module: {module}")
                else:
                    logger.warning(f"⚠️ Module not found: {module}")
            except Exception as e:
                logger.error(f"❌ Failed to load {module}: {e}")
    
    def add_basic_commands(self):
        """Add basic commands that all profiles have"""
        
        @self.command(name='help')
        async def help_command(ctx: commands.Context, command: Optional[str] = None):
            """Show help information"""
            embed = discord.Embed(
                title=f"🌟 {self.profile_name} Help",
                description=self.profile['description'],
                color=self.colors['primary']
            )
            
            if command:
                # Show specific command help
                cmd = self.get_command(command)
                if cmd:
                    embed.add_field(
                        name=f"{self.command_prefix}{cmd.name}",
                        value=cmd.help or "No description",
                        inline=False
                    )
                    if cmd.aliases:
                        embed.add_field(
                            name="Aliases",
                            value=", ".join(cmd.aliases),
                            inline=False
                        )
                else:
                    embed.description = f"Command '{command}' not found!"
                    embed.color = self.colors['error']
            else:
                # Show general help
                # Group commands by cog
                cogs_dict = {}
                for cmd in self.commands:
                    if not cmd.hidden:
                        cog_name = cmd.cog_name or "Basic"
                        if cog_name not in cogs_dict:
                            cogs_dict[cog_name] = []
                        cogs_dict[cog_name].append(cmd.name)
                
                for cog_name, commands in cogs_dict.items():
                    if commands:
                        embed.add_field(
                            name=cog_name,
                            value=", ".join(f"`{cmd}`" for cmd in sorted(commands)[:10]),
                            inline=False
                        )
                
                embed.set_footer(text=f"Use {self.command_prefix}help <command> for more info")
            
            await ctx.send(embed=embed)
        
        @self.command(name='profile')
        async def profile_info(ctx: commands.Context):
            """Show current bot profile information"""
            embed = discord.Embed(
                title=f"🤖 Bot Profile: {self.profile_name}",
                description=self.profile['description'],
                color=self.colors['primary']
            )
            
            embed.add_field(name="Prefix", value=f"`{self.command_prefix}`", inline=True)
            embed.add_field(name="Modules", value=str(len(self.loaded_modules)), inline=True)
            embed.add_field(name="Language", value=self.features.get('language', 'en'), inline=True)
            
            # Show features
            features_text = []
            if self.features.get('reputation_negative'):
                features_text.append("✅ Negative Reputation")
            if self.features.get('advanced_mode'):
                features_text.append("✅ Advanced Mode")
            if self.features.get('ai_learning'):
                features_text.append("✅ AI Learning")
            if self.features.get('quantum_processing'):
                features_text.append("✅ Quantum Processing")
            
            if features_text:
                embed.add_field(
                    name="Special Features",
                    value="\n".join(features_text),
                    inline=False
                )
            
            await ctx.send(embed=embed)
        
        @self.command(name='ping')
        async def ping(ctx: commands.Context):
            """Check bot latency"""
            latency = round(self.latency * 1000)
            
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Latency: {latency}ms",
                color=self.colors['success'] if latency < 100 else self.colors['warning']
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='status')
        async def status(ctx: commands.Context):
            """Show bot status information"""
            embed = discord.Embed(
                title=f"📊 {self.profile_name} Status",
                color=self.colors['primary']
            )
            
            # Basic info
            embed.add_field(name="🤖 Bot", value=self.user.name, inline=True)
            embed.add_field(name="🆔 ID", value=self.user.id, inline=True)
            embed.add_field(name="🌐 Servers", value=len(self.guilds), inline=True)
            
            # Uptime
            if hasattr(self, 'start_time'):
                uptime = datetime.now() - self.start_time
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                embed.add_field(name="⏱️ Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
            
            # Profile info
            embed.add_field(name="🎭 Profile", value=self.profile_name, inline=True)
            embed.add_field(name="📝 Prefix", value=f"`{self.command_prefix}`", inline=True)
            
            # System info
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                embed.add_field(name="💾 Memory", value=f"{memory_mb:.1f} MB", inline=True)
                embed.add_field(name="🖥️ CPU", value=f"{psutil.cpu_percent(interval=1)}%", inline=True)
            except:
                pass
            
            # Loaded modules
            embed.add_field(
                name="📦 Loaded Modules",
                value=f"{len(self.loaded_modules)} modules",
                inline=True
            )
            
            # Features
            feature_count = sum(1 for v in self.features.values() if v is True)
            embed.add_field(
                name="✨ Active Features",
                value=f"{feature_count} features",
                inline=True
            )
            
            embed.set_footer(text=f"{self.profile['description']}")
            embed.timestamp = datetime.utcnow()
            
            await ctx.send(embed=embed)


def create_bot(profile: Optional[str] = None) -> ConfigurableBot:
    """Factory function to create a bot instance"""
    return ConfigurableBot(profile)
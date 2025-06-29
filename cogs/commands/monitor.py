"""Performance monitoring for GOLEM cogs."""

import discord
from discord.ext import commands, tasks
import time
import psutil
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MonitorCog(commands.Cog):
    """Monitor cog performance and bot health."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Performance tracking
        self.command_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.command_counts: Dict[str, int] = defaultdict(int)
        self.command_errors: Dict[str, int] = defaultdict(int)
        
        # Cog metrics
        self.cog_load_times: Dict[str, float] = {}
        self.cog_command_counts: Dict[str, int] = defaultdict(int)
        
        # System metrics
        self.start_time = datetime.utcnow()
        self.message_count = 0
        self.command_count = 0
        
        # Don't start tasks during testing
        self._task_started = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Start background tasks when bot is ready."""
        if not self._task_started:
            self.system_monitor.start()
            self._task_started = True
    
    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.system_monitor.cancel()
    
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """Track command execution start."""
        ctx.start_time = time.perf_counter()
        self.command_count += 1
        self.command_counts[ctx.command.name] += 1
        
        # Track by cog
        if ctx.command.cog:
            cog_name = ctx.command.cog.__class__.__name__
            self.cog_command_counts[cog_name] += 1
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        """Track successful command completion."""
        if hasattr(ctx, 'start_time'):
            execution_time = time.perf_counter() - ctx.start_time
            self.command_times[ctx.command.name].append(execution_time)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Track command errors."""
        if ctx.command:
            self.command_errors[ctx.command.name] += 1
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Track message count."""
        if not message.author.bot:
            self.message_count += 1
    
    @tasks.loop(minutes=5)
    async def system_monitor(self):
        """Monitor system resources."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=1)
            
            # Check for alerts
            alerts = []
            
            # Memory alert
            if memory_mb > 500:
                logger.warning(f"High memory usage: {memory_mb:.1f} MB")
                alerts.append(f"⚠️ **Memory Alert**: {memory_mb:.1f} MB (threshold: 500 MB)")
            
            # CPU alert
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                alerts.append(f"⚠️ **CPU Alert**: {cpu_percent:.1f}% (threshold: 80%)")
            
            # Error rate alert
            total_commands = sum(self.command_counts.values())
            total_errors = sum(self.command_errors.values())
            error_rate = (total_errors / total_commands * 100) if total_commands > 0 else 0
            
            if error_rate > 1.0 and total_commands > 100:
                alerts.append(f"⚠️ **Error Rate Alert**: {error_rate:.2f}% (threshold: 1%)")
            
            # Send alerts to monitoring channel if configured
            if alerts and hasattr(self.bot, 'config') and self.bot.config:
                channel_id = self.bot.config.get('monitoring_channel')
                if channel_id:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        embed = discord.Embed(
                            title="🚨 GOLEM System Alert",
                            description="\n".join(alerts),
                            color=discord.Color.red(),
                            timestamp=datetime.utcnow()
                        )
                        embed.add_field(
                            name="System Stats",
                            value=f"Memory: {memory_mb:.1f} MB\nCPU: {cpu_percent:.1f}%\nError Rate: {error_rate:.2f}%",
                            inline=False
                        )
                        await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"System monitor error: {e}")
    
    @system_monitor.before_loop
    async def before_system_monitor(self):
        """Wait for bot to be ready."""
        await self.bot.wait_until_ready()
    
    @commands.hybrid_command(name="performance", aliases=["perf", "stats"])
    @commands.has_permissions(administrator=True)
    async def performance(self, ctx: commands.Context):
        """Show bot performance metrics."""
        embed = discord.Embed(
            title="🔧 GOLEM Performance Monitor",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # System info
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=0.1)
            
            embed.add_field(
                name="💻 System Resources",
                value=f"**Memory:** {memory_mb:.1f} MB\n**CPU:** {cpu_percent:.1f}%",
                inline=True
            )
        except:
            pass
        
        # Bot stats
        uptime = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed.add_field(
            name="🤖 Bot Statistics",
            value=(
                f"**Uptime:** {hours}h {minutes}m {seconds}s\n"
                f"**Messages:** {self.message_count:,}\n"
                f"**Commands:** {self.command_count:,}"
            ),
            inline=True
        )
        
        # Connection info
        embed.add_field(
            name="📡 Connection",
            value=(
                f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                f"**Guilds:** {len(self.bot.guilds)}\n"
                f"**Users:** {sum(g.member_count for g in self.bot.guilds):,}"
            ),
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="cogstats", aliases=["cogs"])
    @commands.has_permissions(administrator=True)
    async def show_cog_stats(self, ctx: commands.Context):
        """Show detailed cog statistics."""
        embed = discord.Embed(
            title="📦 Cog Performance Statistics",
            color=discord.Color.green()
        )
        
        # Sort cogs by command usage
        sorted_cogs = sorted(
            self.cog_command_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        if sorted_cogs:
            cog_list = "\n".join([
                f"**{cog}:** {count:,} commands"
                for cog, count in sorted_cogs[:10]
            ])
            embed.add_field(
                name="🎯 Most Active Cogs",
                value=cog_list or "No data yet",
                inline=False
            )
        
        # Loaded cogs
        loaded_cogs = [cog for cog in self.bot.cogs]
        embed.add_field(
            name="✅ Loaded Cogs",
            value=f"{len(loaded_cogs)} cogs active",
            inline=True
        )
        
        # Error rate
        total_errors = sum(self.command_errors.values())
        error_rate = (total_errors / self.command_count * 100) if self.command_count > 0 else 0
        
        embed.add_field(
            name="❌ Error Rate",
            value=f"{error_rate:.1f}% ({total_errors} errors)",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="commandstats", aliases=["cmdstats"])
    @commands.has_permissions(administrator=True)
    async def command_stats(self, ctx: commands.Context, top: int = 10):
        """Show command usage statistics."""
        embed = discord.Embed(
            title="📊 Command Statistics",
            color=discord.Color.purple()
        )
        
        # Most used commands
        sorted_commands = sorted(
            self.command_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top]
        
        if sorted_commands:
            command_list = "\n".join([
                f"**{i+1}.** `{cmd}` - {count:,} uses"
                for i, (cmd, count) in enumerate(sorted_commands)
            ])
            embed.add_field(
                name=f"🏆 Top {top} Commands",
                value=command_list,
                inline=False
            )
        
        # Slowest commands
        avg_times = {}
        for cmd, times in self.command_times.items():
            if times:
                avg_times[cmd] = sum(times) / len(times)
        
        if avg_times:
            sorted_times = sorted(
                avg_times.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            slow_list = "\n".join([
                f"**{cmd}:** {time*1000:.1f}ms avg"
                for cmd, time in sorted_times
            ])
            embed.add_field(
                name="🐌 Slowest Commands",
                value=slow_list,
                inline=False
            )
        
        # Commands with most errors
        if self.command_errors:
            sorted_errors = sorted(
                self.command_errors.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            error_list = "\n".join([
                f"**{cmd}:** {errors} errors"
                for cmd, errors in sorted_errors
            ])
            embed.add_field(
                name="⚠️ Error-Prone Commands",
                value=error_list,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="health")
    @commands.has_permissions(administrator=True)
    async def health_check(self, ctx: commands.Context):
        """Quick health check of all systems."""
        embed = discord.Embed(
            title="🏥 GOLEM Health Check",
            description="Checking all systems...",
            color=discord.Color.yellow()
        )
        
        msg = await ctx.send(embed=embed)
        
        # Check each cog
        results = []
        for cog_name, cog in self.bot.cogs.items():
            try:
                # Simple check - cog exists and has commands
                commands_count = len([c for c in cog.get_commands()])
                status = "✅" if commands_count > 0 else "⚠️"
                results.append(f"{status} **{cog_name}** ({commands_count} commands)")
            except Exception as e:
                results.append(f"❌ **{cog_name}** - Error: {str(e)[:50]}")
        
        # Update embed
        embed.description = "\n".join(results)
        
        # Overall status
        error_count = len([r for r in results if "❌" in r])
        if error_count == 0:
            embed.color = discord.Color.green()
            embed.set_footer(text="All systems operational! 🚀")
        else:
            embed.color = discord.Color.red()
            embed.set_footer(text=f"{error_count} systems with issues!")
        
        await msg.edit(embed=embed)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(MonitorCog(bot))
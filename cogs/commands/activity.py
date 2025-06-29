"""Activity tracking and leveling system for GOLEM."""

import discord
from discord.ext import commands, tasks
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class ActivityCog(commands.Cog):
    """Track user activity and manage levels."""
    
    def __init__(self, bot):
        self.bot = bot
        # Simple in-memory storage
        self.user_points: Dict[int, int] = {}
        self.user_levels: Dict[int, int] = {}
        self.last_message: Dict[int, datetime] = {}
        
        # Points configuration
        self.message_points = 10
        self.voice_points_per_minute = 5
        self.cooldown_seconds = 60
        
        # Don't start tasks during testing
        self._task_started = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Start background tasks when bot is ready."""
        if not self._task_started:
            self.voice_activity_tracker.start()
            self._task_started = True
    
    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.voice_activity_tracker.cancel()
    
    def get_level_from_points(self, points: int) -> int:
        """Calculate level from points."""
        # Simple level calculation: level = sqrt(points / 100)
        return int((points / 100) ** 0.5)
    
    def get_points_for_level(self, level: int) -> int:
        """Get points required for a level."""
        return level ** 2 * 100
    
    def add_points(self, user_id: int, points: int) -> tuple[int, bool]:
        """Add points to user. Returns (new_total, leveled_up)."""
        old_points = self.user_points.get(user_id, 0)
        old_level = self.get_level_from_points(old_points)
        
        new_points = old_points + points
        self.user_points[user_id] = new_points
        
        new_level = self.get_level_from_points(new_points)
        self.user_levels[user_id] = new_level
        
        leveled_up = new_level > old_level
        
        return new_points, leveled_up
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Award points for messages."""
        if message.author.bot or not message.guild:
            return
        
        user_id = message.author.id
        now = datetime.utcnow()
        
        # Check cooldown
        if user_id in self.last_message:
            if (now - self.last_message[user_id]).total_seconds() < self.cooldown_seconds:
                return
        
        self.last_message[user_id] = now
        
        # Award points
        points_to_add = self.message_points
        
        # Bonus for longer messages
        if len(message.content) > 100:
            points_to_add += 5
        
        new_total, leveled_up = self.add_points(user_id, points_to_add)
        
        # Announce level up
        if leveled_up:
            level = self.user_levels[user_id]
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} reached **Level {level}**!",
                color=discord.Color.gold()
            )
            
            await message.channel.send(embed=embed, delete_after=10)
    
    @tasks.loop(minutes=1)
    async def voice_activity_tracker(self):
        """Award points for voice activity."""
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                # Skip AFK channel
                if channel == guild.afk_channel:
                    continue
                
                # Award points to non-bot members
                for member in channel.members:
                    if not member.bot:
                        self.add_points(member.id, self.voice_points_per_minute)
    
    @voice_activity_tracker.before_loop
    async def before_voice_tracker(self):
        """Wait until bot is ready."""
        await self.bot.wait_until_ready()
    
    @commands.hybrid_command(name="level", aliases=["lvl", "rank"])
    async def level(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Check your or someone's level and points."""
        target = member or ctx.author
        
        points = self.user_points.get(target.id, 0)
        level = self.get_level_from_points(points)
        
        # Calculate progress to next level
        current_level_points = self.get_points_for_level(level)
        next_level_points = self.get_points_for_level(level + 1)
        progress = points - current_level_points
        needed = next_level_points - current_level_points
        
        embed = discord.Embed(
            title=f"📊 {target.display_name}'s Stats",
            color=target.color if target.color != discord.Color.default() else discord.Color.blue()
        )
        
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="Points", value=f"**{points:,}**", inline=True)
        embed.add_field(name="Progress", value=f"{progress:,}/{needed:,} ({progress/needed*100:.1f}%)", inline=False)
        
        # Create progress bar
        bar_length = 20
        filled = int(bar_length * progress / needed)
        bar = "█" * filled + "░" * (bar_length - filled)
        embed.add_field(name="Progress Bar", value=f"`{bar}`", inline=False)
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="leaderboard", aliases=["lb", "top"])
    async def activity_leaderboard(self, ctx: commands.Context, page: int = 1):
        """Show activity leaderboard."""
        sorted_users = sorted(self.user_points.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_users:
            await ctx.send("No activity recorded yet!")
            return
        
        # Pagination
        per_page = 10
        total_pages = (len(sorted_users) + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        embed = discord.Embed(
            title="🏆 Activity Leaderboard",
            color=discord.Color.gold()
        )
        
        description = ""
        for i, (user_id, points) in enumerate(sorted_users[start_idx:end_idx], start_idx + 1):
            user = self.bot.get_user(user_id)
            if user:
                level = self.get_level_from_points(points)
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
                description += f"{emoji} **{i}.** {user.mention} - Level {level} ({points:,} pts)\n"
        
        embed.description = description
        embed.set_footer(text=f"Page {page}/{total_pages}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="addpoints")
    @commands.has_permissions(administrator=True)
    async def add_points_cmd(self, ctx: commands.Context, member: discord.Member, points: int):
        """Add points to a user (Admin only)."""
        old_level = self.get_level_from_points(self.user_points.get(member.id, 0))
        new_total, leveled_up = self.add_points(member.id, points)
        new_level = self.get_level_from_points(new_total)
        
        embed = discord.Embed(
            title="✨ Points Added",
            description=f"Added **{points:,}** points to {member.mention}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="New Total", value=f"{new_total:,} points", inline=True)
        
        if leveled_up:
            embed.add_field(name="Level Up!", value=f"Level {old_level} → {new_level}", inline=True)
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(ActivityCog(bot))
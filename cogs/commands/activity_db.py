"""Activity tracking with database and automatic XP"""

import discord
from discord.ext import commands, tasks
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from core.database import db

logger = logging.getLogger(__name__)


class ActivityCog(commands.Cog):
    """Track user activity with automatic XP and database persistence"""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_cooldowns: Dict[int, datetime] = {}
        self.voice_tracker: Dict[int, datetime] = {}
        
        # XP configuration
        self.message_xp = 10
        self.voice_xp_per_minute = 5
        self.message_cooldown = 60  # seconds
        
        # Start background tasks
        self.voice_xp_task.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.voice_xp_task.cancel()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Award XP for messages"""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Check cooldown
        user_id = message.author.id
        now = datetime.now()
        
        if user_id in self.message_cooldowns:
            last_message = self.message_cooldowns[user_id]
            if (now - last_message).total_seconds() < self.message_cooldown:
                return
        
        # Award XP
        xp_multiplier = self.bot.features.get('activity_xp_rate', 1.0)
        xp_amount = int(self.message_xp * xp_multiplier)
        
        await db.add_xp(user_id, xp_amount, "message")
        self.message_cooldowns[user_id] = now
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Track voice channel activity"""
        # User joined voice
        if not before.channel and after.channel and not member.bot:
            self.voice_tracker[member.id] = datetime.now()
        
        # User left voice
        elif before.channel and not after.channel and member.id in self.voice_tracker:
            # Calculate time spent
            join_time = self.voice_tracker.pop(member.id)
            time_spent = (datetime.now() - join_time).total_seconds() / 60  # minutes
            
            if time_spent >= 1:  # Minimum 1 minute
                xp_multiplier = self.bot.features.get('activity_xp_rate', 1.0)
                xp_amount = int(time_spent * self.voice_xp_per_minute * xp_multiplier)
                await db.add_xp(member.id, xp_amount, "voice")
    
    @tasks.loop(minutes=5)
    async def voice_xp_task(self):
        """Award XP to users in voice channels every 5 minutes"""
        for user_id, join_time in list(self.voice_tracker.items()):
            user = self.bot.get_user(user_id)
            if user:
                # Award 5 minutes worth of XP
                xp_multiplier = self.bot.features.get('activity_xp_rate', 1.0)
                xp_amount = int(5 * self.voice_xp_per_minute * xp_multiplier)
                await db.add_xp(user_id, xp_amount, "voice")
                
                # Update join time
                self.voice_tracker[user_id] = datetime.now()
    
    @voice_xp_task.before_loop
    async def before_voice_xp_task(self):
        """Wait until bot is ready"""
        await self.bot.wait_until_ready()
    
    def get_level_from_xp(self, xp: int) -> int:
        """Calculate level from XP"""
        return int((xp / 100) ** 0.5)
    
    def get_xp_for_level(self, level: int) -> int:
        """Get XP required for a level"""
        return level ** 2 * 100
    
    @commands.hybrid_command(name="level", aliases=["lvl", "rank", "poziom"])
    async def level(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Sprawdź poziom i punkty"""
        target = member or ctx.author
        
        # Get user data from database
        leaderboard = await db.get_leaderboard(sort_by="xp", limit=1000)
        user_data = next((entry for entry in leaderboard if entry['user_id'] == target.id), None)
        
        if not user_data:
            xp = 0
            level = 0
            rank = len(leaderboard) + 1
        else:
            xp = user_data['value']
            level = user_data.get('level', self.get_level_from_xp(xp))
            rank = next((i for i, entry in enumerate(leaderboard, 1) if entry['user_id'] == target.id), 0)
        
        # Calculate progress to next level
        current_level_xp = self.get_xp_for_level(level)
        next_level_xp = self.get_xp_for_level(level + 1)
        progress_xp = xp - current_level_xp
        needed_xp = next_level_xp - current_level_xp
        progress_percent = int((progress_xp / needed_xp) * 100) if needed_xp > 0 else 0
        
        # Create progress bar
        bar_length = 10
        filled = int(bar_length * progress_percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        embed = discord.Embed(
            title=f"📊 Poziom {target.display_name}",
            color=self.bot.colors.get('primary', discord.Color.blue())
        )
        
        embed.add_field(
            name="🎖️ Poziom",
            value=f"**{level}**",
            inline=True
        )
        
        embed.add_field(
            name="✨ XP",
            value=f"**{xp:,}**",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Ranking",
            value=f"**#{rank}**",
            inline=True
        )
        
        embed.add_field(
            name="📈 Postęp do poziomu " + str(level + 1),
            value=f"{bar} {progress_percent}%\n{progress_xp:,}/{needed_xp:,} XP",
            inline=False
        )
        
        # Add level rewards info
        if level < 10:
            embed.add_field(
                name="🎁 Następna nagroda",
                value=f"Poziom {((level // 5) + 1) * 5} - Specjalna rola!",
                inline=False
            )
        
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        embed.set_footer(
            text=f"Zapytał: {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="leaderboard", aliases=["lb", "xptop", "ranking"])
    async def leaderboard(self, ctx: commands.Context, page: int = 1):
        """Ranking aktywności użytkowników"""
        # Get leaderboard from database
        per_page = 10
        offset = (page - 1) * per_page
        
        all_users = await db.get_leaderboard(sort_by="xp", limit=1000)
        total_pages = (len(all_users) + per_page - 1) // per_page
        
        if page < 1 or page > total_pages:
            embed = discord.Embed(
                description=f"❌ Nieprawidłowa strona! Dostępne: 1-{total_pages}",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Get users for current page
        page_users = all_users[offset:offset + per_page]
        
        embed = discord.Embed(
            title="🏆 Ranking Aktywności",
            color=self.bot.colors.get('primary', discord.Color.gold())
        )
        
        description = []
        for i, entry in enumerate(page_users, offset + 1):
            user = self.bot.get_user(entry['user_id'])
            if user:
                # Medal for top 3
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"**{i}.**"
                
                xp = entry['value']
                level = entry.get('level', self.get_level_from_xp(xp))
                description.append(f"{medal} {user.mention} • Lvl **{level}** • **{xp:,}** XP")
        
        embed.description = "\n".join(description)
        
        # Add page info
        embed.set_footer(text=f"Strona {page}/{total_pages} • Użyj {ctx.prefix}lb <strona>")
        
        # Check author's position if not in current page
        author_rank = next((i for i, entry in enumerate(all_users, 1) if entry['user_id'] == ctx.author.id), 0)
        if author_rank > offset + per_page or author_rank <= offset:
            author_data = next((entry for entry in all_users if entry['user_id'] == ctx.author.id), None)
            if author_data:
                author_xp = author_data['value']
                author_level = author_data.get('level', self.get_level_from_xp(author_xp))
                embed.add_field(
                    name="📊 Twoja pozycja",
                    value=f"**#{author_rank}** • Lvl **{author_level}** • **{author_xp:,}** XP",
                    inline=False
                )
        
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="addxp", aliases=["addpoints", "dodajxp"])
    @commands.has_permissions(administrator=True)
    async def addxp(self, ctx: commands.Context, member: discord.Member, amount: int):
        """Dodaj XP użytkownikowi (Admin)"""
        if amount == 0:
            embed = discord.Embed(
                description="❌ Ilość XP nie może być 0!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Add XP
        await db.add_xp(member.id, amount, "admin")
        
        # Get new stats
        leaderboard = await db.get_leaderboard(sort_by="xp", limit=1000)
        user_data = next((entry for entry in leaderboard if entry['user_id'] == member.id), None)
        
        if user_data:
            new_xp = user_data['value']
            new_level = user_data.get('level', self.get_level_from_xp(new_xp))
        else:
            new_xp = amount
            new_level = self.get_level_from_xp(new_xp)
        
        embed = discord.Embed(
            title="✨ XP Zaktualizowane",
            color=self.bot.colors.get('success', discord.Color.green()) if amount > 0 else self.bot.colors.get('error', discord.Color.red())
        )
        
        embed.add_field(
            name="👤 Użytkownik",
            value=member.mention,
            inline=False
        )
        
        embed.add_field(
            name="➕ Dodano" if amount > 0 else "➖ Odjęto",
            value=f"**{amount:+,}** XP",
            inline=True
        )
        
        embed.add_field(
            name="✨ Nowe XP",
            value=f"**{new_xp:,}**",
            inline=True
        )
        
        embed.add_field(
            name="🎖️ Poziom",
            value=f"**{new_level}**",
            inline=True
        )
        
        embed.set_footer(
            text=f"Admin: {ctx.author} • ID: {ctx.author.id}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
        
        logger.info(f"Admin {ctx.author} gave {amount} XP to {member}")


async def setup(bot):
    """Setup the cog"""
    await bot.add_cog(ActivityCog(bot))
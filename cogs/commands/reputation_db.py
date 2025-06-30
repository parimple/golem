"""Reputation commands with database persistence"""

import discord
from discord.ext import commands
from typing import Optional
import logging
from datetime import datetime
from core.database import db

logger = logging.getLogger(__name__)


class ReputationCog(commands.Cog):
    """Reputation system with database persistence"""
    
    def __init__(self, bot):
        self.bot = bot
        # Check if negative reputation is enabled
        self.negative_enabled = self.bot.features.get('reputation_negative', False)
    
    @commands.hybrid_command(name="rep", aliases=["+rep", "addrep", "plusrep"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_positive_rep(self, ctx: commands.Context, member: discord.Member):
        """Daj pozytywną reputację użytkownikowi"""
        if member == ctx.author:
            embed = discord.Embed(
                description="❌ Nie możesz dać reputacji samemu sobie!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if member.bot:
            embed = discord.Embed(
                description="❌ Nie możesz dać reputacji botom!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Give reputation
        success, error_msg = await db.give_reputation(ctx.author.id, member.id, "positive")
        
        if not success:
            embed = discord.Embed(
                title="⏰ Cooldown Reputacji",
                description=f"❌ {error_msg}",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            embed.set_footer(text="Reputację możesz dawać raz na 24 godziny tej samej osobie")
            await ctx.send(embed=embed)
            return
        
        # Get updated reputation
        await db.ensure_user(member.id)
        leaderboard = await db.get_leaderboard(sort_by="reputation", limit=1000)
        user_data = next((entry for entry in leaderboard if entry['user_id'] == member.id), None)
        
        if user_data:
            total_rep = user_data['value']
        else:
            total_rep = 1
        
        embed = discord.Embed(
            title="✨ Reputacja Dodana!",
            color=self.bot.colors.get('success', discord.Color.green())
        )
        
        embed.add_field(
            name="👤 Użytkownik",
            value=member.mention,
            inline=False
        )
        
        embed.add_field(
            name="⬆️ Pozytywna",
            value="+1",
            inline=True
        )
        
        embed.add_field(
            name="📊 Łączna Reputacja",
            value=f"**{total_rep:+}**",
            inline=True
        )
        
        embed.set_footer(
            text=f"Od: {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
        
        # Log command use
        await db.log_command_use("+rep", ctx.guild.id, ctx.author.id)
    
    @commands.hybrid_command(name="minusrep", aliases=["-rep", "removerep"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_negative_rep(self, ctx: commands.Context, member: discord.Member):
        """Daj negatywną reputację użytkownikowi"""
        if not self.negative_enabled:
            embed = discord.Embed(
                description="❌ Negatywna reputacja jest wyłączona na tym serwerze!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = discord.Embed(
                description="❌ Nie możesz dać reputacji samemu sobie!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if member.bot:
            embed = discord.Embed(
                description="❌ Nie możesz dać reputacji botom!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Give reputation
        success, error_msg = await db.give_reputation(ctx.author.id, member.id, "negative")
        
        if not success:
            embed = discord.Embed(
                title="⏰ Cooldown Reputacji",
                description=f"❌ {error_msg}",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            embed.set_footer(text="Reputację możesz dawać raz na 24 godziny tej samej osobie")
            await ctx.send(embed=embed)
            return
        
        # Get updated reputation
        await db.ensure_user(member.id)
        leaderboard = await db.get_leaderboard(sort_by="reputation", limit=1000)
        user_data = next((entry for entry in leaderboard if entry['user_id'] == member.id), None)
        
        if user_data:
            total_rep = user_data['value']
        else:
            total_rep = -1
        
        embed = discord.Embed(
            title="💔 Reputacja Odjęta!",
            color=self.bot.colors.get('error', discord.Color.red())
        )
        
        embed.add_field(
            name="👤 Użytkownik",
            value=member.mention,
            inline=False
        )
        
        embed.add_field(
            name="⬇️ Negatywna",
            value="-1",
            inline=True
        )
        
        embed.add_field(
            name="📊 Łączna Reputacja",
            value=f"**{total_rep:+}**",
            inline=True
        )
        
        embed.set_footer(
            text=f"Od: {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
        
        # Log command use
        await db.log_command_use("-rep", ctx.guild.id, ctx.author.id)
    
    @commands.hybrid_command(name="reputation", aliases=["reputacja", "checkrep"])
    async def check_reputation(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Sprawdź reputację użytkownika"""
        target = member or ctx.author
        
        # Get reputation data from database
        await db.ensure_user(target.id)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT positive, negative FROM reputation WHERE user_id = ?
            """, (target.id,))
            
            result = cursor.fetchone()
            if result:
                positive = result['positive']
                negative = result['negative']
            else:
                positive = negative = 0
        
        total = positive - negative
        
        # Get rank
        leaderboard = await db.get_leaderboard(sort_by="reputation", limit=1000)
        rank = next((i for i, entry in enumerate(leaderboard, 1) if entry['user_id'] == target.id), 0)
        
        # Determine reputation level and color
        if total >= 100:
            level = "🌟 Legenda"
            color = discord.Color.gold()
        elif total >= 50:
            level = "⭐ Gwiazda"
            color = discord.Color.from_rgb(255, 215, 0)
        elif total >= 25:
            level = "💎 Diament"
            color = discord.Color.from_rgb(0, 255, 255)
        elif total >= 10:
            level = "💚 Szanowany"
            color = discord.Color.green()
        elif total >= 0:
            level = "👤 Neutralny"
            color = discord.Color.blurple()
        elif total >= -10:
            level = "⚠️ Kontrowersyjny"
            color = discord.Color.orange()
        else:
            level = "💀 Zły"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title=f"📊 Reputacja {target.display_name}",
            color=color
        )
        
        embed.add_field(
            name="🎖️ Poziom",
            value=level,
            inline=False
        )
        
        # Create visual bar
        bar_length = 20
        positive_ratio = positive / (positive + negative) if (positive + negative) > 0 else 0.5
        positive_bars = int(bar_length * positive_ratio)
        negative_bars = bar_length - positive_bars
        
        bar = "🟢" * positive_bars + "🔴" * negative_bars
        
        embed.add_field(
            name="📊 Rozkład",
            value=bar,
            inline=False
        )
        
        embed.add_field(
            name="⬆️ Pozytywna",
            value=f"**{positive}**",
            inline=True
        )
        
        embed.add_field(
            name="⬇️ Negatywna",
            value=f"**{negative}**",
            inline=True
        )
        
        embed.add_field(
            name="📈 Łącznie",
            value=f"**{total:+}**",
            inline=True
        )
        
        if rank > 0:
            embed.add_field(
                name="🏆 Ranking",
                value=f"**#{rank}** na serwerze",
                inline=False
            )
        
        # Add recent givers if available
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT from_user, type, COUNT(*) as count
                FROM reputation_logs
                WHERE to_user = ?
                GROUP BY from_user, type
                ORDER BY MAX(timestamp) DESC
                LIMIT 5
            """, (target.id,))
            
            recent_givers = cursor.fetchall()
            if recent_givers:
                givers_text = []
                for giver in recent_givers[:3]:
                    user = self.bot.get_user(giver['from_user'])
                    if user:
                        emoji = "⬆️" if giver['type'] == 'positive' else "⬇️"
                        givers_text.append(f"{emoji} {user.display_name}")
                
                if givers_text:
                    embed.add_field(
                        name="🕐 Ostatnio od",
                        value="\n".join(givers_text),
                        inline=False
                    )
        
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        embed.set_footer(
            text=f"Zapytał: {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="reptop", aliases=["toprep", "reputacjatop"])
    async def reputation_leaderboard(self, ctx: commands.Context):
        """Top 10 użytkowników z najwyższą reputacją"""
        leaderboard = await db.get_leaderboard(sort_by="reputation", limit=10)
        
        if not leaderboard:
            embed = discord.Embed(
                description="Brak użytkowników z reputacją!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🏆 Top 10 Reputacja",
            color=self.bot.colors.get('primary', discord.Color.gold())
        )
        
        description = []
        for i, entry in enumerate(leaderboard, 1):
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
                
                total_rep = entry['value']
                
                # Get positive/negative breakdown
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT positive, negative FROM reputation WHERE user_id = ?
                    """, (entry['user_id'],))
                    rep_data = cursor.fetchone()
                    if rep_data:
                        pos = rep_data['positive']
                        neg = rep_data['negative']
                        description.append(f"{medal} {user.mention} • **{total_rep:+}** (⬆️{pos} ⬇️{neg})")
                    else:
                        description.append(f"{medal} {user.mention} • **{total_rep:+}**")
        
        embed.description = "\n".join(description)
        
        # Check author's position
        author_data = next((entry for entry in await db.get_leaderboard(sort_by="reputation", limit=1000) 
                           if entry['user_id'] == ctx.author.id), None)
        
        if author_data:
            author_rank = next((i for i, entry in enumerate(await db.get_leaderboard(sort_by="reputation", limit=1000), 1) 
                               if entry['user_id'] == ctx.author.id), 0)
            
            if author_rank > 10:
                embed.add_field(
                    name="📊 Twoja pozycja",
                    value=f"**#{author_rank}** • **{author_data['value']:+}** reputacji",
                    inline=False
                )
        
        embed.set_footer(text="Reputacja = Pozytywna - Negatywna")
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog"""
    await bot.add_cog(ReputationCog(bot))
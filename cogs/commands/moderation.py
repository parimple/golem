"""Moderation commands for GOLEM."""

import discord
from discord.ext import commands
from typing import Optional, Union
import asyncio
import logging

logger = logging.getLogger(__name__)


class ModerationCog(commands.Cog):
    """Moderation commands for server management."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        """Kick a member from the server."""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot kick someone with equal or higher role!")
            return
        
        reason = reason or "No reason provided"
        
        try:
            await member.kick(reason=f"Kicked by {ctx.author} - {reason}")
            
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"{member.mention} has been kicked",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        """Ban a member from the server."""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot ban someone with equal or higher role!")
            return
        
        reason = reason or "No reason provided"
        
        try:
            await member.ban(reason=f"Banned by {ctx.author} - {reason}")
            
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{member.mention} has been banned",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int):
        """Unban a user by their ID."""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            
            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"{user.mention} has been unbanned",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int, member: Optional[discord.Member] = None):
        """Clear messages from the channel."""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Please specify an amount between 1 and 100!")
            return
        
        # Delete the command message
        await ctx.message.delete()
        
        def check(msg):
            if member:
                return msg.author == member
            return True
        
        deleted = await ctx.channel.purge(limit=amount, check=check)
        
        embed = discord.Embed(
            title="🧹 Messages Cleared",
            description=f"Deleted {len(deleted)} messages",
            color=discord.Color.blue()
        )
        if member:
            embed.add_field(name="From", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await msg.delete()
    
    @commands.hybrid_command(name="mute", aliases=["timeout"])
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, duration: str = "10m", *, reason: Optional[str] = None):
        """Mute a member for a specified duration."""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot mute someone with equal or higher role!")
            return
        
        # Parse duration
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = duration[-1]
        
        if unit not in time_units:
            await ctx.send("❌ Invalid duration format! Use: 10s, 5m, 2h, 1d")
            return
        
        try:
            amount = int(duration[:-1])
            seconds = amount * time_units[unit]
            
            if seconds > 2419200:  # 28 days max (Discord limit)
                await ctx.send("❌ Duration cannot exceed 28 days!")
                return
            
            await member.timeout(discord.utils.utcnow() + discord.timedelta(seconds=seconds), reason=reason)
            
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"{member.mention} has been muted for {duration}",
                color=discord.Color.orange()
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Invalid duration format! Use: 10s, 5m, 2h, 1d")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to mute this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name="unmute", aliases=["untimeout"])
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        """Unmute a member."""
        try:
            await member.timeout(None)
            
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"{member.mention} has been unmuted",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, seconds: int):
        """Set slowmode for the current channel."""
        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Slowmode must be between 0 and 21600 seconds (6 hours)!")
            return
        
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            embed = discord.Embed(
                title="⏰ Slowmode Disabled",
                description="Slowmode has been disabled in this channel",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="⏰ Slowmode Enabled",
                description=f"Slowmode set to {seconds} seconds",
                color=discord.Color.blue()
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(ModerationCog(bot))
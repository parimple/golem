"""Voice channel management commands for GOLEM."""

import discord
from discord.ext import commands
from typing import Optional, Dict, List
import asyncio
import logging

logger = logging.getLogger(__name__)


class VoiceCog(commands.Cog):
    """Voice channel management system."""
    
    def __init__(self, bot):
        self.bot = bot
        # Track temporary voice channels
        self.temp_channels: Dict[int, int] = {}  # channel_id: owner_id
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice channel events."""
        # Clean up empty temporary channels
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                    del self.temp_channels[before.channel.id]
                    logger.info(f"Deleted empty temp channel: {before.channel.name}")
                except:
                    pass
        
        # Check if member joined a create channel
        if after.channel and self.bot.config:
            create_channels = self.bot.config.get('channels_create', [])
            if after.channel.id in create_channels:
                await self.create_temp_channel(member, after.channel)
    
    async def create_temp_channel(self, member: discord.Member, create_channel: discord.VoiceChannel):
        """Create a temporary voice channel for the member."""
        category = create_channel.category
        
        # Generate channel name
        channel_name = f"{member.display_name}'s Channel"
        
        # Create the channel
        try:
            new_channel = await category.create_voice_channel(
                name=channel_name,
                user_limit=0,
                position=create_channel.position + 1
            )
            
            # Set permissions
            await new_channel.set_permissions(member, connect=True, speak=True, manage_channels=True)
            
            # Move member to new channel
            await member.move_to(new_channel)
            
            # Track the channel
            self.temp_channels[new_channel.id] = member.id
            
            logger.info(f"Created temp channel for {member}: {channel_name}")
            
        except Exception as e:
            logger.error(f"Failed to create temp channel: {e}")
    
    @commands.hybrid_group(name="voice", aliases=["vc"])
    async def voice(self, ctx: commands.Context):
        """Voice channel management commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @voice.command(name="lock")
    async def voice_lock(self, ctx: commands.Context):
        """Lock your voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("❌ You don't own this channel!")
            return
        
        # Lock the channel
        await channel.set_permissions(ctx.guild.default_role, connect=False)
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{channel.mention} is now locked",
            color=discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="unlock")
    async def voice_unlock(self, ctx: commands.Context):
        """Unlock your voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("❌ You don't own this channel!")
            return
        
        # Unlock the channel
        await channel.set_permissions(ctx.guild.default_role, connect=True)
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{channel.mention} is now unlocked",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="limit")
    async def voice_limit(self, ctx: commands.Context, limit: int):
        """Set user limit for your voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("❌ You don't own this channel!")
            return
        
        if limit < 0 or limit > 99:
            await ctx.send("❌ Limit must be between 0 and 99!")
            return
        
        await channel.edit(user_limit=limit)
        
        embed = discord.Embed(
            title="👥 User Limit Set",
            description=f"{channel.mention} limit: {limit if limit > 0 else 'No limit'}",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="name", aliases=["rename"])
    async def voice_name(self, ctx: commands.Context, *, name: str):
        """Rename your voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("❌ You don't own this channel!")
            return
        
        if len(name) > 100:
            await ctx.send("❌ Name too long! Maximum 100 characters.")
            return
        
        await channel.edit(name=name)
        
        embed = discord.Embed(
            title="✏️ Channel Renamed",
            description=f"Channel renamed to: **{name}**",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="kick")
    async def voice_kick(self, ctx: commands.Context, member: discord.Member):
        """Kick someone from your voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("❌ You don't own this channel!")
            return
        
        if member not in channel.members:
            await ctx.send("❌ That user is not in your channel!")
            return
        
        # Disconnect the member
        await member.move_to(None)
        
        embed = discord.Embed(
            title="👢 Member Kicked",
            description=f"{member.mention} was kicked from the channel",
            color=discord.Color.orange()
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="transfer")
    async def voice_transfer(self, ctx: commands.Context, member: discord.Member):
        """Transfer channel ownership to another member."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            await ctx.send("❌ You don't own this channel!")
            return
        
        if member not in channel.members:
            await ctx.send("❌ That user must be in your channel!")
            return
        
        # Transfer ownership
        self.temp_channels[channel.id] = member.id
        await channel.set_permissions(ctx.author, manage_channels=False)
        await channel.set_permissions(member, manage_channels=True)
        
        embed = discord.Embed(
            title="🔄 Ownership Transferred",
            description=f"Channel ownership transferred to {member.mention}",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(VoiceCog(bot))
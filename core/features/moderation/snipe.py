"""
Advanced snipe system for GOLEM bots
Tracks deleted and edited messages with safety features
"""
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import re
import asyncio
from collections import defaultdict

class SnipeData:
    """Container for snipe information"""
    def __init__(self, message: discord.Message, action: str = "deleted"):
        self.author = message.author
        self.content = message.content
        self.channel = message.channel
        self.timestamp = datetime.utcnow()
        self.action = action  # "deleted" or "edited"
        self.attachments = [a.url for a in message.attachments]
        self.embeds = message.embeds
        
        # For edited messages
        self.edited_content = None
        
    def is_safe(self) -> bool:
        """Check if content is safe to display"""
        # Check for URLs
        url_pattern = re.compile(r'https?://\S+')
        if url_pattern.search(self.content):
            return False
            
        # Check for discord invites
        invite_pattern = re.compile(r'discord\.gg/\S+')
        if invite_pattern.search(self.content):
            return False
            
        # Check if has attachments
        if self.attachments:
            return False
            
        return True
    
    def format_content(self, max_length: int = 1000) -> str:
        """Format content for display"""
        content = self.content or "*[No text content]*"
        if len(content) > max_length:
            content = content[:max_length] + "..."
        return content


class SnipeSystem:
    """Advanced snipe tracking system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.deleted_messages: Dict[int, SnipeData] = {}  # channel_id -> SnipeData
        self.edited_messages: Dict[int, List[Tuple[SnipeData, SnipeData]]] = defaultdict(list)  # channel_id -> [(before, after)]
        self.max_history = 10  # Max edit history per channel
        
        # Start cleanup task
        self.cleanup_task.start()
    
    def cleanup(self):
        """Stop cleanup task"""
        self.cleanup_task.cancel()
    
    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Clean up old snipe data"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=24)
        
        # Clean deleted messages
        channels_to_remove = []
        for channel_id, snipe_data in self.deleted_messages.items():
            if snipe_data.timestamp < cutoff_time:
                channels_to_remove.append(channel_id)
        
        for channel_id in channels_to_remove:
            del self.deleted_messages[channel_id]
        
        # Clean edited messages
        for channel_id in list(self.edited_messages.keys()):
            self.edited_messages[channel_id] = [
                (before, after) for before, after in self.edited_messages[channel_id]
                if after.timestamp >= cutoff_time
            ]
            if not self.edited_messages[channel_id]:
                del self.edited_messages[channel_id]
    
    def add_deleted(self, message: discord.Message):
        """Track a deleted message"""
        # Don't track bot messages
        if message.author.bot:
            return
            
        snipe_data = SnipeData(message, "deleted")
        self.deleted_messages[message.channel.id] = snipe_data
    
    def add_edited(self, before: discord.Message, after: discord.Message):
        """Track an edited message"""
        # Don't track bot messages or same content
        if before.author.bot or before.content == after.content:
            return
            
        before_data = SnipeData(before, "edited")
        after_data = SnipeData(after, "edited")
        after_data.edited_content = after.content
        
        # Add to history
        self.edited_messages[before.channel.id].append((before_data, after_data))
        
        # Limit history size
        if len(self.edited_messages[before.channel.id]) > self.max_history:
            self.edited_messages[before.channel.id].pop(0)
    
    def get_last_deleted(self, channel_id: int) -> Optional[SnipeData]:
        """Get last deleted message in channel"""
        return self.deleted_messages.get(channel_id)
    
    def get_edit_history(self, channel_id: int) -> List[Tuple[SnipeData, SnipeData]]:
        """Get edit history for channel"""
        return self.edited_messages.get(channel_id, [])


class SnipeCommands(commands.Cog):
    """Snipe commands for GOLEM bots"""
    
    def __init__(self, bot):
        self.bot = bot
        self.snipe_system = SnipeSystem(bot)
    
    def cog_unload(self):
        """Cleanup when cog unloads"""
        self.snipe_system.cleanup()
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Track deleted messages"""
        self.snipe_system.add_deleted(message)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Track edited messages"""
        self.snipe_system.add_edited(before, after)
    
    @commands.hybrid_command(name='snipe', description='Pokaż ostatnio usuniętą wiadomość')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def snipe(self, ctx: commands.Context):
        """Show the last deleted message in this channel"""
        snipe_data = self.snipe_system.get_last_deleted(ctx.channel.id)
        
        if not snipe_data:
            embed = discord.Embed(
                description="Nie znaleziono usuniętych wiadomości w tym kanale!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if content is safe
        if not snipe_data.is_safe():
            embed = discord.Embed(
                description="⚠️ Usunięta wiadomość zawiera niebezpieczną zawartość (linki/załączniki)",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Create embed
        embed = discord.Embed(
            description=snipe_data.format_content(),
            color=discord.Color.red(),
            timestamp=snipe_data.timestamp
        )
        embed.set_author(
            name=f"{snipe_data.author} (usunięte)",
            icon_url=snipe_data.author.avatar.url if snipe_data.author.avatar else None
        )
        embed.set_footer(text=f"Usunięte w #{snipe_data.channel.name}")
        
        # Add attachment info if any
        if snipe_data.attachments:
            embed.add_field(
                name="Załączniki",
                value=f"{len(snipe_data.attachments)} załącznik(ów) [ukryte]",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='editsnipe', description='Pokaż historię edycji wiadomości')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def editsnipe(self, ctx: commands.Context):
        """Show edit history in this channel"""
        history = self.snipe_system.get_edit_history(ctx.channel.id)
        
        if not history:
            embed = discord.Embed(
                description="Nie znaleziono edytowanych wiadomości w tym kanale!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Get last edit
        before_data, after_data = history[-1]
        
        # Check if content is safe
        if not before_data.is_safe() or not after_data.is_safe():
            embed = discord.Embed(
                description="⚠️ Edytowana wiadomość zawiera niebezpieczną zawartość",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Create embed
        embed = discord.Embed(
            title="Edytowana Wiadomość",
            color=discord.Color.blue(),
            timestamp=after_data.timestamp
        )
        embed.set_author(
            name=str(before_data.author),
            icon_url=before_data.author.avatar.url if before_data.author.avatar else None
        )
        
        embed.add_field(
            name="Przed",
            value=before_data.format_content(500),
            inline=False
        )
        embed.add_field(
            name="Po",
            value=after_data.format_content(500),
            inline=False
        )
        
        embed.set_footer(text=f"Edytowane w #{before_data.channel.name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='clearsnipe', description='Wyczyść dane snipe (tylko admin)')
    @commands.has_permissions(administrator=True)
    async def clearsnipe(self, ctx: commands.Context):
        """Clear snipe data for this channel"""
        # Clear deleted messages
        if ctx.channel.id in self.snipe_system.deleted_messages:
            del self.snipe_system.deleted_messages[ctx.channel.id]
        
        # Clear edit history
        if ctx.channel.id in self.snipe_system.edited_messages:
            del self.snipe_system.edited_messages[ctx.channel.id]
        
        embed = discord.Embed(
            description="✅ Wyczyszczono dane snipe dla tego kanału",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SnipeCommands(bot))
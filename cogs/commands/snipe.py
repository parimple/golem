"""
Snipe commands - show deleted and edited messages
Based on BOHT bot functionality
"""
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio

class SnipeData:
    """Container for sniped message data"""
    def __init__(self, content: str, author: discord.Member, channel: discord.TextChannel, timestamp: datetime):
        self.content = content
        self.author = author
        self.channel = channel
        self.timestamp = timestamp
        self.attachments = []

class EditSnipeData:
    """Container for edited message data"""
    def __init__(self, before: str, after: str, author: discord.Member, channel: discord.TextChannel, timestamp: datetime):
        self.before = before
        self.after = after
        self.author = author
        self.channel = channel
        self.timestamp = timestamp

class Snipe(commands.Cog):
    """Snipe deleted and edited messages"""
    
    def __init__(self, bot):
        self.bot = bot
        # Store deleted messages by channel ID
        self.deleted_messages: Dict[int, SnipeData] = {}
        # Store edited messages by channel ID
        self.edited_messages: Dict[int, EditSnipeData] = {}
        # Auto-clear after 5 minutes
        self.clear_time = 300  # 5 minutes
        
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Track deleted messages"""
        # Ignore bot messages
        if message.author.bot:
            return
            
        # Store the deleted message
        self.deleted_messages[message.channel.id] = SnipeData(
            content=message.content,
            author=message.author,
            channel=message.channel,
            timestamp=datetime.utcnow()
        )
        
        # Store attachments
        if message.attachments:
            self.deleted_messages[message.channel.id].attachments = [
                attachment.url for attachment in message.attachments
            ]
        
        # Auto-clear after 5 minutes
        await asyncio.sleep(self.clear_time)
        if message.channel.id in self.deleted_messages:
            if self.deleted_messages[message.channel.id].timestamp == datetime.utcnow():
                del self.deleted_messages[message.channel.id]
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Track edited messages"""
        # Ignore bot messages
        if before.author.bot:
            return
            
        # Ignore if content didn't change
        if before.content == after.content:
            return
            
        # Store the edit
        self.edited_messages[before.channel.id] = EditSnipeData(
            before=before.content,
            after=after.content,
            author=before.author,
            channel=before.channel,
            timestamp=datetime.utcnow()
        )
        
        # Auto-clear after 5 minutes
        await asyncio.sleep(self.clear_time)
        if before.channel.id in self.edited_messages:
            if self.edited_messages[before.channel.id].timestamp == datetime.utcnow():
                del self.edited_messages[before.channel.id]
    
    @commands.hybrid_command(name='snipe', description='Pokaż ostatnią usuniętą wiadomość')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def snipe(self, ctx: commands.Context):
        """Show the last deleted message in this channel"""
        if ctx.channel.id not in self.deleted_messages:
            embed = discord.Embed(
                description="Brak usuniętych wiadomości do pokazania!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed, delete_after=5)
            return
        
        snipe_data = self.deleted_messages[ctx.channel.id]
        
        # Calculate time ago
        time_ago = datetime.utcnow() - snipe_data.timestamp
        if time_ago.total_seconds() < 60:
            time_str = f"{int(time_ago.total_seconds())}s temu"
        elif time_ago.total_seconds() < 3600:
            time_str = f"{int(time_ago.total_seconds() / 60)}m temu"
        else:
            time_str = f"{int(time_ago.total_seconds() / 3600)}h temu"
        
        embed = discord.Embed(
            description=snipe_data.content or "*[Brak tekstu]*",
            color=self.bot.colors.get('primary', discord.Color.blue()),
            timestamp=snipe_data.timestamp
        )
        
        embed.set_author(
            name=f"{snipe_data.author.display_name} ({time_str})",
            icon_url=snipe_data.author.avatar.url if snipe_data.author.avatar else None
        )
        
        # Add attachments if any
        if snipe_data.attachments:
            attachments_text = "\n".join([f"[Załącznik {i+1}]({url})" for i, url in enumerate(snipe_data.attachments)])
            embed.add_field(name="📎 Załączniki", value=attachments_text, inline=False)
        
        embed.set_footer(text=f"Sniped by {ctx.author}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='editsnipe', aliases=['esnipe'], description='Pokaż ostatnią edytowaną wiadomość')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def edit_snipe(self, ctx: commands.Context):
        """Show the last edited message in this channel"""
        if ctx.channel.id not in self.edited_messages:
            embed = discord.Embed(
                description="Brak edytowanych wiadomości do pokazania!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed, delete_after=5)
            return
        
        edit_data = self.edited_messages[ctx.channel.id]
        
        # Calculate time ago
        time_ago = datetime.utcnow() - edit_data.timestamp
        if time_ago.total_seconds() < 60:
            time_str = f"{int(time_ago.total_seconds())}s temu"
        elif time_ago.total_seconds() < 3600:
            time_str = f"{int(time_ago.total_seconds() / 60)}m temu"
        else:
            time_str = f"{int(time_ago.total_seconds() / 3600)}h temu"
        
        embed = discord.Embed(
            title="✏️ Edytowana Wiadomość",
            color=self.bot.colors.get('warning', discord.Color.orange()),
            timestamp=edit_data.timestamp
        )
        
        embed.set_author(
            name=f"{edit_data.author.display_name} ({time_str})",
            icon_url=edit_data.author.avatar.url if edit_data.author.avatar else None
        )
        
        # Add before and after
        embed.add_field(
            name="📝 Przed",
            value=edit_data.before[:1024] or "*[Brak tekstu]*",
            inline=False
        )
        embed.add_field(
            name="📝 Po",
            value=edit_data.after[:1024] or "*[Brak tekstu]*",
            inline=False
        )
        
        embed.set_footer(text=f"Edit-sniped by {ctx.author}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='clearsnipe', description='Wyczyść dane snipe [Admin]')
    @commands.has_permissions(administrator=True)
    async def clear_snipe(self, ctx: commands.Context):
        """Clear all snipe data for this channel"""
        cleared = []
        
        if ctx.channel.id in self.deleted_messages:
            del self.deleted_messages[ctx.channel.id]
            cleared.append("usunięte wiadomości")
        
        if ctx.channel.id in self.edited_messages:
            del self.edited_messages[ctx.channel.id]
            cleared.append("edytowane wiadomości")
        
        if cleared:
            embed = discord.Embed(
                title="🗑️ Wyczyszczono Snipe",
                description=f"Usunięto: {', '.join(cleared)}",
                color=self.bot.colors.get('success', discord.Color.green())
            )
        else:
            embed = discord.Embed(
                title="ℹ️ Brak Danych",
                description="Brak danych snipe do wyczyszczenia!",
                color=self.bot.colors.get('primary', discord.Color.blue())
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='snipestats', description='Statystyki snipe [Admin]')
    @commands.has_permissions(administrator=True)
    async def snipe_stats(self, ctx: commands.Context):
        """Show snipe statistics"""
        embed = discord.Embed(
            title="📊 Statystyki Snipe",
            color=self.bot.colors.get('primary', discord.Color.blue())
        )
        
        embed.add_field(
            name="🗑️ Usunięte",
            value=f"{len(self.deleted_messages)} kanałów",
            inline=True
        )
        embed.add_field(
            name="✏️ Edytowane",
            value=f"{len(self.edited_messages)} kanałów",
            inline=True
        )
        embed.add_field(
            name="⏱️ Auto-clear",
            value=f"{self.clear_time}s ({self.clear_time//60}m)",
            inline=True
        )
        
        # Show active channels
        if self.deleted_messages or self.edited_messages:
            channels = set()
            channels.update(self.deleted_messages.keys())
            channels.update(self.edited_messages.keys())
            
            channel_list = []
            for channel_id in list(channels)[:10]:  # Max 10
                channel = self.bot.get_channel(channel_id)
                if channel:
                    channel_list.append(f"#{channel.name}")
            
            if channel_list:
                embed.add_field(
                    name="📍 Aktywne Kanały",
                    value="\n".join(channel_list),
                    inline=False
                )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Snipe(bot))
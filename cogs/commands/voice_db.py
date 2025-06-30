"""Voice channel management with database persistence"""

import discord
from discord.ext import commands
from typing import Optional, Dict, List
import asyncio
import logging
import json
from datetime import datetime
from core.database import db

logger = logging.getLogger(__name__)


class VoiceCog(commands.Cog):
    """Voice channel management system with database persistence"""
    
    def __init__(self, bot):
        self.bot = bot
        # Track temporary voice channels in memory for quick access
        self.temp_channels: Dict[int, int] = {}  # channel_id: owner_id
        # Load existing channels from database on startup
        asyncio.create_task(self.load_channels_from_db())
    
    async def load_channels_from_db(self):
        """Load existing voice channels from database"""
        await self.bot.wait_until_ready()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT channel_id, owner_id FROM voice_channels
            """)
            
            for row in cursor.fetchall():
                channel_id = row['channel_id']
                owner_id = row['owner_id']
                
                # Verify channel still exists
                channel = self.bot.get_channel(channel_id)
                if channel:
                    self.temp_channels[channel_id] = owner_id
                else:
                    # Clean up database if channel no longer exists
                    cursor.execute("""
                        DELETE FROM voice_channels WHERE channel_id = ?
                    """, (channel_id,))
        
        logger.info(f"Loaded {len(self.temp_channels)} voice channels from database")
    
    async def save_channel_to_db(self, channel_id: int, owner_id: int, guild_id: int, settings: dict = None):
        """Save voice channel to database"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO voice_channels (channel_id, owner_id, guild_id, settings)
                VALUES (?, ?, ?, ?)
            """, (channel_id, owner_id, guild_id, json.dumps(settings or {})))
    
    async def remove_channel_from_db(self, channel_id: int):
        """Remove voice channel from database"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM voice_channels WHERE channel_id = ?
            """, (channel_id,))
    
    async def get_channel_settings(self, channel_id: int) -> dict:
        """Get channel settings from database"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT settings FROM voice_channels WHERE channel_id = ?
            """, (channel_id,))
            
            result = cursor.fetchone()
            if result and result['settings']:
                return json.loads(result['settings'])
            return {}
    
    async def update_channel_settings(self, channel_id: int, settings: dict):
        """Update channel settings in database"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE voice_channels SET settings = ? WHERE channel_id = ?
            """, (json.dumps(settings), channel_id))
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice channel events"""
        # Clean up empty temporary channels
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                    del self.temp_channels[before.channel.id]
                    await self.remove_channel_from_db(before.channel.id)
                    logger.info(f"Deleted empty temp channel: {before.channel.name}")
                except Exception as e:
                    logger.error(f"Failed to delete channel: {e}")
        
        # Check if member joined a create channel
        if after.channel and hasattr(self.bot, 'profile'):
            create_channels = self.bot.profile.get('voice_create_channels', [])
            if after.channel.id in create_channels:
                await self.create_temp_channel(member, after.channel)
    
    async def create_temp_channel(self, member: discord.Member, create_channel: discord.VoiceChannel):
        """Create a temporary voice channel for the member"""
        category = create_channel.category
        
        # Check user's existing channels count
        user_channels = sum(1 for owner_id in self.temp_channels.values() if owner_id == member.id)
        max_channels = self.bot.features.get('voice_max_channels_per_user', 1)
        
        if user_channels >= max_channels:
            try:
                await member.send(f"❌ Możesz mieć maksymalnie {max_channels} kanał(ów) jednocześnie!")
            except:
                pass
            return
        
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
            
            # Save to database
            await self.save_channel_to_db(new_channel.id, member.id, member.guild.id, {
                'created_at': datetime.utcnow().isoformat(),
                'original_name': channel_name
            })
            
            logger.info(f"Created temp channel for {member}: {channel_name}")
            
        except Exception as e:
            logger.error(f"Failed to create temp channel: {e}")
    
    @commands.hybrid_group(name="voice", aliases=["vc", "kanał", "kanal"])
    async def voice(self, ctx: commands.Context):
        """Zarządzanie kanałami głosowymi"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @voice.command(name="lock", aliases=["zamknij"])
    async def voice_lock(self, ctx: commands.Context):
        """Zamknij swój kanał głosowy"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Musisz być na kanale głosowym!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            embed = discord.Embed(
                description="❌ Nie jesteś właścicielem tego kanału!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Lock the channel
        await channel.set_permissions(ctx.guild.default_role, connect=False)
        
        # Update settings in database
        settings = await self.get_channel_settings(channel.id)
        settings['locked'] = True
        await self.update_channel_settings(channel.id, settings)
        
        embed = discord.Embed(
            title="🔒 Kanał Zamknięty",
            description=f"{channel.mention} jest teraz zamknięty",
            color=self.bot.colors.get('error', discord.Color.red())
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="unlock", aliases=["otworz", "otwórz"])
    async def voice_unlock(self, ctx: commands.Context):
        """Otwórz swój kanał głosowy"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Musisz być na kanale głosowym!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            embed = discord.Embed(
                description="❌ Nie jesteś właścicielem tego kanału!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Unlock the channel
        await channel.set_permissions(ctx.guild.default_role, connect=True)
        
        # Update settings in database
        settings = await self.get_channel_settings(channel.id)
        settings['locked'] = False
        await self.update_channel_settings(channel.id, settings)
        
        embed = discord.Embed(
            title="🔓 Kanał Otwarty",
            description=f"{channel.mention} jest teraz otwarty",
            color=self.bot.colors.get('success', discord.Color.green())
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="limit")
    async def voice_limit(self, ctx: commands.Context, limit: int):
        """Ustaw limit użytkowników dla swojego kanału głosowego"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Musisz być na kanale głosowym!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            embed = discord.Embed(
                description="❌ Nie jesteś właścicielem tego kanału!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if limit < 0 or limit > 99:
            embed = discord.Embed(
                description="❌ Limit musi być między 0 a 99!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        await channel.edit(user_limit=limit)
        
        # Update settings in database
        settings = await self.get_channel_settings(channel.id)
        settings['user_limit'] = limit
        await self.update_channel_settings(channel.id, settings)
        
        embed = discord.Embed(
            title="👥 Limit Użytkowników Ustawiony",
            description=f"{channel.mention} limit: **{limit if limit > 0 else 'Brak limitu'}**",
            color=self.bot.colors.get('primary', discord.Color.blue())
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="name", aliases=["rename", "nazwa"])
    async def voice_name(self, ctx: commands.Context, *, name: str):
        """Zmień nazwę swojego kanału głosowego"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Musisz być na kanale głosowym!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            embed = discord.Embed(
                description="❌ Nie jesteś właścicielem tego kanału!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if len(name) > 100:
            embed = discord.Embed(
                description="❌ Nazwa za długa! Maksymalnie 100 znaków.",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        await channel.edit(name=name)
        
        # Update settings in database
        settings = await self.get_channel_settings(channel.id)
        settings['custom_name'] = name
        settings['name_changed_at'] = datetime.utcnow().isoformat()
        await self.update_channel_settings(channel.id, settings)
        
        embed = discord.Embed(
            title="✏️ Nazwa Kanału Zmieniona",
            description=f"Nazwa zmieniona na: **{name}**",
            color=self.bot.colors.get('primary', discord.Color.blue())
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="kick", aliases=["wyrzuc", "wyrzuć"])
    async def voice_kick(self, ctx: commands.Context, member: discord.Member):
        """Wyrzuć kogoś ze swojego kanału głosowego"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Musisz być na kanale głosowym!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            embed = discord.Embed(
                description="❌ Nie jesteś właścicielem tego kanału!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if member not in channel.members:
            embed = discord.Embed(
                description="❌ Ten użytkownik nie jest na twoim kanale!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = discord.Embed(
                description="❌ Nie możesz wyrzucić samego siebie!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Disconnect the member
        await member.move_to(None)
        
        # Update settings in database
        settings = await self.get_channel_settings(channel.id)
        if 'kicked_users' not in settings:
            settings['kicked_users'] = []
        settings['kicked_users'].append({
            'user_id': member.id,
            'kicked_at': datetime.utcnow().isoformat(),
            'kicked_by': ctx.author.id
        })
        await self.update_channel_settings(channel.id, settings)
        
        embed = discord.Embed(
            title="👢 Użytkownik Wyrzucony",
            description=f"{member.mention} został wyrzucony z kanału",
            color=self.bot.colors.get('warning', discord.Color.orange())
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="transfer", aliases=["przekaz", "przekaż"])
    async def voice_transfer(self, ctx: commands.Context, member: discord.Member):
        """Przekaż własność kanału innemu użytkownikowi"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Musisz być na kanale głosowym!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        # Check if user owns the channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id] != ctx.author.id:
            embed = discord.Embed(
                description="❌ Nie jesteś właścicielem tego kanału!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if member not in channel.members:
            embed = discord.Embed(
                description="❌ Ten użytkownik musi być na twoim kanale!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        if member.bot:
            embed = discord.Embed(
                description="❌ Nie możesz przekazać kanału botowi!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        # Transfer ownership
        self.temp_channels[channel.id] = member.id
        await channel.set_permissions(ctx.author, manage_channels=False)
        await channel.set_permissions(member, manage_channels=True)
        
        # Update database
        await self.save_channel_to_db(channel.id, member.id, ctx.guild.id, {
            'transferred_from': ctx.author.id,
            'transferred_at': datetime.utcnow().isoformat()
        })
        
        embed = discord.Embed(
            title="🔄 Własność Przekazana",
            description=f"Własność kanału przekazana do {member.mention}",
            color=self.bot.colors.get('success', discord.Color.green())
        )
        
        await ctx.send(embed=embed)
    
    @voice.command(name="info")
    async def voice_info(self, ctx: commands.Context):
        """Pokaż informacje o swoim kanale głosowym"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Musisz być na kanale głosowym!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        
        # Check if channel is temporary
        if channel.id not in self.temp_channels:
            embed = discord.Embed(
                description="❌ To nie jest tymczasowy kanał!",
                color=self.bot.colors.get('error', discord.Color.red())
            )
            await ctx.send(embed=embed)
            return
        
        owner_id = self.temp_channels[channel.id]
        owner = self.bot.get_user(owner_id)
        settings = await self.get_channel_settings(channel.id)
        
        embed = discord.Embed(
            title="🎤 Informacje o Kanale",
            color=self.bot.colors.get('primary', discord.Color.blue())
        )
        
        embed.add_field(
            name="📍 Nazwa",
            value=channel.name,
            inline=False
        )
        
        embed.add_field(
            name="👑 Właściciel",
            value=owner.mention if owner else f"ID: {owner_id}",
            inline=True
        )
        
        embed.add_field(
            name="👥 Użytkownicy",
            value=f"{len(channel.members)}/{channel.user_limit if channel.user_limit else '∞'}",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Status",
            value="Zamknięty" if settings.get('locked', False) else "Otwarty",
            inline=True
        )
        
        if 'created_at' in settings:
            created_at = datetime.fromisoformat(settings['created_at'])
            duration = datetime.utcnow() - created_at
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            embed.add_field(
                name="⏱️ Czas trwania",
                value=f"{hours}h {minutes}m",
                inline=True
            )
        
        embed.set_footer(
            text=f"ID kanału: {channel.id}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog"""
    await bot.add_cog(VoiceCog(bot))
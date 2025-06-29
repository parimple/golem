"""
Advanced giveaway system for GOLEM bots
Supports role-based and message-based giveaways
"""
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Set
import random
import asyncio
from enum import Enum

class GiveawayType(Enum):
    MESSAGE = "message"  # Pick from channel messages
    ROLE = "role"        # Pick from role members
    REACTION = "reaction" # Pick from message reactions

class GiveawayRequirement(Enum):
    AND = "and"  # All roles required
    OR = "or"    # Any role required

class Giveaway:
    """Container for giveaway information"""
    def __init__(self, 
                 host: discord.Member,
                 prize: str,
                 winners_count: int,
                 giveaway_type: GiveawayType,
                 channel: discord.TextChannel,
                 duration: Optional[timedelta] = None):
        
        self.id = f"giveaway_{datetime.utcnow().timestamp()}"
        self.host = host
        self.prize = prize
        self.winners_count = winners_count
        self.type = giveaway_type
        self.channel = channel
        self.created_at = datetime.utcnow()
        self.ends_at = self.created_at + duration if duration else None
        
        # Type-specific data
        self.message_id: Optional[int] = None  # For reaction giveaways
        self.required_roles: List[discord.Role] = []
        self.requirement_type = GiveawayRequirement.OR
        self.exclude_bots = True
        self.include_webhooks = False
        self.unique_winners = True
        
        # Results
        self.ended = False
        self.winners: List[discord.Member] = []
        self.participants: Set[int] = set()


class GiveawayManager:
    """Manages active giveaways"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways: Dict[str, Giveaway] = {}
        self.giveaway_tasks: Dict[str, asyncio.Task] = {}
    
    def create_giveaway(self, **kwargs) -> Giveaway:
        """Create a new giveaway"""
        giveaway = Giveaway(**kwargs)
        self.active_giveaways[giveaway.id] = giveaway
        
        # Schedule end if duration is set
        if giveaway.duration:
            task = asyncio.create_task(self._schedule_end(giveaway))
            self.giveaway_tasks[giveaway.id] = task
        
        return giveaway
    
    async def _schedule_end(self, giveaway: Giveaway):
        """Schedule giveaway end"""
        if giveaway.ends_at:
            wait_time = (giveaway.ends_at - datetime.utcnow()).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                if not giveaway.ended:
                    await self.end_giveaway(giveaway.id)
    
    async def end_giveaway(self, giveaway_id: str) -> Optional[List[discord.Member]]:
        """End a giveaway and pick winners"""
        giveaway = self.active_giveaways.get(giveaway_id)
        if not giveaway or giveaway.ended:
            return None
        
        # Get participants based on type
        participants = await self._get_participants(giveaway)
        
        if not participants:
            giveaway.ended = True
            return []
        
        # Pick winners
        winners = []
        available_participants = list(participants)
        
        for _ in range(min(giveaway.winners_count, len(available_participants))):
            if not available_participants:
                break
                
            winner = random.choice(available_participants)
            winners.append(winner)
            
            if giveaway.unique_winners:
                available_participants.remove(winner)
        
        giveaway.winners = winners
        giveaway.ended = True
        
        # Cancel scheduled task if exists
        if giveaway_id in self.giveaway_tasks:
            self.giveaway_tasks[giveaway_id].cancel()
            del self.giveaway_tasks[giveaway_id]
        
        return winners
    
    async def _get_participants(self, giveaway: Giveaway) -> List[discord.Member]:
        """Get participants based on giveaway type"""
        participants = []
        
        if giveaway.type == GiveawayType.MESSAGE:
            # Get messages from channel
            messages = []
            async for message in giveaway.channel.history(limit=1000):
                if message.created_at < giveaway.created_at:
                    break
                    
                # Check author type
                if message.author.bot and giveaway.exclude_bots:
                    continue
                if message.webhook_id and not giveaway.include_webhooks:
                    continue
                    
                # Check if member meets role requirements
                if isinstance(message.author, discord.Member):
                    if self._check_role_requirements(message.author, giveaway):
                        messages.append(message)
            
            # Get unique authors
            seen = set()
            for message in messages:
                if message.author.id not in seen:
                    participants.append(message.author)
                    seen.add(message.author.id)
                    
        elif giveaway.type == GiveawayType.ROLE:
            # Get members with required roles
            for member in giveaway.channel.guild.members:
                if member.bot and giveaway.exclude_bots:
                    continue
                    
                if self._check_role_requirements(member, giveaway):
                    participants.append(member)
                    
        elif giveaway.type == GiveawayType.REACTION:
            # Get users who reacted to message
            if giveaway.message_id:
                try:
                    message = await giveaway.channel.fetch_message(giveaway.message_id)
                    for reaction in message.reactions:
                        async for user in reaction.users():
                            if isinstance(user, discord.Member):
                                if user.bot and giveaway.exclude_bots:
                                    continue
                                if self._check_role_requirements(user, giveaway):
                                    if user not in participants:
                                        participants.append(user)
                except discord.NotFound:
                    pass
        
        return participants
    
    def _check_role_requirements(self, member: discord.Member, giveaway: Giveaway) -> bool:
        """Check if member meets role requirements"""
        if not giveaway.required_roles:
            return True
        
        member_roles = set(member.roles)
        required_roles = set(giveaway.required_roles)
        
        if giveaway.requirement_type == GiveawayRequirement.AND:
            return required_roles.issubset(member_roles)
        else:  # OR
            return bool(required_roles.intersection(member_roles))


class GiveawayView(discord.ui.View):
    """View for giveaway configuration"""
    def __init__(self, manager: GiveawayManager, giveaway: Giveaway):
        super().__init__(timeout=300)
        self.manager = manager
        self.giveaway = giveaway
        
    @discord.ui.button(label='Dodaj Rolę', style=discord.ButtonStyle.primary)
    async def add_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add role requirement"""
        # This would open a role select menu
        await interaction.response.send_message("Wybierz rolę do dodania...", ephemeral=True)
        
    @discord.ui.button(label='Start', style=discord.ButtonStyle.success)
    async def start_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start the giveaway"""
        await interaction.response.send_message("🎉 Giveaway rozpoczęty!", ephemeral=True)
        self.stop()


class GiveawayCommands(commands.Cog):
    """Giveaway commands for GOLEM bots"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = GiveawayManager(bot)
    
    @commands.hybrid_group(name='giveaway', description='Zarządzaj giveaway')
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx: commands.Context):
        """Giveaway command group"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @giveaway.command(name='message', description='Losuj z wiadomości w kanale')
    async def giveaway_message(
        self,
        ctx: commands.Context,
        winners: int,
        prize: str,
        channel: Optional[discord.TextChannel] = None
    ):
        """Create a message-based giveaway"""
        channel = channel or ctx.channel
        
        # Create giveaway
        giveaway = self.manager.create_giveaway(
            host=ctx.author,
            prize=prize,
            winners_count=winners,
            giveaway_type=GiveawayType.MESSAGE,
            channel=channel
        )
        
        embed = discord.Embed(
            title="🎉 Giveaway z Wiadomości",
            description=f"Losuję **{winners}** zwycięzców z wiadomości w {channel.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Nagroda", value=prize)
        embed.add_field(name="Host", value=ctx.author.mention)
        embed.set_footer(text="Użyj /giveaway end aby zakończyć")
        
        await ctx.send(embed=embed)
        
        # End immediately for message giveaways
        winners = await self.manager.end_giveaway(giveaway.id)
        
        if winners:
            winner_mentions = [w.mention for w in winners]
            result_embed = discord.Embed(
                title="🎊 Zwycięzcy Giveaway!",
                description=f"Gratulacje!\n" + "\n".join(winner_mentions),
                color=discord.Color.gold()
            )
            result_embed.add_field(name="Nagroda", value=prize)
            await ctx.send(embed=result_embed)
        else:
            await ctx.send("❌ Brak uczestników spełniających wymagania!")
    
    @giveaway.command(name='role', description='Losuj z członków z określonymi rolami')
    async def giveaway_role(
        self,
        ctx: commands.Context,
        winners: int,
        prize: str,
        *roles: discord.Role
    ):
        """Create a role-based giveaway"""
        if not roles:
            await ctx.send("❌ Musisz podać przynajmniej jedną rolę!")
            return
        
        # Create giveaway
        giveaway = self.manager.create_giveaway(
            host=ctx.author,
            prize=prize,
            winners_count=winners,
            giveaway_type=GiveawayType.ROLE,
            channel=ctx.channel
        )
        
        giveaway.required_roles = list(roles)
        giveaway.requirement_type = GiveawayRequirement.OR  # Any role
        
        embed = discord.Embed(
            title="🎉 Giveaway Rolowy",
            description=f"Losuję **{winners}** zwycięzców z członków z rolami",
            color=discord.Color.blue()
        )
        embed.add_field(name="Nagroda", value=prize)
        embed.add_field(name="Wymagane Role", value=" lub ".join([r.mention for r in roles]))
        embed.add_field(name="Host", value=ctx.author.mention)
        
        await ctx.send(embed=embed)
        
        # End immediately
        winners_list = await self.manager.end_giveaway(giveaway.id)
        
        if winners_list:
            winner_mentions = [w.mention for w in winners_list]
            result_embed = discord.Embed(
                title="🎊 Zwycięzcy Giveaway!",
                description=f"Gratulacje!\n" + "\n".join(winner_mentions),
                color=discord.Color.gold()
            )
            result_embed.add_field(name="Nagroda", value=prize)
            await ctx.send(embed=result_embed)
        else:
            await ctx.send("❌ Brak uczestników z wymaganymi rolami!")
    
    @giveaway.command(name='reaction', description='Losuj z reakcji pod wiadomością')
    async def giveaway_reaction(
        self,
        ctx: commands.Context,
        winners: int,
        prize: str,
        duration: str = "1h"
    ):
        """Create a reaction-based giveaway"""
        # Parse duration
        time_dict = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = duration[-1]
        if unit not in time_dict:
            await ctx.send("❌ Nieprawidłowy format czasu! Użyj: 1h, 30m, etc.")
            return
        
        amount = int(duration[:-1])
        seconds = amount * time_dict[unit]
        
        # Create giveaway
        giveaway = self.manager.create_giveaway(
            host=ctx.author,
            prize=prize,
            winners_count=winners,
            giveaway_type=GiveawayType.REACTION,
            channel=ctx.channel,
            duration=timedelta(seconds=seconds)
        )
        
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Nagroda:** {prize}\n\nReaguj 🎉 aby wziąć udział!",
            color=discord.Color.blue(),
            timestamp=giveaway.ends_at
        )
        embed.add_field(name="Zwycięzców", value=str(winners))
        embed.add_field(name="Czas", value=duration)
        embed.add_field(name="Host", value=ctx.author.mention)
        embed.set_footer(text="Kończy się")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction('🎉')
        
        giveaway.message_id = message.id
        
        # Wait for end
        await asyncio.sleep(seconds)
        
        # End giveaway
        winners_list = await self.manager.end_giveaway(giveaway.id)
        
        if winners_list:
            winner_mentions = [w.mention for w in winners_list]
            result_embed = discord.Embed(
                title="🎊 Giveaway Zakończony!",
                description=f"**Zwycięzcy:**\n" + "\n".join(winner_mentions),
                color=discord.Color.gold()
            )
            result_embed.add_field(name="Nagroda", value=prize)
            await message.reply(embed=result_embed)
        else:
            await message.reply("❌ Nikt nie wziął udziału w giveaway!")
    
    @giveaway.command(name='list', description='Lista aktywnych giveaway')
    async def giveaway_list(self, ctx: commands.Context):
        """List active giveaways"""
        active = [g for g in self.manager.active_giveaways.values() if not g.ended]
        
        if not active:
            await ctx.send("Brak aktywnych giveaway!")
            return
        
        embed = discord.Embed(
            title="Aktywne Giveaway",
            color=discord.Color.blue()
        )
        
        for giveaway in active:
            time_left = "N/A"
            if giveaway.ends_at:
                remaining = giveaway.ends_at - datetime.utcnow()
                if remaining.total_seconds() > 0:
                    time_left = f"{int(remaining.total_seconds() // 60)}m"
            
            embed.add_field(
                name=f"{giveaway.prize}",
                value=f"Host: {giveaway.host.mention}\n"
                      f"Typ: {giveaway.type.value}\n"
                      f"Pozostało: {time_left}",
                inline=False
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(GiveawayCommands(bot))
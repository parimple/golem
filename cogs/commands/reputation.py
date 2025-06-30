"""
Reputation system with positive and negative reputation
Based on BOHT bot functionality
"""
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import re
from enum import Enum

class ReputationType(Enum):
    POSITIVE = 1
    NEGATIVE = -1

class ReputationData:
    """Container for reputation information"""
    def __init__(self):
        self.positive_rep: int = 0
        self.negative_rep: int = 0
        self.last_given: Dict[int, datetime] = {}  # user_id -> last time
        self.history: List[Tuple[int, ReputationType, datetime]] = []  # (from_user, type, when)
    
    @property
    def total_rep(self) -> int:
        """Calculate total reputation"""
        return self.positive_rep - self.negative_rep
    
    def can_give_to(self, user_id: int, cooldown_hours: int = 24) -> Tuple[bool, Optional[timedelta]]:
        """Check if can give reputation to user"""
        if user_id not in self.last_given:
            return True, None
        
        time_passed = datetime.utcnow() - self.last_given[user_id]
        cooldown = timedelta(hours=cooldown_hours)
        
        if time_passed >= cooldown:
            return True, None
        
        remaining = cooldown - time_passed
        return False, remaining


class Reputation(commands.Cog):
    """Reputation commands - positive and negative"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reputation_data: Dict[int, ReputationData] = {}
        self.cooldown_hours = 24
        self.min_account_age_days = 7
        self.min_server_age_days = 3
        
        # Check if negative reputation is enabled for this profile
        self.negative_enabled = bot.features.get('reputation_negative', True)
    
    def get_user_data(self, user_id: int) -> ReputationData:
        """Get or create user reputation data"""
        if user_id not in self.reputation_data:
            self.reputation_data[user_id] = ReputationData()
        return self.reputation_data[user_id]
    
    async def give_reputation(
        self, 
        from_member: discord.Member, 
        to_member: discord.Member,
        rep_type: ReputationType
    ) -> Dict:
        """Give reputation with all checks"""
        
        result = {
            'success': False,
            'message': '',
            'cooldown_remaining': None
        }
        
        # Self-check
        if from_member.id == to_member.id:
            result['message'] = "Nie możesz dać reputacji samemu sobie!"
            return result
        
        # Bot check
        if to_member.bot:
            result['message'] = "Nie możesz dać reputacji botom!"
            return result
        
        # Account age check
        account_age = datetime.utcnow() - from_member.created_at
        if account_age.days < self.min_account_age_days:
            result['message'] = f"Twoje konto musi mieć minimum {self.min_account_age_days} dni!"
            return result
        
        # Server age check
        if from_member.joined_at:
            server_age = datetime.utcnow() - from_member.joined_at
            if server_age.days < self.min_server_age_days:
                result['message'] = f"Musisz być na serwerze minimum {self.min_server_age_days} dni!"
                return result
        
        # Get reputation data
        from_data = self.get_user_data(from_member.id)
        to_data = self.get_user_data(to_member.id)
        
        # Cooldown check
        can_give, remaining = from_data.can_give_to(to_member.id, self.cooldown_hours)
        if not can_give:
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            result['message'] = f"Musisz poczekać {hours}h {minutes}m przed kolejną reputacją dla tego użytkownika!"
            result['cooldown_remaining'] = remaining
            return result
        
        # Give reputation
        if rep_type == ReputationType.POSITIVE:
            to_data.positive_rep += 1
        else:
            to_data.negative_rep += 1
        
        # Update cooldown
        from_data.last_given[to_member.id] = datetime.utcnow()
        
        # Add to history
        to_data.history.append((from_member.id, rep_type, datetime.utcnow()))
        
        result['success'] = True
        result['message'] = f"{'Dodano' if rep_type == ReputationType.POSITIVE else 'Odjęto'} reputację!"
        return result
    
    @commands.hybrid_command(name='rep', aliases=['addrep', '+rep'], description='Daj pozytywną reputację użytkownikowi')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_positive_rep(self, ctx: commands.Context, member: discord.Member):
        """Give positive reputation to a user"""
        result = await self.give_reputation(
            ctx.author, 
            member, 
            ReputationType.POSITIVE
        )
        
        if result['success']:
            embed = discord.Embed(
                title="✅ Reputacja Dodana",
                description=f"{ctx.author.mention} dał **+1** reputacji {member.mention}!",
                color=discord.Color.green()
            )
            
            # Add total reputation
            user_data = self.get_user_data(member.id)
            embed.add_field(
                name="Łączna Reputacja",
                value=f"**{user_data.total_rep}** (➕{user_data.positive_rep} | ➖{user_data.negative_rep})"
            )
        else:
            embed = discord.Embed(
                title="❌ Błąd",
                description=result['message'],
                color=discord.Color.red()
            )
            
            if result['cooldown_remaining']:
                embed.set_footer(text="Spróbuj ponownie później")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='-rep', aliases=['removerep', 'minusrep'], description='Daj negatywną reputację użytkownikowi')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_negative_rep(self, ctx: commands.Context, member: discord.Member):
        """Give negative reputation to a user"""
        # Check if negative reputation is enabled
        if not self.negative_enabled:
            embed = discord.Embed(
                title="❌ Funkcja Wyłączona",
                description="Negatywna reputacja nie jest dostępna w tym profilu bota.",
                color=self.bot.colors['error']
            )
            await ctx.send(embed=embed)
            return
        result = await self.give_reputation(
            ctx.author, 
            member, 
            ReputationType.NEGATIVE
        )
        
        if result['success']:
            embed = discord.Embed(
                title="❌ Reputacja Odjęta",
                description=f"{ctx.author.mention} dał **-1** reputacji {member.mention}!",
                color=discord.Color.red()
            )
            
            # Add total reputation
            user_data = self.get_user_data(member.id)
            embed.add_field(
                name="Łączna Reputacja",
                value=f"**{user_data.total_rep}** (➕{user_data.positive_rep} | ➖{user_data.negative_rep})"
            )
        else:
            embed = discord.Embed(
                title="❌ Błąd",
                description=result['message'],
                color=discord.Color.red()
            )
            
            if result['cooldown_remaining']:
                embed.set_footer(text="Spróbuj ponownie później")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='repinfo', aliases=['reputation', 'myrep'], description='Sprawdź swoją lub czyjąś reputację')
    async def rep_info(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Check reputation info"""
        target = member or ctx.author
        user_data = self.get_user_data(target.id)
        
        # Determine embed color based on reputation
        if user_data.total_rep > 0:
            color = discord.Color.green()
        elif user_data.total_rep < 0:
            color = discord.Color.red()
        else:
            color = discord.Color.blue()
        
        embed = discord.Embed(
            title=f"Reputacja {target.display_name}",
            color=color
        )
        
        # Main reputation display
        embed.add_field(
            name="Łączna Reputacja",
            value=f"**{user_data.total_rep}**",
            inline=False
        )
        embed.add_field(name="➕ Pozytywna", value=str(user_data.positive_rep), inline=True)
        embed.add_field(name="➖ Negatywna", value=str(user_data.negative_rep), inline=True)
        
        # Add reputation bar visualization
        total_reps = user_data.positive_rep + user_data.negative_rep
        if total_reps > 0:
            positive_ratio = user_data.positive_rep / total_reps
            bar_length = 10
            positive_blocks = int(positive_ratio * bar_length)
            negative_blocks = bar_length - positive_blocks
            
            bar = "🟩" * positive_blocks + "🟥" * negative_blocks
            embed.add_field(
                name="Proporcje",
                value=bar,
                inline=False
            )
        
        # Recent history
        if user_data.history:
            recent = user_data.history[-5:]  # Last 5
            history_text = []
            for giver_id, rep_type, when in reversed(recent):
                giver = self.bot.get_user(giver_id)
                giver_name = giver.name if giver else f"User {giver_id}"
                type_emoji = "➕" if rep_type == ReputationType.POSITIVE else "➖"
                time_ago = datetime.utcnow() - when
                
                if time_ago.days > 0:
                    time_str = f"{time_ago.days}d temu"
                elif time_ago.seconds > 3600:
                    time_str = f"{time_ago.seconds // 3600}h temu"
                else:
                    time_str = f"{time_ago.seconds // 60}m temu"
                
                history_text.append(f"{type_emoji} od **{giver_name}** - {time_str}")
            
            embed.add_field(
                name="Ostatnie Transakcje",
                value="\n".join(history_text),
                inline=False
            )
        
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        embed.set_footer(text=f"Użyj !rep @user lub !-rep @user aby dać reputację")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='toprep', aliases=['reptop', 'repleaderboard'], description='Top 10 użytkowników z największą reputacją')
    async def top_reputation(self, ctx: commands.Context):
        """Show top 10 users by reputation"""
        # Get all users with reputation
        user_reps = []
        for user_id, data in self.reputation_data.items():
            if data.total_rep != 0:  # Only include users with non-zero reputation
                user_reps.append((user_id, data))
        
        # Sort by total reputation
        user_reps.sort(key=lambda x: x[1].total_rep, reverse=True)
        
        if not user_reps:
            embed = discord.Embed(
                description="Brak danych o reputacji!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🏆 Top 10 Reputacji",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        description = []
        for i, (user_id, data) in enumerate(user_reps[:10], 1):
            user = self.bot.get_user(user_id)
            if user:
                # Determine medal emoji
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"**{i}.**"
                
                name = user.display_name
                total = data.total_rep
                
                # Add + or - sign to total
                total_str = f"+{total}" if total > 0 else str(total)
                
                description.append(
                    f"{medal} {name} - **{total_str}** (➕{data.positive_rep} | ➖{data.negative_rep})"
                )
        
        embed.description = "\n".join(description)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='repstatus', aliases=['repcooldown', 'repcd'], description='Sprawdź swoje cooldowny reputacji')
    async def rep_status(self, ctx: commands.Context):
        """Check your reputation cooldowns"""
        user_data = self.get_user_data(ctx.author.id)
        
        embed = discord.Embed(
            title="⏰ Status Cooldownów Reputacji",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Check cooldowns
        cooldown_info = []
        available_count = 0
        
        for target_id, last_time in user_data.last_given.items():
            target = self.bot.get_user(target_id)
            if not target:
                continue
                
            can_give, remaining = user_data.can_give_to(target_id, self.cooldown_hours)
            
            if can_give:
                status = "✅ Dostępne"
                available_count += 1
            else:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                status = f"⏰ {hours}h {minutes}m"
            
            cooldown_info.append(f"**{target.name}**: {status}")
        
        if cooldown_info:
            embed.add_field(
                name=f"Cooldowny ({available_count} dostępnych)",
                value="\n".join(cooldown_info[:10]),  # Show max 10
                inline=False
            )
        else:
            embed.description = "Nie dałeś jeszcze nikomu reputacji!"
        
        # Account info
        account_age = datetime.utcnow() - ctx.author.created_at
        server_age = datetime.utcnow() - ctx.author.joined_at if ctx.author.joined_at else timedelta(0)
        
        embed.add_field(
            name="📅 Wiek Konta",
            value=f"{account_age.days} dni",
            inline=True
        )
        embed.add_field(
            name="🏠 Na Serwerze",
            value=f"{server_age.days} dni",
            inline=True
        )
        embed.add_field(
            name="⏱️ Cooldown",
            value=f"{self.cooldown_hours}h między rep",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='clearrep', description='Wyczyść całą reputację użytkownika (tylko admin)')
    @commands.has_permissions(administrator=True)
    async def clear_reputation(self, ctx: commands.Context, member: discord.Member):
        """Clear all reputation for a user (admin only)"""
        if member.id in self.reputation_data:
            old_data = self.reputation_data[member.id]
            old_total = old_data.total_rep
            del self.reputation_data[member.id]
            
            embed = discord.Embed(
                title="🗑️ Reputacja Wyczyszczona",
                description=f"Reputacja {member.mention} została wyczyszczona przez {ctx.author.mention}",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="Usunięto",
                value=f"**{old_total}** (➕{old_data.positive_rep} | ➖{old_data.negative_rep})"
            )
        else:
            embed = discord.Embed(
                title="ℹ️ Brak Danych",
                description=f"{member.mention} nie ma żadnej reputacji do wyczyszczenia.",
                color=discord.Color.blue()
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Reputation(bot))
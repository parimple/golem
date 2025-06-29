"""
Advanced reputation system for GOLEM bots
Includes anti-bot protection and comprehensive tracking
"""
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import re
import asyncio
from enum import Enum

class ReputationType(Enum):
    POSITIVE = 1
    NEGATIVE = -1

class ReputationProtection:
    """Anti-bot and abuse protection for reputation system"""
    
    # Suspicious username patterns
    SUSPICIOUS_PATTERNS = [
        r'^\d{4,}$',  # Only numbers
        r'^[a-zA-Z]{1,2}\d{3,}$',  # Letter(s) + numbers
        r'^user\d+$',  # user123 pattern
        r'^test',  # test accounts
        r'^bot',  # bot accounts
        r'^\W+$',  # Only special characters
    ]
    
    @classmethod
    def is_suspicious_username(cls, username: str) -> bool:
        """Check if username matches suspicious patterns"""
        username_lower = username.lower()
        
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.match(pattern, username_lower):
                return True
        
        # Check for too many numbers in proportion
        digit_ratio = sum(c.isdigit() for c in username) / len(username)
        if digit_ratio > 0.7:
            return True
            
        return False
    
    @classmethod
    def check_account_age(cls, member: discord.Member, min_days: int = 7) -> bool:
        """Check if account is old enough"""
        account_age = datetime.utcnow() - member.created_at
        return account_age.days >= min_days
    
    @classmethod
    def check_server_age(cls, member: discord.Member, min_days: int = 3) -> bool:
        """Check how long member has been in server"""
        if not member.joined_at:
            return False
        server_age = datetime.utcnow() - member.joined_at
        return server_age.days >= min_days


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


class ReputationSystem:
    """Core reputation system"""
    
    def __init__(self, bot, config: Dict):
        self.bot = bot
        self.config = config
        self.reputation_data: Dict[int, ReputationData] = {}  # user_id -> ReputationData
        
        # Configuration
        self.cooldown_hours = config.get('cooldown_hours', 24)
        self.min_account_age_days = config.get('min_account_age_days', 7)
        self.min_server_age_days = config.get('min_server_age_days', 3)
        self.allow_negative = config.get('allow_negative', True)
        self.require_mutual_server = config.get('require_mutual_server', True)
        
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
        if not ReputationProtection.check_account_age(from_member, self.min_account_age_days):
            result['message'] = f"Twoje konto musi mieć minimum {self.min_account_age_days} dni!"
            return result
        
        # Server age check
        if not ReputationProtection.check_server_age(from_member, self.min_server_age_days):
            result['message'] = f"Musisz być na serwerze minimum {self.min_server_age_days} dni!"
            return result
        
        # Suspicious username check
        if ReputationProtection.is_suspicious_username(from_member.name):
            result['message'] = "Twoja nazwa użytkownika została oznaczona jako podejrzana. Skontaktuj się z administracją."
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
        
        # Log transaction
        await self.log_reputation_transaction(from_member, to_member, rep_type)
        
        result['success'] = True
        result['message'] = f"{'Dodano' if rep_type == ReputationType.POSITIVE else 'Odjęto'} reputację!"
        return result
    
    async def log_reputation_transaction(
        self, 
        from_member: discord.Member, 
        to_member: discord.Member,
        rep_type: ReputationType
    ):
        """Log reputation transaction for audit"""
        log_channel_id = self.config.get('log_channel_id')
        if not log_channel_id:
            return
        
        channel = self.bot.get_channel(log_channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title="Transakcja Reputacji",
            color=discord.Color.green() if rep_type == ReputationType.POSITIVE else discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Od", value=f"{from_member.mention} ({from_member.id})")
        embed.add_field(name="Do", value=f"{to_member.mention} ({to_member.id})")
        embed.add_field(name="Typ", value="➕ Pozytywna" if rep_type == ReputationType.POSITIVE else "➖ Negatywna")
        
        # Add suspicious flags if any
        flags = []
        if ReputationProtection.is_suspicious_username(from_member.name):
            flags.append("⚠️ Podejrzana nazwa (od)")
        if ReputationProtection.is_suspicious_username(to_member.name):
            flags.append("⚠️ Podejrzana nazwa (do)")
        
        if flags:
            embed.add_field(name="Flagi", value="\n".join(flags), inline=False)
        
        await channel.send(embed=embed)
    
    def get_top_users(self, limit: int = 10) -> List[Tuple[int, int]]:
        """Get top users by reputation"""
        user_reps = [(user_id, data.total_rep) for user_id, data in self.reputation_data.items()]
        user_reps.sort(key=lambda x: x[1], reverse=True)
        return user_reps[:limit]


class ReputationCommands(commands.Cog):
    """Reputation commands for GOLEM bots"""
    
    def __init__(self, bot):
        self.bot = bot
        # Get config from bot
        rep_config = getattr(bot.config, 'reputation', {
            'cooldown_hours': 24,
            'min_account_age_days': 7,
            'min_server_age_days': 3,
            'allow_negative': True
        })
        self.reputation_system = ReputationSystem(bot, rep_config)
    
    @commands.hybrid_command(name='rep', description='Daj reputację użytkownikowi')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_rep(self, ctx: commands.Context, member: discord.Member):
        """Give positive reputation to a user"""
        result = await self.reputation_system.give_reputation(
            ctx.author, 
            member, 
            ReputationType.POSITIVE
        )
        
        if result['success']:
            embed = discord.Embed(
                title="✅ Reputacja Dodana",
                description=f"{ctx.author.mention} dał +1 reputacji {member.mention}!",
                color=discord.Color.green()
            )
            
            # Add total reputation
            user_data = self.reputation_system.get_user_data(member.id)
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
    
    @commands.hybrid_command(name='repinfo', description='Sprawdź swoją reputację')
    async def rep_info(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Check reputation info"""
        target = member or ctx.author
        user_data = self.reputation_system.get_user_data(target.id)
        
        embed = discord.Embed(
            title=f"Reputacja {target.display_name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Łączna Reputacja",
            value=f"**{user_data.total_rep}**",
            inline=False
        )
        embed.add_field(name="➕ Pozytywna", value=str(user_data.positive_rep))
        embed.add_field(name="➖ Negatywna", value=str(user_data.negative_rep))
        
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
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='toprep', description='Top 10 użytkowników z największą reputacją')
    async def top_reputation(self, ctx: commands.Context):
        """Show top 10 users by reputation"""
        top_users = self.reputation_system.get_top_users(10)
        
        if not top_users:
            embed = discord.Embed(
                description="Brak danych o reputacji!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🏆 Top 10 Reputacji",
            color=discord.Color.gold()
        )
        
        description = []
        for i, (user_id, total_rep) in enumerate(top_users, 1):
            user = self.bot.get_user(user_id)
            if user:
                user_data = self.reputation_system.get_user_data(user_id)
                name = user.display_name
                description.append(
                    f"**{i}.** {name} - **{total_rep}** (➕{user_data.positive_rep} | ➖{user_data.negative_rep})"
                )
        
        embed.description = "\n".join(description)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='repstatus', description='Sprawdź swój status reputacji')
    async def rep_status(self, ctx: commands.Context):
        """Check your reputation cooldowns"""
        user_data = self.reputation_system.get_user_data(ctx.author.id)
        
        embed = discord.Embed(
            title="Status Reputacji",
            color=discord.Color.blue()
        )
        
        # Check cooldowns
        cooldown_info = []
        for target_id, last_time in user_data.last_given.items():
            target = self.bot.get_user(target_id)
            if not target:
                continue
                
            can_give, remaining = user_data.can_give_to(target_id, self.reputation_system.cooldown_hours)
            
            if can_give:
                status = "✅ Dostępne"
            else:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                status = f"⏰ {hours}h {minutes}m"
            
            cooldown_info.append(f"**{target.name}**: {status}")
        
        if cooldown_info:
            embed.add_field(
                name="Cooldowny",
                value="\n".join(cooldown_info[:10]),  # Show max 10
                inline=False
            )
        else:
            embed.description = "Nie dałeś jeszcze nikomu reputacji!"
        
        # Account info
        account_age = datetime.utcnow() - ctx.author.created_at
        server_age = datetime.utcnow() - ctx.author.joined_at if ctx.author.joined_at else timedelta(0)
        
        embed.add_field(
            name="Wiek Konta",
            value=f"{account_age.days} dni",
            inline=True
        )
        embed.add_field(
            name="Na Serwerze",
            value=f"{server_age.days} dni",
            inline=True
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(ReputationCommands(bot))
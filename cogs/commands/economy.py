"""Economy commands for GOLEM."""

import discord
from discord.ext import commands
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EconomyCog(commands.Cog):
    """Basic economy system for GOLEM."""
    
    def __init__(self, bot):
        self.bot = bot
        # Simple in-memory storage for now
        self.balances = {}
    
    def get_balance(self, user_id: int) -> int:
        """Get user balance."""
        return self.balances.get(user_id, 0)
    
    def add_balance(self, user_id: int, amount: int) -> int:
        """Add to user balance."""
        current = self.get_balance(user_id)
        self.balances[user_id] = current + amount
        return self.balances[user_id]
    
    @commands.hybrid_command(name="balance", aliases=["bal", "wallet", "portfel"])
    async def balance(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Check your or someone else's balance."""
        target = member or ctx.author
        balance = self.get_balance(target.id)
        
        embed = discord.Embed(
            title="💰 Wallet Balance",
            description=f"{target.mention} has **{balance:,} G**",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="daily", aliases=["dzienny"])
    async def daily(self, ctx: commands.Context):
        """Claim your daily reward."""
        reward = 100
        new_balance = self.add_balance(ctx.author.id, reward)
        
        embed = discord.Embed(
            title="📅 Daily Reward",
            description=f"You claimed **{reward} G**!\nNew balance: **{new_balance:,} G**",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="pay", aliases=["transfer", "send"])
    async def pay(self, ctx: commands.Context, member: discord.Member, amount: int):
        """Transfer money to another user."""
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        sender_balance = self.get_balance(ctx.author.id)
        
        if sender_balance < amount:
            await ctx.send(f"❌ You don't have enough G! You have {sender_balance:,} G.")
            return
        
        # Transfer money
        self.add_balance(ctx.author.id, -amount)
        self.add_balance(member.id, amount)
        
        embed = discord.Embed(
            title="💸 Transfer Complete",
            description=f"{ctx.author.mention} sent **{amount:,} G** to {member.mention}",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="addmoney", aliases=["addbal"])
    @commands.has_permissions(administrator=True)
    async def add_money(self, ctx: commands.Context, member: discord.Member, amount: int):
        """Add money to a user's balance (Admin only)."""
        new_balance = self.add_balance(member.id, amount)
        
        embed = discord.Embed(
            title="💵 Balance Updated",
            description=f"Added **{amount:,} G** to {member.mention}\nNew balance: **{new_balance:,} G**",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="richest", aliases=["rich", "balancetop"])
    async def richest(self, ctx: commands.Context):
        """Show the richest users."""
        sorted_users = sorted(self.balances.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if not sorted_users:
            await ctx.send("No one has any money yet!")
            return
        
        embed = discord.Embed(
            title="💎 Richest Users",
            color=discord.Color.gold()
        )
        
        description = ""
        for i, (user_id, balance) in enumerate(sorted_users, 1):
            user = self.bot.get_user(user_id)
            if user:
                description += f"**{i}.** {user.mention} - {balance:,} G\n"
        
        embed.description = description
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(EconomyCog(bot))
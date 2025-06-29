"""Premium system commands for GOLEM."""

import discord
from discord.ext import commands
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PremiumCog(commands.Cog):
    """Premium roles and benefits management."""
    
    def __init__(self, bot):
        self.bot = bot
        # Track premium users (in-memory for now)
        self.premium_users: Dict[int, List[str]] = {}  # user_id: [role_names]
        
    def get_premium_config(self) -> List[Dict]:
        """Get premium roles configuration."""
        if self.bot.config:
            return self.bot.config.get_premium_roles()
        return []
    
    def has_premium(self, member: discord.Member) -> bool:
        """Check if member has any premium role."""
        if not self.bot.config:
            return False
            
        premium_role_names = self.bot.config.get_premium_role_names()
        
        for role in member.roles:
            if role.name in premium_role_names:
                return True
        
        return False
    
    def get_member_premium_roles(self, member: discord.Member) -> List[str]:
        """Get list of premium roles the member has."""
        if not self.bot.config:
            return []
            
        premium_role_names = self.bot.config.get_premium_role_names()
        member_premium = []
        
        for role in member.roles:
            if role.name in premium_role_names:
                member_premium.append(role.name)
        
        return member_premium
    
    @commands.hybrid_command(name="premium", aliases=["vip"])
    async def premium(self, ctx: commands.Context):
        """Show premium roles and benefits."""
        premium_roles = self.get_premium_config()
        
        if not premium_roles:
            await ctx.send("No premium roles configured!")
            return
        
        embed = discord.Embed(
            title="💎 Premium Roles",
            description="Support the server and get exclusive benefits!",
            color=discord.Color.gold()
        )
        
        for role in premium_roles:
            features = "\n".join([f"• {feature}" for feature in role.get('features', [])])
            
            field_value = f"**Price:** {role.get('price', 'N/A')} PLN"
            if 'usd' in role:
                field_value += f" (${role['usd']})"
            field_value += f"\n\n{features}"
            
            embed.add_field(
                name=f"{role['name']} - {role.get('premium', 'Premium')}",
                value=field_value,
                inline=False
            )
        
        # Add donation link if configured
        if self.bot.config:
            donate_url = self.bot.config.get('donate_url')
            if donate_url:
                embed.add_field(
                    name="💖 Support Us",
                    value=f"[Click here to donate]({donate_url})",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mypremium", aliases=["myrank"])
    async def my_premium(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Check your premium status."""
        target = member or ctx.author
        
        premium_roles = self.get_member_premium_roles(target)
        
        if not premium_roles:
            embed = discord.Embed(
                title="❌ No Premium",
                description=f"{target.mention} doesn't have any premium roles.\nUse `,premium` to see available roles!",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="💎 Premium Status",
                description=f"{target.mention}'s premium roles:",
                color=discord.Color.gold()
            )
            
            # Get benefits for each role
            premium_config = self.get_premium_config()
            
            for role_name in premium_roles:
                # Find the role config
                role_config = next((r for r in premium_config if r['name'] == role_name), None)
                if role_config:
                    features = "\n".join([f"• {feature}" for feature in role_config.get('features', [])])
                    embed.add_field(
                        name=f"{role_name} - {role_config.get('premium', 'Premium')}",
                        value=features or "No features listed",
                        inline=False
                    )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="givepremium")
    @commands.has_permissions(administrator=True)
    async def give_premium(self, ctx: commands.Context, member: discord.Member, role_name: str):
        """Give premium role to a member (Admin only)."""
        # Find the role
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if not role:
            await ctx.send(f"❌ Role '{role_name}' not found!")
            return
        
        # Check if it's a premium role
        premium_role_names = self.bot.config.get_premium_role_names() if self.bot.config else []
        if role_name not in premium_role_names:
            await ctx.send(f"❌ '{role_name}' is not a premium role!")
            return
        
        # Give the role
        try:
            await member.add_roles(role)
            
            embed = discord.Embed(
                title="✅ Premium Granted",
                description=f"{member.mention} received **{role_name}**!",
                color=discord.Color.green()
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage roles!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name="removepremium")
    @commands.has_permissions(administrator=True)
    async def remove_premium(self, ctx: commands.Context, member: discord.Member, role_name: str):
        """Remove premium role from a member (Admin only)."""
        # Find the role
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if not role:
            await ctx.send(f"❌ Role '{role_name}' not found!")
            return
        
        # Remove the role
        try:
            await member.remove_roles(role)
            
            embed = discord.Embed(
                title="✅ Premium Removed",
                description=f"Removed **{role_name}** from {member.mention}",
                color=discord.Color.orange()
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage roles!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name="team", aliases=["druzyna"])
    async def team(self, ctx: commands.Context):
        """Manage your premium team."""
        if not self.has_premium(ctx.author):
            await ctx.send("❌ You need a premium role to manage teams!")
            return
        
        premium_roles = self.get_member_premium_roles(ctx.author)
        highest_role = premium_roles[0]  # Assume first is highest
        
        # Get team size limit
        premium_config = self.get_premium_config()
        role_config = next((r for r in premium_config if r['name'] == highest_role), None)
        
        if not role_config:
            await ctx.send("❌ Could not find premium configuration!")
            return
        
        team_size = role_config.get('team_size', 0)
        
        if team_size == 0:
            await ctx.send("❌ Your premium tier doesn't include team features!")
            return
        
        embed = discord.Embed(
            title="👥 Team Management",
            description=f"Your {highest_role} allows a team of up to **{team_size}** members",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Commands",
            value=(
                "`,team add @member` - Add member to team\n"
                "`,team remove @member` - Remove from team\n"
                "`,team list` - Show team members"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(PremiumCog(bot))
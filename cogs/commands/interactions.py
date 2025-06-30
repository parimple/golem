"""
Social interaction commands like hug, slap, kiss etc.
Based on BOHT bot functionality
"""
import discord
from discord.ext import commands
from typing import Optional
import random
from datetime import datetime

class Interactions(commands.Cog):
    """Social interaction commands"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # GIF URLs for different interactions
        self.gifs = {
            'hug': [
                'https://media.giphy.com/media/3bqtLDeiDtwhq/giphy.gif',
                'https://media.giphy.com/media/lrr9rHuoJOE0w/giphy.gif',
                'https://media.giphy.com/media/svXXBgduBsJ1u/giphy.gif',
                'https://media.giphy.com/media/EvYHHSntaIl5m/giphy.gif',
                'https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif'
            ],
            'slap': [
                'https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif',
                'https://media.giphy.com/media/xUO4t2gkWBxDi/giphy.gif',
                'https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif',
                'https://media.giphy.com/media/RXGNsyRb1hDJm/giphy.gif',
                'https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif'
            ],
            'kiss': [
                'https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif',
                'https://media.giphy.com/media/zkppEMFvRX5FC/giphy.gif',
                'https://media.giphy.com/media/ka2Ik9BbgNmU0/giphy.gif',
                'https://media.giphy.com/media/nyGFcsP0kAobm/giphy.gif',
                'https://media.giphy.com/media/dP8ONh1mN8YWQ/giphy.gif'
            ],
            'pat': [
                'https://media.giphy.com/media/4HP0ddZnNVvKU/giphy.gif',
                'https://media.giphy.com/media/Z7x24IHBcmV7W/giphy.gif',
                'https://media.giphy.com/media/X9MUeQelKifU4/giphy.gif',
                'https://media.giphy.com/media/5tmRHwTlHAA9WkVxTU/giphy.gif',
                'https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif'
            ],
            'cuddle': [
                'https://media.giphy.com/media/3bqtLDeiDtwhq/giphy.gif',
                'https://media.giphy.com/media/wnsgren9NtITS/giphy.gif',
                'https://media.giphy.com/media/A3ZsM7GCxNUvC/giphy.gif',
                'https://media.giphy.com/media/svXXBgduBsJ1u/giphy.gif',
                'https://media.giphy.com/media/143v0Z4767T15e/giphy.gif'
            ],
            'poke': [
                'https://media.giphy.com/media/FdinyvXRa8zekBkcdK/giphy.gif',
                'https://media.giphy.com/media/pWd3gD577gOqs/giphy.gif',
                'https://media.giphy.com/media/LXTQN2kRbaqAw/giphy.gif',
                'https://media.giphy.com/media/WvVzZ9mCyMjsc/giphy.gif',
                'https://media.giphy.com/media/4PHy5rR2Iu8N2/giphy.gif'
            ]
        }
        
        # Action messages
        self.messages = {
            'hug': '{author} przytula {target}! 🤗',
            'slap': '{author} daje klapsa {target}! 👋',
            'kiss': '{author} całuje {target}! 💋',
            'pat': '{author} głaszcze {target}! 🤚',
            'cuddle': '{author} przytula się do {target}! 🫂',
            'poke': '{author} szturchnął {target}! 👉'
        }
    
    def create_interaction_embed(self, ctx: commands.Context, target: discord.Member, action: str) -> discord.Embed:
        """Create embed for interaction"""
        message = self.messages[action].format(
            author=ctx.author.display_name,
            target=target.display_name
        )
        
        embed = discord.Embed(
            description=message,
            color=discord.Color.pink(),
            timestamp=datetime.utcnow()
        )
        
        # Add random GIF
        if action in self.gifs:
            embed.set_image(url=random.choice(self.gifs[action]))
        
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        return embed
    
    @commands.hybrid_command(name='hug', aliases=['przytul'], description='Przytul kogoś!')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hug(self, ctx: commands.Context, member: discord.Member):
        """Hug someone!"""
        if member == ctx.author:
            await ctx.send("Nie możesz przytulić samego siebie! Przytulę cię ja! 🤗")
            member = ctx.guild.me
        
        embed = self.create_interaction_embed(ctx, member, 'hug')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='slap', aliases=['klaps', 'uderz'], description='Daj komuś klapsa!')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slap(self, ctx: commands.Context, member: discord.Member):
        """Slap someone!"""
        if member == ctx.author:
            await ctx.send("Nie bij się! 😢")
            return
        
        if member == ctx.guild.me:
            await ctx.send(f"Jak śmiesz! {ctx.author.mention} dostaje klapsa w rewanżu! 👋")
            member = ctx.author
        
        embed = self.create_interaction_embed(ctx, member, 'slap')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='kiss', aliases=['pocaluj', 'cmok'], description='Pocałuj kogoś!')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kiss(self, ctx: commands.Context, member: discord.Member):
        """Kiss someone!"""
        if member == ctx.author:
            await ctx.send("Nie możesz pocałować samego siebie! 😅")
            return
        
        embed = self.create_interaction_embed(ctx, member, 'kiss')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='pat', aliases=['poglaskaj', 'headpat'], description='Pogłaszcz kogoś!')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx: commands.Context, member: discord.Member):
        """Pat someone!"""
        if member == ctx.author:
            await ctx.send("*głaszcze cię po głowie* Proszę bardzo! 🤚")
            return
        
        embed = self.create_interaction_embed(ctx, member, 'pat')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='cuddle', aliases=['przytulas'], description='Przytul się do kogoś!')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cuddle(self, ctx: commands.Context, member: discord.Member):
        """Cuddle someone!"""
        if member == ctx.author:
            await ctx.send("Chodź, przytulę cię! 🫂")
            member = ctx.guild.me
        
        embed = self.create_interaction_embed(ctx, member, 'cuddle')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='poke', aliases=['szturchnij', 'dźgnij'], description='Szturchnij kogoś!')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def poke(self, ctx: commands.Context, member: discord.Member):
        """Poke someone!"""
        if member == ctx.author:
            await ctx.send("Po co się szturchasz? 🤔")
            return
        
        if member == ctx.guild.me:
            await ctx.send(f"*szturchnij z powrotem* Hej {ctx.author.mention}! 👉")
        
        embed = self.create_interaction_embed(ctx, member, 'poke')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='f', description='Press F to pay respects')
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def pay_respects(self, ctx: commands.Context, *, reason: Optional[str] = None):
        """Press F to pay respects"""
        embed = discord.Embed(
            title="🕯️ Wyrazy Szacunku",
            color=discord.Color.dark_gray(),
            timestamp=datetime.utcnow()
        )
        
        if reason:
            embed.description = f"**{ctx.author.display_name}** składa wyrazy szacunku\n\n*{reason}*"
        else:
            embed.description = f"**{ctx.author.display_name}** składa wyrazy szacunku"
        
        embed.set_footer(text="Press F to pay respects")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction('🇫')
    
    @commands.hybrid_command(name='ship', aliases=['love', 'milosc'], description='Sprawdź poziom miłości między dwoma osobami!')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ship(self, ctx: commands.Context, person1: discord.Member, person2: Optional[discord.Member] = None):
        """Check love compatibility between two people"""
        if person2 is None:
            person2 = ctx.author
        
        # Generate "random" but consistent percentage
        combined_id = person1.id + person2.id
        random.seed(combined_id)
        love_percent = random.randint(0, 100)
        random.seed()  # Reset seed
        
        # Create ship name
        name1 = person1.display_name
        name2 = person2.display_name
        ship_name = name1[:len(name1)//2] + name2[len(name2)//2:]
        
        # Determine relationship status
        if love_percent < 20:
            status = "💔 Nie ma szans..."
            color = discord.Color.dark_gray()
        elif love_percent < 40:
            status = "😕 Przyjaźń to maximum"
            color = discord.Color.orange()
        elif love_percent < 60:
            status = "💕 Jest potencjał!"
            color = discord.Color.gold()
        elif love_percent < 80:
            status = "💖 Świetna para!"
            color = discord.Color.pink()
        else:
            status = "💘 Idealni dla siebie!"
            color = discord.Color.red()
        
        # Create progress bar
        filled = int(love_percent / 10)
        bar = "❤️" * filled + "🖤" * (10 - filled)
        
        embed = discord.Embed(
            title="💕 Love Calculator",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Sprawdzam miłość między:",
            value=f"**{person1.mention}** & **{person2.mention}**",
            inline=False
        )
        
        embed.add_field(
            name="Ship Name",
            value=f"**{ship_name}**",
            inline=True
        )
        
        embed.add_field(
            name="Kompatybilność",
            value=f"**{love_percent}%**",
            inline=True
        )
        
        embed.add_field(
            name="Meter Miłości",
            value=bar,
            inline=False
        )
        
        embed.add_field(
            name="Status",
            value=status,
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Interactions(bot))
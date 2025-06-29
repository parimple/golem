"""Fun commands for GOLEM."""

import discord
from discord.ext import commands
import random
from typing import Optional
import asyncio

class FunCog(commands.Cog):
    """Fun and entertainment commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="coinflip", aliases=["flip", "coin"])
    async def coinflip(self, ctx: commands.Context):
        """Flip a coin."""
        result = random.choice(["Heads", "Tails"])
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="roll", aliases=["dice"])
    async def roll(self, ctx: commands.Context, dice: str = "1d6"):
        """Roll dice (e.g., 2d6, 1d20)."""
        try:
            parts = dice.lower().split('d')
            if len(parts) != 2:
                raise ValueError
            
            num_dice = int(parts[0]) if parts[0] else 1
            sides = int(parts[1])
            
            if num_dice > 100 or sides > 1000 or num_dice < 1 or sides < 1:
                await ctx.send("❌ Please keep dice reasonable (max 100 dice, 1000 sides)")
                return
            
            rolls = [random.randint(1, sides) for _ in range(num_dice)]
            total = sum(rolls)
            
            embed = discord.Embed(
                title="🎲 Dice Roll",
                color=discord.Color.blue()
            )
            
            if num_dice == 1:
                embed.description = f"You rolled a **{total}**"
            else:
                embed.description = f"Rolls: {', '.join(map(str, rolls))}\nTotal: **{total}**"
            
            await ctx.send(embed=embed)
            
        except:
            await ctx.send("❌ Invalid dice format! Use: `1d6`, `2d20`, etc.")
    
    @commands.hybrid_command(name="8ball", aliases=["ask", "magic8ball"])
    async def eight_ball(self, ctx: commands.Context, *, question: str):
        """Ask the magic 8-ball a question."""
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.purple()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="rps", aliases=["rockpaperscissors"])
    async def rps(self, ctx: commands.Context, choice: str = None):
        """Play rock, paper, scissors."""
        if not choice:
            await ctx.send("Choose: rock, paper, or scissors!")
            return
        
        choice = choice.lower()
        if choice not in ["rock", "paper", "scissors"]:
            await ctx.send("❌ Invalid choice! Pick rock, paper, or scissors.")
            return
        
        bot_choice = random.choice(["rock", "paper", "scissors"])
        
        # Determine winner
        if choice == bot_choice:
            result = "It's a tie! 🤝"
            color = discord.Color.yellow()
        elif (choice == "rock" and bot_choice == "scissors") or \
             (choice == "paper" and bot_choice == "rock") or \
             (choice == "scissors" and bot_choice == "paper"):
            result = "You win! 🎉"
            color = discord.Color.green()
        else:
            result = "You lose! 😔"
            color = discord.Color.red()
        
        emoji_map = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        
        embed = discord.Embed(
            title="Rock Paper Scissors",
            description=result,
            color=color
        )
        embed.add_field(name="Your Choice", value=f"{emoji_map[choice]} {choice.title()}", inline=True)
        embed.add_field(name="My Choice", value=f"{emoji_map[bot_choice]} {bot_choice.title()}", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="choose", aliases=["pick"])
    async def choose(self, ctx: commands.Context, *, options: str):
        """Choose between multiple options (separated by 'or' or ',')."""
        # Split by 'or' or comma
        if ' or ' in options.lower():
            choices = [c.strip() for c in options.split(' or ')]
        else:
            choices = [c.strip() for c in options.split(',')]
        
        if len(choices) < 2:
            await ctx.send("❌ Please provide at least 2 options separated by 'or' or commas!")
            return
        
        choice = random.choice(choices)
        
        embed = discord.Embed(
            title="🤔 I Choose...",
            description=f"**{choice}**",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="rate", aliases=["rating"])
    async def rate(self, ctx: commands.Context, *, thing: str):
        """Rate something from 0 to 10."""
        # Generate consistent rating for same input
        rating = sum(ord(c) for c in thing.lower()) % 11
        
        embed = discord.Embed(
            title="⭐ Rating",
            description=f"I rate **{thing}** a **{rating}/10**",
            color=discord.Color.blue()
        )
        
        # Add comment based on rating
        if rating >= 9:
            embed.add_field(name="Comment", value="Absolutely amazing! 🌟", inline=False)
        elif rating >= 7:
            embed.add_field(name="Comment", value="Pretty good! 👍", inline=False)
        elif rating >= 5:
            embed.add_field(name="Comment", value="Not bad, could be better 🤷", inline=False)
        elif rating >= 3:
            embed.add_field(name="Comment", value="Needs improvement 😐", inline=False)
        else:
            embed.add_field(name="Comment", value="Yikes... 😬", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="say", aliases=["echo"])
    async def say(self, ctx: commands.Context, *, message: str):
        """Make the bot say something."""
        # Delete original message if possible
        try:
            await ctx.message.delete()
        except:
            pass
        
        await ctx.send(message)
    
    @commands.hybrid_command(name="reverse", aliases=["backwards"])
    async def reverse(self, ctx: commands.Context, *, text: str):
        """Reverse text."""
        reversed_text = text[::-1]
        
        embed = discord.Embed(
            title="🔄 Reversed Text",
            description=reversed_text,
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mock", aliases=["spongebob"])
    async def mock(self, ctx: commands.Context, *, text: str):
        """MoCk SoMeOnE's TeXt."""
        mocked = ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
        
        embed = discord.Embed(
            title="🧽 Mocking Text",
            description=mocked,
            color=discord.Color.yellow()
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(FunCog(bot))
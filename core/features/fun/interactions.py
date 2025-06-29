"""
Fun interactions system for GOLEM bots
Provides social interactions, memes, and entertainment features
"""
import discord
from discord.ext import commands
import aiohttp
import random
from typing import Optional, Dict, List
import asyncio
from datetime import datetime, timedelta

class FunInteractions:
    """Fun and social interaction commands"""
    
    # GIF URLs for interactions
    INTERACTION_GIFS = {
        'hug': [
            'https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif',
            'https://media.giphy.com/media/3bqtLDeiDtwhq/giphy.gif',
        ],
        'kiss': [
            'https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif',
            'https://media.giphy.com/media/zkppEMFvRX5FC/giphy.gif',
        ],
        'slap': [
            'https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif',
            'https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif',
        ],
        'pat': [
            'https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif',
            'https://media.giphy.com/media/N0CIxcyPLputW/giphy.gif',
        ],
        'cuddle': [
            'https://media.giphy.com/media/l2QDSTa1bJSyqUSZO/giphy.gif',
            'https://media.giphy.com/media/143v0Z4767T15e/giphy.gif',
        ],
        'poke': [
            'https://media.giphy.com/media/WvVzZ9mCyMjsc/giphy.gif',
            'https://media.giphy.com/media/4PHt0xgIjqEBa/giphy.gif',
        ],
    }
    
    # 8ball responses
    EIGHTBALL_RESPONSES = [
        # Positive
        "Tak, zdecydowanie! 🎱",
        "Bez wątpienia! ✨",
        "Na pewno tak! 💫",
        "Możesz na to liczyć! 🌟",
        "Wszystko wskazuje na tak! 🎯",
        
        # Negative
        "Nie licz na to... 🚫",
        "Moje źródła mówią nie 📚",
        "Bardzo wątpliwe 🤔",
        "Lepiej nie... 😬",
        "Zdecydowanie nie! ❌",
        
        # Uncertain
        "Zapytaj ponownie później 🔮",
        "Trudno powiedzieć... 🌫️",
        "Skoncentruj się i zapytaj ponownie 🧘",
        "Nie mogę teraz przewidzieć 🔍",
        "Mgliście to widzę... 🌁"
    ]
    
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        
    async def setup(self):
        """Initialize the fun interactions system"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def create_interaction_embed(
        self, 
        ctx: commands.Context, 
        target: discord.Member, 
        action: str
    ) -> discord.Embed:
        """Create an embed for social interactions"""
        
        action_messages = {
            'hug': f'{ctx.author.mention} przytula {target.mention}! 🤗',
            'kiss': f'{ctx.author.mention} całuje {target.mention}! 💋',
            'slap': f'{ctx.author.mention} daje klapsa {target.mention}! 👋',
            'pat': f'{ctx.author.mention} głaszcze {target.mention}! 🤚',
            'cuddle': f'{ctx.author.mention} przytula się do {target.mention}! 🫂',
            'poke': f'{ctx.author.mention} szturchnął {target.mention}! 👉'
        }
        
        embed = discord.Embed(
            description=action_messages.get(action, f'{ctx.author.mention} interacts with {target.mention}!'),
            color=discord.Color.random()
        )
        
        # Add random GIF
        if action in self.INTERACTION_GIFS:
            gif_url = random.choice(self.INTERACTION_GIFS[action])
            embed.set_image(url=gif_url)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.timestamp = datetime.utcnow()
        
        return embed
    
    async def fetch_meme(self) -> Optional[Dict]:
        """Fetch a random meme from Reddit"""
        subreddits = ['memes', 'dankmemes', 'me_irl', 'wholesomememes']
        subreddit = random.choice(subreddits)
        
        try:
            async with self.session.get(
                f'https://www.reddit.com/r/{subreddit}/random/.json',
                headers={'User-Agent': 'GOLEM Discord Bot'}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    post = data[0]['data']['children'][0]['data']
                    
                    # Check if it's an image
                    if post['url'].endswith(('.jpg', '.png', '.gif')):
                        return {
                            'title': post['title'],
                            'url': post['url'],
                            'subreddit': post['subreddit'],
                            'author': post['author'],
                            'ups': post['ups']
                        }
        except Exception as e:
            print(f"Error fetching meme: {e}")
        
        return None
    
    async def get_animal_fact(self, animal: str) -> Optional[Dict]:
        """Get a random fact about an animal"""
        
        animal_apis = {
            'cat': 'https://catfact.ninja/fact',
            'dog': 'https://dog-api.kinduff.com/api/facts',
            'bird': 'https://some-random-api.ml/animal/bird',
            'fox': 'https://some-random-api.ml/animal/fox',
            'panda': 'https://some-random-api.ml/animal/panda'
        }
        
        if animal not in animal_apis:
            return None
        
        try:
            async with self.session.get(animal_apis[animal]) as response:
                if response.status == 200:
                    data = await response.json()
                    # Normalize response format
                    if animal == 'cat':
                        return {'fact': data['fact'], 'animal': 'cat'}
                    elif animal == 'dog':
                        return {'fact': data['facts'][0], 'animal': 'dog'}
                    else:
                        return {'fact': data['fact'], 'animal': animal, 'image': data.get('image')}
        except Exception as e:
            print(f"Error fetching animal fact: {e}")
        
        return None


class FunCommands(commands.Cog):
    """Fun commands for GOLEM bots"""
    
    def __init__(self, bot):
        self.bot = bot
        self.fun = FunInteractions(bot)
        
    async def cog_load(self):
        """Initialize the cog"""
        await self.fun.setup()
        
    async def cog_unload(self):
        """Cleanup the cog"""
        await self.fun.cleanup()
    
    @commands.hybrid_command(name='hug', description='Przytul kogoś!')
    async def hug(self, ctx: commands.Context, member: discord.Member):
        """Hug someone!"""
        if member == ctx.author:
            await ctx.send("Nie możesz przytulić samego siebie! Przytulę cię ja! 🤗")
            member = ctx.guild.me
        
        embed = await self.fun.create_interaction_embed(ctx, member, 'hug')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='slap', description='Daj komuś klapsa!')
    async def slap(self, ctx: commands.Context, member: discord.Member):
        """Slap someone!"""
        if member == ctx.author:
            await ctx.send("Nie bij się! 😢")
            return
        
        embed = await self.fun.create_interaction_embed(ctx, member, 'slap')
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='8ball', description='Zapytaj magiczną kulę!')
    async def eightball(self, ctx: commands.Context, *, question: str):
        """Ask the magic 8-ball!"""
        response = random.choice(FunInteractions.EIGHTBALL_RESPONSES)
        
        embed = discord.Embed(
            title="🎱 Magiczna Kula 8",
            color=discord.Color.purple()
        )
        embed.add_field(name="Pytanie", value=question, inline=False)
        embed.add_field(name="Odpowiedź", value=response, inline=False)
        embed.set_footer(text=f"Pytał: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='meme', description='Pokaż losowego mema!')
    async def meme(self, ctx: commands.Context):
        """Show a random meme!"""
        await ctx.defer()
        
        meme_data = await self.fun.fetch_meme()
        if not meme_data:
            await ctx.send("Nie mogłem znaleźć mema! Spróbuj ponownie 😢")
            return
        
        embed = discord.Embed(
            title=meme_data['title'],
            color=discord.Color.orange()
        )
        embed.set_image(url=meme_data['url'])
        embed.set_footer(text=f"r/{meme_data['subreddit']} • {meme_data['ups']} ⬆️")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='animal', description='Pokaż ciekawostkę o zwierzęciu!')
    async def animal(self, ctx: commands.Context):
        """Show an animal fact with selection menu"""
        
        # Create select menu
        class AnimalSelect(discord.ui.Select):
            def __init__(self, fun_interactions):
                self.fun = fun_interactions
                options = [
                    discord.SelectOption(label='Kot', value='cat', emoji='🐱'),
                    discord.SelectOption(label='Pies', value='dog', emoji='🐶'),
                    discord.SelectOption(label='Ptak', value='bird', emoji='🦜'),
                    discord.SelectOption(label='Lis', value='fox', emoji='🦊'),
                    discord.SelectOption(label='Panda', value='panda', emoji='🐼')
                ]
                super().__init__(placeholder='Wybierz zwierzę...', options=options)
            
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                
                fact_data = await self.fun.get_animal_fact(self.values[0])
                if not fact_data:
                    await interaction.followup.send("Nie mogłem znaleźć ciekawostki! 😢")
                    return
                
                embed = discord.Embed(
                    title=f"Ciekawostka o {self.values[0]}",
                    description=fact_data['fact'],
                    color=discord.Color.green()
                )
                
                if 'image' in fact_data:
                    embed.set_image(url=fact_data['image'])
                
                await interaction.followup.send(embed=embed)
        
        view = discord.ui.View()
        view.add_item(AnimalSelect(self.fun))
        
        await ctx.send("Wybierz zwierzę, o którym chcesz poznać ciekawostkę!", view=view)
    
    @commands.hybrid_command(name='why', description='Zapytaj dlaczego...')
    async def why(self, ctx: commands.Context):
        """Generate a random 'why' question"""
        subjects = [
            "niebo jest niebieskie",
            "trawa jest zielona",
            "koty mruczą",
            "psy szczekają",
            "ludzie się śmieją",
            "czas płynie do przodu",
            "pizza jest okrągła",
            "tydzień ma 7 dni",
            "rok ma 365 dni",
            "Discord jest fioletowy"
        ]
        
        question = f"Dlaczego {random.choice(subjects)}? 🤔"
        await ctx.send(question)
    
    @commands.hybrid_command(name='f', description='Press F to pay respects')
    async def pay_respects(self, ctx: commands.Context, *, reason: Optional[str] = None):
        """Press F to pay respects"""
        if reason:
            text = f"**{ctx.author.mention}** składa wyrazy szacunku dla:\n*{reason}*"
        else:
            text = f"**{ctx.author.mention}** składa wyrazy szacunku"
        
        embed = discord.Embed(
            description=f"{text}\n\n**F** 🕯️",
            color=discord.Color.dark_gray()
        )
        
        message = await ctx.send(embed=embed)
        await message.add_reaction('🇫')


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(FunCommands(bot))
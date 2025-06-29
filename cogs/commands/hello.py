"""Simple hello command for GOLEM."""

import time
from discord.ext import commands


class HelloCog(commands.Cog):
    """Test cog for GOLEM."""

    def __init__(self, bot):
        self.bot = bot
        self.created_at = time.time()

    @commands.hybrid_command(name="hello2", aliases=["hej", "czesc"])
    async def hello2(self, ctx):
        """Advanced hello world command."""
        load_time = time.time() - self.created_at
        await ctx.send(f"🌟 Hello from GOLEM! (Cog loaded {load_time:.2f}s ago)")


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(HelloCog(bot))
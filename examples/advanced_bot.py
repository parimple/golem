"""
GOLEM Advanced Example - Neural Commands and Self-Assembly
Shows the power hiding beneath the simplicity
"""
import os
from golem import transcend, neural_command
from core.quantum import QuantumObserver, Response
from core.self_assembly import SelfAssemblingModule
import discord
from discord.ext import commands


# Create a bot with advanced features
bot = transcend()


# Add a neural command that learns user preferences
@bot.command()
@neural_command(name="greet")
async def greet(ctx: commands.Context, style: str = "friendly"):
    """
    A greeting command that learns what style each user prefers
    The more you use it, the better it gets at predicting your preference
    """
    styles = {
        "friendly": "Hey there, {user}! 👋 Hope you're having an awesome day!",
        "formal": "Good day, {user}. How may I assist you today?",
        "cool": "Yo {user}! What's good? 😎",
        "quantum": "Greetings, {user}. Your quantum signature resonates beautifully today. ✨"
    }
    
    greeting = styles.get(style, styles["friendly"]).format(user=ctx.author.display_name)
    
    embed = discord.Embed(
        title=f"{style.title()} Greeting",
        description=greeting,
        color=discord.Color.blue()
    )
    
    # The neural wrapper learns this user prefers this style
    await ctx.send(embed=embed)


# Create a custom quantum observer for special behaviors
class MoodObserver(QuantumObserver):
    """Observes user mood from messages"""
    
    def can_observe(self, signal):
        return signal.intent == "message" and signal.context.get('content')
        
    async def observe(self, state, signal):
        content = signal.context['content'].lower()
        
        # Simple mood detection
        if any(word in content for word in ['happy', 'great', 'awesome', 'love']):
            mood = 'positive'
            response = "I'm sensing positive vibes! 🌟"
        elif any(word in content for word in ['sad', 'upset', 'angry', 'hate']):
            mood = 'negative'
            response = "I'm here if you need support. 💙"
        else:
            return None
            
        return Response(
            content=response,
            confidence=0.7,
            metadata={'mood': mood}
        )


# Create a self-assembling music module
class MusicModule(SelfAssemblingModule):
    """A music module that configures itself based on available resources"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.capabilities.commands = ['play', 'skip', 'queue']
        self.capabilities.features = ['youtube', 'spotify', 'soundcloud']
        
    async def _auto_configure(self):
        """Auto-configure based on what's available"""
        await super()._auto_configure()
        
        # Check for youtube-dl
        try:
            import youtube_dl
            self.config['youtube_enabled'] = True
        except ImportError:
            self.config['youtube_enabled'] = False
            
        # Optimize for available memory
        system = self.config.get('system', {})
        if system.get('memory_gb', 0) > 4:
            self.config['cache_songs'] = True
            self.config['max_cache_size'] = 100
        else:
            self.config['cache_songs'] = False
            
    async def process(self, input):
        """Process music commands"""
        # This would implement actual music functionality
        return {"status": "Music module is self-optimizing..."}


# Add our custom components on startup
@bot.event
async def on_ready():
    # Add mood observer to quantum core
    bot.quantum_core.add_observer(MoodObserver())
    
    # Register and create music module
    bot.module_factory.register(MusicModule)
    music = await bot.module_factory.create("MusicModule", "music_main")
    
    print(f"🎵 Music module configured: {music.config}")
    print(f"🧠 Neural commands ready to learn")
    print(f"⚛️ Quantum observers active")
    print(f"✨ {bot.user} has transcended!")


# Add a command that shows GOLEM's self-awareness
@bot.command()
async def status(ctx: commands.Context):
    """Shows GOLEM's self-awareness and health"""
    health = await bot._check_health()
    quantum = bot.quantum_core.health
    memory = bot.collective_memory.get_memory_health()
    
    embed = discord.Embed(
        title="🤖 GOLEM Status Report",
        color=discord.Color.green() if health['error_rate'] < 0.01 else discord.Color.orange()
    )
    
    # Quantum metrics
    embed.add_field(
        name="⚛️ Quantum Core",
        value=f"Coherence: {quantum['quantum_coherence']:.1%}\n"
              f"Observers: {quantum['observers']}\n"
              f"Interactions: {quantum['total_interactions']}",
        inline=True
    )
    
    # Memory metrics
    embed.add_field(
        name="🧠 Collective Memory",
        value=f"Echoes: {memory['total_echoes']}\n"
              f"Health: {memory['health_status']}\n"
              f"Authors: {memory['unique_authors']}",
        inline=True
    )
    
    # Performance metrics
    embed.add_field(
        name="📊 Performance",
        value=f"Commands: {bot.metrics['commands_processed']}\n"
              f"Errors: {health['error_rate']:.1%}\n"
              f"Delight: {health['user_delight']:.1%}",
        inline=True
    )
    
    # Self-assembling modules
    embed.add_field(
        name="🔧 Active Modules",
        value="\n".join([f"• {name}: {m.health.status}" for name, m in bot.modules.items()]) or "None",
        inline=False
    )
    
    await ctx.send(embed=embed)


# Add a command that demonstrates learning
@bot.command()
@neural_command(name="remember")
async def remember(ctx: commands.Context, *, memory: str):
    """
    Remember something in collective memory
    The bot learns what kinds of things you like to remember
    """
    # Store in collective memory
    echo = await bot.collective_memory.add_echo(
        content=memory,
        author_id=ctx.author.id,
        echo_type="memory",
        weight=2.0  # Important memories have more weight
    )
    
    embed = discord.Embed(
        title="💭 Memory Stored",
        description=f"I'll remember: *{memory}*",
        color=discord.Color.purple()
    )
    
    # Neural command learns patterns in what users remember
    embed.set_footer(text=f"Memory #{echo.id} | Weight: {echo.weight}")
    
    await ctx.send(embed=embed)


# Add a command to recall memories
@bot.command()
async def recall(ctx: commands.Context, query: str = None):
    """Recall memories from the collective"""
    memories = await bot.collective_memory.search_echoes(
        query=query,
        author_id=ctx.author.id if not query else None,
        limit=5
    )
    
    if not memories:
        await ctx.send("No memories found matching your query.")
        return
        
    embed = discord.Embed(
        title="🌟 Recalled Memories",
        color=discord.Color.blue()
    )
    
    for i, echo in enumerate(memories, 1):
        embed.add_field(
            name=f"Memory {i} (resonance: {echo.resonance})",
            value=f"{echo.content[:100]}..." if len(echo.content) > 100 else echo.content,
            inline=False
        )
        
    await ctx.send(embed=embed)


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        # Still just one line to run
        bot.run(token)
    else:
        print("Set DISCORD_TOKEN environment variable")
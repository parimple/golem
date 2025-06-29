"""
GOLEM Core - Full version with all systems
This extends the simple version with advanced features
"""
import asyncio
import logging
from typing import Optional
import discord
from discord.ext import commands

from golem_simple import GOLEM as SimpleGOLEM

# Import core systems (they'll be gradually activated)
try:
    from core.quantum import QuantumCore, Signal, Response
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False
    
try:
    from core.neural import neural_command
    NEURAL_AVAILABLE = True
except ImportError:
    NEURAL_AVAILABLE = False

try:
    from core.memory.collective_memory import CollectiveMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

logger = logging.getLogger(__name__)


class GOLEMCore(SimpleGOLEM):
    """
    Full GOLEM with all advanced systems
    Extends the simple version
    """
    
    def __init__(self):
        super().__init__()
        
        # Advanced systems (initialized in setup_hook)
        self.quantum_core = None
        self.collective_memory = None
        self.systems_status = {
            'quantum': False,
            'neural': False,
            'memory': False,
            'evolution': False,
            'scaling': False
        }
        
    async def setup_hook(self):
        """Initialize all systems"""
        await super().setup_hook()
        
        # Initialize advanced systems
        await self._init_quantum()
        await self._init_memory()
        await self._init_neural()
        
        # Add advanced commands
        self._add_advanced_commands()
        
        logger.info(f"🧬 Systems Status: {self._get_systems_summary()}")
        
    async def _init_quantum(self):
        """Initialize Quantum Core if available"""
        if QUANTUM_AVAILABLE:
            try:
                from core.quantum import transcend as quantum_transcend
                self.quantum_core = quantum_transcend()
                self.systems_status['quantum'] = True
                logger.info("⚛️ Quantum Core initialized")
            except Exception as e:
                logger.warning(f"Quantum Core initialization failed: {e}")
                
    async def _init_memory(self):
        """Initialize Collective Memory if available"""
        if MEMORY_AVAILABLE:
            try:
                self.collective_memory = CollectiveMemory(self)
                await self.collective_memory.start()
                self.systems_status['memory'] = True
                logger.info("💭 Collective Memory initialized")
            except Exception as e:
                logger.warning(f"Collective Memory initialization failed: {e}")
                
    async def _init_neural(self):
        """Check if Neural system is available"""
        if NEURAL_AVAILABLE:
            self.systems_status['neural'] = True
            logger.info("🤖 Neural Command system available")
            
    def _add_advanced_commands(self):
        """Add commands that use advanced systems"""
        
        @self.command(name='systems')
        async def systems_status(ctx: commands.Context):
            """Show advanced systems status"""
            embed = discord.Embed(
                title="🧬 GOLEM Systems Status",
                color=discord.Color.blue()
            )
            
            status_emoji = {
                True: "✅",
                False: "❌"
            }
            
            for system, active in self.systems_status.items():
                embed.add_field(
                    name=f"{status_emoji[active]} {system.title()}",
                    value="Active" if active else "Inactive",
                    inline=True
                )
                
            # Add system health if available
            if self.quantum_core and self.systems_status['quantum']:
                health = self.quantum_core.health
                embed.add_field(
                    name="⚛️ Quantum Health",
                    value=f"Coherence: {health.get('quantum_coherence', 0):.1%}",
                    inline=False
                )
                
            if self.collective_memory and self.systems_status['memory']:
                health = self.collective_memory.get_memory_health()
                embed.add_field(
                    name="💭 Memory Health",
                    value=f"Echoes: {health['total_echoes']} | Status: {health['health_status']}",
                    inline=False
                )
                
            await ctx.send(embed=embed)
            
        # Add quantum command if available
        if self.systems_status['quantum']:
            @self.command(name='quantum')
            async def quantum_test(ctx: commands.Context, *, message: str):
                """Process message through quantum core"""
                signal = Signal(
                    source=ctx.message,
                    intent="command",
                    context={
                        'content': message,
                        'author': ctx.author,
                        'command': 'quantum'
                    }
                )
                
                response = await self.quantum_core.receive(signal)
                
                embed = discord.Embed(
                    title="⚛️ Quantum Response",
                    description=response.content or "Quantum fluctuation detected",
                    color=discord.Color.purple()
                )
                embed.add_field(
                    name="Confidence",
                    value=f"{response.confidence:.1%}",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
        # Add memory command if available
        if self.systems_status['memory']:
            @self.command(name='remember')
            async def remember(ctx: commands.Context, *, memory: str):
                """Store something in collective memory"""
                from core.memory.collective_memory import EchoType
                
                echo = await self.collective_memory.add_echo(
                    content=memory,
                    author_id=ctx.author.id,
                    echo_type=EchoType.MEMORY,
                    weight=2.0
                )
                
                embed = discord.Embed(
                    title="💭 Memory Stored",
                    description=f"I'll remember: *{memory}*",
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"Echo ID: {echo.id}")
                
                await ctx.send(embed=embed)
                
            @self.command(name='recall')
            async def recall(ctx: commands.Context, *, query: Optional[str] = None):
                """Recall memories"""
                echoes = await self.collective_memory.search_echoes(
                    query=query,
                    author_id=ctx.author.id if not query else None,
                    limit=3
                )
                
                if not echoes:
                    await ctx.send("No memories found.")
                    return
                    
                embed = discord.Embed(
                    title="🌟 Recalled Memories",
                    color=discord.Color.blue()
                )
                
                for i, echo in enumerate(echoes, 1):
                    embed.add_field(
                        name=f"Memory {i}",
                        value=echo.content[:100] + "..." if len(echo.content) > 100 else echo.content,
                        inline=False
                    )
                    
                await ctx.send(embed=embed)
                
        # Add neural command example if available  
        if self.systems_status['neural']:
            @self.command(name='learn')
            async def learn_example(ctx: commands.Context, *, text: str = "Hello"):
                """A command that learns from usage"""
                # Mark as neural command for future use
                response = f"Processing: {text}\n*This command improves with each use!*"
                
                embed = discord.Embed(
                    title="🤖 Neural Command",
                    description=response,
                    color=discord.Color.green()
                )
                embed.set_footer(text="Powered by Neural Learning")
                
                await ctx.send(embed=embed)
            
            # Mark it as neural
            learn_example.__neural__ = True
                
    def _get_systems_summary(self):
        """Get summary of active systems"""
        active = [name for name, status in self.systems_status.items() if status]
        return f"{len(active)}/{len(self.systems_status)} systems active"
        
    async def on_message(self, message: discord.Message):
        """Process messages through quantum core if available"""
        if message.author.bot:
            return
            
        # Store in collective memory if available
        if self.collective_memory and self.systems_status['memory'] and message.content:
            try:
                from core.memory.collective_memory import EchoType
                await self.collective_memory.add_echo(
                    content=message.content,
                    author_id=message.author.id,
                    echo_type=EchoType.INTERACTION,
                    weight=1.0
                )
            except Exception as e:
                logger.debug(f"Memory storage failed: {e}")
                
        # Process through quantum core if available
        if self.quantum_core and self.systems_status['quantum']:
            try:
                signal = Signal(
                    source=message,
                    intent="message",
                    context={
                        'content': message.content,
                        'author': message.author,
                        'channel': message.channel
                    }
                )
                
                response = await self.quantum_core.receive(signal)
                # Quantum core processes but doesn't auto-respond
            except Exception as e:
                logger.debug(f"Quantum processing failed: {e}")
                
        # Continue with normal command processing
        await self.process_commands(message)
        
    async def close(self):
        """Graceful shutdown"""
        logger.info("🌙 GOLEM shutting down...")
        
        # Stop collective memory
        if self.collective_memory and self.systems_status['memory']:
            await self.collective_memory.stop()
            
        await super().close()


def transcend_core():
    """Create a full GOLEM instance with all systems"""
    return GOLEMCore()


# For backward compatibility
transcend = transcend_core
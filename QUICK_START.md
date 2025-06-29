# 🚀 GOLEM Quick Start

## 1. Install
```bash
./install.sh
```

## 2. Configure
Edit `.env` file:
```
DISCORD_TOKEN=your_bot_token_here
```

## 3. Run
```bash
source venv/bin/activate
python run.py
```

## 4. Test Commands
- `/help` - Show available commands
- `/ping` - Check bot latency
- `/status` - Show bot status
- `/hello` - Simple greeting

## 🎯 That's it!

The bot is now running and ready to evolve.

### Next Steps
- Add more commands in `golem_simple.py`
- Enable advanced features from `core/`
- Watch the bot evolve itself

## 🧬 Extending GOLEM

### Add a Command
```python
@bot.command(name='mycommand')
async def my_command(ctx):
    await ctx.send("Hello from my command!")
```

### Enable Neural Commands
```python
from core.neural import neural_command

@bot.command()
@neural_command()
async def smart_command(ctx):
    # This command learns!
    pass
```

### Add Self-Assembling Module
```python
from core.self_assembly import SelfAssemblingModule

class MyModule(SelfAssemblingModule):
    async def process(self, input):
        return "Processed!"
```

## 🌟 Philosophy

Start simple. Let it evolve.
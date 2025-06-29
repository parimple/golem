"""
GOLEM Example - The Simplest Discord Bot
Inspired by Tesla's "No Part is the Best Part" philosophy
"""
import os
from golem import transcend

# This is literally all you need
bot = transcend()

# Run with your token
if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("Set DISCORD_TOKEN environment variable")
#!/usr/bin/env python3
"""
Main entry point for configurable Discord bot
Can run as BOHT, zgdk, or GOLEM based on environment variables
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.bot_factory import create_bot
from config.bot_profiles import get_available_profiles

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
    # Get bot profile from environment
    profile = os.getenv('BOT_PROFILE', 'GOLEM').upper()
    
    # Validate profile
    available = get_available_profiles()
    if profile not in available:
        logger.error(f"❌ Invalid BOT_PROFILE: {profile}")
        logger.info(f"Available profiles: {', '.join(available)}")
        sys.exit(1)
    
    # Get token based on profile
    token_var = f"DISCORD_TOKEN_{profile}"
    token = os.getenv(token_var) or os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error(f"❌ No token found! Set {token_var} or DISCORD_TOKEN in .env")
        sys.exit(1)
    
    # Create bot instance
    logger.info(f"🚀 Starting bot with profile: {profile}")
    bot = create_bot(profile)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
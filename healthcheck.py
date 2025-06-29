#!/usr/bin/env python3
"""
Simple healthcheck endpoint for GOLEM
Can be used by monitoring systems
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from golem_simple import GOLEM


async def health_check():
    """Perform health check on GOLEM systems"""
    health_data = {
        "status": "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    try:
        # Create bot instance
        bot = GOLEM()
        
        # Check bot initialization
        health_data["checks"]["bot_init"] = "ok"
        
        # Check cogs can be loaded
        await bot.setup_hook()
        health_data["checks"]["cogs_loaded"] = len(bot.cogs_loaded)
        
        # Check configuration
        if bot.config:
            health_data["checks"]["config"] = "ok"
        else:
            health_data["checks"]["config"] = "missing"
        
        # Overall status
        if all(v == "ok" or isinstance(v, int) for v in health_data["checks"].values()):
            health_data["status"] = "healthy"
        else:
            health_data["status"] = "degraded"
            
        await bot.close()
        
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["error"] = str(e)
    
    return health_data


def main():
    """Run health check and output JSON"""
    health = asyncio.run(health_check())
    print(json.dumps(health, indent=2))
    
    # Exit with appropriate code
    if health["status"] == "healthy":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
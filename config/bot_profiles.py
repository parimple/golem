"""
Bot profiles configuration
Defines different bot personalities and module sets
"""
from typing import Dict, List, Any

# Bot profiles configuration
BOT_PROFILES = {
    "BOHT": {
        "name": "BOHT",
        "description": "Bot Oficjalny Hejt Team",
        "prefix": ",",
        "presence": {
            "type": "watching",
            "text": "serwer | {prefix}help"
        },
        "modules": [
            "cogs.commands.economy",
            "cogs.commands.activity_db", 
            "cogs.commands.moderation",
            "cogs.commands.reputation_db",
            "cogs.commands.interactions",
            "cogs.commands.fun",
            "cogs.commands.voice_db",
            "cogs.commands.premium",
            "cogs.commands.hello",
            "cogs.commands.monitor",
            "cogs.commands.snipe"
        ],
        "features": {
            "reputation_negative": True,
            "economy_daily_amount": 1000,
            "activity_xp_rate": 1.0,
            "premium_roles": ["VIP", "Premium", "Supporter"],
            "language": "pl"
        },
        "colors": {
            "primary": 0x7289da,  # Discord blue
            "success": 0x43b581,
            "error": 0xf04747,
            "warning": 0xfaa61a
        }
    },
    
    "zgdk": {
        "name": "zgdk", 
        "description": "zaGadka Bot",
        "prefix": ",",
        "presence": {
            "type": "playing",
            "text": "zaGadka | {prefix}help"
        },
        "modules": [
            "cogs.commands.economy",
            "cogs.commands.activity_db",
            "cogs.commands.moderation", 
            "cogs.commands.fun",
            "cogs.commands.voice_db",
            "cogs.commands.premium",
            "cogs.commands.hello"
        ],
        "features": {
            "reputation_negative": False,  # zgdk doesn't have negative rep
            "economy_daily_amount": 500,
            "activity_xp_rate": 1.5,
            "premium_roles": ["Premium"],
            "language": "pl"
        },
        "colors": {
            "primary": 0x9b59b6,  # Purple
            "success": 0x2ecc71,
            "error": 0xe74c3c,
            "warning": 0xf39c12
        }
    },
    
    "GOLEM": {
        "name": "GOLEM",
        "description": "Greatest Omnipotent Learning Entity Machine",
        "prefix": "!",
        "presence": {
            "type": "watching",
            "text": "reality unfold | {prefix}help"
        },
        "modules": [
            "cogs.commands.economy",
            "cogs.commands.activity_db",
            "cogs.commands.moderation",
            "cogs.commands.reputation_db",
            "cogs.commands.interactions",
            "cogs.commands.fun",
            "cogs.commands.voice_db",
            "cogs.commands.premium",
            "cogs.commands.hello",
            "cogs.commands.monitor",
            "cogs.commands.snipe",
            # GOLEM exclusive modules
            "cogs.advanced.quantum",
            "cogs.advanced.neural",
            "cogs.advanced.collective_memory"
        ],
        "features": {
            "reputation_negative": True,
            "economy_daily_amount": 2000,
            "activity_xp_rate": 2.0,
            "premium_roles": ["Quantum", "Neural", "Transcendent"],
            "language": "multi",  # Multiple languages
            "advanced_mode": True,
            "ai_learning": True,
            "quantum_processing": True
        },
        "colors": {
            "primary": 0x00d4ff,  # Cyan
            "success": 0x00ff88,
            "error": 0xff0044,
            "warning": 0xffaa00,
            "quantum": 0x8000ff  # Purple for quantum features
        }
    }
}

def get_bot_profile(profile_name: str) -> Dict[str, Any]:
    """Get bot profile configuration"""
    profile = BOT_PROFILES.get(profile_name.upper(), BOT_PROFILES["GOLEM"])
    return profile

def get_available_profiles() -> List[str]:
    """Get list of available bot profiles"""
    return list(BOT_PROFILES.keys())
#!/usr/bin/env python3
"""
GOLEM Bot Runner
Choose your transcendence level and environment
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_banner():
    """Show GOLEM banner"""
    print("""
    ╔═══════════════════════════════════════╗
    ║           G O L E M                   ║
    ║   The Ultimate Discord Bot            ║
    ║                                       ║
    ║   Where complexity dies               ║
    ║   And simplicity transcends           ║
    ╚═══════════════════════════════════════╝
    """)

def load_environment(env: str = "prod"):
    """Load environment configuration"""
    env_file = f".env.{env}"
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"❌ Environment file {env_file} not found!")
        print("Using default .env file")
        load_dotenv()
    else:
        print(f"📋 Loading {env} environment from {env_file}")
        load_dotenv(env_file, override=True)
        # Also load base .env for any missing values
        load_dotenv()

if __name__ == "__main__":
    show_banner()
    
    # Check for environment flag
    env = "prod"
    if "--env" in sys.argv:
        env_index = sys.argv.index("--env")
        if env_index + 1 < len(sys.argv):
            env = sys.argv[env_index + 1]
    
    # Load environment
    load_environment(env)
    
    # Show environment info
    prefix = os.getenv('COMMAND_PREFIX', ',')
    print(f"🌍 Environment: {env.upper()}")
    print(f"📝 Command prefix: {prefix}")
    
    # Check for --advanced flag
    if "--advanced" in sys.argv:
        print("🧬 Starting GOLEM in ADVANCED mode...")
        print("⚡ Quantum systems initializing...")
        from main import main
        main()
    else:
        print("🚀 Starting GOLEM in SIMPLE mode...")
        print("✨ All core features active")
        from golem_simple import main
        main()
    
    print("\nPress Ctrl+C to stop")
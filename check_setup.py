#!/usr/bin/env python3
"""
GOLEM Setup Checker
Verifies everything is ready to run
"""
import os
import sys

print("🔍 GOLEM Setup Checker")
print("=" * 50)

# Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")
if sys.version_info < (3, 9):
    print("  ⚠️  Python 3.9+ recommended")

# Check .env file
env_exists = os.path.exists('.env')
print(f"\n{'✓' if env_exists else '❌'} .env file: {'Found' if env_exists else 'Not found'}")

if env_exists:
    # Check for token
    with open('.env', 'r') as f:
        content = f.read()
        has_token = 'DISCORD_TOKEN=' in content and 'your_bot_token_here' not in content
        print(f"  {'✓' if has_token else '❌'} Discord token: {'Configured' if has_token else 'Not configured'}")
else:
    print("  ℹ️  Run: cp .env.example .env")
    has_token = False

# Check virtual environment
venv_exists = os.path.exists('venv')
print(f"\n{'✓' if venv_exists else '❌'} Virtual environment: {'Found' if venv_exists else 'Not found'}")
if not venv_exists:
    print("  ℹ️  Run: ./install.sh")

# Check requirements
try:
    import discord
    discord_installed = True
    print(f"\n✓ discord.py: Installed (v{discord.__version__})")
except ImportError:
    discord_installed = False
    print("\n❌ discord.py: Not installed")
    print("  ℹ️  Run: pip install -r requirements.txt")

# Check core modules
modules_ok = True
try:
    from golem_simple import GOLEM
    print("\n✓ GOLEM Simple: Ready")
except ImportError as e:
    print(f"\n❌ GOLEM Simple: Error - {e}")
    modules_ok = False

# Summary
print("\n" + "=" * 50)
print("📊 Summary:")

all_ready = env_exists and has_token and discord_installed and modules_ok

if all_ready:
    print("✅ Everything is ready! Run: python run.py")
else:
    print("❌ Setup incomplete. Please fix the issues above.")
    
    if not env_exists:
        print("\n1. Create .env file:")
        print("   cp .env.example .env")
    
    if env_exists and not has_token:
        print("\n2. Add Discord token to .env file")
        print("   - Get token from https://discord.com/developers/applications")
        print("   - Edit .env and replace 'your_bot_token_here' with actual token")
    
    if not venv_exists or not discord_installed:
        print("\n3. Install dependencies:")
        print("   ./install.sh")

print("\n💡 For a demo without Discord: python demo_simple.py")
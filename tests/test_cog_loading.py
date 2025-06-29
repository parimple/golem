#!/usr/bin/env python3
"""
Integration test for GOLEM cog loading
Ensures all cogs load properly after updates
"""

import asyncio
import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golem_simple import GOLEM
import discord
from discord.ext import commands


class TestCogLoading(unittest.TestCase):
    """Test that all cogs load successfully."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.bot = None
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up."""
        if cls.bot:
            cls.loop.run_until_complete(cls.bot.close())
        cls.loop.close()
    
    def test_bot_initialization(self):
        """Test bot can be initialized."""
        try:
            bot = GOLEM()
            self.assertIsInstance(bot, commands.Bot)
            self.assertEqual(bot.command_prefix, ',')
            # Don't run the bot, just test initialization
        except Exception as e:
            self.fail(f"Bot initialization failed: {e}")
    
    def test_cog_discovery(self):
        """Test that cogs can be discovered."""
        cogs_dir = Path("cogs/commands")
        self.assertTrue(cogs_dir.exists(), "Cogs directory not found")
        
        cog_files = list(cogs_dir.glob("*.py"))
        cog_files = [f for f in cog_files if not f.name.startswith("_")]
        
        self.assertGreater(len(cog_files), 0, "No cog files found")
        
        expected_cogs = [
            "hello.py",
            "economy.py", 
            "activity.py",
            "moderation.py",
            "voice.py",
            "premium.py",
            "fun.py",
            "monitor.py"
        ]
        
        found_cogs = [f.name for f in cog_files]
        for expected in expected_cogs:
            self.assertIn(expected, found_cogs, f"Expected cog {expected} not found")
    
    def test_cog_syntax(self):
        """Test that all cog files have valid Python syntax."""
        cogs_dir = Path("cogs/commands")
        errors = []
        
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
                
            try:
                with open(cog_file, 'r') as f:
                    compile(f.read(), cog_file, 'exec')
            except SyntaxError as e:
                errors.append(f"{cog_file.name}: {e}")
        
        self.assertEqual(len(errors), 0, f"Syntax errors found:\n" + "\n".join(errors))
    
    def test_cog_structure(self):
        """Test that cogs have required structure."""
        cogs_dir = Path("cogs/commands")
        
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
            
            with open(cog_file, 'r') as f:
                content = f.read()
            
            # Check for required elements
            self.assertIn("commands.Cog", content, 
                         f"{cog_file.name} doesn't inherit from commands.Cog")
            self.assertIn("async def setup(bot)", content,
                         f"{cog_file.name} missing setup function")
            self.assertIn("await bot.add_cog", content,
                         f"{cog_file.name} doesn't add cog in setup")


class TestCogLoadingAsync(unittest.TestCase):
    """Async tests for cog loading."""
    
    def setUp(self):
        """Set up for each test."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after each test."""
        self.loop.close()
    
    def test_async_cog_loading(self):
        """Test that cogs can actually be loaded."""
        async def _test():
            bot = GOLEM()
            loaded_cogs = []
            failed_cogs = []
            
            # Manually load each cog
            cogs_dir = Path("cogs/commands")
            for cog_file in cogs_dir.glob("*.py"):
                if cog_file.name.startswith("_"):
                    continue
                
                cog_name = f"cogs.commands.{cog_file.stem}"
                try:
                    await bot.load_extension(cog_name)
                    loaded_cogs.append(cog_name)
                except Exception as e:
                    failed_cogs.append((cog_name, str(e)))
            
            # Check results
            self.assertGreater(len(loaded_cogs), 0, "No cogs loaded successfully")
            self.assertEqual(len(failed_cogs), 0, 
                           f"Failed to load cogs:\n" + 
                           "\n".join([f"{name}: {error}" for name, error in failed_cogs]))
            
            # Check specific cogs are loaded
            expected_cogs = [
                "cogs.commands.hello",
                "cogs.commands.economy",
                "cogs.commands.activity",
                "cogs.commands.moderation",
                "cogs.commands.voice",
                "cogs.commands.premium",
                "cogs.commands.fun",
                "cogs.commands.monitor"
            ]
            
            for expected in expected_cogs:
                self.assertIn(expected, loaded_cogs, f"Expected cog {expected} not loaded")
            
            await bot.close()
        
        self.loop.run_until_complete(_test())


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCogLoading))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCogLoadingAsync))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
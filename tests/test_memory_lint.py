#!/usr/bin/env python3
"""
Memory lint test - check for empty echoes percentage
Fails if empty echoes exceed 5%
"""
import unittest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.collective_memory import CollectiveMemory, EchoType
from golem_simple import GOLEM


class TestMemoryLint(unittest.TestCase):
    """Test collective memory health"""
    
    def setUp(self):
        """Set up test environment"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        """Clean up"""
        self.loop.close()
    
    def test_memory_empty_percentage(self):
        """Test that empty echoes don't exceed 5%"""
        async def _test():
            # Create bot and memory
            bot = GOLEM()
            memory = CollectiveMemory(bot)
            
            # Simulate some data
            # Add 100 echoes, some empty
            for i in range(100):
                content = "" if i % 25 == 0 else f"Test echo {i}"  # 4% empty
                await memory.add_echo(
                    content=content,
                    author_id=12345,
                    echo_type=EchoType.MEMORY,
                    weight=1.0
                )
            
            # Get health metrics
            health = memory.get_memory_health()
            empty_percentage = health['empty_percentage']
            
            # Assert empty percentage is under 5%
            self.assertLess(
                empty_percentage,
                5.0,
                f"Empty echoes percentage too high: {empty_percentage:.2f}% (max 5%)"
            )
            
            # Also check health status
            self.assertEqual(
                health['health_status'],
                'healthy',
                f"Memory health status is {health['health_status']}, expected 'healthy'"
            )
            
            # Clean up
            await memory.stop()
            await bot.close()
        
        self.loop.run_until_complete(_test())
    
    def test_memory_snapshot(self):
        """Test memory snapshot functionality"""
        async def _test():
            bot = GOLEM()
            memory = CollectiveMemory(bot)
            
            # Add some test data
            for i in range(10):
                await memory.add_echo(
                    content=f"Snapshot test {i}",
                    author_id=54321,
                    echo_type=EchoType.WISDOM,
                    weight=float(i)
                )
            
            # Create snapshot
            snapshot = await memory.snapshot()
            
            # Verify snapshot structure
            self.assertIn('timestamp', snapshot)
            self.assertIn('total_echoes', snapshot)
            self.assertIn('layers', snapshot)
            self.assertIn('statistics', snapshot)
            
            # Verify statistics
            stats = snapshot['statistics']
            self.assertIn('empty_echoes', stats)
            self.assertIn('empty_percentage', stats)
            self.assertIn('average_weight', stats)
            
            # Verify echoes were captured
            self.assertEqual(snapshot['total_echoes'], 10)
            self.assertGreater(stats['average_weight'], 0)
            
            await memory.stop()
            await bot.close()
        
        self.loop.run_until_complete(_test())


def main():
    """Run memory lint tests"""
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMemoryLint))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
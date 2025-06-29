#!/usr/bin/env python3
"""
Memory Lint - Check collective memory health
Warns if empty echo percentage exceeds threshold
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.memory.collective_memory import CollectiveMemory, EchoType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryLinter:
    """Linter for collective memory health"""
    
    def __init__(self, warning_threshold: float = 5.0):
        self.warning_threshold = warning_threshold
        self.errors = []
        self.warnings = []
    
    async def lint_memory(self, memory: CollectiveMemory) -> bool:
        """
        Lint the collective memory for issues
        Returns True if healthy, False if issues found
        """
        health = memory.get_memory_health()
        
        # Check empty echo percentage
        empty_percentage = health["empty_percentage"]
        total_echoes = health["total_echoes"]
        empty_echoes = health["empty_echoes"]
        
        if empty_percentage > self.warning_threshold:
            self.warnings.append(
                f"⚠️  Empty echo percentage ({empty_percentage:.1f}%) exceeds threshold ({self.warning_threshold}%)"
            )
            self.warnings.append(
                f"   Found {empty_echoes} empty echoes out of {total_echoes} total"
            )
        
        # Check layer distribution
        layers = health["layers"]
        if layers.get("immediate", 0) > 1000:
            self.warnings.append(
                f"⚠️  Immediate layer is getting full: {layers['immediate']} echoes"
            )
        
        # Check for no echoes
        if total_echoes == 0:
            self.warnings.append("⚠️  No echoes found in collective memory")
        
        # Report results
        if self.warnings:
            logger.warning("Memory lint found issues:")
            for warning in self.warnings:
                logger.warning(warning)
            return False
        else:
            logger.info(f"✅ Memory is healthy: {total_echoes} echoes, {empty_percentage:.1f}% empty")
            return True
    
    async def generate_test_data(self, memory: CollectiveMemory, empty_ratio: float = 0.1):
        """Generate test data for linting"""
        total_echoes = 100
        empty_count = int(total_echoes * empty_ratio)
        
        for i in range(total_echoes):
            if i < empty_count:
                content = "   "  # Empty
            else:
                content = f"Test echo {i}: The memory lives on"
            
            await memory.add_echo(
                content=content,
                author_id=1000 + i,
                echo_type=EchoType.MEMORY
            )
        
        logger.info(f"Generated {total_echoes} test echoes ({empty_count} empty)")


async def main():
    """Main linting function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Lint collective memory for health issues")
    parser.add_argument(
        "--threshold", 
        type=float, 
        default=5.0,
        help="Warning threshold for empty echo percentage (default: 5.0)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Generate test data for linting"
    )
    parser.add_argument(
        "--empty-ratio",
        type=float,
        default=0.1,
        help="Ratio of empty echoes for test data (default: 0.1)"
    )
    
    args = parser.parse_args()
    
    # Create mock bot for testing
    class MockBot:
        pass
    
    bot = MockBot()
    memory = CollectiveMemory(bot)
    
    try:
        await memory.start()
        
        linter = MemoryLinter(warning_threshold=args.threshold)
        
        if args.test:
            await linter.generate_test_data(memory, args.empty_ratio)
        
        # Run lint
        is_healthy = await linter.lint_memory(memory)
        
        # Create snapshot for inspection
        snapshot = await memory.snapshot()
        logger.info(f"Snapshot created with {snapshot['total_echoes']} echoes")
        
        # Exit with appropriate code
        sys.exit(0 if is_healthy else 1)
        
    finally:
        await memory.stop()


if __name__ == "__main__":
    asyncio.run(main())
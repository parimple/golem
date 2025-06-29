"""
GOLEM - The Tesla/Apple of Discord Bots
Simple. Powerful. Transcendent.
"""
import os
import sys
import logging

logger = logging.getLogger(__name__)

# Determine which version to use based on environment
USE_SIMPLE = os.getenv('GOLEM_SIMPLE', 'true').lower() == 'true'

if USE_SIMPLE:
    # Use simple version for quick start
    from golem_simple import transcend, GOLEM, main
    logger.info("Using GOLEM Simple version")
else:
    # Use full version with all features
    try:
        from golem_core import transcend_core as transcend, GOLEMCore as GOLEM
        from golem_simple import main  # Still use simple main
        logger.info("Using GOLEM Core version with advanced features")
    except ImportError as e:
        logger.warning(f"Failed to load GOLEM Core: {e}")
        logger.info("Falling back to GOLEM Simple version")
        from golem_simple import transcend, GOLEM, main

# For backward compatibility with examples
from golem_simple import neural_command

# Export main components
__all__ = ['transcend', 'GOLEM', 'main', 'neural_command']

if __name__ == "__main__":
    main()
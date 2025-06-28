#!/usr/bin/env python3
"""Test script to demonstrate logging functionality"""

import asyncio
import logging
import pytest
from agent.flow import create_general_agent_flow

def test_logging_levels():
    """Test different logging levels"""
    
    print("🧪 Testing Logging Levels")
    print("=" * 50)
    
    # Test INFO level
    print("\n📝 INFO Level Logging:")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger('test')
    
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test DEBUG level
    print("\n🔍 DEBUG Level Logging:")
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger('test')
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    
    # Test ERROR level only
    print("\n🔇 ERROR Level Only Logging:")
    logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger('test')
    
    logger.info("This info message should not appear")
    logger.warning("This warning message should not appear")
    logger.error("This error message should appear")

@pytest.mark.asyncio
async def test_workflow_logging():
    """Test workflow execution with logging"""
    
    print("\n🚀 Testing Workflow with Logging:")
    print("=" * 50)
    
    # Setup INFO logging for workflow test
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger('test_workflow')
    
    logger.info("Starting workflow test")
    
    # Create a simple shared store
    shared_store = {
        "user_message": "Test workflow with logging",
        "conversation_history": []
    }
    
    # Create and run flow
    flow = create_general_agent_flow()
    
    try:
        logger.info("Executing workflow...")
        await flow.run_async(shared_store)
        logger.info("Workflow completed successfully")
    except Exception as e:
        logger.error(f"Workflow failed: {e}")

if __name__ == "__main__":
    # Test different logging levels
    test_logging_levels()
    
    # Test workflow logging
    asyncio.run(test_workflow_logging())
    
    print("\n✅ Logging tests completed!")
    print("\nUsage:")
    print("  python test_logging.py                    # Test all logging levels")
    print("  LOG_LEVEL=DEBUG python test_logging.py    # Set debug logging")
    print("  LOG_LEVEL=ERROR python test_logging.py    # Set error-only logging")

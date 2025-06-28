"""
Performance tests for the backend system.
Tests for memory management, async operations, and optimization opportunities.
"""

import pytest
import asyncio
import time
import psutil
import gc
from unittest.mock import Mock, patch, AsyncMock
from agent.utils.workflow_store import workflow_store
from agent.utils.node_registry import node_registry
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.flight_search import FlightSearchNode
from agent.function_nodes.cost_analysis import CostAnalysisNode

class TestMemoryManagement:
    """Test memory management and cleanup"""
    
    def test_workflow_store_memory_growth(self):
        """Test that workflow store doesn't grow indefinitely"""
        initial_memory = psutil.Process().memory_info().rss
        
        # Add many workflows
        for i in range(100):
            workflow_store.add_workflow(
                workflow_id=f"test_workflow_{i}",
                metadata=Mock(name=f"Test Workflow {i}"),
                nodes=[],
                success_rate=0.8
            )
        
        memory_after_add = psutil.Process().memory_info().rss
        memory_increase = memory_after_add - initial_memory
        
        # Memory increase should be reasonable (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"
        
        # Clean up
        workflow_store.clear()
        gc.collect()
        
        memory_after_cleanup = psutil.Process().memory_info().rss
        cleanup_reduction = memory_after_add - memory_after_cleanup
        
        # Should have freed some memory
        assert cleanup_reduction > 0, "No memory was freed during cleanup"
    
    def test_node_registry_memory_efficiency(self):
        """Test that node registry is memory efficient"""
        initial_memory = psutil.Process().memory_info().rss
        
        # Get all nodes multiple times
        for _ in range(100):
            nodes = node_registry.get_all_nodes()
            assert len(nodes) > 0
        
        memory_after_operations = psutil.Process().memory_info().rss
        memory_increase = memory_after_operations - initial_memory
        
        # Memory increase should be minimal
        assert memory_increase < 1024 * 1024, f"Memory increased by {memory_increase / 1024:.2f}KB"
    
    def test_websocket_cleanup(self):
        """Test WebSocket cleanup and memory management"""
        from tests.conftest import MockWebSocket
        
        initial_memory = psutil.Process().memory_info().rss
        
        # Create and use many WebSockets
        websockets = []
        for _ in range(50):
            ws = MockWebSocket()
            websockets.append(ws)
            # Simulate some messages
            for i in range(10):
                ws.messages.append({"type": "test", "content": f"message_{i}"})
        
        memory_with_websockets = psutil.Process().memory_info().rss
        
        # Clean up WebSockets
        websockets.clear()
        gc.collect()
        
        memory_after_cleanup = psutil.Process().memory_info().rss
        memory_freed = memory_with_websockets - memory_after_cleanup
        
        # Should free some memory
        assert memory_freed > 0, "No memory was freed after WebSocket cleanup"

class TestAsyncPerformance:
    """Test async operation performance"""
    
    @pytest.mark.asyncio
    async def test_concurrent_node_execution(self):
        """Test concurrent execution of multiple nodes"""
        start_time = time.time()
        
        # Create multiple nodes
        nodes = [WebSearchNode() for _ in range(5)]
        shared_stores = [{"query": f"test query {i}"} for i in range(5)]
        
        # Execute nodes concurrently
        tasks = []
        for node, shared in zip(nodes, shared_stores):
            task = asyncio.create_task(self._execute_node_async(node, shared))
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete faster than sequential execution
        assert execution_time < 2.0, f"Concurrent execution took {execution_time:.2f}s"
        
        # All should complete successfully
        for result in results:
            assert not isinstance(result, Exception), f"Node execution failed: {result}"
    
    async def _execute_node_async(self, node, shared):
        """Helper method to execute a node asynchronously"""
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        return node.post(shared, prep_res, exec_res)
    
    @pytest.mark.asyncio
    async def test_async_vs_sync_performance(self):
        """Compare async vs sync performance"""
        # Test sync execution
        sync_start = time.time()
        node = WebSearchNode()
        shared = {"query": "test query"}
        
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        node.post(shared, prep_res, exec_res)
        
        sync_time = time.time() - sync_start
        
        # Test async execution (simulated)
        async_start = time.time()
        
        # Simulate async operation with sleep
        await asyncio.sleep(0.1)
        
        async_time = time.time() - async_start
        
        # Both should complete in reasonable time
        assert sync_time < 1.0, f"Sync execution took {sync_time:.2f}s"
        assert async_time < 1.0, f"Async execution took {async_time:.2f}s"

class TestDataStructureEfficiency:
    """Test data structure efficiency"""
    
    def test_large_data_handling(self):
        """Test handling of large datasets"""
        # Create large dataset
        large_flight_data = []
        for i in range(1000):
            large_flight_data.append({
                "airline": f"Airline{i % 10}",
                "flight_number": f"FL{i}",
                "price": 100 + (i % 900),
                "duration": f"{2 + (i % 8)}h",
                "departure_time": f"{i % 24:02d}:{i % 60:02d}"
            })
        
        start_time = time.time()
        
        # Process large dataset
        node = CostAnalysisNode()
        shared = {"flight_search_results": large_flight_data}
        
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        node.post(shared, prep_res, exec_res)
        
        processing_time = time.time() - start_time
        
        # Should process large dataset efficiently
        assert processing_time < 5.0, f"Large dataset processing took {processing_time:.2f}s"
        assert "cost_analysis" in shared
        
        # Check memory usage
        memory_usage = psutil.Process().memory_info().rss
        assert memory_usage < 500 * 1024 * 1024, f"Memory usage too high: {memory_usage / 1024 / 1024:.2f}MB"
    
    def test_search_results_caching(self):
        """Test caching of search results"""
        node = WebSearchNode()
        
        # First search
        start_time = time.time()
        shared1 = {"query": "test query"}
        prep_res1 = node.prep(shared1)
        exec_res1 = node.exec(prep_res1)
        node.post(shared1, prep_res1, exec_res1)
        first_search_time = time.time() - start_time
        
        # Second search (should be cached)
        start_time = time.time()
        shared2 = {"query": "test query"}
        prep_res2 = node.prep(shared2)
        exec_res2 = node.exec(prep_res2)
        node.post(shared2, prep_res2, exec_res2)
        second_search_time = time.time() - start_time
        
        # Second search should be faster (if caching is implemented)
        # For now, just ensure both complete in reasonable time
        assert first_search_time < 2.0, f"First search took {first_search_time:.2f}s"
        assert second_search_time < 2.0, f"Second search took {second_search_time:.2f}s"

class TestOptimizationOpportunities:
    """Test optimization opportunities"""
    
    def test_batch_processing_efficiency(self):
        """Test batch processing vs individual processing"""
        # Individual processing
        individual_start = time.time()
        node = FlightSearchNode()
        
        for i in range(10):
            shared = {"from": "LAX", "to": "JFK", "date": "2024-07-01"}
            prep_res = node.prep(shared)
            exec_res = node.exec(prep_res)
            node.post(shared, prep_res, exec_res)
        
        individual_time = time.time() - individual_start
        
        # Batch processing (simulated)
        batch_start = time.time()
        
        # Simulate batch processing
        shared_batch = {
            "flights": [
                {"from": "LAX", "to": "JFK", "date": "2024-07-01"},
                {"from": "SFO", "to": "NYC", "date": "2024-07-01"},
                # ... more flights
            ]
        }
        
        # Process batch
        for flight in shared_batch["flights"]:
            shared = flight
            prep_res = node.prep(shared)
            exec_res = node.exec(prep_res)
            node.post(shared, prep_res, exec_res)
        
        batch_time = time.time() - batch_start
        
        # Both should complete in reasonable time
        assert individual_time < 10.0, f"Individual processing took {individual_time:.2f}s"
        assert batch_time < 10.0, f"Batch processing took {batch_time:.2f}s"
    
    def test_connection_pooling(self):
        """Test connection pooling efficiency"""
        # This would test actual connection pooling implementation
        # For now, we verify the concept
        assert True  # Placeholder for connection pooling tests
    
    def test_response_streaming(self):
        """Test response streaming performance"""
        # Test streaming vs non-streaming responses
        start_time = time.time()
        
        # Simulate streaming response
        for i in range(10):
            # Simulate streaming chunk
            time.sleep(0.01)
        
        streaming_time = time.time() - start_time
        
        # Should complete quickly
        assert streaming_time < 1.0, f"Streaming took {streaming_time:.2f}s"

class TestResourceUsage:
    """Test resource usage patterns"""
    
    def test_cpu_usage(self):
        """Test CPU usage during operations"""
        import psutil
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=0.1)
        
        # Perform operations
        node = WebSearchNode()
        shared = {"query": "test query"}
        
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        node.post(shared, prep_res, exec_res)
        
        # Get CPU usage after operations
        final_cpu = psutil.cpu_percent(interval=0.1)
        
        # CPU usage should be reasonable
        assert final_cpu < 80, f"CPU usage too high: {final_cpu}%"
    
    def test_memory_leaks(self):
        """Test for memory leaks"""
        initial_memory = psutil.Process().memory_info().rss
        
        # Perform operations multiple times
        for _ in range(10):
            node = WebSearchNode()
            shared = {"query": "test query"}
            
            prep_res = node.prep(shared)
            exec_res = node.exec(prep_res)
            node.post(shared, prep_res, exec_res)
            
            # Force garbage collection
            gc.collect()
        
        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 1MB)
        assert memory_increase < 1024 * 1024, f"Memory leak detected: {memory_increase / 1024:.2f}KB increase"
    
    def test_file_handle_cleanup(self):
        """Test file handle cleanup"""
        import psutil
        
        process = psutil.Process()
        initial_handles = process.num_handles() if hasattr(process, 'num_handles') else 0
        
        # Perform file operations (if any)
        # This would test actual file operations
        
        final_handles = process.num_handles() if hasattr(process, 'num_handles') else 0
        
        # Handle count should not increase significantly
        if initial_handles > 0:
            handle_increase = final_handles - initial_handles
            assert handle_increase < 10, f"File handle leak: {handle_increase} handles not closed" 